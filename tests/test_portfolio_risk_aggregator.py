"""
Unit & Integration Tests for Portfolio Risk Aggregator (Phase 7B Track C / Governance).
Validates 4-tier hierarchical deterministic validation:
Account -> Strategy -> Symbol -> Order,
cross-strategy capital partitioning, combined symbol exposure caps, and fatal non-executable assertions.
"""

import pytest

from src.portfolio.multi_strategy_research import (
    PortfolioRiskAggregator,
    StrategyPositionRecord,
    RiskCheckResult,
)


def test_portfolio_risk_aggregator_non_executable_fatal_assertions():
    """Verifies that PortfolioRiskAggregator strictly prohibits order routing or capital mutation."""
    agg = PortfolioRiskAggregator()
    with pytest.raises(PermissionError, match="FATAL SAFETY VIOLATION"):
        agg.submit_order(symbol="NVDA", qty=10)

    with pytest.raises(PermissionError, match="FATAL SAFETY VIOLATION"):
        agg.allocate_live_capital(amount_usd=1000.0)


def test_four_tier_hierarchical_risk_validation_clean_pass():
    """Verifies that clean orders passing all 4 risk tiers receive approved status."""
    agg = PortfolioRiskAggregator()
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
            cohort_id="A_001",
            signal_id="SIG_001",
            decision_id="DEC_001",
            symbol="NVDA",
            side="BUY",
            shares=8,
            entry_price=120.0,
            notional_usd=960.0,
        )
    ]

    res = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="AMD",
        side="BUY",
        notional_usd=333.33,
        current_account_daily_loss_usd=15.0,
        current_strategy_daily_loss_usd=5.0,
        existing_positions=existing,
    )
    assert res.is_approved is True
    assert res.rejection_tier == "NONE"
    assert res.reason_code == "CLEAN"


def test_hierarchical_risk_tier1_account_risk_violations():
    """Verifies Tier 1 Account Risk rejections when account limits or loss budgets are breached."""
    agg = PortfolioRiskAggregator()
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
            cohort_id="A_001",
            signal_id="SIG_001",
            decision_id="DEC_001",
            symbol="NVDA",
            side="BUY",
            shares=80,
            entry_price=120.0,
            notional_usd=9600.0,
        ),
        StrategyPositionRecord(
            strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
            cohort_id="B_001",
            signal_id="SIG_002",
            decision_id="DEC_002",
            symbol="AMD",
            side="BUY",
            shares=6,
            entry_price=150.0,
            notional_usd=900.0,
        ),
    ]

    # Total exposure: $9600 + $900 = $10,500. Order $800 exceeds $11,000 account limit
    res_cap = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
        symbol="TSLA",
        side="BUY",
        notional_usd=800.0,
        current_account_daily_loss_usd=50.0,
        current_strategy_daily_loss_usd=40.0,
        existing_positions=existing,
    )
    assert res_cap.is_approved is False
    assert res_cap.rejection_tier == "ACCOUNT_RISK"
    assert res_cap.reason_code == "ACCOUNT_CAPITAL_EXCEEDED"

    # Account daily loss breach ($230 limit)
    res_loss = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="TSLA",
        side="BUY",
        notional_usd=300.0,
        current_account_daily_loss_usd=235.0,
        current_strategy_daily_loss_usd=10.0,
        existing_positions=[],
    )
    assert res_loss.is_approved is False
    assert res_loss.rejection_tier == "ACCOUNT_RISK"
    assert res_loss.reason_code == "ACCOUNT_DAILY_LOSS_LIMIT"


def test_hierarchical_risk_tier2_strategy_budget_violations():
    """Verifies Tier 2 Strategy Risk rejections when strategy capital partition is exceeded."""
    agg = PortfolioRiskAggregator()
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
            cohort_id="B_001",
            signal_id="SIG_001",
            decision_id="DEC_001",
            symbol="NVDA",
            side="BUY",
            shares=5,
            entry_price=150.0,
            notional_usd=750.0,
        )
    ]

    # Alpha B budget is $1,000. Existing $750 + Order $300 = $1,050 -> REJECT
    res = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="AMD",
        side="BUY",
        notional_usd=300.0,
        current_account_daily_loss_usd=10.0,
        current_strategy_daily_loss_usd=5.0,
        existing_positions=existing,
    )
    assert res.is_approved is False
    assert res.rejection_tier == "STRATEGY_RISK"
    assert res.reason_code == "STRATEGY_CAPITAL_EXCEEDED"


def test_hierarchical_risk_tier3_combined_symbol_cap_violations():
    """Verifies Tier 3 Symbol Risk rejections when cross-strategy combined symbol exposure exceeds $3,500."""
    agg = PortfolioRiskAggregator()
    existing = [
        StrategyPositionRecord(
            strategy_id="ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
            cohort_id="A_001",
            signal_id="SIG_001",
            decision_id="DEC_001",
            symbol="NVDA",
            side="BUY",
            shares=28,
            entry_price=120.0,
            notional_usd=3360.0,
        )
    ]

    # NVDA already has $3,360 notional. Alpha B attempting $300 pushes it to $3,660 (> $3,500 cap)
    res = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="NVDA",
        side="BUY",
        notional_usd=300.0,
        current_account_daily_loss_usd=10.0,
        current_strategy_daily_loss_usd=0.0,
        existing_positions=existing,
    )
    assert res.is_approved is False
    assert res.rejection_tier == "SYMBOL_RISK"
    assert res.reason_code == "COMBINED_SYMBOL_CAP_EXCEEDED"


def test_hierarchical_risk_tier4_order_risk_and_short_veto():
    """Verifies Tier 4 Order Risk rejections for size overage and Alpha B short veto."""
    agg = PortfolioRiskAggregator()

    # Alpha B single order cap is $333.33
    res_size = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="NVDA",
        side="BUY",
        notional_usd=500.0,
        current_account_daily_loss_usd=0.0,
        current_strategy_daily_loss_usd=0.0,
        existing_positions=[],
    )
    assert res_size.is_approved is False
    assert res_size.rejection_tier == "ORDER_RISK"
    assert res_size.reason_code == "ORDER_SIZE_EXCEEDED"

    # Alpha B short veto
    res_short = agg.validate_hierarchical_risk(
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL",
        symbol="NVDA",
        side="SELL",
        notional_usd=200.0,
        current_account_daily_loss_usd=0.0,
        current_strategy_daily_loss_usd=0.0,
        existing_positions=[],
    )
    assert res_short.is_approved is False
    assert res_short.rejection_tier == "ORDER_RISK"
    assert res_short.reason_code == "SHORT_PROHIBITED"
