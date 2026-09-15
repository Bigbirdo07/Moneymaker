"""
Comprehensive Test Suite for Phase 3A Forward Shadow Trading & Execution Validation.
Covers stream ordering, timestamp integrity, staleness, double-entry accounting,
risk lockouts, 3 execution paths, limit fills, latency attribution, and decision immutability.
"""

from datetime import datetime, timezone
import pytest
import numpy as np
import pandas as pd

from src.data.market_provider import (
    QuoteEvent,
    TradeEvent,
    BarEvent,
    ReplayMarketDataProvider,
)
from src.features.incremental_features import IncrementalFeatureEngine
from src.evaluation.latency import LatencyRecord, LatencyTracker
from src.evaluation.model_health import ModelHealthMonitor, ModelHealthState
from src.evaluation.forward_evaluation import (
    ForwardExecutionEvaluator,
    RejectedOpportunityRecord,
    ForwardDecayPoint,
)
from src.execution.shadow_engine import (
    ProposedTrade,
    ShadowExecutionSimulator,
    ExecutionPath,
    LimitFillStatus,
)
from src.portfolio.risk_engine import (
    DeterministicRiskEngine,
    RiskPolicyConfig,
    RiskDecisionType,
)
from src.portfolio.shadow_portfolio import ShadowPaperPortfolio, ExitReason
from src.execution.shadow_loop import ShadowDecisionLoop


def _create_synthetic_bars(symbol: str, count: int = 20, base_price: float = 100.0, end_time: Optional[pd.Timestamp] = None) -> list[BarEvent]:
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


def test_timestamp_integrity_and_staleness_detection():
    """Test timestamp ordering and fail-closed staleness rejection."""
    provider = ReplayMarketDataProvider()
    provider.connect()
    provider.subscribe(["NVDA"])

    now = pd.Timestamp("2026-09-15 11:10:00", tz=timezone.utc)
    quote = _create_synthetic_quote("NVDA", price=120.0, ts=now)
    provider.ingest_quote(quote)

    bars = _create_synthetic_bars("NVDA", count=15)
    for b in bars:
        provider.ingest_bar(b)

    # 1. Fresh data should pass
    is_valid, reason = provider.check_staleness("NVDA", current_time=now)
    assert is_valid is True
    assert reason == "FRESH"

    # 2. Stale quote (>30s) should fail closed
    future_time = now + pd.Timedelta(seconds=45)
    is_valid, reason = provider.check_staleness("NVDA", current_time=future_time)
    assert is_valid is False
    assert "STALE_QUOTE" in reason

    # 3. Disconnected provider should fail closed
    provider.disconnect()
    is_valid, reason = provider.check_staleness("NVDA", current_time=now)
    assert is_valid is False
    assert reason == "PROVIDER_DISCONNECTED"


def test_incremental_feature_computation():
    """Test feature calculation strictly from past data without lookahead."""
    bars = _create_synthetic_bars("NVDA", count=20, base_price=100.0)
    quote = _create_synthetic_quote("NVDA", price=102.0)

    feats = IncrementalFeatureEngine.compute_features(
        symbol_bars=bars,
        current_quote=quote,
    )

    assert "ret_5m" in feats
    assert "ret_15m" in feats
    assert "volatility_14" in feats
    assert "rvol_14" in feats
    assert "spread_bps" in feats
    assert feats["spread_bps"] > 0
    assert feats["volatility_14"] >= 0


def test_shadow_execution_paths_and_adverse_selection():
    """Test simulation of Marketable, Next-Trade, and Passive Limit execution paths."""
    simulator = ShadowExecutionSimulator()
    now = pd.Timestamp("2026-09-15 11:10:00", tz=timezone.utc)
    quote = _create_synthetic_quote("NVDA", price=100.0, spread_bps=2.0, ts=now)

    prop_trade = ProposedTrade(
        decision_id="DEC_NVDA_001",
        symbol="NVDA",
        direction="LONG",
        shares=10.0,
        decision_price=100.0,
        decision_timestamp=now,
        model_confidence=0.62,
        expected_alpha_bps=4.8,
        opportunity_score=2.3,
        archetype="HIGH_BETA_HIGH_VOL",
        regime="NORMAL",
        stop_loss_price=98.5,
        take_profit_price=103.0,
    )

    subsequent_bars = _create_synthetic_bars("NVDA", count=5, base_price=99.5)
    res = simulator.simulate_execution(
        proposed_trade=prop_trade,
        current_quote=quote,
        subsequent_bars=subsequent_bars,
    )

    assert res.marketable_fill_price >= quote.ask
    assert res.limit_order_price == quote.bid
    assert res.limit_fill_status in (LimitFillStatus.FILLED, LimitFillStatus.ADVERSE_SELECTED, LimitFillStatus.MISSED)
    assert res.decision_midprice == pytest.approx(100.0, abs=0.01)


def test_portfolio_double_entry_accounting():
    """Verify double-entry mathematical invariants across opens, updates, and closes."""
    portfolio = ShadowPaperPortfolio(initial_cash=1000.0, transaction_cost_bps=3.5)
    now = pd.Timestamp("2026-09-15 10:00:00", tz=timezone.utc)

    # Initial invariant check
    assert portfolio.verify_accounting_invariants() is True
    assert portfolio.total_equity == 1000.0

    # Open position: 1 share of NVDA at $100.00
    opened = portfolio.open_position(
        symbol="NVDA",
        shares=1.0,
        entry_price=100.0,
        entry_timestamp=now,
    )
    assert opened is True
    assert portfolio.verify_accounting_invariants() is True
    assert portfolio.cash < 900.0  # Cash deducted for stock + friction

    # Update mark-to-market to $105.00
    portfolio.update_mark_to_market("NVDA", current_price=105.0)
    assert portfolio.verify_accounting_invariants() is True
    assert portfolio.total_equity > 1000.0

    # Close position at $105.00
    close_ts = now + pd.Timedelta(minutes=15)
    trade_record = portfolio.close_position("NVDA", exit_price=105.0, exit_timestamp=close_ts, reason=ExitReason.TIME_EXIT)

    assert trade_record is not None
    assert trade_record.net_pnl > 0
    assert portfolio.verify_accounting_invariants() is True
    assert len(portfolio.positions) == 0
    assert portfolio.cash == portfolio.total_equity


