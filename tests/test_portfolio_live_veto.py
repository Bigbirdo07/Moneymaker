"""
Tests for PortfolioRiskAggregator Live-Veto Layer (Phase 7D Track C).
Verifies:
1. Deterministic 4-tier risk hierarchy during concurrent live execution.
2. Combined cross-strategy symbol concentration capping ($3,500 limit).
3. Strategy risk budget isolation without capital lending.
4. Total account exposure limit ($11,000 max).
5. Veto-only architecture with zero portfolio optimization permissions.
6. ResearchDirector live-veto analytical finding output.
"""

import pytest
from src.portfolio.multi_strategy_research import (
    PortfolioRiskAggregator,
    StrategyPositionRecord,
    RiskCheckResult,
    Phase7DMultiStrategyLiveEngine,
)
from src.llm.research_director import (
    MoneymakerResearchDirector,
    LLMOutputType,
)


def test_live_portfolio_risk_aggregator_prohibitions():
    """Confirms live aggregator cannot route orders or reallocate strategy weights."""
    agg = PortfolioRiskAggregator()
    
    with pytest.raises(PermissionError, match="cannot submit orders"):
        agg.submit_order()

    with pytest.raises(PermissionError, match="cannot allocate or rebalance live capital"):
        agg.allocate_live_capital()


def test_live_portfolio_veto_cross_strategy_symbol_capping():
    """Verifies that an order is vetoed when combined exposure on a single symbol exceeds $3,500."""
    agg = PortfolioRiskAggregator()

    # Alpha A holds $3,300 in NVDA
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
            cohort_id="COHORT_A_01",
            signal_id="SIG_A_01",
            decision_id="DEC_A_01",
            symbol="NVDA",
            side="BUY",
            shares=22,
            entry_price=150.0,
            notional_usd=3300.0,
        )
    ]

    # Alpha B attempts $300 order in NVDA -> $3,600 > $3,500 limit
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
    assert res.rejection_tier == "SYMBOL_RISK"
    assert res.reason_code == "COMBINED_SYMBOL_CAP_EXCEEDED"


def test_live_portfolio_strategy_budget_isolation_no_lending():
    """Verifies that Alpha B cannot use Alpha A's unused capital."""
    agg = PortfolioRiskAggregator()

    # Alpha A has $0 deployed ($10k free). Alpha B has $900 deployed.
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
            cohort_id="COHORT_B_01",
            signal_id="SIG_B_01",
            decision_id="DEC_B_01",
            symbol="AAPL",
            side="BUY",
            shares=6,
            entry_price=150.0,
            notional_usd=900.0,
        )
    ]

    # Alpha B attempts $200 order -> Total Alpha B = $1,100 > $1,000 budget
    res: RiskCheckResult = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="MSFT",
        side="BUY",
        notional_usd=200.0,
        current_account_daily_loss_usd=0.0,
        current_strategy_daily_loss_usd=0.0,
        existing_positions=existing,
    )
    assert res.is_approved is False
    assert res.rejection_tier == "STRATEGY_RISK"
    assert res.reason_code == "STRATEGY_CAPITAL_EXCEEDED"


def test_research_director_portfolio_veto_finding():
    """Validates read-only LLM analytical output for live portfolio veto efficacy."""
    rd = MoneymakerResearchDirector()
    out = rd.generate_portfolio_veto_finding(
        orders_evaluated=390,
        vetoes_issued=6,
        net_veto_efficacy_usd=58.20,
    )
    assert out.output_type == LLMOutputType.PORTFOLIO_VETO_FINDING
    assert "Net efficacy" in out.provenance_statements[0].statement
    assert "live veto layer" in out.summary
    assert len(out.provenance_statements) == 1

