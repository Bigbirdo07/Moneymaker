"""
Tests for Alpha B Human-Alpha Decomposition and Autonomy Readiness (Phase 7C Track B).
Verifies:
1. Model-eligible proposal population accounting.
2. Safety rejection vs discretionary rejection taxonomy.
3. Blinded vs unblinded approval experiment stats.
4. Human alpha decomposition arithmetic and latency metrics.
5. Autonomous counterfactual (Book D) autonomy-gap math.
6. ResearchDirector read-only structured analytical outputs.
"""

import pytest
from src.strategies.alpha_b_reversal import (
    AlphaBExtendedLiveEvaluator,
    AlphaBHumanAlphaDecompositionResult,
    AlphaBRejectionCategory,
    AlphaBRejectionReasonCode,
    AlphaBInformationViewType,
    AlphaBHumanInformationAuditPayload,
    AlphaBRejectedCounterfactualOutcome,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)


def test_human_alpha_decomposition_math_and_proportions():
    """Validates additive decomposition of governed live performance into intrinsic vs human components."""
    evaluator = AlphaBExtendedLiveEvaluator()
    decomp: AlphaBHumanAlphaDecompositionResult = evaluator.decompose_human_alpha(total_proposals=160)

    assert decomp.total_model_eligible_proposals == 160
    assert decomp.human_approved_count == 144
    assert decomp.human_rejected_count == 16
    assert decomp.safety_rejections_count == 13
    assert decomp.discretionary_rejections_count == 3
    assert decomp.safety_rejections_count + decomp.discretionary_rejections_count == decomp.human_rejected_count

    # Additive identity in bps:
    # Net Governed = Model Intrinsic + Human Discretionary - Human Latency - Live Impl
    expected_net = (
        decomp.model_intrinsic_alpha_bps
        + decomp.human_discretionary_alpha_bps
        - decomp.human_latency_cost_bps
        - decomp.live_implementation_effect_bps
    )
    assert abs(decomp.net_governed_realized_bps - expected_net) < 1e-6
    assert decomp.net_governed_realized_bps == pytest.approx(10.68, abs=0.01)

    # Intrinsic model edge accounts for >99% of total edge
    assert decomp.model_intrinsic_alpha_bps >= 10.50
    assert decomp.human_discretionary_alpha_bps <= 0.15


def test_blinded_approval_experiment_and_latency_distribution():
    """Validates blinded vs unblinded experiment and operator latency metrics."""
    evaluator = AlphaBExtendedLiveEvaluator()
    decomp = evaluator.decompose_human_alpha(total_proposals=160)

    # Blinded difference is not statistically significant (p > 0.05)
    assert decomp.blinded_difference_p_value > 0.50
    assert abs(decomp.full_info_net_expectancy_bps - decomp.safety_only_net_expectancy_bps) < 0.20

    # Latency percentiles
    assert decomp.median_latency_sec < decomp.p75_latency_sec < decomp.p95_latency_sec < decomp.max_latency_sec
    assert decomp.median_latency_sec == 142.0
    assert decomp.p95_latency_sec == 680.0


def test_human_information_audit_payload_and_rejected_counterfactual():
    """Verifies structured audit payload formatting and rejected trade tracking."""
    payload = AlphaBHumanInformationAuditPayload(
        proposal_id="PROP_20260915_NVDA_01",
        symbol="NVDA",
        decision_date="2026-09-15",
        order_side="BUY",
        target_shares=2,
        notional_usd=300.0,
        current_premarket_spread_bps=2.1,
        overnight_gap_pct=0.008,
        has_earnings_event=False,
        current_symbol_exposure_usd=0.0,
        current_account_loss_usd=0.0,
        model_score=0.88,
        universe_rank=1,
        expected_alpha_bps=18.5,
        recent_cohort_pnl_bps=12.4,
        view_type=AlphaBInformationViewType.FULL_INFORMATION,
    )
    assert payload.symbol == "NVDA"
    assert payload.model_score == 0.88

    rejected_rec = AlphaBRejectedCounterfactualOutcome(
        proposal_id="PROP_20260915_NVDA_01",
        symbol="NVDA",
        decision_date="2026-09-15",
        rejection_category=AlphaBRejectionCategory.SAFETY_REJECTION,
        reason_code=AlphaBRejectionReasonCode.OVERNIGHT_GAP_EXCEEDED,
        realized_ret_1d_bps=-12.0,
        realized_ret_2d_bps=-8.5,
        realized_ret_3d_bps=-5.0,
        realized_ret_5d_bps=+2.0,
    )
    assert rejected_rec.rejection_category == AlphaBRejectionCategory.SAFETY_REJECTION
    assert rejected_rec.realized_ret_3d_bps == -5.0


def test_research_director_human_selection_and_autonomy_readiness_methods():
    """Validates read-only LLM analytical methods for human selection and autonomy readiness."""
    rd = MoneymakerResearchDirector()
    
    # Human Selection Finding
    hs_out = rd.generate_human_selection_finding(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        model_intrinsic_alpha_bps=10.70,
        human_discretionary_alpha_bps=0.08,
        human_latency_cost_bps=0.05,
        p_value=0.785,
    )
    assert hs_out.output_type == LLMOutputType.HUMAN_SELECTION_FINDING
    assert "model-intrinsic" in hs_out.summary
    assert len(hs_out.provenance_statements) == 1

    # Autonomy Readiness Finding
    ar_out = rd.generate_autonomy_readiness_finding(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        autonomy_gap_bps=0.02,
        gap_ci_lower_bps=-0.45,
        gap_ci_upper_bps=+0.49,
        is_candidate=True,
    )
    assert ar_out.output_type == LLMOutputType.AUTONOMY_READINESS_FINDING
    assert "AUTONOMOUS_RESEARCH_CANDIDATE" in ar_out.summary
