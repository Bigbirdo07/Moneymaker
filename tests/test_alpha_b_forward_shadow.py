"""
Alpha B Forward Shadow Simulation & Dual-Book Validation Tests.
Validates Book B1 (Long-Only Shadow) deployability isolation,
Book B2 (Long-Short Research Shadow) research-only marking,
overlapping cohort turnover, multiple testing borderline classification, and timing barriers.
"""

import pytest
from src.strategies.alpha_b_reversal import (
    AlphaBMultiDayReversalStrategy,
    AlphaBShadowBookType,
    AlphaBShadowBookResult,
    AlphaBExecutionViolation,
    ExecutionMode,
)


def test_alpha_b_dual_shadow_books_generation():
    """Verify separate tracking of Book B1 (Long-Only) and Book B2 (Long-Short Research)."""
    strategy = AlphaBMultiDayReversalStrategy()
    books = strategy.simulate_forward_shadow_books(forward_days=60, modeled_friction_bps=5.0)

    assert AlphaBShadowBookType.BOOK_B1_LONG_ONLY in books
    assert AlphaBShadowBookType.BOOK_B2_LONG_SHORT in books

    b1 = books[AlphaBShadowBookType.BOOK_B1_LONG_ONLY]
    b2 = books[AlphaBShadowBookType.BOOK_B2_LONG_SHORT]

    # B1 (Long-Only) is deployability candidate under long-only mandate
    assert b1.is_deployable_under_current_rules is True
    assert b1.net_annualized_return_pct > 0
    assert b1.net_alpha_per_cycle_bps > 10.0
    assert b1.spearman_rank_ic > 0.030

    # B2 (Long-Short) is strictly research-only because shorting is prohibited
    assert b2.is_deployable_under_current_rules is False
    assert b2.net_annualized_return_pct > b1.net_annualized_return_pct
    assert b2.max_drawdown_pct < b1.max_drawdown_pct


def test_alpha_b_overlapping_cohort_turnover_modeling():
    """Verify that 3-day holding period generates ~18% daily turnover across overlapping cohorts."""
    strategy = AlphaBMultiDayReversalStrategy()
    books = strategy.simulate_forward_shadow_books(forward_days=60)
    b1 = books[AlphaBShadowBookType.BOOK_B1_LONG_ONLY]

    # Daily turnover should be approximately 1/3 / 2 * 100% ~ 16.7% to 18.0%
    assert 15.0 <= b1.daily_turnover_pct <= 20.0
    assert b1.completed_cohorts == 57


def test_alpha_b_multiple_testing_borderline_classification():
    """Verify that q=0.054 is accurately characterized as borderline at alpha=0.05."""
    strategy = AlphaBMultiDayReversalStrategy()
    p_vals = [0.011, 0.014, 0.018, 0.024, 0.035, 0.038, 0.045, 0.082, 0.120]
    fdr_res = strategy.compute_multiple_testing_correction(p_vals, alpha=0.05)

    assert fdr_res["h3_candidate_raw_p"] == 0.011
    assert 0.050 < fdr_res["h3_candidate_fdr_q"] <= 0.055

    # At strict alpha = 0.05, q=0.054 does NOT strictly pass -> borderline classification
    status = "PASS" if fdr_res["h3_candidate_fdr_q"] < 0.05 else "BORDERLINE_AFTER_MULTIPLE_TESTING"
    assert status == "BORDERLINE_AFTER_MULTIPLE_TESTING"


def test_alpha_b_forward_shadow_execution_mode_barrier():
    """Verify that Alpha B cannot execute in broker paper or live modes."""
    strategy = AlphaBMultiDayReversalStrategy()
    with pytest.raises(AlphaBExecutionViolation):
        strategy.assert_execution_allowed(ExecutionMode.BROKER_PAPER)
    with pytest.raises(AlphaBExecutionViolation):
        strategy.assert_execution_allowed(ExecutionMode.LIVE_AUTONOMOUS_MICRO)
    # Shadow execution is permitted
    strategy.assert_execution_allowed(ExecutionMode.SHADOW)
