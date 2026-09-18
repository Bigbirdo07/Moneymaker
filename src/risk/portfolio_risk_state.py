"""
Portfolio Risk State and Tracking.

Maintains point-in-time account equity, daily P&L, rolling drawdowns,
active exposures, and available risk budgets for deterministic position sizing.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone


@dataclass
class PositionRecord:
    symbol: str
    shares: float
    entry_price: float
    current_price: float
    entry_timestamp: str
    effective_stop_price: float
    peak_price: float
    sector: str = "UNKNOWN"

    @property
    def notional_value(self) -> float:
        return self.shares * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        return (self.current_price - self.entry_price) * self.shares

    @property
    def current_risk_dollars(self) -> float:
        stop_dist = max(0.0, self.current_price - self.effective_stop_price)
        return self.shares * stop_dist


@dataclass
class PortfolioRiskState:
    """
    Immutable snapshot of the portfolio's financial and risk state at decision timestamp.
    """
    timestamp: str
    starting_day_equity: float
    current_equity: float
    cash: float
    peak_equity: float
    realized_pnl_today: float
    open_positions: Dict[str, PositionRecord] = field(default_factory=dict)
    rolling_drawdown_pct: float = 0.0
    daily_drawdown_pct: float = 0.0
    remaining_daily_loss_budget: float = 0.0

    @classmethod
    def create(
        cls,
        timestamp: str,
        starting_day_equity: float,
        current_equity: float,
        cash: float,
        peak_equity: float,
        realized_pnl_today: float,
        open_positions: Optional[Dict[str, PositionRecord]] = None,
        max_daily_loss_pct: float = 0.015,
    ) -> "PortfolioRiskState":
        pos = open_positions or {}
        unrealized = sum(p.unrealized_pnl for p in pos.values())
        total_eq = current_equity + unrealized

        # Compute drawdowns
        peak = max(peak_equity, total_eq)
        rolling_dd = max(0.0, (peak - total_eq) / peak) if peak > 0 else 0.0
        daily_dd = max(0.0, (starting_day_equity - total_eq) / starting_day_equity) if starting_day_equity > 0 else 0.0

        max_daily_loss_dollars = starting_day_equity * max_daily_loss_pct
        current_daily_loss = starting_day_equity - total_eq
        remaining_budget = max(0.0, max_daily_loss_dollars - max(0.0, current_daily_loss))

        return cls(
            timestamp=timestamp,
            starting_day_equity=starting_day_equity,
            current_equity=total_eq,
            cash=cash,
            peak_equity=peak,
            realized_pnl_today=realized_pnl_today,
            open_positions=pos,
            rolling_drawdown_pct=rolling_dd,
            daily_drawdown_pct=daily_dd,
            remaining_daily_loss_budget=remaining_budget,
        )

    @property
    def gross_exposure_dollars(self) -> float:
        return sum(p.notional_value for p in self.open_positions.values())

    @property
    def gross_exposure_pct(self) -> float:
        return (self.gross_exposure_dollars / self.current_equity) if self.current_equity > 0 else 0.0

    @property
    def active_position_count(self) -> int:
        return len(self.open_positions)

    def get_symbol_exposure_dollars(self, symbol: str) -> float:
        if symbol in self.open_positions:
            return self.open_positions[symbol].notional_value
        return 0.0

    def get_sector_exposure_dollars(self, sector: str) -> float:
        return sum(p.notional_value for p in self.open_positions.values() if p.sector == sector)
