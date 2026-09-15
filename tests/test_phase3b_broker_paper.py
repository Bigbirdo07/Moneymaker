"""
Comprehensive Test Suite for Phase 3B Broker Paper Trading & Execution Validation.
Covers absolute safety prohibition of LIVE mode, order state machine, idempotency,
reconciliation & mismatch freeze, crash recovery, failure/chaos injection, kill switch,
and dual execution ledger tracking.
"""

from datetime import datetime, timezone
import pytest
import numpy as np
import pandas as pd

from src.broker.adapter import (
    BrokerAdapter,
    BrokerOrder,
    BrokerAccount,
    BrokerPosition,
    ExecutionMode,
    OrderStatus,
    OrderSide,
    OrderType,
    MockBrokerPaperAdapter,
    verify_execution_mode,
)
from src.broker.reconciliation import (
    AccountReconciler,
    DualExecutionComparison,
    DualExecutionLedger,
    KillSwitchCommand,
)
from src.broker.broker_loop import BrokerPaperDecisionLoop
from src.data.market_provider import ReplayMarketDataProvider, BarEvent, QuoteEvent
from src.portfolio.shadow_portfolio import ShadowPaperPortfolio, ExitReason


def _create_synthetic_bars(symbol: str, count: int = 20, base_price: float = 100.0, end_time: pd.Timestamp = None) -> list[BarEvent]:
    bars = []
    if end_time is None:
        end_time = pd.Timestamp("2026-09-15 11:10:00", tz=timezone.utc)
    start_base = end_time - pd.Timedelta(minutes=5 * count)
    for i in range(count):
        start_ts = start_base + pd.Timedelta(minutes=5 * i)
        close_ts = start_ts + pd.Timedelta(minutes=5)
        p = base_price * (1.0 + 0.001 * i)
        b = BarEvent(
            symbol=symbol,
            timeframe="5m",
            open=p,
            high=p * 1.002,
            low=p * 0.998,
            close=p * 1.001,
            volume=50000.0,
            vwap=p * 1.0005,
            bar_start_timestamp=start_ts,
            bar_close_timestamp=close_ts,
            provider_timestamp=close_ts + pd.Timedelta(milliseconds=10),
            received_timestamp=close_ts + pd.Timedelta(milliseconds=20),
        )
        bars.append(b)
    return bars


def _create_synthetic_quote(symbol: str, price: float = 102.0, spread_bps: float = 2.0, ts: pd.Timestamp = None) -> QuoteEvent:
    if ts is None:
        ts = pd.Timestamp("2026-09-15 11:10:00", tz=timezone.utc)
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


def test_mode_safety_and_live_rejection():
    """Verify that LIVE mode raises a fatal error and fails closed."""
    # SHADOW & BROKER_PAPER are permitted
    verify_execution_mode(ExecutionMode.SHADOW)
    verify_execution_mode(ExecutionMode.BROKER_PAPER)

    # LIVE execution must raise fatal RuntimeError
    with pytest.raises(RuntimeError, match="FATAL SAFETY VIOLATION"):
        verify_execution_mode(ExecutionMode.LIVE)


def test_paper_environment_verification():
    """Verify system aborts if broker is not verified in paper mode."""
    # Verified paper broker connects successfully
    broker_ok = MockBrokerPaperAdapter(is_paper_verified=True)
    assert broker_ok.connect() is True

    # Non-paper broker fails with fatal error
    broker_fail = MockBrokerPaperAdapter(is_paper_verified=False)
    with pytest.raises(RuntimeError, match="Failed paper environment verification"):
        broker_fail.connect()


def test_order_state_machine_valid_and_invalid_transitions():
    """Test deterministic order transitions and rejection of invalid state jumps."""
    order = BrokerOrder(
        client_order_id="ORD_001",
        symbol="NVDA",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        qty=10.0,
    )
    assert order.status == OrderStatus.CREATED

    # Valid: CREATED -> RISK_APPROVED -> SUBMITTING -> SUBMITTED -> ACKNOWLEDGED -> FILLED
    order.transition_to(OrderStatus.RISK_APPROVED)
    assert order.status == OrderStatus.RISK_APPROVED

    order.transition_to(OrderStatus.SUBMITTING)
    assert order.status == OrderStatus.SUBMITTING

    order.transition_to(OrderStatus.SUBMITTED)
    assert order.status == OrderStatus.SUBMITTED

    order.transition_to(OrderStatus.ACKNOWLEDGED)
    assert order.status == OrderStatus.ACKNOWLEDGED

    order.transition_to(OrderStatus.FILLED)
    assert order.status == OrderStatus.FILLED

    # Invalid: FILLED is terminal, cannot transition to SUBMITTED
    with pytest.raises(ValueError, match="Invalid Order State Transition"):
        order.transition_to(OrderStatus.SUBMITTED)


