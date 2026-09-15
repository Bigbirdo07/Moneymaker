"""
Tests for Phase 5A Governed Micro-Capital Pilot.
Validates:
1. ExecutionMode.LIVE remains fatally blocked, while LIVE_GOVERNED_MICRO is permitted under governance.
2. Account holdings audit (strictly cash + approved positions, zero margin, max $1,000 capital).
3. Session arming manager (daily tokens, hash verification, exclusive lock).
4. Human approval gate (card display, 30s expiration, pre-submit staleness check, selection bias audit).
5. Staged notional sizing ($25 -> $50 -> $100).
6. Tri-Book tracking & live execution penalty analysis.
7. End-to-end governed live decision loop execution with failsafe kill switches.
"""

from datetime import datetime, timedelta, timezone
import os
import pytest
import pandas as pd
import numpy as np

from src.broker.adapter import (
    BrokerAccount,
    BrokerOrder,
    BrokerPosition,
    ExecutionMode,
    MockBrokerPaperAdapter,
    OrderStatus,
    OrderSide,
    OrderType,
    verify_execution_mode,
)
from src.data.market_provider import ReplayMarketDataProvider, QuoteEvent, BarEvent
from src.governance.human_approval import (
    ApprovalAction,
    HumanApprovalGate,
    HumanApprovalRecord,
    ProposedOrderCard,
)
from src.governance.session_arming import (
    SessionArmingError,
    SessionArmingManager,
    SessionAuthorizationToken,
)
from src.governance.governed_loop import (
    GovernedMicroDecisionLoop,
    TriBookComparison,
)


def _make_quote(symbol: str, price: float = 125.0, spread_bps: float = 2.0, ts: pd.Timestamp = None) -> QuoteEvent:
    if ts is None:
        ts = pd.Timestamp("2026-09-15 14:00:00", tz=timezone.utc)
    half_spread = price * (spread_bps / 20000.0)
    return QuoteEvent(
        symbol=symbol,
        bid=price - half_spread,
        ask=price + half_spread,
        bid_size=100.0,
        ask_size=100.0,
        exchange_timestamp=ts - pd.Timedelta(milliseconds=15),
        provider_timestamp=ts - pd.Timedelta(milliseconds=5),
        received_timestamp=ts,
    )


def _make_bars(symbol: str, count: int = 20, base_price: float = 100.0, end_ts: pd.Timestamp = None) -> list[BarEvent]:
    if end_ts is None:
        end_ts = pd.Timestamp("2026-09-15 14:00:00", tz=timezone.utc)
    bars = []
    for i in range(count):
        close_ts = end_ts - pd.Timedelta(minutes=(count - 1 - i) * 5)
        start_ts = close_ts - pd.Timedelta(minutes=5)
        px = base_price + (i * 0.1)
        b = BarEvent(
            symbol=symbol,
            timeframe="5m",
            open=px,
            high=px + 0.4,
            low=px - 0.4,
            close=px + 0.1,
            volume=50000.0,
            vwap=px + 0.05,
            bar_start_timestamp=start_ts,
            bar_close_timestamp=close_ts,
            provider_timestamp=close_ts + pd.Timedelta(milliseconds=10),
            received_timestamp=close_ts + pd.Timedelta(milliseconds=20),
        )
        bars.append(b)
    return bars


def test_live_execution_mode_fatal_block_and_governed_micro():
    """Verify unrestricted LIVE remains prohibited while LIVE_GOVERNED_MICRO is allowed."""
    with pytest.raises(RuntimeError, match="Unrestricted LIVE money execution is strictly prohibited"):
        verify_execution_mode(ExecutionMode.LIVE)

    # LIVE_GOVERNED_MICRO, SHADOW, and BROKER_PAPER pass without error
    verify_execution_mode(ExecutionMode.LIVE_GOVERNED_MICRO)
    verify_execution_mode(ExecutionMode.SHADOW)
    verify_execution_mode(ExecutionMode.BROKER_PAPER)


