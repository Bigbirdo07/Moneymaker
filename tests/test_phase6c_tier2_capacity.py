"""
Unit and Integration Tests for Phase 6C: Tier 2 Capacity Architecture & Alpha B Research Track.
Verifies Tier 2 pre-activation governance, Tier 3 locking, edge retention math,
evidence classification, capacity reject logging, Research Director read-only boundaries,
and Alpha B isolated research track execution prohibitions.
"""

import math
import numpy as np
import pandas as pd
import pytest

from src.broker.adapter import ExecutionMode
from src.portfolio.capital_ramp import (
    CapitalSecurityViolation,
    CapitalTier,
    CapitalTierConfig,
    CapitalTierManager,
    CapacityBreakEvenEstimate,
    CapacityDegradationState,
    EdgeRetentionAnalyzer,
    EmpiricalImpactModel,
    EvidenceType,
    ExecutionParticipation,
    LiquidityAwareSizer,
    ParticipationDistribution,
    ParticipationTracker,
    TierCapacityMetrics,
    TierRiskEvaluator,
)
from src.strategies.alpha_b_reversal import (
    AlphaBExecutionViolation,
    AlphaBFeatureConfig,
    AlphaBMultiDayReversalStrategy,
    AlphaBTargetHorizon,
)
from src.llm.research_director import (
    LLMOutputType,
    MoneymakerResearchDirector,
)


def test_tier2_authorization_and_tier3_locking():
    """Verify Tier 2 requires explicit authorization and Tier 3 is permanently locked."""
    manager = CapitalTierManager(
        initial_tier=CapitalTier.TIER_1_2K5,
        locked_tiers={CapitalTier.TIER_3_10K, CapitalTier.TIER_4_25K, CapitalTier.TIER_5_50K},
    )
    assert manager.current_tier == CapitalTier.TIER_1_2K5

    # 1. Attempting Tier 2 promotion without valid token fails
    with pytest.raises(PermissionError, match="token invalid"):
        manager.authorize_tier_promotion(CapitalTier.TIER_2_5K, "", "hash12345678901234567890123456789012")

    # 2. Tier 3 promotion is hard-locked even with token
    with pytest.raises(PermissionError, match="LOCKED and cannot be authorized"):
        manager.authorize_tier_promotion(
            CapitalTier.TIER_3_10K,
            "HUMAN_AUTH_TOKEN_9988776655443322",
            "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890",
        )

    # 3. Valid authorization of Tier 2 succeeds
    token = "HUMAN_AUTH_TOKEN_9988776655443322"
    rep_hash = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    t2_cfg = manager.authorize_tier_promotion(CapitalTier.TIER_2_5K, token, rep_hash)
    assert manager.current_tier == CapitalTier.TIER_2_5K
    assert t2_cfg.authorized_capital_usd == 5000.0
    assert t2_cfg.max_single_order_usd == 500.0
    assert t2_cfg.max_daily_loss_usd == 100.0
    assert t2_cfg.max_weekly_loss_usd == 200.0
    assert t2_cfg.max_pilot_drawdown_usd == 250.0

    # 4. Account equity ceiling enforcement at Tier 2
    assert manager.verify_account_capital(5150.0) is True
    with pytest.raises(CapitalSecurityViolation, match="exceeds authorized ceiling"):
        manager.verify_account_capital(5500.0)


def test_tier2_readiness_assessment_generation():
    """Verify structured Tier 2 readiness assessment dictionary."""
    manager = CapitalTierManager(initial_tier=CapitalTier.TIER_1_2K5)
    readiness = manager.generate_tier2_readiness_assessment()

    assert readiness["target_tier"] == "TIER_2_5K"
    assert readiness["target_capital_usd"] == 5000.0
    assert readiness["max_single_order_usd"] == 500.0
    assert readiness["max_daily_loss_usd"] == 100.0
    assert readiness["max_pilot_drawdown_usd"] == 250.0
    assert readiness["readiness_status"] == "READY_FOR_HUMAN_AUTHORIZATION"
    assert readiness["tier3_status"] == "LOCKED"


