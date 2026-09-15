"""
Shadow Paper Portfolio with Double-Entry Style Accounting for Phase 3A.
Maintains positions, cash, realized/unrealized PnL, transaction friction, and drawdown metrics.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
import pandas as pd


class ExitReason(str, Enum):
    TIME_EXIT = "TIME_EXIT"  # 15-minute horizon reached
    SIGNAL_DETERIORATION = "SIGNAL_DETERIORATION"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    EOD_LIQUIDATION = "EOD_LIQUIDATION"


@dataclass
class ShadowPosition:
    symbol: str
    shares: float
    entry_price: float
    entry_timestamp: pd.Timestamp
    sector: str
    target_exit_bars: int = 3
    bars_held: int = 0
    current_price: float = field(default=0.0)
    stop_loss_price: float = field(default=0.0)
    take_profit_price: float = field(default=0.0)

    @property
    def cost_basis(self) -> float:
        return self.shares * self.entry_price

    @property
    def market_value(self) -> float:
        return self.shares * (self.current_price if self.current_price > 0 else self.entry_price)

    @property
    def unrealized_pnl(self) -> float:
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_bps(self) -> float:
        if self.cost_basis <= 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 10000.0


@dataclass
class ClosedTradeRecord:
    trade_id: str
    symbol: str
    direction: str
    shares: float
    entry_price: float
    entry_timestamp: pd.Timestamp
    exit_price: float
    exit_timestamp: pd.Timestamp
    exit_reason: ExitReason
    bars_held: int
    gross_pnl: float
    gross_pnl_bps: float
    friction_cost: float
    friction_cost_bps: float
    net_pnl: float
    net_pnl_bps: float


class ShadowPaperPortfolio:
    """Manages simulated paper trading balance, positions, and accounting invariants."""

    def __init__(self, initial_cash: float = 1000.0, transaction_cost_bps: float = 3.5):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.reserved_cash = 0.0
        self.transaction_cost_bps = transaction_cost_bps

        self.positions: Dict[str, ShadowPosition] = {}
        self.closed_trades: List[ClosedTradeRecord] = []

        self.total_realized_pnl = 0.0
        self.total_friction_cost = 0.0
        self.daily_pnl = 0.0
        self.peak_equity = initial_cash

    @property
    def total_unrealized_pnl(self) -> float:
        return sum(pos.unrealized_pnl for pos in self.positions.values())

    @property
    def total_equity(self) -> float:
        return self.cash + sum(pos.market_value for pos in self.positions.values())

    @property
    def current_drawdown_pct(self) -> float:
        if self.peak_equity <= 0:
            return 0.0
        eq = self.total_equity
        if eq > self.peak_equity:
            self.peak_equity = eq
        return max(0.0, (self.peak_equity - eq) / self.peak_equity)

    def verify_accounting_invariants(self) -> bool:
        """
        Verify double-entry accounting integrity:
        Equity = Cash + Market Value of Positions
        Cash = Initial Cash + Realized PnL - Friction - Net Cost Basis
        """
        expected_equity = self.cash + sum(pos.market_value for pos in self.positions.values())
        cost_basis_open = sum(pos.cost_basis for pos in self.positions.values())
        expected_cash = self.initial_cash + self.total_realized_pnl - self.total_friction_cost - cost_basis_open

        equity_diff = abs(self.total_equity - expected_equity)
        cash_diff = abs(self.cash - expected_cash)

        return equity_diff < 1e-4 and cash_diff < 1e-4

    def open_position(
        self,
        symbol: str,
        shares: float,
        entry_price: float,
        entry_timestamp: pd.Timestamp,
        sector: str = "Technology",
        stop_loss_pct: float = 0.015,
        take_profit_pct: float = 0.030,
    ) -> bool:
        """Open a new long position and deduct cash + friction."""
        cost = shares * entry_price
        friction = cost * (self.transaction_cost_bps / 10000.0)
        total_outlay = cost + friction

        if total_outlay > self.cash:
            return False

        self.cash -= total_outlay
        self.total_friction_cost += friction

        pos = ShadowPosition(
            symbol=symbol,
            shares=shares,
            entry_price=entry_price,
            entry_timestamp=entry_timestamp,
            sector=sector,
            current_price=entry_price,
            stop_loss_price=entry_price * (1.0 - stop_loss_pct),
            take_profit_price=entry_price * (1.0 + take_profit_pct),
        )
        self.positions[symbol] = pos

        # Update peak equity
        if self.total_equity > self.peak_equity:
            self.peak_equity = self.total_equity

        return True

    def update_mark_to_market(self, symbol: str, current_price: float) -> None:
        """Update position mark-to-market valuation and advance holding bar."""
        if symbol in self.positions:
            self.positions[symbol].current_price = current_price
            self.positions[symbol].bars_held += 1

            if self.total_equity > self.peak_equity:
                self.peak_equity = self.total_equity

    def close_position(
        self,
        symbol: str,
        exit_price: float,
        exit_timestamp: pd.Timestamp,
        reason: ExitReason,
    ) -> Optional[ClosedTradeRecord]:
        """Close an existing position, realize PnL, deduct exit friction, and restore cash."""
        if symbol not in self.positions:
            return None

        pos = self.positions.pop(symbol)
        proceeds = pos.shares * exit_price
        exit_friction = proceeds * (self.transaction_cost_bps / 10000.0)
        net_proceeds = proceeds - exit_friction

        gross_pnl = (exit_price - pos.entry_price) * pos.shares
        total_friction = (pos.cost_basis * (self.transaction_cost_bps / 10000.0)) + exit_friction
        net_pnl = gross_pnl - total_friction

        gross_pnl_bps = ((exit_price - pos.entry_price) / pos.entry_price) * 10000.0
        friction_bps = (total_friction / pos.cost_basis) * 10000.0
        net_pnl_bps = gross_pnl_bps - friction_bps

        self.cash += proceeds - exit_friction
        self.total_realized_pnl += gross_pnl
        self.total_friction_cost += exit_friction
        self.daily_pnl += net_pnl

        record = ClosedTradeRecord(
            trade_id=f"TRADE_{symbol}_{pos.entry_timestamp.strftime('%Y%m%d%H%M')}",
            symbol=symbol,
            direction="LONG",
            shares=pos.shares,
            entry_price=pos.entry_price,
            entry_timestamp=pos.entry_timestamp,
            exit_price=exit_price,
            exit_timestamp=exit_timestamp,
            exit_reason=reason,
            bars_held=pos.bars_held,
            gross_pnl=gross_pnl,
            gross_pnl_bps=gross_pnl_bps,
            friction_cost=total_friction,
            friction_cost_bps=friction_bps,
            net_pnl=net_pnl,
            net_pnl_bps=net_pnl_bps,
        )
        self.closed_trades.append(record)
        return record
