"""
Deterministic Drawdown State Machine and Throttling Engine.

Maps daily and rolling portfolio drawdowns into actionable risk states:
- NORMAL: 100% risk budget
- REDUCED_RISK: 50% risk budget
- CASH_PRESERVATION: 0% risk budget (no new trades)
- HALTED: Circuit breaker tripped
"""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple, List

from src.risk.portfolio_risk_state import PortfolioRiskState


class AccountRiskState(str, Enum):
    NORMAL = "NORMAL"
    REDUCED_RISK = "REDUCED_RISK"
    CASH_PRESERVATION = "CASH_PRESERVATION"
    HALTED = "HALTED"


@dataclass(frozen=True)
class DrawdownThrottleDecision:
    risk_state: AccountRiskState
    risk_budget_multiplier: float
    is_trading_allowed: bool
    reason_codes: List[str]


class DrawdownThrottleEngine:
    """
    Evaluates account risk state deterministically from portfolio drawdown metrics.
    """
    def __init__(
        self,
        daily_loss_limit_pct: float = 0.015,       # 1.5% daily loss limit -> CASH_PRESERVATION
        daily_caution_limit_pct: float = 0.010,    # 1.0% daily loss limit -> REDUCED_RISK
        rolling_dd_caution_pct: float = 0.040,     # 4.0% rolling drawdown -> REDUCED_RISK
        rolling_dd_preservation_pct: float = 0.070,# 7.0% rolling drawdown -> CASH_PRESERVATION
        rolling_dd_halt_pct: float = 0.100,        # 10.0% rolling drawdown -> HALTED
    ):
        self.daily_loss_limit_pct = daily_loss_limit_pct
        self.daily_caution_limit_pct = daily_caution_limit_pct
        self.rolling_dd_caution_pct = rolling_dd_caution_pct
        self.rolling_dd_preservation_pct = rolling_dd_preservation_pct
        self.rolling_dd_halt_pct = rolling_dd_halt_pct

    def evaluate(self, state: PortfolioRiskState) -> DrawdownThrottleDecision:
        reasons: List[str] = []

        # 1. Hard Halt Check (10% Rolling Drawdown)
        if state.rolling_drawdown_pct >= self.rolling_dd_halt_pct:
            reasons.append(f"ROLLING_DRAWDOWN_EXCEEDED_HALT_LIMIT_{state.rolling_drawdown_pct*100:.1f}PCT")
            return DrawdownThrottleDecision(
                risk_state=AccountRiskState.HALTED,
                risk_budget_multiplier=0.0,
                is_trading_allowed=False,
                reason_codes=reasons,
            )

        # 2. Cash Preservation Check (Daily >= 1.5% or Rolling >= 7.0%)
        if state.daily_drawdown_pct >= self.daily_loss_limit_pct:
            reasons.append(f"DAILY_LOSS_LIMIT_BREACHED_{state.daily_drawdown_pct*100:.1f}PCT")
            return DrawdownThrottleDecision(
                risk_state=AccountRiskState.CASH_PRESERVATION,
                risk_budget_multiplier=0.0,
                is_trading_allowed=False,
                reason_codes=reasons,
            )

        if state.rolling_drawdown_pct >= self.rolling_dd_preservation_pct:
            reasons.append(f"ROLLING_DRAWDOWN_PRESERVATION_TRIGGERED_{state.rolling_drawdown_pct*100:.1f}PCT")
            return DrawdownThrottleDecision(
                risk_state=AccountRiskState.CASH_PRESERVATION,
                risk_budget_multiplier=0.0,
                is_trading_allowed=False,
                reason_codes=reasons,
            )

        # 3. Reduced Risk Caution Check (Daily >= 1.0% or Rolling >= 4.0%)
        if state.daily_drawdown_pct >= self.daily_caution_limit_pct or state.rolling_drawdown_pct >= self.rolling_dd_caution_pct:
            if state.daily_drawdown_pct >= self.daily_caution_limit_pct:
                reasons.append(f"DAILY_DRAWDOWN_CAUTION_{state.daily_drawdown_pct*100:.1f}PCT")
            if state.rolling_drawdown_pct >= self.rolling_dd_caution_pct:
                reasons.append(f"ROLLING_DRAWDOWN_CAUTION_{state.rolling_drawdown_pct*100:.1f}PCT")
            return DrawdownThrottleDecision(
                risk_state=AccountRiskState.REDUCED_RISK,
                risk_budget_multiplier=0.50,
                is_trading_allowed=True,
                reason_codes=reasons,
            )

        # 4. Normal State
        reasons.append("PORTFOLIO_DRAWDOWN_NOMINAL")
        return DrawdownThrottleDecision(
            risk_state=AccountRiskState.NORMAL,
            risk_budget_multiplier=1.0,
            is_trading_allowed=True,
            reason_codes=reasons,
        )
