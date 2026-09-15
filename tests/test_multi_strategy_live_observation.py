"""
Tests for Multi-Strategy Concurrent Live Observation & Risk Attribution (Phase 7D Track C).
Verifies:
1. Combined marked-to-market live equity accounting ($11,000 capital).
2. Live portfolio Sharpe, annualized volatility, and drawdown containment.
3. Live risk contribution and return attribution across strategies.
4. Multi-horizon rolling correlation stability during concurrent live execution.
5. ResearchDirector analytical outputs for live health and risk contribution.
"""

import pytest
from src.portfolio.multi_strategy_research import (
    Phase7DMultiStrategyLiveEngine,
    MultiStrategyLiveObservationMetrics,
    MultiStrategyLiveRiskAttribution,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)


def test_multi_strategy_live_observation_accounting_and_metrics():
    """Validates 60-session concurrent live observation metrics on $11,000 account capital."""
    engine = Phase7DMultiStrategyLiveEngine()
    metrics: MultiStrategyLiveObservationMetrics = engine.evaluate_live_observation(n_sessions=60)

    assert metrics.total_live_sessions == 60
    assert metrics.initial_account_equity_usd == 11000.0
    assert metrics.final_account_equity_usd > 11800.0
    assert metrics.total_realized_pnl_usd == pytest.approx(850.60, abs=1e-2)
    assert metrics.cumulative_return_pct == pytest.approx(7.73, abs=1e-2)
    assert metrics.annualized_volatility_pct < 5.30
    assert metrics.sharpe_ratio > 3.45
    assert metrics.max_drawdown_pct <= 1.55
    assert metrics.is_live_diversification_confirmed is True


def test_multi_strategy_live_risk_and_return_attribution():
    """Validates return and risk attribution between Alpha A ($10k) and Alpha B ($1k)."""
    engine = Phase7DMultiStrategyLiveEngine()
    metrics = engine.evaluate_live_observation(n_sessions=60)
    attr: MultiStrategyLiveRiskAttribution = metrics.risk_attribution

    # Capital shares: 90.91% Alpha A, 9.09% Alpha B
    assert attr.alpha_a_capital_share_pct == pytest.approx(90.91, abs=0.01)
    assert attr.alpha_b_capital_share_pct == pytest.approx(9.09, abs=0.01)

    # Return shares
    assert attr.alpha_a_pnl_share_pct + attr.alpha_b_pnl_share_pct == pytest.approx(100.0, abs=1e-4)
    assert attr.alpha_a_pnl_usd == 666.00
    assert attr.alpha_b_pnl_usd == 184.60

    # Risk shares: Alpha A represents ~85.2% of volatility, Alpha B ~14.8%
    assert attr.alpha_a_volatility_contribution_pct > 80.0
    assert attr.alpha_b_volatility_contribution_pct < 20.0
    assert attr.alpha_a_expected_shortfall_contribution_pct > 80.0


def test_multi_strategy_live_rolling_correlation_stability():
    """Validates live rolling correlation metrics and tail correlation."""
    engine = Phase7DMultiStrategyLiveEngine()
    metrics = engine.evaluate_live_observation(n_sessions=60)

    assert metrics.rolling_20d_pearson_mean < 0.0
    assert metrics.rolling_20d_pearson_peak < 0.30  # Strictly below 0.30 WATCH threshold
    assert metrics.downside_correlation < 0.0
    assert metrics.tail_correlation_5th_pct < 0.0


def test_research_director_live_health_and_risk_warning():
    """Validates read-only LLM analytical outputs for multi-strategy live health."""
    rd = MoneymakerResearchDirector()

    health_out = rd.generate_multi_strategy_live_health(
        total_account_equity_usd=11850.60,
        realized_pnl_usd=850.60,
        combined_volatility_pct=5.15,
        sharpe_ratio=3.54,
    )
    assert health_out.output_type == LLMOutputType.MULTI_STRATEGY_LIVE_HEALTH
    assert "Sharpe" in health_out.summary

    risk_out = rd.generate_cross_strategy_risk_warning(
        strategy_a_risk_share_pct=85.2,
        strategy_b_risk_share_pct=14.8,
        dominant_strategy_id="ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
    )
    assert risk_out.output_type == LLMOutputType.CROSS_STRATEGY_RISK_WARNING
    assert "85.2%" in risk_out.provenance_statements[0].statement
