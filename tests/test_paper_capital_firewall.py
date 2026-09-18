"""Tests for StrategyCapitalLedger & Capital Firewall (Phases F7, F8)."""

import pytest
from src.portfolio.strategy_capital_ledger import StrategyCapitalLedger
from src.risk.capital_tiers import CapitalTier


def test_strategy_capital_firewall_1k_tier():
    ledger = StrategyCapitalLedger(authorized_strategy_capital=1000.0)
    assert ledger.authorized_strategy_capital == 1000.0
    assert ledger.current_strategy_equity == 1000.0
    # 75% max position equity ceiling
    assert ledger.max_position_dollars == 750.0
    # 0.75% max risk per trade
    assert ledger.max_risk_per_trade_dollars == 7.50
    assert ledger.max_open_positions == 1


def test_capital_ledger_pnl_updates():
    ledger = StrategyCapitalLedger(authorized_strategy_capital=1000.0)
    ledger.update_pnl(realized_delta=25.50, unrealized=10.0)
    assert ledger.realized_pnl_dollars == 25.50
    assert ledger.current_strategy_equity == 1035.50
    assert ledger.current_cash_dollars == 1025.50
