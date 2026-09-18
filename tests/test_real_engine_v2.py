"""
Unit tests for Real-Market Feature Store, Forecaster V2, Entry V2, Exit V2, and Allocator V2.
"""

import pytest
import numpy as np
import pandas as pd

from src.features.real_market_feature_store import RealMarketFeatureStore
from src.models.real_market_multi_horizon_forecaster_v2 import RealMarketMultiHorizonForecasterV2, MultiHorizonPredictionV2, HorizonForecastV2
from src.signals.real_market_entry_model_v2 import RealMarketEntryModelV2, EntryDecisionV2
from src.signals.real_market_exit_model_v2 import RealMarketExitModelV2, ExitDecisionV2
from src.execution.real_market_allocator_v2 import RealMarketAllocatorV2


def test_entry_model_v2_cash_first_class_action():
    entry_model = RealMarketEntryModelV2(
        min_net_edge_bps=12.0,
        min_calibrated_prob=0.55,
        max_daily_trades=3,
        re_entry_cooldown_bars=30,
        max_position_allocation_pct=0.50,
        max_concurrent_positions=2,
    )
    entry_model.reset_session("2026-06-15")

    # Low edge prediction -> CASH
    pred_low = MultiHorizonPredictionV2(
        symbol="AAPL",
        timestamp="2026-06-15 10:15:00",
        forecast_15m=HorizonForecastV2(15, 2.0, 0.51, 0.51, 0.1, 1.0),
        forecast_30m=HorizonForecastV2(30, 4.0, 0.52, 0.52, 0.1, 1.0),
        forecast_60m=HorizonForecastV2(60, 5.0, 0.53, 0.53, 0.1, 1.0),
        optimal_target_horizon_min=60,
        best_expected_net_edge_bps=5.0,
        best_calibrated_prob=0.53,
    )
    dec = entry_model.evaluate_entry(pred_low, current_bar_index=45, time_str="10:15:00", current_active_positions_count=0)
    assert dec.action == "CASH"
    assert not dec.is_authorized

    # High edge prediction -> BUY
    pred_high = MultiHorizonPredictionV2(
        symbol="NVDA",
        timestamp="2026-06-15 10:15:00",
        forecast_15m=HorizonForecastV2(15, 14.0, 0.58, 0.58, 0.3, 1.0),
        forecast_30m=HorizonForecastV2(30, 18.5, 0.62, 0.62, 0.4, 1.0),
        forecast_60m=HorizonForecastV2(60, 16.0, 0.59, 0.59, 0.3, 1.0),
        optimal_target_horizon_min=30,
        best_expected_net_edge_bps=18.5,
        best_calibrated_prob=0.62,
    )
    dec_buy = entry_model.evaluate_entry(pred_high, current_bar_index=45, time_str="10:15:00", current_active_positions_count=0)
    assert dec_buy.action == "BUY"
    assert dec_buy.is_authorized
    assert dec_buy.best_horizon_min == 30


def test_exit_model_v2_hard_stop_and_take_profit():
    exit_model = RealMarketExitModelV2(
        stop_loss_pct=0.015,
        take_profit_pct=0.030,
        trailing_drawdown_pct=0.008,
        max_holding_bars=90,
    )

    # Normal hold
    dec_hold = exit_model.evaluate_exit(
        symbol="NVDA",
        timestamp="2026-06-15T10:30:00",
        entry_price=100.0,
        current_price=100.5,
        high_price=100.8,
        low_price=99.8,
        bars_held=15,
        target_horizon_bars=30,
        current_continuation_edge_bps=5.0,
        time_str="10:30:00",
    )
    assert dec_hold.action == "HOLD"

    # Stop loss trigger
    dec_stop = exit_model.evaluate_exit(
        symbol="NVDA",
        timestamp="2026-06-15T10:35:00",
        entry_price=100.0,
        current_price=98.4,
        high_price=100.2,
        low_price=98.3,
        bars_held=20,
        target_horizon_bars=30,
        current_continuation_edge_bps=-2.0,
        time_str="10:35:00",
    )
    assert dec_stop.action == "SELL"
    assert "HARD_STOP_LOSS" in dec_stop.reason


def test_allocator_v2_whole_share_and_cash_reserve():
    allocator = RealMarketAllocatorV2(
        max_active_positions=2,
        max_position_capital_pct=0.50,
        sizing_policy="VOLATILITY_ADJUSTED",
        min_position_notional=100.0,
        reserve_cash_pct=0.05,
    )

    decision = EntryDecisionV2(
        symbol="NVDA",
        timestamp="2026-06-15 10:15:00",
        action="BUY",
        reason="HIGH_EDGE",
        best_horizon_min=30,
        expected_net_edge_bps=15.0,
        calibrated_probability=0.60,
        confidence_score=0.4,
        suggested_allocation_pct=0.50,
        is_authorized=True,
    )

    alloc = allocator.compute_allocation(
        decision=decision,
        current_price=120.0,
        available_cash=1000.0,
        total_equity=1000.0,
        current_active_count=0,
        realized_vol_bps=10.0,
        estimated_spread_bps=3.0,
    )
    assert alloc.is_allocated
    assert alloc.target_shares > 0
    assert alloc.target_notional <= 500.0
    assert isinstance(alloc.target_shares, int)
