"""
Unit tests for drawdown state machine and throttling engine.
"""

import pytest
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.drawdown_state import DrawdownThrottleEngine, AccountRiskState


def test_nominal_state():
    engine = DrawdownThrottleEngine()
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T10:00:00Z",
        starting_day_equity=1000.0,
        current_equity=1000.0,
        cash=1000.0,
        peak_equity=1000.0,
        realized_pnl_today=0.0,
    )
    dec = engine.evaluate(state)
    assert dec.risk_state == AccountRiskState.NORMAL
    assert dec.risk_budget_multiplier == 1.0
    assert dec.is_trading_allowed


def test_daily_drawdown_caution_reduces_risk():
    engine = DrawdownThrottleEngine(daily_caution_limit_pct=0.010, daily_loss_limit_pct=0.015)
    # Down 1.1% on the day ($11 loss)
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T14:00:00Z",
        starting_day_equity=1000.0,
        current_equity=989.0,
        cash=989.0,
        peak_equity=1000.0,
        realized_pnl_today=-11.0,
    )
    dec = engine.evaluate(state)
    assert dec.risk_state == AccountRiskState.REDUCED_RISK
    assert dec.risk_budget_multiplier == 0.50
    assert dec.is_trading_allowed


def test_daily_loss_limit_triggers_cash_preservation():
    engine = DrawdownThrottleEngine(daily_loss_limit_pct=0.015)
    # Down 1.6% on the day ($16 loss)
    state = PortfolioRiskState.create(
        timestamp="2025-01-15T14:30:00Z",
        starting_day_equity=1000.0,
        current_equity=984.0,
        cash=984.0,
        peak_equity=1000.0,
        realized_pnl_today=-16.0,
    )
    dec = engine.evaluate(state)
    assert dec.risk_state == AccountRiskState.CASH_PRESERVATION
    assert dec.risk_budget_multiplier == 0.0
    assert not dec.is_trading_allowed
