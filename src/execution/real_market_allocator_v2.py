"""
Real-Market Capital Allocator V2 for Phase 10.4.
Enforces whole-share allocation, capital concentration rules, volatility-adjusted sizing,
and explicit CASH retention policies.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import numpy as np

from src.core.logging import get_logger
from src.core.types import EvidenceClass, PortfolioState
from src.signals.real_market_entry_model_v2 import EntryDecisionV2

logger = get_logger("execution.real_allocator_v2")


@dataclass
class AllocationResultV2:
    """Position sizing and capital deployment artifact for an authorized entry."""
    symbol: str
    decision_id: str
    target_shares: int
    target_notional: float
    allocated_pct_of_portfolio: float
    estimated_entry_friction: float
    is_allocated: bool
    rejection_reason: Optional[str] = None
    evidence_class: str = EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RealMarketAllocatorV2:
    """
    Capital Allocator V2 with support for single-position concentration,
    equal weighting, and volatility-adjusted sizing.
    """

    def __init__(
        self,
        max_active_positions: int = 2,
        max_position_capital_pct: float = 0.50,
        sizing_policy: str = "VOLATILITY_ADJUSTED",  # EQUAL_WEIGHT, VOLATILITY_ADJUSTED, FIXED_DOLLAR
        min_position_notional: float = 100.0,
        reserve_cash_pct: float = 0.05,
    ) -> None:
        self.max_active_positions = max_active_positions
        self.max_position_capital_pct = max_position_capital_pct
        self.sizing_policy = sizing_policy
        self.min_position_notional = min_position_notional
        self.reserve_cash_pct = reserve_cash_pct

    def compute_allocation(
        self,
        decision: EntryDecisionV2,
        current_price: float,
        available_cash: float,
        total_equity: float,
        current_active_count: int,
        realized_vol_bps: float = 10.0,
        estimated_spread_bps: float = 3.0,
    ) -> AllocationResultV2:
        """
        Computes whole-share allocation for an authorized entry candidate.
        """
        sym = decision.symbol
        if not decision.is_authorized or decision.action != "BUY":
            return AllocationResultV2(
                symbol=sym,
                decision_id=f"ALLOC_{sym}",
                target_shares=0,
                target_notional=0.0,
                allocated_pct_of_portfolio=0.0,
                estimated_entry_friction=0.0,
                is_allocated=False,
                rejection_reason="ENTRY_NOT_AUTHORIZED",
            )

        if current_active_count >= self.max_active_positions:
            return AllocationResultV2(
                symbol=sym,
                decision_id=f"ALLOC_{sym}",
                target_shares=0,
                target_notional=0.0,
                allocated_pct_of_portfolio=0.0,
                estimated_entry_friction=0.0,
                is_allocated=False,
                rejection_reason="CAPACITY_FULL",
            )

        if current_price <= 0:
            return AllocationResultV2(
                symbol=sym,
                decision_id=f"ALLOC_{sym}",
                target_shares=0,
                target_notional=0.0,
                allocated_pct_of_portfolio=0.0,
                estimated_entry_friction=0.0,
                is_allocated=False,
                rejection_reason="INVALID_PRICE",
            )

        # Usable cash considering reserve
        usable_cash = max(0.0, available_cash - (total_equity * self.reserve_cash_pct))
        
        # Max capital per position
        max_notional_cap = total_equity * self.max_position_capital_pct
        target_budget = min(usable_cash, max_notional_cap)

        # Policy adjustment
        if self.sizing_policy == "VOLATILITY_ADJUSTED":
            # Scale inversely with volatility relative to baseline 10 bps vol
            vol_factor = np.clip(10.0 / max(3.0, realized_vol_bps), 0.50, 1.50)
            target_budget = target_budget * vol_factor
            target_budget = min(target_budget, usable_cash, max_notional_cap)
        elif self.sizing_policy == "FIXED_DOLLAR":
            target_budget = min(target_budget, 400.0)

        if target_budget < self.min_position_notional:
            return AllocationResultV2(
                symbol=sym,
                decision_id=f"ALLOC_{sym}",
                target_shares=0,
                target_notional=0.0,
                allocated_pct_of_portfolio=0.0,
                estimated_entry_friction=0.0,
                is_allocated=False,
                rejection_reason="INSUFFICIENT_USABLE_CASH",
            )

        shares = int(target_budget / current_price)
        if shares < 1:
            return AllocationResultV2(
                symbol=sym,
                decision_id=f"ALLOC_{sym}",
                target_shares=0,
                target_notional=0.0,
                allocated_pct_of_portfolio=0.0,
                estimated_entry_friction=0.0,
                is_allocated=False,
                rejection_reason="SHARE_PRICE_EXCEEDS_BUDGET",
            )

        notional = shares * current_price
        friction_est = notional * (estimated_spread_bps / 10000.0) + max(0.01, shares * 0.0005)

        # Ensure cash can pay notional + friction
        if notional + friction_est > usable_cash:
            shares = int((usable_cash - friction_est) / current_price)
            if shares < 1:
                return AllocationResultV2(
                    symbol=sym,
                    decision_id=f"ALLOC_{sym}",
                    target_shares=0,
                    target_notional=0.0,
                    allocated_pct_of_portfolio=0.0,
                    estimated_entry_friction=0.0,
                    is_allocated=False,
                    rejection_reason="INSUFFICIENT_CASH_AFTER_FRICTION",
                )
            notional = shares * current_price

        return AllocationResultV2(
            symbol=sym,
            decision_id=f"ALLOC_{sym}",
            target_shares=shares,
            target_notional=round(notional, 2),
            allocated_pct_of_portfolio=round((notional / total_equity) * 100.0, 2),
            estimated_entry_friction=round(friction_est, 4),
            is_allocated=True,
        )
