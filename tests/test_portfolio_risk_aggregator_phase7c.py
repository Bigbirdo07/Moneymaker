"""
Tests for PortfolioRiskAggregator and Veto Counterfactuals (Phase 7C Track C).
Verifies:
1. Deterministic 4-tier risk hierarchy (Account -> Strategy -> Symbol -> Order).
2. Fail-closed prohibition on order execution and live capital allocation.
3. Veto-only behavior and combined cross-strategy concentration capping.
4. Aggregator veto counterfactual evaluation and efficacy summary.
5. ResearchDirector analytical veto output generation.
"""

import pytest
from src.portfolio.multi_strategy_research import (
    PortfolioRiskAggregator,
    StrategyPositionRecord,
    RiskCheckResult,
    Phase7CMultiStrategyEngine,
    PortfolioVetoEffectivenessSummary,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)


def test_portfolio_risk_aggregator_fatal_prohibitions():
    """Confirms PortfolioRiskAggregator cannot submit orders or allocate live capital."""
    agg = PortfolioRiskAggregator()
    
    with pytest.raises(PermissionError, match="cannot submit orders"):
        agg.submit_order()

    with pytest.raises(PermissionError, match="cannot allocate or rebalance live capital"):
        agg.allocate_live_capital()


def test_portfolio_risk_aggregator_cross_strategy_symbol_veto():
    """Verifies that an order is vetoed when combined cross-strategy symbol exposure exceeds $3,500."""
    agg = PortfolioRiskAggregator()
    
    # Alpha A has $3,300 in AAPL
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
            cohort_id="COHORT_A_01",
            signal_id="SIG_01",
            decision_id="DEC_01",
            symbol="AAPL",
            side="BUY",
            shares=22,
            entry_price=150.0,
            notional_usd=3300.0,
        ),
    ]

    # Alpha B tries to add $300 in AAPL -> Combined = $3,600 > $3,500 limit
    res: RiskCheckResult = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="AAPL",
        side="BUY",
        notional_usd=300.0,
        current_account_daily_loss_usd=0.0,
        current_strategy_daily_loss_usd=0.0,
        existing_positions=existing,
    )
    assert res.is_approved is False
    assert res.rejection_tier == "SYMBOL_RISK"
    assert res.reason_code == "COMBINED_SYMBOL_CAP_EXCEEDED"


def test_portfolio_risk_aggregator_strategy_budget_isolation():
    """Verifies that Alpha B cannot exceed its $1,000 budget even if Alpha A is using $0."""
    agg = PortfolioRiskAggregator()
    
    # Alpha B has $800 deployed; attempts $300 new order -> Total = $1,100 > $1,000 budget
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
            cohort_id="COHORT_B_01",
            signal_id="SIG_02",
            decision_id="DEC_02",
            symbol="MSFT",
            side="BUY",
            shares=2,
            entry_price=400.0,
            notional_usd=800.0,
        ),
    ]

    
    res: RiskCheckResult = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="NVDA",
        side="BUY",
        notional_usd=300.0,
        current_account_daily_loss_usd=0.0,
        current_strategy_daily_loss_usd=0.0,
        existing_positions=existing,
    )
    assert res.is_approved is False
    assert res.rejection_tier == "STRATEGY_RISK"
    assert res.reason_code == "STRATEGY_CAPITAL_EXCEEDED"


def test_portfolio_veto_effectiveness_evaluation():
    """Validates aggregator veto counterfactual logging and cost/benefit summary."""
    engine = Phase7CMultiStrategyEngine()
    summary: PortfolioVetoEffectivenessSummary = engine.evaluate_veto_effectiveness()

    assert summary.total_orders_evaluated == 480
    assert summary.total_vetoes_issued == 8
    assert summary.symbol_tier_vetoes == 5
    assert summary.strategy_tier_vetoes == 2
    assert summary.gross_risk_avoided_usd == 2850.0
    assert summary.max_drawdown_avoided_usd == 85.00
    assert summary.net_veto_efficacy_usd > 70.0


def test_research_director_portfolio_veto_analysis():
    """Validates read-only LLM analytical method for portfolio veto analysis."""
    rd = MoneymakerResearchDirector()
    out = rd.generate_portfolio_veto_analysis(
        total_vetoes=8,
        gross_risk_avoided_usd=2850.0,
        net_veto_efficacy_usd=76.50,
    )
    assert out.output_type == LLMOutputType.PORTFOLIO_VETO_ANALYSIS
    assert "Net efficacy" in out.summary
    assert len(out.provenance_statements) == 1
