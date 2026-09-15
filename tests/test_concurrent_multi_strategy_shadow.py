"""
Unit & Integration Tests for Concurrent Multi-Strategy Shadow Engine (Phase 7B Track C).
Validates concurrent daily MTM records, rolling 20d correlation, downside correlation,
collision records, and Research Director Phase 7B analytical outputs.
"""

import pytest

from src.portfolio.multi_strategy_research import (
    ConcurrentMultiStrategyShadowEngine,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)


def test_concurrent_multi_strategy_shadow_engine_simulation():
    """Verifies that the concurrent shadow engine simulates multi-strategy equity paths and rolling correlations."""
    engine = ConcurrentMultiStrategyShadowEngine()
    records = engine.simulate_concurrent_shadow_history(n_days=40, seed=42)

    assert len(records) == 40
    assert len(engine.daily_records) == 40

    # Test equity progression
    assert records[0].combined_equity_usd > 10000.0
    assert records[-1].combined_equity_usd > 10000.0

    # Test rolling correlation and downside correlation bounds
    for r in records:
        assert abs(r.rolling_20d_pearson) < 0.25
        assert abs(r.rolling_20d_spearman) < 0.25
        assert r.downside_correlation <= 0.0
        assert r.drawdown_overlap_pct < 25.0


def test_research_director_phase7b_analytical_methods_and_bounds():
    """Verifies that Research Director generates Phase 7B structured findings while remaining read-only."""
    rd = MoneymakerResearchDirector()
    assert rd.is_read_only is True

    # 1. Live vs paper divergence
    div_out = rd.generate_live_paper_divergence_finding(
        strategy_id="ALPHA_B",
        live_net_bps=10.80,
        paper_net_bps=11.80,
        gap_bps=-1.00,
    )
    assert div_out.output_type == LLMOutputType.LIVE_PAPER_DIVERGENCE
    assert len(div_out.provenance_statements) == 1

    # 2. Strategy collision warning
    coll_out = rd.generate_strategy_collision_warning(
        symbol="NVDA",
        alpha_a_notional_usd=1000.0,
        alpha_b_notional_usd=333.33,
        combined_cap_usd=3500.0,
    )
    assert coll_out.output_type == LLMOutputType.STRATEGY_COLLISION_WARNING

    # 3. Portfolio concentration warning
    conc_out = rd.generate_portfolio_concentration_warning(
        concentration_metric="HIGH_BETA_HIGH_VOL",
        observed_value=62.5,
        threshold_value=75.0,
    )
    assert conc_out.output_type == LLMOutputType.PORTFOLIO_CONCENTRATION_WARNING

    # 4. Diversification decay warning
    decay_out = rd.generate_diversification_decay_warning(
        rolling_window_days=20,
        observed_correlation=-0.038,
        baseline_correlation=-0.040,
    )
    assert decay_out.output_type == LLMOutputType.DIVERSIFICATION_DECAY_WARNING

    # 5. Strategy health summary
    health_out = rd.generate_strategy_health_summary(
        strategy_id="ALPHA_B",
        capital_authorized_usd=1000.0,
        net_expectancy_bps=10.80,
        cost_break_even_mult=3.00,
        status="LIVE_GOVERNED_MICRO_VALIDATED",
    )
    assert health_out.output_type == LLMOutputType.STRATEGY_HEALTH_SUMMARY
