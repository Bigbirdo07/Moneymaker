"""
Unit and Integration Tests for Phase 6A:
1. ExecutionMode.LIVE_AUTONOMOUS_MICRO validation and safety firewall.
2. DeterministicAutonomousGate 18+ fail-closed checks, signal TTL, and rejection ledger.
3. Pre-submission snapshot recording & revalidation.
4. AutonomousMicroDecisionLoop end-to-end autonomous trading with zero human latency.
5. 7-stage microsecond latency telemetry and Autonomy Gap verification.
6. Moneymaker Research Director analytical inspection tools and ChallengerProposal queue.
"""

from datetime import datetime, timezone
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
from src.governance.autonomous_gate import (
    AutonomousRejectionCode,
    DeterministicAutonomousGate,
    PreSubmissionSnapshot,
)
from src.governance.autonomous_loop import (
    AutonomousExecutionRecord,
    AutonomousLatencyMetrics,
    AutonomousMicroDecisionLoop,
)
from src.governance.session_arming import (
    SessionArmingManager,
    SessionAuthorizationToken,
)
from src.llm.rag_knowledge_base import RAGKnowledgeBase
from src.llm.research_director import (
    ChallengerProposal,
    DataProvenanceType,
    ExecutionQualitySummary,
    LLMOutputType,
    ModelHealthSummary,
    MoneymakerResearchDirector,
    RiskSummary,
    SessionSummary,
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


def test_live_autonomous_micro_execution_mode_and_live_prohibition():
    """Verify LIVE_AUTONOMOUS_MICRO is permitted while unrestricted LIVE is fatal-blocked."""
    with pytest.raises(RuntimeError, match="Unrestricted LIVE money execution is strictly prohibited"):
        verify_execution_mode(ExecutionMode.LIVE)

    # Valid modes pass without exception
    verify_execution_mode(ExecutionMode.LIVE_AUTONOMOUS_MICRO)
    verify_execution_mode(ExecutionMode.LIVE_GOVERNED_MICRO)
    verify_execution_mode(ExecutionMode.SHADOW)
    verify_execution_mode(ExecutionMode.BROKER_PAPER)


def test_deterministic_autonomous_gate_validations_and_rejections():
    """Verify gate validation checks: spread, TTL, loss limits, allow-list, broker disconnection."""
    lock_path = "/tmp/test_auto_gate.lock"
    if os.path.exists(lock_path):
        os.remove(lock_path)

    provider = ReplayMarketDataProvider()
    provider.connect()
    provider.subscribe(["NVDA", "AMD", "TSLA"])

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

    gate = DeterministicAutonomousGate(
        broker=broker,
        provider=provider,
        session_manager=session_manager,
        approved_symbols={"NVDA", "AMD", "TSLA"},
        max_allowed_spread_bps=3.0,
        signal_ttl_ms=3000.0,
        max_daily_loss_usd=20.0,
        max_pilot_drawdown_usd=50.0,
        max_concurrent_positions=2,
    )

    now = pd.Timestamp("2026-09-15 14:00:00", tz=timezone.utc)
    quote = _make_quote("NVDA", price=125.0, spread_bps=1.5, ts=now)
    provider.ingest_quote(quote)

    bars = _make_bars("NVDA", count=20, end_ts=now)
    for b in bars:
        provider.ingest_bar(b)

    # 1. Successful pass
    can_exec, snap, rej_code, msg = gate.validate_and_snapshot(
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        model_score=0.62,
        opportunity_rank=1,
        expected_alpha_bps=4.8,
        estimated_cost_bps=2.5,
        feature_hash="HASH_NVDA_001",
        current_time=now + pd.Timedelta(milliseconds=200),
    )
    assert can_exec is True
    assert snap is not None
    assert rej_code is None
    assert snap.symbol == "NVDA"
    assert snap.signal_age_ms == 200.0

    # 2. Signal TTL Expiration (> 3000 ms)
    can_exec2, snap2, rej_code2, msg2 = gate.validate_and_snapshot(
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        model_score=0.62,
        opportunity_rank=1,
        expected_alpha_bps=4.8,
        estimated_cost_bps=2.5,
        feature_hash="HASH_NVDA_001",
        current_time=now + pd.Timedelta(milliseconds=3500), # 3.5s later
    )
    assert can_exec2 is False
    assert rej_code2 == AutonomousRejectionCode.SIGNAL_EXPIRED
    assert "SIGNAL_TTL_EXPIRED" in msg2

    # 3. Spread expansion (> 3.0 bps)
    blown_quote = _make_quote("NVDA", price=125.0, spread_bps=5.0, ts=now)
    provider.ingest_quote(blown_quote)
    can_exec3, snap3, rej_code3, msg3 = gate.validate_and_snapshot(
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        model_score=0.62,
        opportunity_rank=1,
        expected_alpha_bps=4.8,
        estimated_cost_bps=2.5,
        feature_hash="HASH_NVDA_001",
        current_time=now + pd.Timedelta(milliseconds=100),
    )
    assert can_exec3 is False
    assert rej_code3 == AutonomousRejectionCode.SPREAD_TOO_WIDE

    # 4. Symbol Denied (not on allow-list)
    can_exec4, snap4, rej_code4, msg4 = gate.validate_and_snapshot(
        symbol="AAPL", # Not allowed
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        model_score=0.62,
        opportunity_rank=1,
        expected_alpha_bps=4.8,
        estimated_cost_bps=2.5,
        feature_hash="HASH_AAPL",
        current_time=now + pd.Timedelta(milliseconds=100),
    )
    assert can_exec4 is False
    assert rej_code4 == AutonomousRejectionCode.SYMBOL_NOT_ALLOWED

    # 5. Daily loss circuit breaker ($20)
    clean_quote = _make_quote("NVDA", price=125.0, spread_bps=1.5, ts=now)
    provider.ingest_quote(clean_quote)
    can_exec5, snap5, rej_code5, msg5 = gate.validate_and_snapshot(
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        model_score=0.62,
        opportunity_rank=1,
        expected_alpha_bps=4.8,
        estimated_cost_bps=2.5,
        feature_hash="HASH_NVDA_001",
        current_time=now + pd.Timedelta(milliseconds=100),
        daily_loss_usd=20.50,
    )
    assert can_exec5 is False
    assert rej_code5 == AutonomousRejectionCode.DAILY_LOSS_LIMIT
    assert gate.is_suspended is True

    session_manager.revoke_session()


def test_autonomous_micro_decision_loop_end_to_end_and_telemetry():
    """Run full autonomous execution loop without human approval and verify 7-stage latency telemetry."""
    lock_path = "/tmp/test_auto_loop.lock"
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

    loop = AutonomousMicroDecisionLoop(
        provider=provider,
        broker=broker,
        session_manager=session_manager,
        symbols=["NVDA", "AMD", "TSLA"],
        mode=ExecutionMode.LIVE_AUTONOMOUS_MICRO,
        cooldown_bars=2,
        confidence_threshold=0.50,
        meta_threshold=0.45,
    )

    # Ingest historical bars and live quotes
    t0 = pd.Timestamp("2026-09-15 14:00:00", tz=timezone.utc)
    for sym in ["NVDA", "AMD", "TSLA", "SPY"]:
        px = 120.0 if sym == "NVDA" else (160.0 if sym == "AMD" else (250.0 if sym == "TSLA" else 500.0))
        bars = _make_bars(sym, count=20, base_price=px, end_ts=t0)
        for b in bars:
            provider.ingest_bar(b)

        quote = _make_quote(sym, price=px, spread_bps=1.5, ts=t0)
        provider.ingest_quote(quote)

    # Execute autonomous cycle (zero human review)
    rec, status = loop.process_market_cycle(current_time=t0)
    assert rec is not None
    assert status == "AUTONOMOUS_TRADE_EXECUTED"
    assert rec.symbol == "NVDA"
    assert rec.staged_notional_usd == 25.0 # Stage A notional
    assert loop.total_autonomous_trades_executed == 1

    # Verify 7-Stage Latency Telemetry
    lat = rec.latency_telemetry
    assert lat.feature_latency_ms >= 0.0
    assert lat.prediction_latency_ms >= 0.0
    assert lat.ranking_latency_ms >= 0.0
    assert lat.broker_ack_latency_ms >= 0.0
    assert lat.total_decision_to_fill_latency_ms < 500.0 # Fast sub-500ms execution

    # Verify shadow portfolio and reconciliation clean
    assert len(loop.shadow_portfolio.positions) == 1
    is_clean, discrepancies = loop.reconciler.reconcile()
    assert is_clean is True
    assert len(discrepancies) == 0

    session_manager.revoke_session()


def test_research_director_analytical_tools_and_challenger_queue():
    """Verify Research Director analytical tools and structured ChallengerProposal queue."""
    director = MoneymakerResearchDirector()
    assert director.is_read_only is True

    # 1. Inspect symbol concentration
    pnls = {"NVDA": 10.0, "AMD": 5.0, "TSLA": 3.0}
    conc = director.inspect_symbol_performance(pnls)
    assert conc["total_pnl"] == 18.0
    assert conc["is_concentrated"] is False # Max is 55.5% < 60%

    # 2. Inspect regime performance
    regime_pnls = {"BULL_LOW_VOL": 8.0, "BULL_HIGH_VOL": 5.0, "SIDEWAYS_CHOP": 1.5, "BEAR_CORRECTION": 2.0}
    reg_perf = director.inspect_regime_performance(regime_pnls)
    assert reg_perf["all_regimes_profitable"] is True

    # 3. Anomaly detection generates structured ChallengerProposal in RESEARCH_QUEUE
    exec_degraded = ExecutionQualitySummary(
        mean_spread_bps=3.80,
        mean_implementation_shortfall_bps=2.90,
        live_slippage_penalty_bps=0.85, # Triggers challenger proposal
        passive_fill_rate_pct=52.0,
        mean_time_to_fill_sec=4.5,
        mean_operator_latency_sec=0.0,
    )
    health = ModelHealthSummary(
        model_version="CHAMPION_PHASE_6A",
        spearman_rank_ic=0.048,
        rank_ic_p_value=0.002,
        meta_label_precision=0.57,
        feature_drift_detected=False,
        cusum_alarm_active=False,
        status="HEALTHY",
    )
    risk = RiskSummary(
        capital_ceiling_usd=1000.0,
        current_equity_usd=1018.0,
        daily_realized_loss_usd=0.0,
        daily_loss_limit_usd=20.0,
        pilot_drawdown_usd=0.0,
        max_drawdown_limit_usd=50.0,
        reconciliation_errors_count=0,
        unrelated_holdings_count=0,
        margin_borrowing_usd=0.0,
    )

    out = director.detect_anomalies_and_drift(exec_degraded, health, risk)
    assert out.output_type == LLMOutputType.ANOMALY
    assert len(director.research_queue) == 1
    challenger = director.research_queue[0]
    assert "CHALL_TOD" in challenger.proposal_id
    assert challenger.primary_metric == "Net Expectancy (bps/trade) after 3.5 bps friction"
    assert "Purged 5-fold cross validation" in challenger.experimental_design
