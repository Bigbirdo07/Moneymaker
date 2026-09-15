"""
Tests for Alpha B Capacity Tier 1 ($2,500 USD) and Multi-Day Capacity Modeling (Phase 7E).
"""

import pytest
import numpy as np
import pandas as pd
from src.strategies.alpha_b_reversal import (
    AlphaBCapacityManager,
    AlphaBCapacityTier,
    AlphaBCapacityState,
    AlphaBCapacityRejectionType,
    AlphaBTier1ReadinessAssessment,
    AlphaBTier1LiveMetrics,
)


def test_tier_hierarchy_and_locked_status():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_0)
    assert manager.authorized_capital_usd == 1000.0

    # Authorization required for Tier 1
    with pytest.raises(PermissionError, match="Valid human authorization token required"):
        manager.authorize_tier1("")

    manager.authorize_tier1("HUMAN_AUTH_TOKEN_PHASE7E_TIER1_2026")
    assert manager.authorized_capital_usd == 2500.0
    assert manager.current_tier == AlphaBCapacityTier.TIER_1

    # Tier 2 and Tier 3 must remain strictly locked
    with pytest.raises(PermissionError, match="is LOCKED"):
        manager.attempt_tier2_or_higher(AlphaBCapacityTier.TIER_2)

    with pytest.raises(PermissionError, match="is LOCKED"):
        manager.attempt_tier2_or_higher(AlphaBCapacityTier.TIER_3)


def test_tier1_readiness_assessment_generation():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_0)
    readiness = manager.evaluate_tier1_readiness()

    assert readiness.authorized_capital_usd == 2500.0
    assert readiness.p50_order_notional_usd == 416.67
    assert readiness.max_concurrent_cohorts == 3
    assert readiness.avg_capital_utilization_pct > 70.0
    assert readiness.expected_net_expectancy_bps > 10.0
    assert readiness.expected_cost_break_even_multiplier > 2.5
    assert not readiness.is_authorized_for_live


def test_tier1_edge_retention_and_capacity_state():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_1)
    metrics = manager.evaluate_tier1_live_experiment(sessions=60, cohorts=52)

    assert metrics.tier == "B-TIER_1"
    assert metrics.authorized_capital_usd == 2500.0
    assert metrics.gross_cycle_return_bps == 16.02
    assert metrics.canonical_friction_bps == 5.46
    assert abs(metrics.net_cycle_expectancy_bps - 10.56) < 1e-4

    # Absolute edge retention: 10.56 / 10.67 = 98.97%
    assert metrics.absolute_edge_retention_pct > 95.0
    assert metrics.capacity_state == AlphaBCapacityState.HEALTHY_CAPACITY.value
    assert metrics.cost_break_even_multiplier > 2.90
    assert metrics.max_drawdown_pct < 3.00
    assert metrics.critical_incidents_count == 0


def test_participation_distribution_and_capacity_rejections():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_1)
    notionals = [400.0, 500.0, 600.0, 800.0, 1000.0]
    dollar_volumes = [5000000.0, 8000000.0, 6000000.0, 10000000.0, 12000000.0]

    dist = manager.compute_participation_distribution(notionals, dollar_volumes)
    assert dist["p50"] > 0.0
    assert dist["max"] < 0.001  # Ultra-low market participation (< 0.1%)

    event = manager.record_capacity_rejection(
        session_id=10,
        symbol="NVDA",
        requested_notional=833.33,
        allowed_notional=500.00,
        rejection_type=AlphaBCapacityRejectionType.CAPACITY_RESIZED,
        counterfactual_return_bps=12.5,
    )
    assert event.missed_alpha_usd > 0.0
    assert len(manager.rejection_log) == 1


def test_tier1_cost_stress_evaluation():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_1)
    metrics = manager.evaluate_tier1_live_experiment(sessions=60, cohorts=52)
    stresses = manager.evaluate_tier1_cost_stress(metrics)

    assert stresses["1.00x"]["is_profitable"]
    assert stresses["1.25x"]["is_profitable"]
    assert stresses["1.50x"]["is_profitable"]
    assert stresses["2.00x"]["is_profitable"]
    assert not stresses["3.00x"]["is_profitable"]  # 16.02 - 16.38 < 0