def test_account_holdings_audit_clean_and_violations():
    """Test account hygiene: reject unrelated assets, shorting, margin, and excess capital."""
    broker = MockBrokerPaperAdapter(account_id="PILOT_ACC_001", initial_cash=1000.0)
    manager = SessionArmingManager(broker=broker, approved_account_id="PILOT_ACC_001", max_live_capital_usd=1000.0)

    # 1. Clean account
    clean, msg = manager.audit_account_holdings()
    assert clean is True
    assert "VERIFIED_CLEAN" in msg

    # 2. Capital ceiling breach
    broker_rich = MockBrokerPaperAdapter(account_id="PILOT_ACC_001", initial_cash=25000.0)
    manager_rich = SessionArmingManager(broker=broker_rich, approved_account_id="PILOT_ACC_001", max_live_capital_usd=1000.0)
    clean, msg = manager_rich.audit_account_holdings()
    assert clean is False
    assert "CAPITAL_CEILING_EXCEEDED" in msg

    # 3. Unrelated asset (e.g. AAPL or ETF within capital limit)
    broker.cash = 900.0
    broker._positions["SPY"] = BrokerPosition(
        symbol="SPY", qty=1, avg_entry_price=100.0, current_price=100.0, market_value=100.0, unrealized_pnl=0.0
    )
    clean, msg = manager.audit_account_holdings()
    assert clean is False
    assert "FORBIDDEN_ASSET_DETECTED" in msg
    del broker._positions["SPY"]
    broker.cash = 1000.0

    # 4. Short position
    broker._positions["NVDA"] = BrokerPosition(
        symbol="NVDA", qty=-5, avg_entry_price=120.0, current_price=120.0, market_value=-600.0, unrealized_pnl=0.0
    )
    clean, msg = manager.audit_account_holdings()
    assert clean is False
    assert "SHORT_POSITION_DETECTED" in msg
    del broker._positions["NVDA"]

    # 5. Margin detected
    broker.get_account = lambda: BrokerAccount(
        account_id="PILOT_ACC_001", is_paper=True, cash=1000.0, buying_power=4000.0, portfolio_value=1000.0
    )
    clean, msg = manager.audit_account_holdings()
    assert clean is False
    assert "MARGIN_DETECTED" in msg


def test_session_arming_and_token_validation():
    """Test daily arming, hash verification, token expiry, and exclusive lock."""
    lock_path = "/tmp/test_session_arming.lock"
    if os.path.exists(lock_path):
        os.remove(lock_path)

    broker = MockBrokerPaperAdapter(account_id="PILOT_ACC_001", initial_cash=1000.0)
    manager = SessionArmingManager(
        broker=broker,
        approved_account_id="PILOT_ACC_001",
        max_live_capital_usd=1000.0,
        lock_file_path=lock_path,
    )

    # 1. Arming fails on model hash mismatch
    with pytest.raises(SessionArmingError, match="Model hash mismatch"):
        manager.arm_session(
            model_hash="HASH_MOD_A",
            expected_model_hash="HASH_MOD_B",
            config_hash="HASH_CFG_A",
            expected_config_hash="HASH_CFG_A",
            operator_arming_secret="SECRET_ARMING_KEY_12345",
        )

    # 2. Arming succeeds with correct parameters
    token = manager.arm_session(
        model_hash="HASH_MOD_A",
        expected_model_hash="HASH_MOD_A",
        config_hash="HASH_CFG_A",
        expected_config_hash="HASH_CFG_A",
        operator_arming_secret="SECRET_ARMING_KEY_12345",
    )
    assert token is not None
    assert token.is_valid() is True
    assert token.account_id == "PILOT_ACC_001"
    assert os.path.exists(lock_path)

    # 3. Second manager cannot acquire lock
    manager2 = SessionArmingManager(
        broker=broker,
        approved_account_id="PILOT_ACC_001",
        lock_file_path=lock_path,
    )
    with pytest.raises(SessionArmingError, match="Failed to acquire exclusive process execution lock"):
        manager2.arm_session(
            model_hash="HASH_MOD_A",
            expected_model_hash="HASH_MOD_A",
            config_hash="HASH_CFG_A",
            expected_config_hash="HASH_CFG_A",
            operator_arming_secret="SECRET_ARMING_KEY_12345",
        )

    # 4. Revocation clears token and lock
    manager.revoke_session()
    assert token.is_valid() is False
    assert not os.path.exists(lock_path)


