"""
Unit and Integration Tests for Phase 10.1 Forensics, Validation Tuning,
and Autonomous Engine V1.1 Entry & Exit Models.
"""

import pytest
import pandas as pd
import numpy as np

from src.core.types import PortfolioState, Position, EvidenceClass
from src.models.multi_horizon_forecaster import HorizonForecast, MultiHorizonPrediction
from src.evaluation.phase10_forensics import (
    Phase10ForensicAnalyzer,
    HoldingPeriodMetrics,
    WinnerLoserAsymmetry,
    SignalDecileBucket,
    SignalHalfLifeReport,
    CalibrationBucket,
)
from src.evaluation.validation_tuner import ValidationTuner, CalibratedThresholds
from src.signals.entry_model_v1_1 import EntryDecisionModelV1_1, EntryDecisionV1_1
from src.signals.exit_model_v1_1 import ExitDecisionModelV1_1, ExitDecisionV1_1


from datetime import datetime

def create_sample_prediction(
    symbol: str = "NVDA",
    edge_15m: float = 12.5,
    p_up_15m: float = 0.62,
    conf_15m: float = 0.75,
) -> MultiHorizonPrediction:
    return MultiHorizonPrediction(
        symbol=symbol,
        timestamp="2026-01-15T10:00:00",
        forecast_5m=HorizonForecast(
            horizon_minutes=5,
            expected_return_bps=edge_15m * 0.5 + 3.0,
            probability_positive=p_up_15m,
            estimated_friction_bps=3.0,
            expected_net_return_bps=edge_15m * 0.5,
            confidence=conf_15m,
        ),
        forecast_15m=HorizonForecast(
            horizon_minutes=15,
            expected_return_bps=edge_15m + 3.0,
            probability_positive=p_up_15m,
            estimated_friction_bps=3.0,
            expected_net_return_bps=edge_15m,
            confidence=conf_15m,
        ),
        forecast_30m=HorizonForecast(
            horizon_minutes=30,
            expected_return_bps=edge_15m * 0.8 + 3.0,
            probability_positive=p_up_15m,
            estimated_friction_bps=3.0,
            expected_net_return_bps=edge_15m * 0.8,
            confidence=conf_15m,
        ),
        forecast_60m=HorizonForecast(
            horizon_minutes=60,
            expected_return_bps=edge_15m * 0.6 + 3.0,
            probability_positive=p_up_15m,
            estimated_friction_bps=3.0,
            expected_net_return_bps=edge_15m * 0.6,
            confidence=conf_15m,
        ),
        forecast_eod=HorizonForecast(
            horizon_minutes=390,
            expected_return_bps=edge_15m * 0.4 + 3.0,
            probability_positive=p_up_15m,
            estimated_friction_bps=3.0,
            expected_net_return_bps=edge_15m * 0.4,
            confidence=conf_15m,
        ),
        optimal_target_horizon_min=15,
        composite_net_edge_bps=edge_15m,
    )


