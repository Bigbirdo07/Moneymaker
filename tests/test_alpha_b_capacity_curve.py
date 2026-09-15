"""
Tests for Alpha B Three-Point Capacity Curve Modeling (Phase 7F).
"""

import pytest
from src.strategies.alpha_b_reversal import (
    AlphaBCapacityManager,
    AlphaBCapacityTier,
    AlphaBThreePointCapacityModel,
)


def test_three_point_capacity_curve_calibration():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_2)
    model = manager.fit_three_point_capacity_curve()

    assert model.is_three_point_calibrated
    assert model.observed_capitals_usd == [1000.0, 2500.0, 5000.0]
    assert model.observed_net_expectancies_bps == [10.67, 10.56, 10.40]
    assert model.observed_frictions_bps == [5.38, 5.46, 5.58]

    # Linear decay slope per $1,000 capital: -0.0675 bps / $1k
    assert abs(model.linear_decay_slope_bps_per_1k - (-0.0675)) < 1e-4

    # Projected $10k net expectancy: ~10.06 bps
    assert model.projected_tier3_10k_net_bps > 9.5
    assert model.break_even_capacity_ceiling_usd > 100000.0