def test_idempotent_order_submission():
    """Verify that retrying an order submission with same client_order_id does NOT duplicate trades."""
    broker = MockBrokerPaperAdapter()
    broker.connect()

    order1 = BrokerOrder(
        client_order_id="ORD_UNIQUE_101",
        symbol="NVDA",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        qty=5.0,
    )
    order1.transition_to(OrderStatus.RISK_APPROVED)

    res1 = broker.submit_order(order1)
    assert res1.status == OrderStatus.ACKNOWLEDGED
    assert len(broker._orders) == 1

    # Retry with identical client_order_id
    order1_retry = BrokerOrder(
        client_order_id="ORD_UNIQUE_101",
        symbol="NVDA",
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        qty=5.0,
    )
    order1_retry.transition_to(OrderStatus.RISK_APPROVED)

    res2 = broker.submit_order(order1_retry)
    assert res2.client_order_id == "ORD_UNIQUE_101"
    assert len(broker._orders) == 1  # No duplicate order created


def test_reconciliation_detects_mismatch_and_freezes():
    """Verify that state discrepancies trigger reconciliation errors and freeze trading."""
    broker = MockBrokerPaperAdapter(initial_cash=1000.0)
    broker.connect()
    internal = ShadowPaperPortfolio(initial_cash=1000.0)
    reconciler = AccountReconciler(broker=broker, internal_portfolio=internal)

    # 1. Clean state reconciles with 0 errors
    clean, errors = reconciler.reconcile()
    assert clean is True
    assert len(errors) == 0

    # 2. Inject cash mismatch
    broker.cash = 900.0  # Mismatch of $100
    clean, errors = reconciler.reconcile()
    assert clean is False
    assert reconciler.has_active_error is True
    assert any(e.error_type == "CASH_MISMATCH" for e in errors)


def test_crash_recovery_from_broker_state():
    """Verify system reconstructs internal portfolio strictly from Broker Ground Truth on restart."""
    broker = MockBrokerPaperAdapter(initial_cash=850.0)
    broker.connect()
    broker._positions["NVDA"] = BrokerPosition(
        symbol="NVDA",
        qty=2.0,
        avg_entry_price=100.0,
        current_price=105.0,
        market_value=210.0,
        unrealized_pnl=10.0,
    )

    # Empty fresh internal portfolio
    internal = ShadowPaperPortfolio(initial_cash=1000.0)
    reconciler = AccountReconciler(broker=broker, internal_portfolio=internal)

    reconciler.recover_from_broker_state()
    assert internal.cash == 850.0
    assert "NVDA" in internal.positions
    assert internal.positions["NVDA"].shares == 2.0
    assert internal.positions["NVDA"].entry_price == 100.0
    assert reconciler.has_active_error is False


def test_broker_failure_scenarios():
    """Test broker failure injection: timeout, rate limit, and rejection."""
    broker = MockBrokerPaperAdapter()
    broker.connect()

    # 1. Rate limit 429
    broker.inject_rate_limit = True
    order = BrokerOrder(
        client_order_id="ORD_ERR_1", symbol="NVDA", side=OrderSide.BUY, order_type=OrderType.MARKET, qty=1.0
    )
    order.transition_to(OrderStatus.RISK_APPROVED)
    with pytest.raises(RuntimeError, match="429 Too Many Requests"):
        broker.submit_order(order)
    broker.inject_rate_limit = False

    # 2. Timeout error
    broker.inject_network_timeout = True
    order2 = BrokerOrder(
        client_order_id="ORD_ERR_2", symbol="NVDA", side=OrderSide.BUY, order_type=OrderType.MARKET, qty=1.0
    )
    order2.transition_to(OrderStatus.RISK_APPROVED)
    with pytest.raises(TimeoutError):
        broker.submit_order(order2)
    broker.inject_network_timeout = False

    # 3. Order rejection
    broker.inject_order_rejection = True
    order3 = BrokerOrder(
        client_order_id="ORD_ERR_3", symbol="NVDA", side=OrderSide.BUY, order_type=OrderType.MARKET, qty=1.0
    )
    order3.transition_to(OrderStatus.RISK_APPROVED)
    res = broker.submit_order(order3)
    assert res.status == OrderStatus.REJECTED
    assert res.rejection_reason == "INJECTED_REJECTION"