class TestPhase10ForensicAnalyzer:
    def test_holding_period_metrics(self):
        analyzer = Phase10ForensicAnalyzer()
        df = pd.DataFrame({
            "action_taken": ["SELL"] * 10,
            "bars_held": [5, 10, 15, 20, 25, 30, 35, 40, 50, 60],
        })
        metrics = analyzer.analyze_holding_periods(df)
        assert isinstance(metrics, HoldingPeriodMetrics)
        assert metrics.mean_bars == 29.0
        assert metrics.median_bars == 27.5
        assert metrics.min_bars == 5.0
        assert metrics.max_bars == 60.0

    def test_winner_loser_asymmetry(self):
        analyzer = Phase10ForensicAnalyzer()
        df = pd.DataFrame({
            "action_taken": ["SELL"] * 6,
            "unrealized_pnl_bps": [50.0, 80.0, -30.0, -40.0, -20.0, -50.0],
        })
        asym = analyzer.analyze_winner_loser_asymmetry(df, total_friction_dollars=1.0)
        assert isinstance(asym, WinnerLoserAsymmetry)
        assert asym.total_trades == 6
        assert asym.winning_trades == 2
        assert asym.losing_trades == 4
        assert asym.win_rate_pct == pytest.approx(33.33, abs=0.1)

    def test_signal_deciles(self):
        analyzer = Phase10ForensicAnalyzer()
        np.random.seed(42)
        df = pd.DataFrame({
            "expected_net_edge_bps": np.linspace(-15, 25, 200),
        })
        deciles = analyzer.analyze_signal_deciles(df)
        assert len(deciles) == 10
        assert deciles[0].decile == 1
        assert deciles[-1].decile == 10
        assert deciles[-1].realized_15m_ret_bps > deciles[0].realized_15m_ret_bps

    def test_half_life_estimation(self):
        analyzer = Phase10ForensicAnalyzer()
        hl = analyzer.estimate_signal_half_life()
        assert isinstance(hl, SignalHalfLifeReport)
        assert hl.empirical_half_life_minutes == 10.5
        assert hl.decay_pct_15m > hl.decay_pct_5m

    def test_probability_calibration(self):
        analyzer = Phase10ForensicAnalyzer()
        df = pd.DataFrame({
            "probability_positive": np.random.uniform(0.50, 0.75, 500),
        })
        bins = analyzer.analyze_probability_calibration(df)
        assert len(bins) > 0
        for b in bins:
            assert isinstance(b, CalibrationBucket)


class TestValidationTuner:
    def test_parameter_grid_search(self):
        tuner = ValidationTuner()
        df = pd.DataFrame({"expected_net_edge_bps": np.random.normal(5, 10, 100)})
        best_params, results = tuner.evaluate_parameter_grid(df)
        assert isinstance(best_params, CalibratedThresholds)
        assert len(results) > 0
        assert best_params.min_net_edge_bps >= 4.0
        assert best_params.min_probability_positive >= 0.53


class TestEntryDecisionModelV1_1:
    def test_high_conviction_entry_accepted(self):
        model = EntryDecisionModelV1_1(min_net_edge_bps=10.0, min_probability_positive=0.58)
        pred = create_sample_prediction(edge_15m=14.0, p_up_15m=0.62)
        portfolio = PortfolioState(timestamp=datetime(2026, 1, 15, 10, 0), cash=1000.0, buying_power=1000.0, positions={})
        
        decision = model.evaluate_entry(pred, current_spread_bps=5.0, portfolio=portfolio)
        assert decision.action == "BUY"
        assert decision.is_authorized is True
        assert decision.reason == "HIGH_CONVICTION_EDGE_CONFIRMED"

    def test_low_edge_entry_rejected(self):
        model = EntryDecisionModelV1_1(min_net_edge_bps=10.0, min_probability_positive=0.58)
        pred = create_sample_prediction(edge_15m=6.0, p_up_15m=0.55)
        portfolio = PortfolioState(timestamp=datetime(2026, 1, 15, 10, 0), cash=1000.0, buying_power=1000.0, positions={})
        
        decision = model.evaluate_entry(pred, current_spread_bps=5.0, portfolio=portfolio)
        assert decision.action == "SKIP"
        assert decision.is_authorized is False
        assert decision.reason == "SUB_THRESHOLD_EDGE_OR_PROBABILITY"

    def test_reentry_cooldown_enforced(self):
        model = EntryDecisionModelV1_1(re_entry_cooldown_bars=30)
        pred = create_sample_prediction(symbol="NVDA", edge_15m=15.0, p_up_15m=0.65)
        portfolio = PortfolioState(timestamp=datetime(2026, 1, 15, 10, 0), cash=1000.0, buying_power=1000.0, positions={})
        
        # Record exit at bar 50
        model.record_symbol_exit("NVDA", current_bar_index=50)

        # Attempt entry at bar 60 (only 10 bars elapsed, cooldown is 30)
        decision = model.evaluate_entry(pred, current_spread_bps=5.0, portfolio=portfolio, current_bar_index=60)
        assert decision.action == "SKIP"
        assert "RE_ENTRY_COOLDOWN_ACTIVE" in decision.reason

        # Attempt entry at bar 85 (35 bars elapsed, cooldown expired)
        decision_ok = model.evaluate_entry(pred, current_spread_bps=5.0, portfolio=portfolio, current_bar_index=85)
        assert decision_ok.action == "BUY"

    def test_daily_trade_cap_enforced(self):
        model = EntryDecisionModelV1_1(max_daily_trades=2)
        pred = create_sample_prediction(edge_15m=15.0, p_up_15m=0.65)
        portfolio = PortfolioState(timestamp=datetime(2026, 1, 15, 10, 0), cash=1000.0, buying_power=1000.0, positions={})

        model.record_trade_executed()
        model.record_trade_executed()

        decision = model.evaluate_entry(pred, current_spread_bps=5.0, portfolio=portfolio)
        assert decision.action == "SKIP"
        assert decision.reason == "DAILY_TRADE_LIMIT_REACHED"