def test_human_approval_gate_workflows():
    """Test proposal card rendering, human approval, rejection, 30s timeout, and pre-submit check."""
    gate = HumanApprovalGate(approval_timeout_seconds=30.0, max_allowed_spread_bps=3.0)
    now = pd.Timestamp("2026-09-15 14:00:00", tz=timezone.utc)

    card = ProposedOrderCard(
        proposal_id="PROP_001",
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        current_bid=125.00,
        current_ask=125.02,
        spread_bps=1.6,
        expected_alpha_bps=4.8,
        estimated_friction_bps=2.6,
        expected_net_edge_bps=2.2,
        model_confidence=0.62,
        rank=1,
        current_portfolio_exposure_usd=0.0,
        daily_realized_pnl_usd=0.0,
        max_allowed_loss_usd=20.0,
        trade_reason="Stage-A Micro-Pilot Entry",
        risk_engine_status="APPROVED",
    )

    rendered = card.render_display()
    assert "LIVE GOVERNED MICRO ORDER PROPOSAL" in rendered
    assert "NVDA" in rendered
    assert "$25.00 notional" in rendered

    # 1. Normal prompt approval (within 10s)
    gate.submit_proposal(card)
    quote = _make_quote("NVDA", price=125.0, spread_bps=1.6, ts=now + pd.Timedelta(seconds=5))
    can_exec, reason = gate.process_operator_action(
        proposal_id="PROP_001",
        operator_id="OPERATOR_1",
        action=ApprovalAction.APPROVE,
        current_time=now + pd.Timedelta(seconds=8),
        current_quote=quote,
    )
    assert can_exec is True
    assert reason == "APPROVED_FOR_EXECUTION"

    # 2. Expiration timeout (>30s)
    card2 = ProposedOrderCard(
        proposal_id="PROP_002",
        symbol="AMD",
        side="BUY",
        shares=0.15,
        notional_usd=25.0,
        decision_timestamp=now,
        current_bid=160.00,
        current_ask=160.03,
        spread_bps=1.8,
        expected_alpha_bps=4.2,
        estimated_friction_bps=2.8,
        expected_net_edge_bps=1.4,
        model_confidence=0.60,
        rank=1,
        current_portfolio_exposure_usd=25.0,
        daily_realized_pnl_usd=0.0,
        max_allowed_loss_usd=20.0,
        trade_reason="Stage-A Micro-Pilot Entry",
        risk_engine_status="APPROVED",
    )
    gate.submit_proposal(card2)
    can_exec2, reason2 = gate.process_operator_action(
        proposal_id="PROP_002",
        operator_id="OPERATOR_1",
        action=ApprovalAction.APPROVE,
        current_time=now + pd.Timedelta(seconds=35),  # 35 seconds later
    )
    assert can_exec2 is False
    assert "EXPIRED_TIMEOUT" in reason2

    # 3. Pre-submission stale quote rejection (>15s quote age or spread > 3.0 bps)
    card3 = ProposedOrderCard(
        proposal_id="PROP_003",
        symbol="TSLA",
        side="BUY",
        shares=0.10,
        notional_usd=25.0,
        decision_timestamp=now,
        current_bid=250.00,
        current_ask=250.05,
        spread_bps=2.0,
        expected_alpha_bps=5.0,
        estimated_friction_bps=3.0,
        expected_net_edge_bps=2.0,
        model_confidence=0.65,
        rank=1,
        current_portfolio_exposure_usd=25.0,
        daily_realized_pnl_usd=0.0,
        max_allowed_loss_usd=20.0,
        trade_reason="Stage-A Micro-Pilot Entry",
        risk_engine_status="APPROVED",
    )
    gate.submit_proposal(card3)
    blown_quote = _make_quote("TSLA", price=250.0, spread_bps=6.0, ts=now + pd.Timedelta(seconds=5))
    can_exec3, reason3 = gate.process_operator_action(
        proposal_id="PROP_003",
        operator_id="OPERATOR_1",
        action=ApprovalAction.APPROVE,
        current_time=now + pd.Timedelta(seconds=8),
        current_quote=blown_quote,
    )
    assert can_exec3 is False
    assert reason3 == "STALE_DATA_PRE_SUBMIT_CANCELLED"

    # 4. Explicit operator rejection
    card4 = ProposedOrderCard(
        proposal_id="PROP_004",
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        current_bid=125.00,
        current_ask=125.02,
        spread_bps=1.6,
        expected_alpha_bps=4.8,
        estimated_friction_bps=2.6,
        expected_net_edge_bps=2.2,
        model_confidence=0.62,
        rank=1,
        current_portfolio_exposure_usd=0.0,
        daily_realized_pnl_usd=0.0,
        max_allowed_loss_usd=20.0,
        trade_reason="Stage-A Micro-Pilot Entry",
        risk_engine_status="APPROVED",
    )
    gate.submit_proposal(card4)
    can_exec4, reason4 = gate.process_operator_action(
        proposal_id="PROP_004",
        operator_id="OPERATOR_1",
        action=ApprovalAction.REJECT,
        current_time=now + pd.Timedelta(seconds=5),
        reason_notes="FOMC statement imminent",
    )
    assert can_exec4 is False
    assert reason4 == "OPERATOR_REJECTED"

    # 5. Selection bias audit
    audit = gate.compute_selection_bias_audit()
    assert audit["total_proposals"] == 4
    assert audit["approved_count"] == 1
    assert audit["rejected_count"] == 1
    assert audit["expired_count"] == 1


