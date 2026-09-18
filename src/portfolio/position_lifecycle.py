"""
Position Lifecycle State Machine (Phase F).

Tracks open paper positions, entry/exit executions, MFE/MAE metrics,
and trapped halt status.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any


class PositionLifecycleState(str, Enum):
    PENDING_ENTRY = "PENDING_ENTRY"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    REDUCING = "REDUCING"
    EXIT_PENDING = "EXIT_PENDING"
    CLOSED = "CLOSED"
    HALTED_TRAPPED = "HALTED_TRAPPED"
    RECONCILIATION_REQUIRED = "RECONCILIATION_REQUIRED"


@dataclass
class ManagedPosition:
    symbol: str
    shares: int
    entry_price: float
    current_price: float
    entry_timestamp: str
    stop_loss_price: float
    take_profit_price: Optional[float] = None
    state: PositionLifecycleState = PositionLifecycleState.OPEN
    max_favorable_excursion_dollars: float = 0.0
    max_adverse_excursion_dollars: float = 0.0
    sector: str = "UNKNOWN"
    realized_pnl: float = 0.0
    is_halted: bool = False

    @property
    def current_notional(self) -> float:
        return self.shares * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.shares

    @property
    def unrealized_pnl_pct(self) -> float:
        if self.entry_price <= 0:
            return 0.0
        return ((self.current_price - self.entry_price) / self.entry_price) * 100.0

    def update_price(self, new_price: float) -> None:
        self.current_price = new_price
        pnl = self.unrealized_pnl
        if pnl > self.max_favorable_excursion_dollars:
            self.max_favorable_excursion_dollars = pnl
        if pnl < self.max_adverse_excursion_dollars:
            self.max_adverse_excursion_dollars = pnl

    def mark_halted(self) -> None:
        self.is_halted = True
        self.state = PositionLifecycleState.HALTED_TRAPPED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "shares": self.shares,
            "entry_price": self.entry_price,
            "current_price": self.current_price,
            "entry_timestamp": self.entry_timestamp,
            "stop_loss_price": self.stop_loss_price,
            "take_profit_price": self.take_profit_price,
            "state": self.state.value if hasattr(self.state, "value") else str(self.state),
            "max_favorable_excursion_dollars": self.max_favorable_excursion_dollars,
            "max_adverse_excursion_dollars": self.max_adverse_excursion_dollars,
            "sector": self.sector,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "is_halted": self.is_halted,
        }
