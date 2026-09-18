"""
Unit tests for CapacityModel and market impact limits.
"""

import pytest
from src.execution.capacity_model import CapacityModel, CapacityState


def test_liquid_mega_cap_unconstrained():
    model = CapacityModel(max_adv_participation_pct=0.010, max_minute_participation_pct=0.050)
    # Target $1,000 in NVDA ($500M ADV, $2M/min)
    assessment = model.estimate_capacity(
        symbol="NVDA",
        target_dollars=1000.0,
        adv_dollars_30d=500_000_000.0,
        minute_dollar_volume=2_000_000.0,
    )
    assert assessment.is_capacity_approved
    assert assessment.capacity_state == CapacityState.UNCONSTRAINED
    assert assessment.adv_participation_pct < 0.0001
    assert assessment.estimated_impact_bps < 1.0


def test_illiquid_stock_capacity_constrained():
    model = CapacityModel(max_adv_participation_pct=0.010, max_minute_participation_pct=0.050)
    # Target $50,000 in smaller stock ($2M ADV -> max safe ADV = $20,000)
    assessment = model.estimate_capacity(
        symbol="SMALL",
        target_dollars=50_000.0,
        adv_dollars_30d=2_000_000.0,
        minute_dollar_volume=20_000.0,
    )
    assert not assessment.is_capacity_approved
    assert assessment.max_safe_position_dollars <= 20_000.0
    assert assessment.capacity_state in (CapacityState.LIQUIDITY_LIMITED, CapacityState.IMPACT_LIMITED)
