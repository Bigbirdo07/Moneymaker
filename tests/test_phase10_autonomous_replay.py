"""
Comprehensive Unit and Integration Test Suite for Moneymaker Phase 10:
Historical Market Data Ingestion, Replay Engine, Leakage Invariance,
Premarket Scanner, Multi-Horizon Forecaster, Entry/Exit Decision Models,
Capital Allocator, Execution Simulator, and Hindsight Oracle Isolation.
"""

import pytest
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import numpy as np
import pandas as pd

from src.core.types import EvidenceClass, OrderSide, PortfolioState, Position, SessionType
from src.data.calendar import ET_TZ, UTC_TZ, TradingCalendar
from src.data.historical_market_data import HistoricalMarketDataManager, STANDARD_50_UNIVERSE
from src.evaluation.hindsight_oracle import HindsightOracle, OracleTradeBenchmark
from src.execution.capital_allocator import AutonomousCapitalAllocator
from src.execution.replay_execution_simulator import ReplayExecutionSimulator
from src.models.multi_horizon_forecaster import MultiHorizonForecaster
from src.ranking.opportunity_ranker import OpportunityRanker
from src.replay.market_replay_engine import FutureDataLeakageError, HistoricalMarketReplayEngine
from src.signals.entry_model import EntryDecisionModel
from src.signals.exit_model import ExitDecisionModel
from src.signals.premarket_scanner import PremarketOpportunityScanner


@pytest.fixture
def market_data_manager(tmp_path):
    data_dir = tmp_path / "market_data"
    prov_dir = tmp_path / "provenance"
    mgr = HistoricalMarketDataManager(data_dir=data_dir, provenance_dir=prov_dir)
    return mgr


@pytest.fixture
def replay_engine(market_data_manager):
    # Generate miniature 3-symbol 2-day dataset for rapid testing
    symbols = ["AAPL", "MSFT", "NVDA"]
    market_data_manager.generate_synthetic_1m_dataset(
        symbols=symbols,
        start_date="2026-01-05",
        num_trading_days=2,
        seed=123,
    )
    engine = HistoricalMarketReplayEngine(market_data_manager=market_data_manager)
    engine.load_universe(symbols)
    return engine


def test_market_data_schema_and_provenance(market_data_manager):
    symbols = ["AAPL", "MSFT"]
    dfs = market_data_manager.generate_synthetic_1m_dataset(symbols=symbols, num_trading_days=2)
    assert len(dfs) == 2
    for sym in symbols:
        df = dfs[sym]
        assert "timestamp" in df.columns
        assert "open" in df.columns
        assert "close" in df.columns
        assert "volume" in df.columns
        assert "vwap" in df.columns
        assert "spread" in df.columns
        assert len(df) == 900  # 450 bars/day * 2 days

    report = market_data_manager.audit_universe_data(symbols)
    assert report.is_valid is True
    assert report.total_bars == 1800
    assert report.missing_bar_count == 0
    assert report.bad_price_count == 0
    assert report.duplicate_timestamp_count == 0
    assert report.provenance_hashes_verified == 2


def test_replay_clock_invariance_and_leakage_assertion(replay_engine):
    session_date = date(2026, 1, 5)
    minute_gen = replay_engine.iterate_session_minutes(session_date, include_premarket=True)
    
    clock_utc, clock_et = next(minute_gen)
    assert replay_engine.simulated_clock == clock_utc

    vis_bars = replay_engine.get_visible_bars("AAPL")
    assert len(vis_bars) == 1
    assert vis_bars["timestamp"].iloc[0] <= clock_utc

    # Test that querying future timestamp triggers FutureDataLeakageError
    future_time = clock_utc + timedelta(minutes=10)
    with pytest.raises(FutureDataLeakageError):
        replay_engine.assert_no_future_leakage(future_time)


def test_premarket_opportunity_scanner(replay_engine):
    session_date = date(2026, 1, 5)
    scanner = PremarketOpportunityScanner()

    # Step clock to 09:15 ET (45 minutes into premarket)
    for clock_utc, clock_et in replay_engine.iterate_session_minutes(session_date, include_premarket=True):
        if clock_et.time() == time(9, 15):
            break

    candidates = scanner.scan_universe(replay_engine, ["AAPL", "MSFT", "NVDA"])
    assert len(candidates) > 0
    for c in candidates:
        assert c.symbol in ["AAPL", "MSFT", "NVDA"]
        assert c.candidate_rank >= 1
        assert c.premarket_volume > 0
        assert c.evidence_class == EvidenceClass.HISTORICAL_REPLAY.value


def test_multi_horizon_forecaster(replay_engine):
    session_date = date(2026, 1, 5)
    forecaster = MultiHorizonForecaster()

    # Advance clock to regular session 09:45 ET
    for clock_utc, clock_et in replay_engine.iterate_session_minutes(session_date, include_premarket=True):
        if clock_et.time() == time(9, 45):
            break

    vis_df = replay_engine.get_visible_bars("NVDA", lookback_bars=60)
    pred = forecaster.predict("NVDA", replay_engine.simulated_clock, vis_df)

    assert pred.symbol == "NVDA"
    assert pred.forecast_5m.horizon_minutes == 5
    assert pred.forecast_15m.horizon_minutes == 15
    assert pred.forecast_30m.horizon_minutes == 30
    assert pred.forecast_60m.horizon_minutes == 60
    assert pred.forecast_eod.horizon_minutes == 390
    assert 0.0 <= pred.forecast_15m.probability_positive <= 1.0


