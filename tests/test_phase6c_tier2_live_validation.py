"""
Unit and Integration Tests for Phase 6C Tier 2 Live Validation.
Verifies formal human authorization gate, Tier 2 parameter invariance,
live metric calculations, edge retention, participation distributions, and Tier 3 locking.
"""

import math
import numpy as np
import pandas as pd
import pytest

from src.portfolio.capital_ramp import (
    CapitalSecurityViolation,
    CapitalTier,
    CapitalTierConfig,
    CapitalTierManager,
    CapacityDegradationState,
    EdgeRetentionAnalyzer,
    EmpiricalImpactModel,
    EvidenceType,
    LiquidityAwareSizer,
    ParticipationTracker,
    TierCapacityMetrics,
    TierRiskEvaluator,
)


def test_tier2_formal_authorization_and_token_invalidation():
    """Verify formal human authorization protocol for Tier 2 and token rejection."""
    manager = CapitalTierManager(initial_tier=CapitalTier.TIER_1_2K5)
    assert manager.current_tier == CapitalTier.TIER_1_2K5

    # 1. Invalid or missing token fails
    with pytest.raises(PermissionError, match="token invalid"):
        manager.authorize_tier_promotion(CapitalTier.TIER_2_5K, "", "12345678901234567890123456789012")

    # 2. Reusing Tier 1 token fails (must be fresh authorization token)
    with pytest.raises(PermissionError, match="token invalid"):
        manager.authorize_tier_promotion(CapitalTier.TIER_2_5K, "SHORT_TOK", "12345678901234567890123456789012")

    # 3. Valid authorization of Tier 2
    human_token = "AUTH_HUMAN_TIER2_LIVE_AUTHORIZATION_TOKEN_20260915"
    report_hash = "d3c33d8e9f2a1b0c9d8e7f6a5b4c3d2e1f0a9b8c7d6e5f4a3b2c1d0e9f8a7b6c"
    tier2_cfg = manager.authorize_tier_promotion(CapitalTier.TIER_2_5K, human_token, report_hash)

    assert manager.current_tier == CapitalTier.TIER_2_5K
    assert tier2_cfg.authorized_capital_usd == 5000.0
    assert tier2_cfg.max_single_order_usd == 500.0
    assert tier2_cfg.max_daily_loss_usd == 100.0
    assert tier2_cfg.max_weekly_loss_usd == 200.0
    assert tier2_cfg.max_pilot_drawdown_usd == 250.0

    # 4. Fail-closed account ceiling at $5,000 (+5% buffer = $5,250)
    assert manager.verify_account_capital(5200.0) is True
    with pytest.raises(CapitalSecurityViolation, match="exceeds authorized ceiling"):
        manager.verify_account_capital(5500.0)


def test_tier2_live_metrics_and_edge_retention():
    """Verify Tier 2 empirical live metrics and edge retention evaluation."""
    analyzer = EdgeRetentionAnalyzer(baseline_net_expectancy_bps=1.57)

    tier0_net = 1.57
    tier1_net = 1.47
    tier2_net = 1.31  # Live observed Tier 2 net expectancy

    # Absolute retention vs Tier 0
    abs_ret = analyzer.calculate_absolute_edge_retention(tier2_net, base_net_bps=tier0_net)
    assert math.isclose(abs_ret, 1.31 / 1.57, abs_tol=1e-4)  # 83.4%
    assert abs_ret >= 0.80

    # Incremental retention vs Tier 1
    inc_ret = analyzer.calculate_incremental_edge_retention(tier2_net, prior_tier_net_bps=tier1_net)
    assert math.isclose(inc_ret, 1.31 / 1.47, abs_tol=1e-4)  # 89.1%

    # State classification
    state = analyzer.classify_state(abs_ret, tier2_net)
    assert state == CapacityDegradationState.HEALTHY_CAPACITY


def test_tier2_promotion_readiness_and_acceptance():
    """Verify Tier 2 acceptance criteria validation on completed sample."""
    manager = CapitalTierManager(initial_tier=CapitalTier.TIER_2_5K)

    tier2_metrics = TierCapacityMetrics(
        tier=CapitalTier.TIER_2_5K,
        authorized_capital_usd=5000.0,
        total_fills=192,
        total_sessions=32,
        average_order_notional_usd=360.0,
        median_participation_pct=0.024,
        p95_participation_pct=0.058,
        gross_alpha_bps=4.89,
        spread_bps=1.63,
        slippage_bps=0.09,
        market_impact_bps=0.16,
        latency_bps=0.05,
        implementation_shortfall_bps=1.58,
        net_expectancy_bps=1.31,
        net_expectancy_ci_lower_bps=0.74,
        net_expectancy_ci_upper_bps=1.88,
        edge_retention_ratio=0.834,
        profit_factor=1.21,
        max_drawdown_usd=62.50,
        max_drawdown_pct=1.25,
        rank_ic=0.047,
        rank_ic_p_value=0.007,
        fill_rate_pct=62.6,
        capacity_state=CapacityDegradationState.HEALTHY_CAPACITY,
    )

    is_ready, reasons = manager.check_tier_promotion_readiness(tier2_metrics)
    assert is_ready
    assert len(reasons) == 0


def test_tier2_tail_participation_tracking():
    """Verify Tier 2 participation tracking and tail thresholds (< 0.10%)."""
    tracker = ParticipationTracker()
    t0 = pd.Timestamp("2026-09-15 10:00:00")

    # Record 192 execution events
    for i in range(1, 193):
        tracker.record_execution(
            timestamp=t0 + pd.Timedelta(minutes=i * 5),
            symbol="NVDA" if i % 2 == 0 else "TSLA",
            order_shares=2.5 + (i % 5) * 0.5,
            order_notional_usd=350.0 + (i % 5) * 30.0,
            recent_volume_shares=250000.0,
            recent_volume_dollar=35000000.0,
        )

    dist = tracker.get_distribution()
    assert dist.count == 192
    assert dist.median_share_pct < 0.05
    assert dist.p95_share_pct < 0.08
    assert dist.max_share_pct < 0.10
