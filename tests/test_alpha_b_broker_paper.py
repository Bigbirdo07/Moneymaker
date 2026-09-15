"""
Unit & Integration Tests for Alpha B Broker Paper Promotion (Phase 7A Track B).
Validates broker paper permissions, live execution prohibition, Book B1 long-only isolation,
3-day cohort lifecycle accounting, leakage prevention, dual-book paper vs shadow comparison,
overnight gap decomposition, and cost sensitivity stress.
"""

import pytest
import pandas as pd
import numpy as np

from src.broker.adapter import ExecutionMode
from src.strategies.alpha_b_reversal import (
    AlphaBExecutionViolation,
    AlphaBMultiDayReversalStrategy,
    AlphaBShadowBookType,
    AlphaBBrokerPaperEngine,
    AlphaBBrokerPaperCohort,
    AlphaBBrokerPaperPositionState,
)


def test_alpha_b_broker_paper_permissions_and_live_fatal_blocks():
    """Verifies that Alpha B permits broker paper and shadow, but fatal blocks all live execution modes."""
    # Permitted modes
    paper_engine = AlphaBBrokerPaperEngine(execution_mode=ExecutionMode.ALPHA_B_BROKER_PAPER)
    assert paper_engine.execution_mode == ExecutionMode.ALPHA_B_BROKER_PAPER

    shadow_engine = AlphaBBrokerPaperEngine(execution_mode=ExecutionMode.SHADOW)
    assert shadow_engine.execution_mode == ExecutionMode.SHADOW

    # Fatal live blocks
    for live_mode in (
        ExecutionMode.LIVE,
        ExecutionMode.LIVE_GOVERNED_MICRO,
        ExecutionMode.LIVE_AUTONOMOUS_MICRO,
    ):
        with pytest.raises(AlphaBExecutionViolation):
            AlphaBBrokerPaperEngine(execution_mode=live_mode)


def test_book_b1_long_only_isolation_and_b2_non_deployability():
    """Verifies Book B1 is deployable prototype while Book B2 remains non-deployable research only."""
    strat = AlphaBMultiDayReversalStrategy(permitted_modes={ExecutionMode.SHADOW, ExecutionMode.ALPHA_B_BROKER_PAPER})
    books = strat.simulate_forward_shadow_books(forward_days=60, modeled_friction_bps=5.0)

    b1 = books[AlphaBShadowBookType.BOOK_B1_LONG_ONLY]
    b2 = books[AlphaBShadowBookType.BOOK_B2_LONG_SHORT]

    assert b1.is_deployable_under_current_rules is True
    assert b2.is_deployable_under_current_rules is False
    assert b1.net_alpha_per_cycle_bps > 0
    assert b2.net_alpha_per_cycle_bps > 0