def test_kill_switch_controls():
    """Test execution of hard kill switch commands."""
    provider = ReplayMarketDataProvider()
    provider.connect()
    broker = MockBrokerPaperAdapter()
    broker.connect()

    loop = BrokerPaperDecisionLoop(
        provider=provider,
        broker=broker,
        symbols=["NVDA"],
    )

    # Pause new orders
    res = loop.execute_kill_switch(KillSwitchCommand.PAUSE_NEW_ORDERS)
    assert res == "PAUSED_NEW_ORDERS"
    assert loop.is_paused is True

    # Resume new orders
    res = loop.execute_kill_switch(KillSwitchCommand.RESUME_NEW_ORDERS)
    assert res == "RESUMED_NEW_ORDERS"
    assert loop.is_paused is False

    # Full system lockout
    res = loop.execute_kill_switch(KillSwitchCommand.FULL_SYSTEM_LOCKOUT)
    assert res == "FULL_SYSTEM_LOCKOUT_EXECUTED"
    assert loop.is_system_locked_out is True


def test_dual_execution_ledger_and_optimism():
    """Test tracking of Dual Execution Book and paper fill optimism metric."""
    ledger = DualExecutionLedger()
    now = pd.Timestamp.now(tz=timezone.utc)

    comp = DualExecutionComparison(
        decision_id="DEC_NVDA_01",
        symbol="NVDA",
        side="BUY",
        decision_midprice=100.0,
        quote_bid=99.98,
        quote_ask=100.02,
        spread_bps=4.0,
        broker_fill_price=100.02,
        broker_fill_ts=now,
        broker_slippage_bps=0.5,
        broker_shortfall_bps=2.0,
        shadow_fill_price=100.025,
        shadow_fill_ts=now,
        shadow_slippage_bps=1.0,
        shadow_shortfall_bps=2.5,
    )
    ledger.record_dual_execution(comp)

    # Paper advantage: 2.5 - 2.0 = 0.5 bps
    assert comp.paper_fill_advantage_bps == pytest.approx(0.5, abs=0.01)

    summary = ledger.compute_optimism_summary()
    assert summary["count"] == 1
    assert summary["mean_paper_advantage_bps"] == pytest.approx(0.5, abs=0.01)
    assert "NVDA" in summary["by_symbol"]


def test_broker_paper_decision_loop_end_to_end():
    """End-to-end integration test of the full BrokerPaperDecisionLoop with market replay."""
    provider = ReplayMarketDataProvider()
    provider.connect()
    symbols = ["NVDA", "AMD", "TSLA", "SPY"]
    provider.subscribe(symbols)

    now = pd.Timestamp("2026-09-15 11:10:00", tz=timezone.utc)
    for sym in symbols:
        bars = _create_synthetic_bars(sym, count=20, base_price=100.0, end_time=now)
        for b in bars:
            provider.ingest_bar(b)
        quote = _create_synthetic_quote(sym, price=102.0, ts=now)
        provider.ingest_quote(quote)

    broker = MockBrokerPaperAdapter(initial_cash=1000.0)
    broker.connect()

    loop = BrokerPaperDecisionLoop(
        provider=provider,
        broker=broker,
        symbols=["NVDA", "AMD", "TSLA"],
        confidence_threshold=0.50,
        meta_threshold=0.50,
    )

    # Execute decision step
    res = loop.step(current_time=now)
    assert res["status"] == "COMPLETED"
    assert res["orders_submitted"] > 0
    assert len(broker.get_positions()) > 0
    assert len(loop.dual_ledger.comparisons) > 0
    assert loop.reconciler.has_active_error is False