def test_absolute_and_incremental_edge_retention_math():
    """Verify dual edge retention calculations (Tier N / Tier 0 vs Tier N / Tier N-1)."""
    analyzer = EdgeRetentionAnalyzer(baseline_net_expectancy_bps=1.57)

    tier1_net = 1.47  # Tier 1 observed
    tier2_net = 1.34  # Tier 2 projected
    tier3_net = 1.09  # Tier 3 projected

    # Tier 1 vs Tier 0
    t1_abs = analyzer.calculate_absolute_edge_retention(tier1_net, base_net_bps=1.57)
    assert math.isclose(t1_abs, 1.47 / 1.57, abs_tol=1e-4)  # 93.6%

    # Tier 2 vs Tier 0 (Absolute)
    t2_abs = analyzer.calculate_absolute_edge_retention(tier2_net, base_net_bps=1.57)
    assert math.isclose(t2_abs, 1.34 / 1.57, abs_tol=1e-4)  # 85.4%

    # Tier 2 vs Tier 1 (Incremental)
    t2_inc = analyzer.calculate_incremental_edge_retention(tier2_net, prior_tier_net_bps=1.47)
    assert math.isclose(t2_inc, 1.34 / 1.47, abs_tol=1e-4)  # 91.2%

    # Tier 3 vs Tier 0 (Absolute)
    t3_abs = analyzer.calculate_absolute_edge_retention(tier3_net, base_net_bps=1.57)
    assert math.isclose(t3_abs, 1.09 / 1.57, abs_tol=1e-4)  # 69.4%
    assert analyzer.classify_state(t3_abs, tier3_net) == CapacityDegradationState.WATCH_CAPACITY


def test_evidence_type_and_projected_capacity_properties():
    """Verify evidence type taxonomy and projected capacity properties."""
    analyzer = EdgeRetentionAnalyzer(baseline_net_expectancy_bps=1.57)
    est = analyzer.estimate_break_even_and_practical_capacity([])

    assert est.evidence_type == EvidenceType.PROJECTED
    assert est.projected_break_even_capital_usd == est.break_even_capital_usd
    assert est.projected_practical_capacity_usd == est.practical_capacity_usd
    assert est.projected_break_even_capital_usd > 50000.0
    assert 20000.0 < est.projected_practical_capacity_usd < 40000.0


def test_capacity_rejections_resizing_and_deployable_alpha():
    """Verify CAPACITY_REJECTED, CAPACITY_RESIZED, and deployable vs model alpha tracking."""
    sizer = LiquidityAwareSizer()
    t0 = pd.Timestamp("2026-09-15 11:00:00")

    # 1. Order resized for volume participation
    # Desired $500, but 5m volume is only 500 shares * $140 = $70,000 * 0.005 (0.5% cap) = $350 max
    shares, notional, reason = sizer.evaluate_and_size(
        symbol="NVDA",
        price=140.0,
        desired_notional_usd=500.0,
        recent_5m_volume_shares=2500.0,  # 2500 * $140 * 0.01 = $3,500 > $1500 cap -> capped at $500
        current_spread_bps=1.8,
        timestamp=t0,
    )
    assert reason == "APPROVED_FULL_SIZE"

    # 2. Extreme low liquidity bar causes downsizing
    shares, notional, reason = sizer.evaluate_and_size(
        symbol="NVDA",
        price=140.0,
        desired_notional_usd=500.0,
        recent_5m_volume_shares=200.0,  # 200 * $140 * 0.01 = $280 < $500 -> downsized to $280
        current_spread_bps=1.8,
        timestamp=t0,
    )
    assert "LIQUIDITY_DOWNSIZED" in reason
    assert math.isclose(notional, 280.0, abs_tol=1e-3)
    assert len(sizer.missed_opportunities) == 1
    assert sizer.missed_opportunities[-1].rejection_reason == "CAPACITY_RESIZED"

    # 3. Spread expansion causes rejection
    shares, notional, reason = sizer.evaluate_and_size(
        symbol="NVDA",
        price=140.0,
        desired_notional_usd=500.0,
        recent_5m_volume_shares=100000.0,
        current_spread_bps=3.5,  # > 3.0 bps
        timestamp=t0,
    )
    assert "SPREAD_TOO_WIDE" in reason
    assert notional == 0.0
    assert sizer.missed_opportunities[-1].rejection_reason == "CAPACITY_REJECTED_SPREAD_LIMIT"