class TestExitDecisionModelV1_1:
    def test_holding_duration_lock_protects_against_premature_decay(self):
        model = ExitDecisionModelV1_1(min_holding_bars_for_signal_decay=15, min_continuation_edge_bps=-4.0)
        pos = Position(symbol="NVDA", shares=10, avg_entry_price=100.0, current_price=99.8, entry_timestamp=datetime(2026, 1, 15, 9, 30), bars_held=5)
        pred = create_sample_prediction(edge_15m=-8.0)

        decision = model.evaluate_exit(pos, current_price=99.8, prediction=pred, minutes_to_close=200.0)
        # Should HOLD because bars_held (5) < 15
        assert decision.action == "HOLD"
        assert decision.reason_category == "HOLD_CONTINUATION"

        # Now simulate position held for 20 bars
        pos.bars_held = 20
        decision_decay = model.evaluate_exit(pos, current_price=99.8, prediction=pred, minutes_to_close=200.0)
        # Should SELL because bars_held (20) >= 15 and edge is negative
        assert decision_decay.action == "SELL"
        assert decision_decay.reason_category == "SIGNAL_DECAY"

    def test_stop_loss_unconditional(self):
        model = ExitDecisionModelV1_1(stop_loss_pct=0.015)
        pos = Position(symbol="NVDA", shares=10, avg_entry_price=100.0, current_price=98.0, entry_timestamp=datetime(2026, 1, 15, 9, 30), bars_held=3)
        pred = create_sample_prediction(edge_15m=10.0)

        decision = model.evaluate_exit(pos, current_price=98.0, prediction=pred, minutes_to_close=200.0)
        assert decision.action == "SELL"
        assert decision.reason_category == "STOP_LOSS"

    def test_opportunity_switching_barrier(self):
        model = ExitDecisionModelV1_1(opportunity_switch_margin_bps=25.0)
        pos = Position(symbol="NVDA", shares=10, avg_entry_price=100.0, current_price=100.0, entry_timestamp=datetime(2026, 1, 15, 9, 30), bars_held=20)
        pred = create_sample_prediction(edge_15m=5.0)

        # Better opportunity with 15 bps edge (Advantage = 15 - 5 = 10 bps < 25 bps hurdle)
        decision_hold = model.evaluate_exit(pos, current_price=100.0, prediction=pred, minutes_to_close=200.0, best_competing_edge_bps=15.0)
        assert decision_hold.action == "HOLD"

        # Better opportunity with 35 bps edge (Advantage = 35 - 5 = 30 bps >= 25 bps hurdle)
        decision_switch = model.evaluate_exit(pos, current_price=100.0, prediction=pred, minutes_to_close=200.0, best_competing_edge_bps=35.0)
        assert decision_switch.action == "SELL"
        assert decision_switch.reason_category == "BETTER_OPPORTUNITY"
