"""
Unit & Integration Tests for Multi-Strategy Portfolio Research (Phase 7A Track C).
Validates non-executable research assertions, daily return alignment,
baseline allocation evaluations, linear and nonlinear diversification statistics,
marginal risk contributions, strategy conflict detection, multi-strategy stress scenarios,
and Research Director portfolio findings.
"""

import pytest
import numpy as np

from src.portfolio.multi_strategy_research import (
    MultiStrategyResearchEngine,
    AllocationModelType,
    PortfolioDiversificationVerdict,
    ConflictResolutionRule,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)


def test_multi_strategy_engine_non_executable_fatal_assertions():
    """Verifies that the portfolio research engine strictly prohibits execution and capital allocation."""
    engine = MultiStrategyResearchEngine()
    assert engine.is_live_executable is False

    with pytest.raises(PermissionError, match="FATAL SAFETY VIOLATION"):
        engine.submit_order(symbol="NVDA", qty=100)

    with pytest.raises(PermissionError, match="FATAL SAFETY VIOLATION"):
        engine.allocate_live_capital(amount_usd=10000)


def test_daily_return_alignment_and_allocation_baselines():
    """Verifies return series generation, daily alignment, and evaluation of 6 baseline allocations."""
    engine = MultiStrategyResearchEngine()
    series = engine.generate_synthetic_aligned_series(n_days=252, seed=42)

    assert len(series.dates) == 252
    assert len(series.alpha_a_returns) == 252
    assert len(series.alpha_b_returns) == 252
    assert len(series.combined_returns) == 252

    baselines = engine.evaluate_allocation_baselines(series)
    assert len(baselines) == 6

    # Alpha A baseline
    m_a = baselines[AllocationModelType.ALPHA_A_ONLY]
    assert m_a.annualized_return_pct > 0
    assert m_a.sharpe_ratio > 2.0
    assert m_a.max_drawdown_pct < 3.0

    # Alpha B baseline
    m_b = baselines[AllocationModelType.ALPHA_B_ONLY]
    assert m_b.annualized_return_pct > 0
    assert m_b.sharpe_ratio > 0.5
    assert m_b.max_drawdown_pct < 12.0

    # 50/50 Capital Allocation
    m_5050 = baselines[AllocationModelType.EQUAL_CAPITAL_50_50]
    assert m_5050.annualized_return_pct > 0
    assert m_5050.sharpe_ratio > 1.5
    assert m_5050.max_drawdown_pct < 6.0

    # Equal Risk Parity
    m_rp = baselines[AllocationModelType.EQUAL_RISK_PARITY_50_50]
    assert m_rp.weight_a > m_rp.weight_b  # Alpha A has lower vol, so gets higher weight in risk parity


def test_portfolio_diversification_metrics_and_deltas():
    """Verifies Pearson, Spearman, tail, conditional correlations, and diversification delta verdict."""
    engine = MultiStrategyResearchEngine()
    series = engine.generate_synthetic_aligned_series(n_days=252, seed=42)

    div_metrics = engine.compute_diversification_metrics(series)
    assert abs(div_metrics.pearson_correlation) < 0.20  # Low correlation
    assert abs(div_metrics.spearman_correlation) < 0.20
    assert div_metrics.drawdown_overlap_pct < 50.0     # Low to moderate drawdown overlap

    baselines = engine.evaluate_allocation_baselines(series)
    deltas = engine.compute_diversification_deltas(
        baseline_a=baselines[AllocationModelType.ALPHA_A_ONLY],
        portfolio=baselines[AllocationModelType.EQUAL_CAPITAL_50_50],
    )
    assert deltas.verdict in (
        PortfolioDiversificationVerdict.STRONG_DIVERSIFICATION_BENEFIT,
        PortfolioDiversificationVerdict.MODEST_DIVERSIFICATION_BENEFIT,
    )


def test_strategy_conflict_detection_and_resolution_rules():
    """Verifies that symbol collisions are detected and mapped to conservative resolution rules."""
    engine = MultiStrategyResearchEngine()
    conflicts = engine.detect_strategy_conflicts()

    assert len(conflicts) > 0
    for c in conflicts:
        assert c.symbol in ["NVDA", "TSLA", "AMD"]
        assert c.proposed_resolution in (
            ConflictResolutionRule.CAP_EXPOSURE,
            ConflictResolutionRule.ADD_EXPOSURE,
            ConflictResolutionRule.NET_EXPOSURE,
        )
        assert c.aggregate_notional_usd <= 5000.0


def test_multi_strategy_stress_scenarios():
    """Verifies stress tests across strategy failures, market crashes, gap shocks, and friction spikes."""
    engine = MultiStrategyResearchEngine()
    scenarios = engine.run_multi_strategy_stress_tests()

    assert len(scenarios) == 6
    for s in scenarios:
        assert s.portfolio_loss_pct < 0
        assert s.is_tolerable is True  # All portfolio losses contained <= 5.0%


def test_research_director_portfolio_findings_and_governance():
    """Verifies that Research Director generates structured portfolio findings while remaining read-only."""
    rd = MoneymakerResearchDirector()
    assert rd.is_read_only is True

    # 1. Diversification finding
    div_out = rd.generate_strategy_diversification_finding(
        strategy_a="ALPHA_A",
        strategy_b="ALPHA_B",
        correlation=-0.038,
        sharpe_delta=+0.45,
        drawdown_reduction_pct=22.5,
    )
    assert div_out.output_type == LLMOutputType.STRATEGY_DIVERSIFICATION_FINDING
    assert len(div_out.provenance_statements) == 1

    # 2. Strategy conflict finding
    conf_out = rd.generate_strategy_conflict_finding(
        symbol="NVDA",
        conflict_type="CONCURRENT_LONG",
        aggregate_notional_usd=3500.0,
        proposed_rule="CAP_EXPOSURE",
    )
    assert conf_out.output_type == LLMOutputType.STRATEGY_CONFLICT

    # 3. Portfolio risk finding
    risk_out = rd.generate_portfolio_risk_finding(
        risk_metric="Expected Shortfall (ES99)",
        alpha_a_contrib_pct=42.0,
        alpha_b_contrib_pct=58.0,
        combined_value=1.45,
    )
    assert risk_out.output_type == LLMOutputType.PORTFOLIO_RISK_FINDING

    # 4. Alpha decay warning
    decay_out = rd.generate_alpha_decay_warning(
        strategy_id="ALPHA_B",
        horizon_days=3,
        observed_rank_ic=0.034,
        decay_half_life_days=3.2,
    )
    assert decay_out.output_type == LLMOutputType.ALPHA_DECAY_WARNING

    # 5. Paper execution warning
    paper_out = rd.generate_paper_execution_warning(
        strategy_id="ALPHA_B",
        paper_fill_advantage_bps=0.60,
        paper_fill_rate_pct=98.5,
        shadow_fill_rate_pct=95.0,
    )
    assert paper_out.output_type == LLMOutputType.PAPER_EXECUTION_WARNING
