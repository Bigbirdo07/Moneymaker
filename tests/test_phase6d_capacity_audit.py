"""
Phase 6D Capacity Model & Friction Accounting Audit Tests.
Validates canonical friction identity, multi-model capacity curve fits,
explicit retention thresholds, Tier 3 lockout, and ModelAuditFinding telemetry.
"""

import pytest
from src.portfolio.capital_ramp import (
    CapitalTier,
    CanonicalRoundTripFriction,
    MultiModelCapacityAuditor,
    CapacityThresholdSummary,
    Tier3PreRegisteredForecast,
    CapitalTierManager,
    EvidenceType,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
    ModelAuditFinding,
)


def test_canonical_friction_reconciliation_identity():
    """Verify that Tier 2 friction components sum exactly to the reported 3.58 bps total."""
    friction = CanonicalRoundTripFriction(
        entry_spread_bps=1.63,
        exit_spread_bps=1.65,
        entry_slippage_bps=0.05,
        exit_slippage_bps=0.04,
        market_impact_bps=0.16,
        latency_cost_bps=0.05,
        commissions_fees_bps=0.00,
        other_explicit_costs_bps=0.00,
    )

    assert round(friction.total_spread_bps, 2) == 3.28
    assert round(friction.total_slippage_bps, 2) == 0.09
    assert round(friction.total_round_trip_friction_bps, 2) == 3.58

    gross_alpha = 4.89
    reported_net = 1.31
    assert friction.validate_net_expectancy_identity(gross_alpha, reported_net, tolerance_bps=0.01)


def test_friction_reconciliation_detects_mismatch():
    """Verify that inconsistent friction arithmetic fails reconciliation."""
    bad_friction = CanonicalRoundTripFriction(
        entry_spread_bps=1.63,
        exit_spread_bps=0.00,  # Missing exit leg
        entry_slippage_bps=0.05,
        exit_slippage_bps=0.04,
        market_impact_bps=0.16,
        latency_cost_bps=0.05,
    )
    assert round(bad_friction.total_round_trip_friction_bps, 2) == 1.93
    gross_alpha = 4.89
    reported_net = 1.31
    # 4.89 - 1.93 = 2.96 != 1.31 -> must fail validation
    assert not bad_friction.validate_net_expectancy_identity(gross_alpha, reported_net, tolerance_bps=0.01)


def test_multi_model_capacity_auditor():
    """Verify fitting of multiple capacity models across observed live points ($1k, $2.5k, $5k)."""
    auditor = MultiModelCapacityAuditor(baseline_gross_bps=4.89, baseline_net_bps=1.57)
    projections = auditor.fit_all_models({1000.0: 1.57, 2500.0: 1.47, 5000.0: 1.31})

    assert len(projections) == 4
    model_names = [p.model_name for p in projections]
    assert "Linear in Notional" in model_names
    assert "Square-Root Sublinear Impact" in model_names
    assert "Log-Linear Model" in model_names
    assert "Quadratic Polynomial" in model_names

    # Check Square-Root Sublinear Impact model predictions
    sqrt_model = [p for p in projections if p.model_name == "Square-Root Sublinear Impact"][0]
    assert sqrt_model.is_monotonic is True
    assert 1.10 <= sqrt_model.projected_net_bps_at_10k <= 1.25
    assert 68.0 <= sqrt_model.retention_pct_at_10k <= 78.0
    assert 70000.0 <= sqrt_model.break_even_capital_usd <= 95000.0


def test_explicit_retention_thresholds_audit():
    """Verify explicit retention thresholds: 80% is ~$6k, 50% is ~$25k, break-even is ~$86k."""
    auditor = MultiModelCapacityAuditor(baseline_net_bps=1.57)
    thresholds = auditor.compute_explicit_retention_thresholds()

    assert isinstance(thresholds, CapacityThresholdSummary)
    assert 5500.0 <= thresholds.capacity_80_retention_usd <= 7500.0
    assert 20000.0 <= thresholds.capacity_50_retention_usd <= 30000.0
    assert 75000.0 <= thresholds.capacity_break_even_usd <= 95000.0


def test_tier3_locked_and_forecast_frozen():
    """Verify Tier 3 ($10,000) cannot be promoted and forecast is frozen."""
    manager = CapitalTierManager(
        initial_tier=CapitalTier.TIER_2_5K,
        locked_tiers={CapitalTier.TIER_3_10K, CapitalTier.TIER_4_25K, CapitalTier.TIER_5_50K},
    )

    # Direct activation of Tier 3 must raise PermissionError
    with pytest.raises(PermissionError, match="LOCKED"):
        manager.authorize_tier_promotion(
            CapitalTier.TIER_3_10K,
            human_auth_token="AUTH_TOKEN_TEST_1234567890",
            tier_report_hash="REPORT_HASH_12345678901234567890123456789012",
        )

    # Check pre-registered forecast
    forecast = Tier3PreRegisteredForecast()
    assert forecast.is_frozen is True
    assert forecast.authorized_capital_usd == 10000.0
    assert forecast.projected_net_expectancy_bps == 1.14
    assert forecast.forecast_evidence_type == EvidenceType.PROJECTED


def test_research_director_model_audit_finding():
    """Verify that Research Director generates structured MODEL_AUDIT_FINDING outputs."""
    director = MoneymakerResearchDirector()
    output = director.generate_model_audit_finding(
        severity="MEDIUM",
        artifact="PHASE_6C_REPORT.md",
        metric="TOTAL_FRICTION_BPS",
        expected_value=3.58,
        observed_value=1.93,
        discrepancy="Single-leg spread reported instead of round-trip spread",
        possible_causes=["Omission of exit spread leg in narrative table"],
        recommended_test="test_canonical_friction_reconciliation_identity",
    )

    assert output.output_type == LLMOutputType.MODEL_AUDIT_FINDING
    assert len(output.model_audit_findings) == 1
    finding = output.model_audit_findings[0]
    assert finding.severity == "MEDIUM"
    assert finding.metric == "TOTAL_FRICTION_BPS"
    assert "test_canonical_friction_reconciliation_identity" in output.proposed_experiments
