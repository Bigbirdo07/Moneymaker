"""
Tests for Extended Concurrent Multi-Strategy Shadow Portfolio (Phase 7C Track C).
Verifies:
1. Multi-Portfolio Books (P1 Actual Governed, P2 Autonomous Shadow, P3 Conservative Shadow).
2. Multi-horizon rolling correlation statistics (20d, 40d, 60d, min, max, P10, P90).
3. Drawdown overlap and simultaneous tail loss metrics.
4. Cross-strategy collision statistics and resolution rules.
5. Scenario stress testing under actual concurrent positions.
6. ResearchDirector rolling correlation and strategy dependence warnings.
"""

import pytest
from src.portfolio.multi_strategy_research import (
    Phase7CMultiStrategyEngine,
    PortfolioBookPerformance,
    PortfolioRollingCorrelationStats,
    PortfolioDrawdownOverlapStats,
    MultiStrategyStressScenario,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)


def test_multi_portfolio_books_performance_and_drawdown():
    """Validates multi-portfolio book metrics across 75 sessions on $11k aggregate capital."""
    engine = Phase7CMultiStrategyEngine()
    books = engine.evaluate_multi_portfolio_books(n_days=75)

    assert "P1" in books and "P2" in books and "P3" in books

    p1: PortfolioBookPerformance = books["P1"]
    assert p1.initial_equity_usd == 11000.0
    assert p1.total_realized_pnl_usd > 1300.0
    assert p1.cumulative_return_pct > 12.0
    assert p1.annualized_volatility_pct < 5.5
    assert p1.sharpe_ratio > 3.4
    assert p1.max_drawdown_pct <= 1.60

    p2: PortfolioBookPerformance = books["P2"]
    assert abs(p2.total_realized_pnl_usd - p1.total_realized_pnl_usd) < 5.0
    assert p2.max_drawdown_pct <= 1.60


def test_multi_horizon_rolling_correlation_and_stability():
    """Validates multi-horizon rolling correlations and percentiles."""
    engine = Phase7CMultiStrategyEngine()
    stats: PortfolioRollingCorrelationStats = engine.compute_rolling_correlation_stats()

    assert stats.mean_rolling_20d_pearson < 0.0
    assert stats.max_rolling_20d_pearson < 0.30  # Strictly below WATCH threshold
    assert stats.p10_rolling_20d_pearson < stats.p90_rolling_20d_pearson
    assert stats.downside_correlation < 0.0
    assert stats.tail_correlation_5th_pct < 0.0
    assert stats.is_diversification_stable is True


def test_drawdown_overlap_and_collision_statistics():
    """Validates joint drawdown days and cross-strategy signal collisions."""
    engine = Phase7CMultiStrategyEngine()
    
    # Drawdown overlap
    dd_stats: PortfolioDrawdownOverlapStats = engine.compute_drawdown_overlap_stats()
    assert dd_stats.total_trading_days == 75
    assert dd_stats.both_strategies_loss_pct < 20.0
    assert dd_stats.both_exceed_1sigma_loss_days <= 3
    assert len(dd_stats.joint_worst_5_days_pnl_usd) == 5

    # Collision statistics
    col_stats = engine.evaluate_collision_statistics()
    assert col_stats["total_evaluated_days"] == 75
    assert col_stats["concurrent_long_signals_count"] > 0
    assert col_stats["concurrent_opposing_signals_count"] == 0
    assert col_stats["concentration_limit_breaches"] == 0


def test_portfolio_stress_scenario_matrix():
    """Validates that all 8 stress scenarios remain strictly tolerable (portfolio loss <= 5.0%)."""
    engine = Phase7CMultiStrategyEngine()
    scenarios = engine.evaluate_portfolio_stress_scenarios()

    assert len(scenarios) == 8
    for sc in scenarios:
        assert sc.is_tolerable is True
        assert sc.portfolio_loss_pct <= 5.0


def test_research_director_rolling_correlation_and_dependence_warnings():
    """Validates LLM read-only outputs for rolling correlation and strategy dependence."""
    rd = MoneymakerResearchDirector()

    rc_out = rd.generate_rolling_correlation_warning(
        mean_correlation=-0.036,
        max_correlation=0.084,
        status="DIVERSIFICATION_STABLE",
    )
    assert rc_out.output_type == LLMOutputType.ROLLING_CORRELATION_WARNING
    assert "DIVERSIFICATION_STABLE" in rc_out.provenance_statements[0].statement

    dep_out = rd.generate_strategy_dependence_warning(
        joint_drawdown_days_pct=14.67,
        tail_correlation=-0.098,
    )
    assert dep_out.output_type == LLMOutputType.STRATEGY_DEPENDENCE_WARNING
    assert "downside diversification" in dep_out.summary
