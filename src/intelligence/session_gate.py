"""
Deterministic Session Gate (Phase E).

Evaluates morning market conditions, portfolio risk states, system readiness,
and macro calendar events to assign:
- GO: Normal risk deployment permitted
- CAUTION: Reduced risk deployment (50% size multiplier)
- NO_GO: Zero new entries authorized
"""

from dataclasses import dataclass
from typing import List, Tuple, Optional

from src.intelligence.morning_market_state import SessionGateState, MarketRegime
from src.risk.drawdown_state import AccountRiskState


@dataclass(frozen=True)
class SessionGateDecision:
    gate_state: SessionGateState
    risk_multiplier: float
    is_trading_authorized: bool
    reason_codes: List[str]


class SessionGate:
    """
    Authoritative deterministic gate deciding whether today's session permits capital deployment.
    """
    def __init__(self):
        pass

    def evaluate(
        self,
        market_regime: MarketRegime,
        portfolio_risk_state: AccountRiskState,
        is_system_ready: bool = True,
        is_macro_event_imminent: bool = False,
        market_wide_event_active: bool = False,
    ) -> SessionGateDecision:
        reasons: List[str] = []

        # 1. Hard NO_GO Checks
        if not is_system_ready:
            reasons.append("SYSTEM_READINESS_NOT_READY")
            return SessionGateDecision(
                gate_state=SessionGateState.NO_GO,
                risk_multiplier=0.0,
                is_trading_authorized=False,
                reason_codes=reasons,
            )

        if portfolio_risk_state in (AccountRiskState.CASH_PRESERVATION, AccountRiskState.HALTED):
            reasons.append(f"PORTFOLIO_DRAWDOWN_RESTRICTION_{portfolio_risk_state.value}")
            return SessionGateDecision(
                gate_state=SessionGateState.NO_GO,
                risk_multiplier=0.0,
                is_trading_authorized=False,
                reason_codes=reasons,
            )

        if market_wide_event_active or market_regime == MarketRegime.HIGH_VOL_SHOCK:
            reasons.append("MARKET_WIDE_VOLATILITY_SHOCK_ACTIVE")
            return SessionGateDecision(
                gate_state=SessionGateState.NO_GO,
                risk_multiplier=0.0,
                is_trading_authorized=False,
                reason_codes=reasons,
            )

        # 2. CAUTION Checks
        if portfolio_risk_state == AccountRiskState.REDUCED_RISK:
            reasons.append("PORTFOLIO_DRAWDOWN_CAUTION")
            return SessionGateDecision(
                gate_state=SessionGateState.CAUTION,
                risk_multiplier=0.50,
                is_trading_authorized=True,
                reason_codes=reasons,
            )

        if is_macro_event_imminent:
            reasons.append("SCHEDULED_HIGH_IMPACT_MACRO_EVENT_WINDOW")
            return SessionGateDecision(
                gate_state=SessionGateState.CAUTION,
                risk_multiplier=0.50,
                is_trading_authorized=True,
                reason_codes=reasons,
            )

        if market_regime in (MarketRegime.LOW_VOL_CHOP, MarketRegime.REGIME_UNCERTAIN):
            reasons.append(f"MARKET_REGIME_{market_regime.value}")
            return SessionGateDecision(
                gate_state=SessionGateState.CAUTION,
                risk_multiplier=0.75,
                is_trading_authorized=True,
                reason_codes=reasons,
            )

        # 3. Nominal GO State
        reasons.append("ALL_SESSION_GATES_NOMINAL_GO")
        return SessionGateDecision(
            gate_state=SessionGateState.GO,
            risk_multiplier=1.0,
            is_trading_authorized=True,
            reason_codes=reasons,
        )
