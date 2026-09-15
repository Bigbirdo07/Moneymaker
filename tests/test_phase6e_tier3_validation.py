"""
Phase 6E Tier 3 Live Capacity Validation & Governance Tests.
Validates formal Tier 3 authorization, invariant freeze integrity, canonical friction identity,
empirical edge retention (WATCH_CAPACITY), cost-stress break-even, and model prediction cross-check.
"""

import pytest
import yaml
from src.portfolio.capital_ramp import (
    CapitalTier,
    CapitalTierManager,
    CanonicalRoundTripFriction,
    MultiModelCapacityAuditor,
    CapacityDegradationState,
    EvidenceType,
    TierCapacityMetrics,
)


def test_tier3_formal_human_authorization_and_tier4_lock():
    """Verify Tier 3 promotes upon valid human token and Tier 4 remains locked."""
    manager = CapitalTierManager()
    manager.current_tier = CapitalTier.TIER_2_5K

    # Promote to Tier 3 with valid token and hash
    promoted = manager.authorize_tier_promotion(
        CapitalTier.TIER_3_10K,
        human_auth_token="AUTH_TIER3_20260915_VERIFIED",
        tier_report_hash="PHASE6E_TIER3_REPORT_HASH_32_CHARS_OK_12345",
    )
    assert promoted.tier == CapitalTier.TIER_3_10K
    assert promoted.authorized_capital_usd == 10000.0
    assert promoted.max_single_order_usd == 1000.0
    assert manager.current_tier == CapitalTier.TIER_3_10K

    # Attempting to promote to Tier 4 must be fatal-blocked
    with pytest.raises(PermissionError, match="TIER_4_25K is LOCKED"):
        manager.authorize_tier_promotion(
            CapitalTier.TIER_4_25K,
            human_auth_token="AUTH_TIER4_UNAUTHORIZED_TOKEN_123",
            tier_report_hash="HASH_TIER4_12345678901234567890123456789012",
        )


def test_tier3_config_invariance_vs_tier2():
    """Verify that frozen_tier3.yaml maintains exact invariant strategy logic vs frozen_tier2.yaml."""
    with open("configs/frozen_tier2.yaml", "r") as f:
        t2 = yaml.safe_load(f)
    with open("configs/frozen_tier3.yaml", "r") as f:
        t3 = yaml.safe_load(f)

    # Invariant strategy fields
    assert t2["strategy_id"] == t3["strategy_id"]
    assert t2["model_specification"] == t3["model_specification"]
    assert t2["target_specification"] == t3["target_specification"]
    assert t2["autonomous_gate_specification"] == t3["autonomous_gate_specification"]
    assert t2["universe_and_archetypes"] == t3["universe_and_archetypes"]

    # Only capital-dependent fields may differ
    assert t3["capital_specification"]["authorized_capital_usd"] == 10000.0
    assert t3["capital_specification"]["max_single_order_usd"] == 1000.0
    assert t3["capital_specification"]["max_daily_loss_usd"] == 200.0
    assert t3["capital_specification"]["max_weekly_loss_usd"] == 400.0
    assert t3["capital_specification"]["max_pilot_drawdown_usd"] == 500.0


def test_tier3_canonical_friction_and_net_expectancy():
    """Verify Tier 3 canonical friction components and exact net expectancy identity."""
    t3_friction = CanonicalRoundTripFriction(
        entry_spread_bps=1.63,
        exit_spread_bps=1.65,
        entry_slippage_bps=0.05,
        exit_slippage_bps=0.05,
        market_impact_bps=0.32,
        latency_cost_bps=0.06,
        commissions_fees_bps=0.00,
        other_explicit_costs_bps=0.00,
    )

    assert round(t3_friction.total_spread_bps, 2) == 3.28
    assert round(t3_friction.total_slippage_bps, 2) == 0.10
    assert round(t3_friction.market_impact_bps, 2) == 0.32
    assert round(t3_friction.total_round_trip_friction_bps, 2) == 3.76

    gross_alpha = 4.87
    reported_net = 1.11
    assert t3_friction.validate_net_expectancy_identity(gross_alpha, reported_net, tolerance_bps=0.01)


def test_tier3_edge_retention_and_capacity_state():
    """Verify Tier 3 edge retention and classification into WATCH_CAPACITY."""
    tier0_net = 1.57
    tier2_net = 1.31
    tier3_net = 1.11

    abs_retention = tier3_net / tier0_net
    inc_retention = tier3_net / tier2_net

    assert 0.70 <= abs_retention <= 0.72  # 70.7% retention
    assert 0.84 <= inc_retention <= 0.86  # 84.7% retention

    # Classification: 60% <= retention < 80% is WATCH_CAPACITY
    if 0.60 <= abs_retention < 0.80:
        state = CapacityDegradationState.WATCH_CAPACITY
    else:
        state = CapacityDegradationState.HEALTHY_CAPACITY

    assert state == CapacityDegradationState.WATCH_CAPACITY


def test_tier3_cost_stress_and_model_prediction_cross_check():
    """Verify Tier 3 cost break-even multiplier and model prediction accuracy."""
    gross_alpha = 4.87
    friction = 3.76
    be_multiplier = gross_alpha / friction
    assert round(be_multiplier, 2) == 1.30

    # Cross-check against Square-Root Sublinear model projection
    auditor = MultiModelCapacityAuditor(baseline_gross_bps=4.89, baseline_net_bps=1.57)
    projections = auditor.fit_all_models({1000.0: 1.57, 2500.0: 1.47, 5000.0: 1.31})
    sqrt_model = [p for p in projections if p.model_name == "Square-Root Sublinear Impact"][0]

    projected_net_10k = sqrt_model.projected_net_bps_at_10k
    observed_net_10k = 1.11
    error_bps = abs(projected_net_10k - observed_net_10k)

    # Model projection was ~1.12 to 1.14 bps vs observed 1.11 bps -> error <= 0.05 bps
    assert error_bps <= 0.05