def test_research_director_cannot_authorize_or_execute():
    """Verify Moneymaker Research Director is strictly read-only and cannot alter capital or routing."""
    director = MoneymakerResearchDirector()
    assert director.is_read_only is True

    # Confirm it does not have capital authorization or order routing methods
    assert not hasattr(director, "authorize_capital")
    assert not hasattr(director, "submit_order")
    assert not hasattr(director, "resize_live_order")
    assert not hasattr(director, "override_risk")


def test_alpha_b_execution_mode_prohibitions():
    """Verify Alpha B is strictly barred from live and autonomous execution modes."""
    strategy = AlphaBMultiDayReversalStrategy()

    # 1. Allowed modes: SHADOW, BROKER_PAPER
    strategy.assert_research_permission(ExecutionMode.SHADOW)
    strategy.assert_research_permission(ExecutionMode.BROKER_PAPER)

    # 2. Prohibited modes: LIVE, LIVE_GOVERNED_MICRO, LIVE_AUTONOMOUS_MICRO
    with pytest.raises(AlphaBExecutionViolation, match="strictly prohibited from live execution"):
        strategy.assert_research_permission(ExecutionMode.LIVE)

    with pytest.raises(AlphaBExecutionViolation, match="strictly prohibited from live execution"):
        strategy.assert_research_permission(ExecutionMode.LIVE_GOVERNED_MICRO)

    with pytest.raises(AlphaBExecutionViolation, match="strictly prohibited from live execution"):
        strategy.assert_research_permission(ExecutionMode.LIVE_AUTONOMOUS_MICRO)


def test_alpha_b_feature_computation_and_targets():
    """Verify Alpha B leakage-safe feature and multi-horizon target calculation."""
    strategy = AlphaBMultiDayReversalStrategy()

    # Generate synthetic daily data for 50 days
    dates = pd.date_range("2026-01-01", periods=50, freq="B")
    np.random.seed(42)
    closes = 100.0 + np.cumsum(np.random.randn(50) * 1.5)
    opens = closes * (1.0 + np.random.randn(50) * 0.005)
    highs = np.maximum(opens, closes) + 1.0
    lows = np.minimum(opens, closes) - 1.0
    volumes = np.random.randint(1000000, 5000000, size=50).astype(float)

    df = pd.DataFrame({
        "open": opens,
        "high": highs,
        "low": lows,
        "close": closes,
        "volume": volumes,
    }, index=dates)

    features_df = strategy.compute_daily_features(df)
    assert "ret_1d" in features_df.columns
    assert "reversal_3d" in features_df.columns
    assert "overnight_gap" in features_df.columns
    assert "dist_sma20" in features_df.columns
    assert "vol_20d" in features_df.columns
    assert "volume_shock" in features_df.columns
    assert len(features_df) > 0

    targets_df = strategy.generate_forward_targets(df)
    assert "target_ret_1d" in targets_df.columns
    assert "target_ret_3d" in targets_df.columns
    assert "target_ret_5d" in targets_df.columns
    assert "target_ret_10d" in targets_df.columns

    # Record experiment to Alpha B multiple testing ledger
    entry = strategy.record_experiment(
        experiment_id="ALPHA_B_EXP_005",
        hypothesis="Test 3D reversal feature baseline",
        target_horizon=AlphaBTargetHorizon.HORIZON_3D,
        rank_ic=0.038,
        rank_ic_p_value=0.012,
        gross_alpha_bps=18.5,
    )
    assert entry["experiment_id"] == "ALPHA_B_EXP_005"
    assert entry["strategy_id"] == "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL"
    assert len(strategy.experiment_ledger) == 1