def test_staged_notional_exposure_and_tri_book_tracking():
    """Test staged sizing ($25 -> $50 -> $100) and Tri-Book penalty calculation."""
    lock_path = "/tmp/test_staged_exposure.lock"
    if os.path.exists(lock_path):
        os.remove(lock_path)

    provider = ReplayMarketDataProvider()
    provider.connect()
    provider.subscribe(["NVDA", "AMD", "TSLA", "SPY"])

    broker = MockBrokerPaperAdapter(account_id="PILOT_ACC_001", initial_cash=1000.0)
    broker.connect()
    session_manager = SessionArmingManager(
        broker=broker,
        approved_account_id="PILOT_ACC_001",
        lock_file_path=lock_path,
    )

    session_manager.arm_session(
        model_hash="MOD_HASH",
        expected_model_hash="MOD_HASH",
        config_hash="CFG_HASH",
        expected_config_hash="CFG_HASH",
        operator_arming_secret="SECRET_ARMING_KEY_12345",
    )

    loop = GovernedMicroDecisionLoop(
        provider=provider,
        broker=broker,
        session_manager=session_manager,
        symbols=["NVDA", "AMD", "TSLA"],
        mode=ExecutionMode.LIVE_GOVERNED_MICRO,
    )

    # Initial Stage A: trades 0-9 -> $25
    assert loop.get_staged_max_notional_usd() == 25.0

    # Stage B: trades 10-39 -> $50
    loop.total_live_trades_executed = 15
    assert loop.get_staged_max_notional_usd() == 50.0

    # Stage C: trades 40+ -> $100
    loop.total_live_trades_executed = 45
    assert loop.get_staged_max_notional_usd() == 100.0

    # Test Tri-Book Comparison
    tri_comp = TriBookComparison(
        decision_id="PROP_TEST_01",
        symbol="NVDA",
        decision_midprice=125.00,
        live_fill_price=125.02,
        live_shortfall_bps=1.60,
        shadow_fill_price=125.018,
        shadow_shortfall_bps=1.44,
        paper_fill_price=125.02,
        paper_shortfall_bps=1.60,
    )
    assert abs(tri_comp.live_execution_penalty_bps - 0.16) < 1e-4

    session_manager.revoke_session()


def test_governed_micro_decision_loop_end_to_end_simulation():
    """Run an end-to-end multi-bar simulation of the governed micro-pilot decision loop."""
    lock_path = "/tmp/test_governed_loop_e2e.lock"
    if os.path.exists(lock_path):
        os.remove(lock_path)

    provider = ReplayMarketDataProvider()
    provider.connect()
    provider.subscribe(["NVDA", "AMD", "TSLA", "SPY"])

    broker = MockBrokerPaperAdapter(account_id="PILOT_ACC_001", initial_cash=1000.0)
    broker.connect()
    session_manager = SessionArmingManager(
        broker=broker,
        approved_account_id="PILOT_ACC_001",
        lock_file_path=lock_path,
    )

    session_manager.arm_session(
        model_hash="M123",
        expected_model_hash="M123",
        config_hash="C123",
        expected_config_hash="C123",
        operator_arming_secret="SECRET_ARMING_KEY_12345",
    )

    loop = GovernedMicroDecisionLoop(
        provider=provider,
        broker=broker,
        session_manager=session_manager,
        symbols=["NVDA", "AMD", "TSLA"],
        mode=ExecutionMode.LIVE_GOVERNED_MICRO,
        cooldown_bars=2,
        confidence_threshold=0.50,
        meta_threshold=0.45,
    )

    # Feed market data
    t0 = pd.Timestamp("2026-09-15 14:00:00", tz=timezone.utc)
    for sym in ["NVDA", "AMD", "TSLA", "SPY"]:
        px = 120.0 if sym == "NVDA" else (160.0 if sym == "AMD" else (250.0 if sym == "TSLA" else 500.0))
        bars = _make_bars(sym, count=20, base_price=px, end_ts=t0)
        for b in bars:
            provider.ingest_bar(b)

        quote = _make_quote(sym, price=px, spread_bps=1.5, ts=t0)
        provider.ingest_quote(quote)

    # 1. Generate proposals
    proposals = loop.generate_candidate_proposals(current_time=t0)
    assert len(proposals) == 1
    prop = proposals[0]
    assert prop.symbol == "NVDA"
    assert prop.notional_usd == 25.0 # Stage A notional

    # 2. Operator reviews and approves within 10 seconds
    t_review = t0 + pd.Timedelta(seconds=10)
    executed, status = loop.execute_approved_proposal(
        proposal_id=prop.proposal_id,
        operator_id="CHIEF_RISK_OFFICER",
        action=ApprovalAction.APPROVE,
        current_time=t_review,
        reason_notes="Valid Stage-A trade proposal",
    )
    assert executed is True
    assert status == "LIVE_ORDER_EXECUTED"
    assert loop.total_live_trades_executed == 1
    assert len(loop.tri_book_comparisons) == 1
    assert len(loop.shadow_portfolio.positions) == 1

    # 3. Verify reconciler is in sync
    is_clean, discrepancies = loop.reconciler.reconcile()
    assert is_clean is True
    assert len(discrepancies) == 0

    session_manager.revoke_session()