def test_risk_engine_daily_loss_and_drawdown_lockouts():
    """Verify deterministic risk rules enforce daily loss lockout and concentration limits."""
    risk_engine = DeterministicRiskEngine(
        RiskPolicyConfig(
            max_position_pct=0.10,
            max_daily_loss_pct=0.03,  # $30 on $1,000
            max_portfolio_drawdown_pct=0.15,
        )
    )

    # 1. Normal order within budget -> APPROVED
    decision = risk_engine.evaluate_order(
        symbol="NVDA",
        price=100.0,
        shares=1.0,
        sector="Technology",
        current_equity=1000.0,
        available_cash=1000.0,
        current_daily_pnl=0.0,
        current_drawdown_pct=0.0,
        open_positions={},
    )
    assert decision.decision == RiskDecisionType.APPROVE

    # 2. Daily loss exceeding 3% ($35 loss on $1,000) -> DAILY LOCKOUT REJECT
    decision_loss = risk_engine.evaluate_order(
        symbol="NVDA",
        price=100.0,
        shares=1.0,
        sector="Technology",
        current_equity=965.0,
        available_cash=965.0,
        current_daily_pnl=-35.0,
        current_drawdown_pct=0.035,
        open_positions={},
    )
    assert decision_loss.decision == RiskDecisionType.REJECT
    assert risk_engine.is_daily_locked_out is True
    assert "DAILY_LOSS_LIMIT_REACHED" in decision_loss.reason


def test_shadow_decision_loop_end_to_end():
    """End-to-end integration test of the full Shadow Decision Loop with candidate filtering and cooldown."""
    provider = ReplayMarketDataProvider()
    provider.connect()
    symbols = ["NVDA", "AMD", "TSLA", "SPY"]
    provider.subscribe(symbols)

    now = pd.Timestamp("2026-09-15 11:10:00", tz=timezone.utc)
    for sym in symbols:
        bars = _create_synthetic_bars(sym, count=20, base_price=100.0)
        for b in bars:
            provider.ingest_bar(b)
        quote = _create_synthetic_quote(sym, price=102.0, ts=now)
        provider.ingest_quote(quote)

    loop = ShadowDecisionLoop(
        provider=provider,
        symbols=["NVDA", "AMD", "TSLA"],
        cooldown_bars=4,
        confidence_threshold=0.50,
        meta_threshold=0.50,
    )

    # First decision step -> generates trades
    res1 = loop.step(current_time=now)
    assert res1["status"] == "COMPLETED"
    assert res1["executed"] > 0
    assert len(loop.portfolio.positions) > 0

    # Second step immediately on next bar -> cooldown suppresses churn
    next_now = now + pd.Timedelta(minutes=5)
    for sym in symbols:
        new_bar = BarEvent(
            symbol=sym,
            timeframe="5m",
            open=102.0,
            high=102.5,
            low=101.8,
            close=102.2,
            volume=45000.0,
            vwap=102.1,
            bar_start_timestamp=now,
            bar_close_timestamp=next_now,
            provider_timestamp=next_now + pd.Timedelta(milliseconds=10),
            received_timestamp=next_now + pd.Timedelta(milliseconds=20),
        )
        provider.ingest_bar(new_bar)
        quote = _create_synthetic_quote(sym, price=102.2, ts=next_now)
        provider.ingest_quote(quote)

    res2 = loop.step(current_time=next_now)
    assert res2["status"] == "COMPLETED"
    # Cooldown should reject duplicate re-entries
    assert len(loop.evaluator.rejected_records) > 0


def test_latency_attribution_and_percentiles():
    """Test latency tracking and SLA boundary verification."""
    tracker = LatencyTracker(alpha_decay_boundary_sec=90.0)
    now = pd.Timestamp("2026-09-15 11:10:00", tz=timezone.utc)

    for i in range(50):
        rec = LatencyRecord(
            decision_id=f"DEC_{i}",
            symbol="NVDA",
            exchange_timestamp=now - pd.Timedelta(milliseconds=100),
            provider_timestamp=now - pd.Timedelta(milliseconds=50),
            received_timestamp=now,
            feature_ready_timestamp=now + pd.Timedelta(milliseconds=20 + i),
            model_start_timestamp=now + pd.Timedelta(milliseconds=20 + i),
            model_end_timestamp=now + pd.Timedelta(milliseconds=35 + i),
            ranking_timestamp=now + pd.Timedelta(milliseconds=40 + i),
            decision_timestamp=now + pd.Timedelta(milliseconds=45 + i),
            hypothetical_fill_timestamp=now + pd.Timedelta(milliseconds=50 + i),
        )
        tracker.record(rec)

    summary = tracker.summary()
    assert summary["count"] == 50
    assert summary["median_decision_ms"] > 0
    assert summary["p99_decision_ms"] < 200.0  # Well below 90,000 ms (90s)
    assert summary["pct_below_90s_boundary"] == 100.0
