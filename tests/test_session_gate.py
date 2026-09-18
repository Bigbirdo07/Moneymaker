"""Tests for SessionGate (Phase E3)."""

import pytest
from src.intelligence.morning_market_state import (
    MarketRegime,
    SessionGateState,
)
from src.intelligence.session_gate import SessionGate
from src.risk.drawdown_state import AccountRiskState


def test_session_gate_normal_go():
    gate = SessionGate()
    decision = gate.evaluate(
        market_regime=MarketRegime.BULLISH_CONTINUATION,
        portfolio_risk_state=AccountRiskState.NORMAL,
        is_system_ready=True,
        is_macro_event_imminent=False,
    )
    assert decision.gate_state == SessionGateState.GO
    assert decision.risk_multiplier == 1.0
    assert decision.is_trading_authorized


def test_session_gate_high_vol_shock_no_go():
    gate = SessionGate()
    decision = gate.evaluate(
        market_regime=MarketRegime.HIGH_VOL_SHOCK,
        portfolio_risk_state=AccountRiskState.NORMAL,
        is_system_ready=True,
        is_macro_event_imminent=False,
    )
    assert decision.gate_state == SessionGateState.NO_GO
    assert decision.risk_multiplier == 0.0
    assert not decision.is_trading_authorized


def test_session_gate_macro_imminent_caution():
    gate = SessionGate()
    decision = gate.evaluate(
        market_regime=MarketRegime.BULLISH_CONTINUATION,
        portfolio_risk_state=AccountRiskState.NORMAL,
        is_system_ready=True,
        is_macro_event_imminent=True,
    )
    assert decision.gate_state == SessionGateState.CAUTION
    assert decision.risk_multiplier == 0.50
    assert decision.is_trading_authorized


def test_session_gate_system_unhealthy_no_go():
    gate = SessionGate()
    decision = gate.evaluate(
        market_regime=MarketRegime.BULLISH_CONTINUATION,
        portfolio_risk_state=AccountRiskState.NORMAL,
        is_system_ready=False,
        is_macro_event_imminent=False,
    )
    assert decision.gate_state == SessionGateState.NO_GO
    assert decision.risk_multiplier == 0.0
    assert not decision.is_trading_authorized


def test_session_gate_severe_drawdown_no_go():
    gate = SessionGate()
    decision = gate.evaluate(
        market_regime=MarketRegime.BULLISH_CONTINUATION,
        portfolio_risk_state=AccountRiskState.CASH_PRESERVATION,
        is_system_ready=True,
        is_macro_event_imminent=False,
    )
    assert decision.gate_state == SessionGateState.NO_GO
    assert decision.risk_multiplier == 0.0
    assert not decision.is_trading_authorized
