"""
Real-Market Allocator V3 for Phase 11B / Engine V3.
Enforces single-position concentration limits, whole-share arithmetic, and volatility-adjusted sizing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np

from src.core.logging import get_logger
from src.core.types import EvidenceClass

logger = get_logger("execution.real_allocator_v3")


@dataclass
class AllocationResultV3:
    """Allocation sizing decision."""
    symbol: str
    target_shares: int
    target_capital: float
    allocation_status: str
    evidence_class: str = EvidenceClass.SIMULATED_EXECUTION_ON_REAL_MARKET_DATA.value


class RealMarketAllocatorV3:
    """
    Capital allocator designed to eliminate multi-position correlation contagion.
    """

    def __init__(
        self,
        max_active_positions: int = 1,
        max_position_capital_pct: float = 0.50,
        target_vol_bps: float = 20.0,
    ) -> None:
        self.max_active_positions = max_active_positions
        self.max_position_capital_pct = max_position_capital_pct
        self.target_vol_bps = target_vol_bps

    def compute_allocation(
        self,
        symbol: str,
        price: float,
        available_cash: float,
        total_equity: float,
        realized_vol_bps: float,
        current_active_positions: int,
    ) -> AllocationResultV3:
        """
        Computes whole-share position size under risk constraints.
        """
        if current_active_positions >= self.max_active_positions:
            return AllocationResultV3(symbol, 0, 0.0, "MAX_POSITIONS_REACHED")

        if price <= 0 or available_cash < 50.0:
            return AllocationResultV3(symbol, 0, 0.0, "INSUFFICIENT_CASH")

        max_cap = total_equity * self.max_position_capital_pct
        vol_scalar = min(1.5, max(0.5, self.target_vol_bps / max(5.0, realized_vol_bps)))
        target_cap = min(max_cap * vol_scalar, available_cash * 0.95)

        shares = int(np.floor(target_cap / price))
        if shares <= 0:
            return AllocationResultV3(symbol, 0, 0.0, "SHARE_CALCULATION_ZERO")

        allocated_dollars = shares * price
        return AllocationResultV3(symbol, shares, allocated_dollars, "AUTHORIZED")
