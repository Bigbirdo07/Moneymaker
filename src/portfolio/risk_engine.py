"""
Deterministic Portfolio Risk Engine for Phase 3A Shadow Trading.
Enforces hard limits on position sizing, daily loss, drawdown, concentration, and daily lockouts.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple
import pandas as pd


class RiskDecisionType(str, Enum):
    APPROVE = "APPROVE"
    RESIZE = "RESIZE"
    REJECT = "REJECT"


@dataclass
class RiskDecision:
    decision: RiskDecisionType
    approved_shares: float
    approved_notional: float
    reason: str


@dataclass
class RiskPolicyConfig:
    max_position_pct: float = 0.10             # 10% max allocation per trade ($100 on $1,000)
    max_concurrent_positions: int = 3          # Max 3 concurrent positions
    max_daily_loss_pct: float = 0.03           # 3% daily loss limit ($30 on $1,000)
    max_portfolio_drawdown_pct: float = 0.15   # 15% max portfolio drawdown ($150 on $1,000)
    max_symbol_exposure_pct: float = 0.10      # 10% max per symbol
    max_sector_exposure_pct: float = 0.20      # 20% max per sector
    allow_shorting: bool = False
    allow_leverage: bool = False


class DeterministicRiskEngine:
    """Evaluates candidate trades against mathematical risk constraints."""

    def __init__(self, config: Optional[RiskPolicyConfig] = None):
        self.config = config or RiskPolicyConfig()
        self.is_daily_locked_out = False
        self.lockout_reason = ""

    def reset_daily_lockout(self) -> None:
        self.is_daily_locked_out = False
        self.lockout_reason = ""

    def evaluate_order(
        self,
        symbol: str,
        price: float,
        shares: float,
        sector: str,
        current_equity: float,
        available_cash: float,
        current_daily_pnl: float,
        current_drawdown_pct: float,
        open_positions: Dict[str, Dict],  # symbol -> {shares, notional, sector}
    ) -> RiskDecision:
        """
        Evaluate proposed trade against deterministic risk rules.
        """
        if self.is_daily_locked_out:
            return RiskDecision(
                decision=RiskDecisionType.REJECT,
                approved_shares=0.0,
                approved_notional=0.0,
                reason=f"DAILY_LOCKOUT_ACTIVE: {self.lockout_reason}",
            )

        # 1. Max Daily Loss Check
        daily_loss_pct = -current_daily_pnl / current_equity if current_equity > 0 else 0.0
        if daily_loss_pct >= self.config.max_daily_loss_pct:
            self.is_daily_locked_out = True
            self.lockout_reason = f"DAILY_LOSS_LIMIT_REACHED_{daily_loss_pct*100:.2f}%"
            return RiskDecision(
                decision=RiskDecisionType.REJECT,
                approved_shares=0.0,
                approved_notional=0.0,
                reason=self.lockout_reason,
            )

        # 2. Max Portfolio Drawdown Check
        if current_drawdown_pct >= self.config.max_portfolio_drawdown_pct:
            self.is_daily_locked_out = True
            self.lockout_reason = f"MAX_DRAWDOWN_LIMIT_REACHED_{current_drawdown_pct*100:.2f}%"
            return RiskDecision(
                decision=RiskDecisionType.REJECT,
                approved_shares=0.0,
                approved_notional=0.0,
                reason=self.lockout_reason,
            )

        # 3. Max Concurrent Positions Check
        if len(open_positions) >= self.config.max_concurrent_positions and symbol not in open_positions:
            return RiskDecision(
                decision=RiskDecisionType.REJECT,
                approved_shares=0.0,
                approved_notional=0.0,
                reason=f"MAX_CONCURRENT_POSITIONS_REACHED_{len(open_positions)}",
            )

        # 4. Position Sizing & Cash Invariants
        max_allowed_notional = current_equity * self.config.max_position_pct
        proposed_notional = price * shares

        # Check existing symbol exposure
        existing_symbol_notional = open_positions.get(symbol, {}).get("notional", 0.0)
        if (existing_symbol_notional + proposed_notional) > (current_equity * self.config.max_symbol_exposure_pct * 1.05):
            return RiskDecision(
                decision=RiskDecisionType.REJECT,
                approved_shares=0.0,
                approved_notional=0.0,
                reason=f"SYMBOL_EXPOSURE_EXCEEDED_{symbol}",
            )

        # Check sector exposure
        sector_notional = sum(p.get("notional", 0.0) for p in open_positions.values() if p.get("sector") == sector)
        if (sector_notional + proposed_notional) > (current_equity * self.config.max_sector_exposure_pct * 1.05):
            return RiskDecision(
                decision=RiskDecisionType.REJECT,
                approved_shares=0.0,
                approved_notional=0.0,
                reason=f"SECTOR_EXPOSURE_EXCEEDED_{sector}",
            )

        # Resize if proposed notional exceeds max allowed or available cash
        effective_notional = min(proposed_notional, max_allowed_notional, available_cash * 0.98)
        if effective_notional < (price * 0.5):  # Must afford at least 0.5 shares
            return RiskDecision(
                decision=RiskDecisionType.REJECT,
                approved_shares=0.0,
                approved_notional=0.0,
                reason="INSUFFICIENT_AVAILABLE_CASH",
            )

        effective_shares = effective_notional / price
        decision_type = RiskDecisionType.RESIZE if effective_notional < proposed_notional * 0.95 else RiskDecisionType.APPROVE

        return RiskDecision(
            decision=decision_type,
            approved_shares=effective_shares,
            approved_notional=effective_notional,
            reason="APPROVED" if decision_type == RiskDecisionType.APPROVE else f"RESIZED_TO_{effective_notional:.2f}",
        )
