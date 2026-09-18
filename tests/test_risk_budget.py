"""
Unit tests for dynamic risk budget and stop distance modeling.
"""

import pytest
from src.risk.risk_budget import DynamicRiskBudgetModel


def test_effective_stop_distance_bounds():
    model = DynamicRiskBudgetModel(min_stop_distance_pct=0.010, max_stop_distance_pct=0.035)

    # Low volatility -> clamped to min stop floor (1.0%)
    stop_low = model.compute_effective_stop(intraday_vol_bps=40.0)
    assert stop_low == 0.010

    # Normal volatility (120 bps) -> 1.5 * 0.0120 = 0.0180 (1.8%)
    stop_norm = model.compute_effective_stop(intraday_vol_bps=120.0)
    assert round(stop_norm, 4) == 0.0180

    # Extreme volatility (350 bps) -> clamped to max stop ceiling (3.5%)
    stop_extreme = model.compute_effective_stop(intraday_vol_bps=350.0)
    assert stop_extreme == 0.035


def test_inverse_volatility_scaling():
    model = DynamicRiskBudgetModel()

    # Higher volatility stock receives a smaller volatility multiplier
    b_low_vol = model.compute_risk_budget(current_equity=1000.0, intraday_vol_bps=80.0)
    b_high_vol = model.compute_risk_budget(current_equity=1000.0, intraday_vol_bps=200.0)

    assert b_low_vol.volatility_multiplier > b_high_vol.volatility_multiplier
    assert b_low_vol.raw_theoretical_position_dollars > b_high_vol.raw_theoretical_position_dollars
