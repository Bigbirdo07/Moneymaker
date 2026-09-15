"""
Unit and Integration Tests for Phase 6B: Controlled Capital Ramp & Capacity Validation.
Verifies discrete tier scaling, hard capital firewalls, per-symbol notional ceilings,
participation rate tracking, empirical impact curve modeling, edge retention ratio auditing,
and deterministic liquidity-aware order downsizing.
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
    CapacityBreakEvenEstimate,
    CapacityDegradationState,
    EdgeRetentionAnalyzer,
    EmpiricalImpactModel,
    ExecutionParticipation,
    FrictionDecomposition,
    LiquidityAwareSizer,
    ParticipationDistribution,
    ParticipationTracker,
    SymbolLiquidityConfig,
    TierCapacityMetrics,
    TierRiskEvaluator,
)
from src.llm.research_director import (
    LLMOutputType,
    MoneymakerResearchDirector,
    DataProvenanceType,
)


def test_capital_tier_manager_containment_and_scale_down():
    """Verify tier configuration, fail-closed ceiling enforcement, and deterministic scale-down."""
    manager = CapitalTierManager(initial_tier=CapitalTier.TIER_0_1K)
    assert manager.current_tier == CapitalTier.TIER_0_1K
    assert manager.active_config.authorized_capital_usd == 1000.0

    # 1. Verification succeeds within allowable equity range
    assert manager.verify_account_capital(1020.0) is True

    # 2. Verification fails closed if account equity exceeds ceiling
    with pytest.raises(CapitalSecurityViolation, match="exceeds authorized ceiling"):
        manager.verify_account_capital(1250.0)

    # 3. Unauthorized promotion attempt without valid token fails
    with pytest.raises(PermissionError, match="token invalid"):
        manager.authorize_tier_promotion(CapitalTier.TIER_1_2K5, "", "12345678901234567890123456789012")

    # 4. Authorized promotion succeeds with valid human token and hash
    valid_token = "AUTH_HUMAN_TIER1_TOKEN_9988776655"
    valid_hash = "abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
    promoted_cfg = manager.authorize_tier_promotion(CapitalTier.TIER_1_2K5, valid_token, valid_hash)
    assert manager.current_tier == CapitalTier.TIER_1_2K5
    assert promoted_cfg.authorized_capital_usd == 2500.0
    assert manager.verify_account_capital(2550.0) is True

    # 5. Deterministic scale-down back to Tier 0 requires zero model changes
    scaled_cfg = manager.scale_down(CapitalTier.TIER_0_1K)
    assert manager.current_tier == CapitalTier.TIER_0_1K
    assert scaled_cfg.authorized_capital_usd == 1000.0


def test_tier_promotion_readiness_checks():
    """Verify strict promotion criteria for Tier 1."""
    manager = CapitalTierManager(initial_tier=CapitalTier.TIER_1_2K5)

    # Incomplete sample: fails promotion readiness
    unready_metrics = TierCapacityMetrics(
        tier=CapitalTier.TIER_1_2K5,
        authorized_capital_usd=2500.0,
        total_fills=45,  # < 100
        total_sessions=10,  # < 20
        average_order_notional_usd=175.0,
        median_participation_pct=0.012,
        p95_participation_pct=0.028,
        gross_alpha_bps=4.90,
        spread_bps=1.62,
        slippage_bps=0.08,
        market_impact_bps=0.07,
        latency_bps=0.05,
        implementation_shortfall_bps=1.48,
        net_expectancy_bps=1.47,
        net_expectancy_ci_lower_bps=0.92,
        net_expectancy_ci_upper_bps=2.02,
        edge_retention_ratio=0.936,
        profit_factor=1.24,
        max_drawdown_usd=32.50,
        max_drawdown_pct=1.30,
        rank_ic=0.048,
        rank_ic_p_value=0.007,
        fill_rate_pct=63.2,
        capacity_state=CapacityDegradationState.HEALTHY_CAPACITY,
    )
    is_ready, reasons = manager.check_tier_promotion_readiness(unready_metrics)
    assert not is_ready
    assert any("sample fills" in r for r in reasons)
    assert any("sessions" in r for r in reasons)

    # Fully validated sample: passes promotion readiness
    ready_metrics = TierCapacityMetrics(
        tier=CapitalTier.TIER_1_2K5,
        authorized_capital_usd=2500.0,
        total_fills=164,
        total_sessions=25,
        average_order_notional_usd=180.0,
        median_participation_pct=0.012,
        p95_participation_pct=0.029,
        gross_alpha_bps=4.91,
        spread_bps=1.62,
        slippage_bps=0.08,
        market_impact_bps=0.07,
        latency_bps=0.05,
        implementation_shortfall_bps=1.48,
        net_expectancy_bps=1.47,
        net_expectancy_ci_lower_bps=0.95,
        net_expectancy_ci_upper_bps=1.99,
        edge_retention_ratio=0.936,
        profit_factor=1.24,
        max_drawdown_usd=33.50,
        max_drawdown_pct=1.34,
        rank_ic=0.048,
        rank_ic_p_value=0.006,
        fill_rate_pct=63.1,
        capacity_state=CapacityDegradationState.HEALTHY_CAPACITY,
    )
    is_ready, reasons = manager.check_tier_promotion_readiness(ready_metrics)
    assert is_ready
    assert len(reasons) == 0


def test_participation_tracker_distributions():
    """Verify participation calculation and percentiles."""
    tracker = ParticipationTracker()
    t0 = pd.Timestamp("2026-09-15 10:00:00")

    # Record 100 execution events with known distribution
    for i in range(1, 101):
        tracker.record_execution(
            timestamp=t0 + pd.Timedelta(minutes=i),
            symbol="NVDA",
            order_shares=i * 2.0,
            order_notional_usd=i * 200.0,
            recent_volume_shares=200000.0,
            recent_volume_dollar=20000000.0,
        )

    dist = tracker.get_distribution()
    assert dist.count == 100
    assert 0.04 < dist.median_share_pct < 0.06
    assert 0.08 < dist.p90_share_pct < 0.10
    assert 0.09 < dist.p95_share_pct < 0.10
    assert dist.max_share_pct == 0.10  # (200 / 200,000) * 100 = 0.10%


def test_empirical_impact_and_friction_decomposition():
    """Verify market impact curve and alpha budget decomposition."""
    model = EmpiricalImpactModel(base_shortfall_bps=1.41, impact_coefficient=0.08)

    # Baseline notional ($100) -> base shortfall
    sf_100 = model.estimate_shortfall_bps(100.0, baseline_notional_usd=100.0)
    assert math.isclose(sf_100, 1.41, abs_tol=1e-5)

    # Scaled notional ($400) -> sqrt(4) * 0.08 - 0.08 = +0.08 bps -> 1.49 bps
    sf_400 = model.estimate_shortfall_bps(400.0, baseline_notional_usd=100.0)
    assert math.isclose(sf_400, 1.49, abs_tol=1e-5)

    # Decompose friction
    fric = model.decompose_friction(
        gross_alpha_bps=4.92,
        spread_bps=1.62,
        slippage_bps=0.08,
        market_impact_bps=0.07,
        latency_bps=0.05,
    )
    assert math.isclose(fric.total_friction_bps, 1.82, abs_tol=1e-5)
    assert math.isclose(fric.remaining_net_alpha_bps, 3.10, abs_tol=1e-5)


def test_edge_retention_and_capacity_state_classification():
    """Verify edge retention calculation, state classification, and break-even estimation."""
    analyzer = EdgeRetentionAnalyzer(baseline_net_expectancy_bps=1.57)

    # 1. Edge retention ratio
    retention_90 = analyzer.calculate_edge_retention(1.45)
    assert math.isclose(retention_90, 1.45 / 1.57, abs_tol=1e-4)

    # 2. Degradation states
    assert analyzer.classify_state(0.92, 1.45) == CapacityDegradationState.HEALTHY_CAPACITY
    assert analyzer.classify_state(0.72, 1.13) == CapacityDegradationState.WATCH_CAPACITY
    assert analyzer.classify_state(0.45, 0.70) == CapacityDegradationState.DEGRADED_CAPACITY
    assert analyzer.classify_state(0.20, 0.30) == CapacityDegradationState.CAPACITY_EXCEEDED
    assert analyzer.classify_state(0.95, -0.10) == CapacityDegradationState.CAPACITY_EXCEEDED

    # 3. Capacity break-even estimation
    tier0 = TierCapacityMetrics(
        tier=CapitalTier.TIER_0_1K,
        authorized_capital_usd=1000.0,
        total_fills=216,
        total_sessions=45,
        average_order_notional_usd=90.0,
        median_participation_pct=0.005,
        p95_participation_pct=0.012,
        gross_alpha_bps=4.92,
        spread_bps=1.62,
        slippage_bps=0.08,
        market_impact_bps=0.00,
        latency_bps=0.05,
        implementation_shortfall_bps=1.41,
        net_expectancy_bps=1.57,
        net_expectancy_ci_lower_bps=1.02,
        net_expectancy_ci_upper_bps=2.12,
        edge_retention_ratio=1.00,
        profit_factor=1.26,
        max_drawdown_usd=13.50,
        max_drawdown_pct=1.35,
        rank_ic=0.049,
        rank_ic_p_value=0.005,
        fill_rate_pct=63.6,
        capacity_state=CapacityDegradationState.HEALTHY_CAPACITY,
    )
    tier1 = TierCapacityMetrics(
        tier=CapitalTier.TIER_1_2K5,
        authorized_capital_usd=2500.0,
        total_fills=164,
        total_sessions=25,
        average_order_notional_usd=180.0,
        median_participation_pct=0.012,
        p95_participation_pct=0.029,
        gross_alpha_bps=4.91,
        spread_bps=1.62,
        slippage_bps=0.08,
        market_impact_bps=0.07,
        latency_bps=0.05,
        implementation_shortfall_bps=1.48,
        net_expectancy_bps=1.47,
        net_expectancy_ci_lower_bps=0.95,
        net_expectancy_ci_upper_bps=1.99,
        edge_retention_ratio=0.936,
        profit_factor=1.24,
        max_drawdown_usd=33.50,
        max_drawdown_pct=1.34,
        rank_ic=0.048,
        rank_ic_p_value=0.006,
        fill_rate_pct=63.1,
        capacity_state=CapacityDegradationState.HEALTHY_CAPACITY,
    )

    estimate = analyzer.estimate_break_even_and_practical_capacity([tier0, tier1])
    assert estimate.break_even_capital_usd > 20000.0
    assert estimate.practical_capacity_usd < estimate.break_even_capital_usd
    assert estimate.practical_capacity_usd > 5000.0


def test_liquidity_aware_sizer_and_per_symbol_ceilings():
    """Verify deterministic downsizing and missed opportunity logging."""
    sizer = LiquidityAwareSizer()
    t0 = pd.Timestamp("2026-09-15 10:30:00")

    # 1. Normal order within NVDA limits ($250 on $140 stock = ~1.78 shares)
    shares, notional, reason = sizer.evaluate_and_size(
        symbol="NVDA",
        price=140.0,
        desired_notional_usd=250.0,
        recent_5m_volume_shares=300000.0,
        current_spread_bps=1.5,
        timestamp=t0,
    )
    assert reason == "APPROVED_FULL_SIZE"
    assert math.isclose(notional, 250.0, abs_tol=1e-4)

    # 2. Order exceeding NVDA ceiling ($2,000 > $1,500 cap)
    shares, notional, reason = sizer.evaluate_and_size(
        symbol="NVDA",
        price=140.0,
        desired_notional_usd=2000.0,
        recent_5m_volume_shares=300000.0,
        current_spread_bps=1.5,
        timestamp=t0,
    )
    assert "LIQUIDITY_DOWNSIZED" in reason
    assert math.isclose(notional, 1500.0, abs_tol=1e-4)
    assert len(sizer.missed_opportunities) == 1

    # 3. Order exceeding spread limit (> 3.0 bps)
    shares, notional, reason = sizer.evaluate_and_size(
        symbol="NVDA",
        price=140.0,
        desired_notional_usd=250.0,
        recent_5m_volume_shares=300000.0,
        current_spread_bps=3.8,
        timestamp=t0,
    )
    assert "SPREAD_TOO_WIDE" in reason
    assert notional == 0.0


def test_tier_risk_evaluator_and_stress_tests():
    """Verify VaR/ES and capacity stress simulations."""
    evaluator = TierRiskEvaluator()
    pnls = [2.5, 3.1, -1.2, 4.0, -2.8, 1.5, -4.5, 0.8, -1.0, 3.5] * 10
    var_res = evaluator.calculate_var_and_es(pnls, capital_usd=2500.0)

    assert var_res["var95_usd"] > 0.0
    assert var_res["es95_usd"] >= var_res["var95_usd"]
    assert var_res["var95_pct"] < 5.0

    stress = evaluator.run_capacity_stress_tests(
        baseline_gross_alpha_bps=4.92,
        baseline_friction_bps=3.35,
        capital_usd=2500.0,
    )
    assert stress["friction_1.00x"]["is_profitable"] is True
    assert stress["friction_1.25x"]["friction_bps"] == 3.35 * 1.25
    assert stress["flash_crash_scenario"]["within_5pct_drawdown_limit"] is True


def test_research_director_phase6b_analytical_methods():
    """Verify Research Director Phase 6B analytical inspections and read-only boundary."""
    director = MoneymakerResearchDirector()
    assert director.is_read_only is True

    # Capacity degradation inspection
    cap_out = director.inspect_capacity_degradation(
        edge_retention_ratio=0.936,
        tier_shortfall_bps=1.48,
        baseline_shortfall_bps=1.41,
    )
    assert cap_out.output_type == LLMOutputType.TIER_COMPARISON
    assert "CAPACITY HEALTHY" in cap_out.summary

    # Degraded capacity warning
    warn_out = director.inspect_capacity_degradation(
        edge_retention_ratio=0.68,
        tier_shortfall_bps=1.95,
        baseline_shortfall_bps=1.41,
    )
    assert warn_out.output_type == LLMOutputType.CAPACITY_WARNING
    assert "CAPACITY WARNING" in warn_out.summary

    # Symbol capacity inspection
    sym_out = director.inspect_symbol_capacity({
        "NVDA": {"median_participation_pct": 0.012, "shortfall_bps": 1.45, "net_expectancy_bps": 1.55},
        "AMD": {"median_participation_pct": 0.015, "shortfall_bps": 1.52, "net_expectancy_bps": 1.38},
        "TSLA": {"median_participation_pct": 0.010, "shortfall_bps": 1.47, "net_expectancy_bps": 1.48},
    })
    assert sym_out.output_type == LLMOutputType.SYMBOL_CAPACITY_ANALYSIS
    assert len(sym_out.provenance_statements) == 3