def test_entry_decision_model_rules(replay_engine):
    session_date = date(2026, 1, 5)
    forecaster = MultiHorizonForecaster()
    entry_model = EntryDecisionModel(min_net_edge_bps=4.0, min_probability_positive=0.53)

    # Advance clock to regular session 10:00 ET
    for clock_utc, clock_et in replay_engine.iterate_session_minutes(session_date, include_premarket=True):
        if clock_et.time() == time(10, 0):
            break

    vis_df = replay_engine.get_visible_bars("AAPL", lookback_bars=60)
    pred = forecaster.predict("AAPL", replay_engine.simulated_clock, vis_df)

    portfolio = PortfolioState(
        timestamp=replay_engine.simulated_clock,
        cash=1000.0,
        buying_power=1000.0,
        positions={},
        portfolio_value=1000.0,
    )

    # Test EOD rejection
    eod_decision = entry_model.evaluate_entry(
        prediction=pred,
        current_spread_bps=2.0,
        portfolio=portfolio,
        minutes_to_close=15.0,
    )
    assert eod_decision.action == "SKIP"
    assert eod_decision.reason == "SESSION_CLOSE_PROXIMITY"

    # Test excessive spread rejection
    spread_decision = entry_model.evaluate_entry(
        prediction=pred,
        current_spread_bps=25.0,
        portfolio=portfolio,
        minutes_to_close=100.0,
    )
    assert spread_decision.action == "SKIP"
    assert spread_decision.reason == "EXCESSIVE_SPREAD_FRICTION"


def test_exit_decision_model_factors():
    exit_model = ExitDecisionModel(
        stop_loss_pct=0.015,
        take_profit_pct=0.025,
        max_holding_bars=120,
    )

    forecaster = MultiHorizonForecaster()
    pred = forecaster.predict("AAPL", datetime.now(timezone.utc), pd.DataFrame())

    pos = Position(
        symbol="AAPL",
        shares=5,
        avg_entry_price=100.0,
        current_price=103.0,  # +3% (Take profit threshold triggered)
        entry_timestamp=datetime.now(timezone.utc),
        bars_held=20,
    )

    tp_decision = exit_model.evaluate_exit(
        position=pos,
        current_price=103.0,
        prediction=pred,
        minutes_to_close=100.0,
    )
    assert tp_decision.action == "SELL"
    assert tp_decision.reason_category == "TAKE_PROFIT"
    assert tp_decision.is_exit_triggered is True

    # Test stop loss
    pos.current_price = 98.0  # -2% (Stop loss threshold triggered)
    sl_decision = exit_model.evaluate_exit(
        position=pos,
        current_price=98.0,
        prediction=pred,
        minutes_to_close=100.0,
    )
    assert sl_decision.action == "SELL"
    assert sl_decision.reason_category == "STOP_LOSS"


def test_capital_allocator_and_friction_execution():
    allocator = AutonomousCapitalAllocator(
        max_position_pct=0.25,
        max_portfolio_exposure_pct=0.80,
        max_active_positions=4,
        allow_fractional_shares=False,
    )
    simulator = ReplayExecutionSimulator()

    portfolio = PortfolioState(
        timestamp=datetime.now(timezone.utc),
        cash=1000.0,
        buying_power=1000.0,
        positions={},
        portfolio_value=1000.0,
    )

    from src.signals.entry_model import EntryDecision
    entry_dec = EntryDecision(
        symbol="NVDA",
        timestamp=datetime.now(timezone.utc).isoformat(),
        action="BUY",
        reason="POSITIVE_NET_EDGE_CONFIRMED",
        expected_gross_return_bps=20.0,
        estimated_friction_bps=6.0,
        expected_net_edge_bps=14.0,
        probability_positive=0.65,
        target_horizon_min=15,
        confidence_score=0.80,
        suggested_allocation_pct=0.25,
        is_authorized=True,
    )

    plan = allocator.allocate(
        timestamp=datetime.now(timezone.utc).isoformat(),
        portfolio=portfolio,
        candidate_entries=[(entry_dec, 200.0)],
    )

    assert len(plan.targets) == 1
    target = plan.targets[0]
    assert target.symbol == "NVDA"
    assert target.target_shares == 1  # $250 max / $200 = 1 share
    assert target.target_dollars == 200.0

    # Simulate fill at next bar open
    fill = simulator.simulate_fill(
        order_id="ORD_001",
        symbol="NVDA",
        side=OrderSide.BUY,
        shares=1,
        decision_timestamp=datetime.now(timezone.utc),
        execution_bar={"open": 200.0, "spread": 0.05, "volume": 10000.0},
    )

    assert fill.symbol == "NVDA"
    assert fill.side == "BUY"
    assert fill.fill_price >= 200.0  # Open + half-spread + slippage
    assert fill.total_friction > 0.0


def test_hindsight_oracle_isolation():
    oracle = HindsightOracle()
    bars = []
    base_ts = datetime(2026, 1, 5, 9, 30, tzinfo=timezone.utc)
    for i in range(100):
        p = 100.0 + float(i * 0.50)  # Steady uptrend from 100 to 149.5
        bars.append({
            "timestamp": base_ts + timedelta(minutes=i),
            "open": p, "high": p + 0.2, "low": p - 0.2, "close": p, "volume": 1000.0
        })
    df = pd.DataFrame(bars)

    bench = oracle.compute_session_oracle_bounds("AAPL", df)
    assert bench.oracle_tag == "HINDSIGHT_ONLY"
    assert bench.tradable is False
    assert bench.max_attainable_return_pct > 0.40

    report = oracle.evaluate_profit_capture(
        symbol="AAPL",
        realized_entry_price=105.0,
        realized_exit_price=125.0,
        realized_net_pnl=20.0,
        oracle_benchmark=bench,
    )
    assert report.profit_capture_ratio > 0.0
    assert report.evidence_class == EvidenceClass.HINDSIGHT_ORACLE.value