def test_three_day_overlapping_cohort_accounting_and_lifecycle():
    """Verifies 3-day cohort registration, aging, auto-expiration, and capital allocation without double counting."""
    engine = AlphaBBrokerPaperEngine(nominal_capital=10000.0)

    # Day 1: Cohort 1
    state1 = engine.register_new_cohort(
        cohort_id="COHORT_20260901",
        entry_date="2026-09-01",
        planned_exit_date="2026-09-04",
        symbols=["NVDA", "AMD"],
        weights={"NVDA": 0.5, "AMD": 0.5},
        entry_prices={"NVDA": 120.0, "AMD": 150.0},
    )
    assert state1.overlap_cohort_count == 1
    assert len(state1.active_cohorts) == 1
    assert state1.aggregate_symbol_exposure_usd["NVDA"] == pytest.approx(1666.67, rel=1e-2)
    assert state1.gross_exposure_pct == pytest.approx(0.333, rel=1e-2)

    # Day 2: Cohort 2
    state2 = engine.register_new_cohort(
        cohort_id="COHORT_20260902",
        entry_date="2026-09-02",
        planned_exit_date="2026-09-05",
        symbols=["NVDA", "TSLA"],
        weights={"NVDA": 0.5, "TSLA": 0.5},
        entry_prices={"NVDA": 122.0, "TSLA": 220.0},
    )
    assert state2.overlap_cohort_count == 2
    assert state2.aggregate_symbol_exposure_usd["NVDA"] == pytest.approx(3333.33, rel=1e-2)
    assert state2.gross_exposure_pct == pytest.approx(0.666, rel=1e-2)

    # Day 3: Cohort 3
    state3 = engine.register_new_cohort(
        cohort_id="COHORT_20260903",
        entry_date="2026-09-03",
        planned_exit_date="2026-09-06",
        symbols=["AAPL", "MSFT"],
        weights={"AAPL": 0.5, "MSFT": 0.5},
        entry_prices={"AAPL": 225.0, "MSFT": 420.0},
    )
    assert state3.overlap_cohort_count == 3
    assert state3.gross_exposure_pct == pytest.approx(1.00, rel=1e-2)

    # Day 4: Cohort 4 (Cohort 1 has reached 3 days and auto-expires)
    state4 = engine.register_new_cohort(
        cohort_id="COHORT_20260904",
        entry_date="2026-09-04",
        planned_exit_date="2026-09-09",
        symbols=["META", "GOOGL"],
        weights={"META": 0.5, "GOOGL": 0.5},
        entry_prices={"META": 510.0, "GOOGL": 165.0},
    )
    assert state4.overlap_cohort_count == 3
    assert len(engine.closed_cohorts) == 1
    assert engine.closed_cohorts[0].cohort_id == "COHORT_20260901"


def test_signal_timing_and_same_close_leakage_prevention():
    """Verifies that signals computed at or after 16:05 ET cannot fill on same-day close."""
    engine = AlphaBBrokerPaperEngine()

    # Valid next-day execution
    assert engine.validate_order_timing("2026-09-01 16:05:00", "2026-09-02 09:30:00") is True

    # Invalid same-day close execution
    with pytest.raises(ValueError, match="LEAKAGE VIOLATION"):
        engine.validate_order_timing("2026-09-01 16:05:00", "2026-09-01 16:00:00")


def test_dual_book_paper_vs_shadow_comparison_and_cost_stress():
    """Verifies dual book paper vs shadow comparison, paper fill optimism, gap decomposition, and cost stress."""
    engine = AlphaBBrokerPaperEngine()

    # Dual book comparison
    dual = engine.evaluate_dual_book_comparison(sessions=50)
    assert dual.sessions_evaluated == 50
    assert dual.paper_net_expectancy_bps == pytest.approx(11.80, rel=1e-2)
    assert dual.shadow_net_expectancy_bps == pytest.approx(11.20, rel=1e-2)
    assert dual.paper_fill_advantage_bps == pytest.approx(0.60, rel=1e-2)
    assert dual.correlation_paper_shadow > 0.95

    # Overnight gap decomposition
    gap = engine.decompose_overnight_gap()
    assert gap.total_cycle_return_bps == 16.2
    assert gap.overnight_gap_contribution_bps == 7.8
    assert gap.intraday_return_contribution_bps == 8.4
    assert gap.overnight_gap_contribution_bps + gap.intraday_return_contribution_bps == pytest.approx(16.2, rel=1e-4)

    # Event attribution
    events = engine.attribute_corporate_events()
    assert events.total_events_tracked == 12
    assert events.earnings_event_return_bps > 0
    assert events.event_free_return_bps > 0

    # Cost stress & break-even multiplier
    stress = engine.run_cost_stress_tests(base_friction_bps=5.0, gross_alpha_bps=16.2)
    assert len(stress) == 5
    assert stress[0].is_profitable is True  # 1.0x (11.2 bps)
    assert stress[1].is_profitable is True  # 1.25x (9.95 bps)
    assert stress[2].is_profitable is True  # 1.50x (8.70 bps)
    assert stress[3].is_profitable is True  # 2.00x (6.20 bps)
    assert stress[4].is_profitable is True  # 3.00x (1.20 bps)

    be_mult = engine.compute_cost_break_even_multiplier(base_friction_bps=5.0, gross_alpha_bps=16.2)
    assert be_mult == pytest.approx(3.24, rel=1e-2)
