"""
Tests for Alpha B Extended Governed Live Evaluation and 4-Book Reconciliation (Phase 7C Track B).
Verifies:
1. Cumulative extended live sample (75 sessions, 72 completed 3-day cohorts) at $1,000 capital.
2. Canonical friction reconciliation and cost break-even multiplier.
3. 4-Book reconciliation (Book A Live vs Book B Shadow vs Book C Paper vs Book D Autonomous Counterfactual).
4. Cost stress test matrix (1.25x, 1.5x, 2.0x, 3.0x).
5. Symbol generalization and event attribution partitioning.
"""

import pytest
from src.strategies.alpha_b_reversal import (
    AlphaBExtendedLiveEvaluator,
    AlphaBFourBookComparisonResult,
    AlphaBExtendedLiveMetrics,
    AlphaBLiveGovernedEngine,
    AlphaBExecutionViolation,
    ExecutionMode,
)


def test_alpha_b_extended_live_metrics_and_friction_reconciliation():
    """Validates cumulative 75-session live metrics and exact friction reconciliation."""
    evaluator = AlphaBExtendedLiveEvaluator()
    metrics = evaluator.compute_extended_live_metrics(sessions=75, completed_cohorts=72)

    assert metrics.total_live_sessions == 75
    assert metrics.completed_cohorts == 72
    assert metrics.gross_cycle_return_bps == 16.10
    
    # Exact canonical friction identity
    expected_friction = (
        metrics.entry_spread_bps
        + metrics.exit_spread_bps
        + metrics.entry_slippage_bps
        + metrics.exit_slippage_bps
        + metrics.fees_bps
    )
    assert abs(metrics.canonical_friction_bps - expected_friction) < 1e-6
    assert abs(metrics.canonical_friction_bps - 5.42) < 1e-6

    # Net expectancy = gross - friction
    expected_net = metrics.gross_cycle_return_bps - metrics.canonical_friction_bps
    assert abs(metrics.net_cycle_expectancy_bps - expected_net) < 1e-6
    assert metrics.net_cycle_expectancy_bps == pytest.approx(10.68, abs=1e-5)

    # Cost coverage and confidence interval
    assert metrics.cost_break_even_multiplier >= 2.90
    assert metrics.ci_95_lower_bps > 5.0
    assert metrics.ci_95_upper_bps > 15.0
    assert metrics.spearman_rank_ic > 0.040
    assert metrics.rank_ic_p_value < 0.01
    assert metrics.profit_factor >= 1.35
    assert metrics.max_drawdown_pct <= 3.0


def test_alpha_b_four_book_reconciliation():
    """Validates 4-book ledger comparison (Books A, B, C, D) and autonomy gap."""
    evaluator = AlphaBExtendedLiveEvaluator()
    books: AlphaBFourBookComparisonResult = evaluator.evaluate_four_books(sessions=75, completed_cohorts=72)

    assert books.sessions_evaluated == 75
    assert books.completed_cohorts == 72
    
    # Book A: Live Governed
    assert books.book_a_net_expectancy_bps == pytest.approx(10.68, abs=1e-5)

    assert books.book_a_pnl_usd > 220.0
    assert books.book_a_fill_rate_pct >= 95.0

    # Book B: Shadow
    assert books.book_b_net_expectancy_bps == pytest.approx(11.10, abs=1e-5)
    assert books.live_shadow_gap_bps == pytest.approx(-0.42, abs=0.01)

    # Book C: Broker Paper
    assert books.book_c_net_expectancy_bps == pytest.approx(11.65, abs=1e-5)
    assert books.live_paper_gap_bps == pytest.approx(-0.97, abs=0.01)

    # Book D: Autonomous Counterfactual
    assert books.book_d_net_expectancy_bps == pytest.approx(10.70, abs=1e-5)
    assert books.autonomy_gap_bps == pytest.approx(+0.02, abs=0.01)
    assert books.autonomy_gap_ci_lower_bps < 0.0 < books.autonomy_gap_ci_upper_bps


def test_alpha_b_cost_stress_testing():
    """Validates that Alpha B edge survives 1.25x, 1.5x, 2.0x friction multipliers."""
    evaluator = AlphaBExtendedLiveEvaluator()
    stress_results = evaluator.evaluate_cost_stress(base_friction_bps=5.42, gross_alpha_bps=16.10)

    assert stress_results["1.00x"]["is_positive"] is True
    assert stress_results["1.25x"]["is_positive"] is True
    assert stress_results["1.50x"]["is_positive"] is True
    assert stress_results["2.00x"]["is_positive"] is True
    # At 2.0x (10.84 bps friction), net expectancy is still +5.26 bps
    assert stress_results["2.00x"]["net_expectancy_bps"] > 5.0
    # Break-even is at 2.97x
    assert stress_results["3.00x"]["is_positive"] is False


def test_alpha_b_symbol_generalization_and_event_attribution():
    """Validates that edge is distributed across multiple symbols and non-earnings cycles."""
    evaluator = AlphaBExtendedLiveEvaluator()
    
    # Symbol generalization
    sym_perf = evaluator.evaluate_symbol_generalization()
    assert len(sym_perf) == 5
    for sym, perf in sym_perf.items():
        assert perf["cohorts"] >= 10
        assert perf["net_bps"] > 9.5
        assert perf["win_rate"] >= 55.0

    # Event attribution
    event_attr = evaluator.evaluate_event_attribution()
    assert event_attr["NON_EARNINGS_CYCLES"]["cohort_count"] >= 60
    assert event_attr["NON_EARNINGS_CYCLES"]["net_expectancy_bps"] > 10.0
    assert event_attr["NORMAL_GAP_CYCLES"]["cohort_count"] >= 60
    assert event_attr["NORMAL_GAP_CYCLES"]["net_expectancy_bps"] > 10.0


def test_alpha_b_live_governed_fatal_blocks_generic_live_and_shorting():
    """Verifies that Alpha B engine strictly rejects generic LIVE modes and shorting."""
    engine = AlphaBLiveGovernedEngine(execution_mode=ExecutionMode.ALPHA_B_LIVE_GOVERNED_MICRO)
    
    # Shorting prohibited
    with pytest.raises(AlphaBExecutionViolation, match="Long-Only"):
        engine.validate_long_only_order(side="SELL")
    
    # Generic LIVE mode prohibited
    with pytest.raises(AlphaBExecutionViolation, match="prohibited from generic/Alpha-A mode"):
        AlphaBLiveGovernedEngine(execution_mode=ExecutionMode.LIVE)
