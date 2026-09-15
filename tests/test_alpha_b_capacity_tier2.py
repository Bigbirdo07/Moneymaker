"""
Tests for Alpha B Capacity Tier 2 ($5,000 USD) Live Capacity Experiment (Phase 7F).
"""

import pytest
from src.strategies.alpha_b_reversal import (
    AlphaBCapacityManager,
    AlphaBCapacityTier,
    AlphaBCapacityState,
    AlphaBTier2ReadinessAssessment,
    AlphaBTier2LiveMetrics,
)


def test_tier2_authorization_and_tier3_locked():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_1)
    assert manager.authorized_capital_usd == 2500.0

    # Authorization required for Tier 2 ($5,000)
    with pytest.raises(PermissionError, match="Valid human authorization token required"):
        manager.authorize_tier2("")

    manager.authorize_tier2("HUMAN_AUTH_TOKEN_PHASE7F_TIER2_2026")
    assert manager.authorized_capital_usd == 5000.0
    assert manager.current_tier == AlphaBCapacityTier.TIER_2

    # Tier 3 ($10,000) must remain strictly locked
    with pytest.raises(PermissionError, match="is LOCKED"):
        manager.attempt_tier3_or_higher(AlphaBCapacityTier.TIER_3)


def test_tier2_readiness_assessment():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_1)
    readiness = manager.evaluate_tier2_readiness()

    assert readiness.authorized_capital_usd == 5000.0
    assert readiness.p50_order_notional_usd == 833.33
    assert readiness.max_concurrent_cohorts == 3
    assert readiness.avg_capital_utilization_pct > 75.0
    assert readiness.expected_net_expectancy_bps > 10.0
    assert readiness.expected_cost_break_even_multiplier > 2.5
    assert not readiness.is_authorized_for_live


def test_tier2_live_experiment_and_retention():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_2)
    metrics = manager.evaluate_tier2_live_experiment(sessions=60, cohorts=52)

    assert metrics.tier == "B-TIER_2"
    assert metrics.authorized_capital_usd == 5000.0
    assert metrics.gross_cycle_return_bps == 15.98
    assert metrics.canonical_friction_bps == 5.58
    assert abs(metrics.net_cycle_expectancy_bps - 10.40) < 1e-4

    # Absolute retention vs Tier 0: 10.40 / 10.67 = 97.47%
    assert metrics.absolute_edge_retention_pct > 95.0
    assert metrics.capacity_state == AlphaBCapacityState.HEALTHY_CAPACITY.value
    # Incremental retention vs Tier 1: 10.40 / 10.56 = 98.48%
    assert metrics.incremental_edge_retention_pct > 95.0
    assert metrics.cost_break_even_multiplier > 2.80
    assert metrics.max_drawdown_pct < 3.00
    assert metrics.critical_incidents_count == 0


def test_tier2_cost_stress():
    manager = AlphaBCapacityManager(AlphaBCapacityTier.TIER_2)
    metrics = manager.evaluate_tier2_live_experiment(sessions=60, cohorts=52)
    stresses = manager.evaluate_tier2_cost_stress(metrics)

    assert stresses["1.00x"]["is_profitable"]
    assert stresses["1.25x"]["is_profitable"]
    assert stresses["1.50x"]["is_profitable"]
    assert stresses["2.00x"]["is_profitable"]
    assert not stresses["3.00x"]["is_profitable"]  # 15.98 - 16.74 < 0
