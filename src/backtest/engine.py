"""Event-driven chronological backtest execution simulator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.core.types import (
    Bar,
    Fill,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    PortfolioState,
    Position,
    Signal,
    SignalDirection,
)
from src.backtest.costs import TransactionCostModel
from src.strategies.base import BaseStrategy
from src.data.calendar import TradingCalendar
from src.core.logging import get_logger

logger = get_logger("backtest.engine")


@dataclass
class CompletedTrade:
    """Record of a completed round-trip trade."""
    trade_id: str
    symbol: str
    entry_timestamp: datetime
    exit_timestamp: datetime
    entry_price: float
    exit_price: float
    shares: int
    gross_pnl: float
    net_pnl: float
    return_pct: float
    spread_paid: float
    slippage_paid: float
    commission_paid: float
    holding_bars: int
    exit_reason: str
    strategy: str


@dataclass
class BacktestResult:
    """Complete output artifact from a backtest run."""
    strategy_name: str
    initial_capital: float
    final_capital: float
    equity_curve: pd.DataFrame
    trades: List[CompletedTrade]
    portfolio_states: List[PortfolioState]
    total_signals: int
    executed_trades: int
    rejected_signals: int
    total_friction_cost: float


class BacktestEngine:
    """Chronological bar-by-bar backtest simulation engine."""

    def __init__(
        self,
        initial_capital: float = 1000.0,
        max_position_pct: float = 0.10,      # Max 10% per trade ($100 on $1k)
        max_concurrent_positions: int = 5,
        cost_model: Optional[TransactionCostModel] = None,
        calendar: Optional[TradingCalendar] = None,
        force_eod_liquidation: bool = True,
    ) -> None:
        self.initial_capital = initial_capital
        self.max_position_pct = max_position_pct
        self.max_concurrent_positions = max_concurrent_positions
        self.cost_model = cost_model or TransactionCostModel()
        self.calendar = calendar or TradingCalendar()
        self.force_eod_liquidation = force_eod_liquidation

    def run(
        self,
        strategy: BaseStrategy,
        df: pd.DataFrame,
        symbol: Optional[str] = None,
    ) -> BacktestResult:
        """Runs the backtest simulation over a single or multi-symbol dataframe."""
        if df.empty:
            raise ValueError("Cannot run backtest on empty DataFrame")

        symbol_name = symbol or str(df["symbol"].iloc[0])
        clean_df = df.sort_values("timestamp").reset_index(drop=True)

        # Generate strategy signals
        signals = strategy.generate_signals(clean_df)
        signal_map = {sig.timestamp: sig for sig in signals}

        portfolio = PortfolioState(
            timestamp=clean_df["timestamp"].iloc[0],
            cash=self.initial_capital,
            buying_power=self.initial_capital,
            positions={},
            portfolio_value=self.initial_capital,
        )

        completed_trades: List[CompletedTrade] = []
        equity_records: List[dict] = []
        portfolio_states: List[PortfolioState] = []
        total_signals_count = len(signals)
        executed_trades_count = 0
        rejected_signals_count = 0
        total_friction_accum = 0.0
        trade_counter = 0

        # Active position tracking
        active_position: Optional[Position] = None
        current_trade_entry_fill: Optional[Fill] = None
        current_trade_strategy_name = strategy.name

        num_bars = len(clean_df)

        for idx, row in clean_df.iterrows():
            ts = row["timestamp"]
            close_price = float(row["close"])
            high_price = float(row["high"])
            low_price = float(row["low"])
            vol = float(row.get("volume", 0.0))
            spread = float(row.get("spread", 0.0)) if "spread" in row else None
            mins_to_close = float(row.get("feature_minutes_to_close", 390.0))

            # 1. Update active position mark-to-market
            if active_position is not None:
                active_position.update_price(close_price)
                active_position.bars_held += 1

            # 2. Check exits for active position
            should_exit = False
            exit_reason = ""
            exit_price = close_price

            if active_position is not None:
                # EOD Liquidation (last 10 minutes of session)
                if self.force_eod_liquidation and mins_to_close <= 10.0:
                    should_exit = True
                    exit_reason = "EOD_FORCE_CLOSE"
                # Stop Loss Hit
                elif active_position.stop_loss is not None and low_price <= active_position.stop_loss:
                    should_exit = True
                    exit_reason = "STOP_LOSS"
                    exit_price = active_position.stop_loss
                # Take Profit Hit
                elif active_position.take_profit is not None and high_price >= active_position.take_profit:
                    should_exit = True
                    exit_reason = "TAKE_PROFIT"
                    exit_price = active_position.take_profit
                # Max Holding Time Expired
                elif active_position.max_holding_bars is not None and active_position.bars_held >= active_position.max_holding_bars:
                    should_exit = True
                    exit_reason = "TIME_STOP"
                # End of dataset exit
                elif idx == num_bars - 1:
                    should_exit = True
                    exit_reason = "END_OF_DATA"

                # Execute Exit Fill
                if should_exit:
                    trade_counter += 1
                    exit_cost = self.cost_model.calculate_fill(
                        side=OrderSide.SELL,
                        price=exit_price,
                        shares=active_position.shares,
                        observed_spread=spread,
                        volume=vol,
                    )
                    gross_proceeds = active_position.shares * exit_price
                    net_proceeds = active_position.shares * exit_cost.net_price - exit_cost.commission
                    
                    portfolio.cash += net_proceeds
                    portfolio.total_fees += exit_cost.commission
                    portfolio.total_slippage += exit_cost.slippage_cost
                    total_friction_accum += exit_cost.total_friction

                    # Compute completed trade metrics
                    entry_price = active_position.avg_entry_price
                    entry_cost_basis = active_position.cost_basis
                    gross_pnl = gross_proceeds - entry_cost_basis
                    entry_friction = current_trade_entry_fill.slippage_cost + current_trade_entry_fill.spread_cost + current_trade_entry_fill.fee if current_trade_entry_fill else 0.0
                    net_pnl = net_proceeds - entry_cost_basis - entry_friction

                    trade_ret = net_pnl / entry_cost_basis if entry_cost_basis > 0 else 0.0

                    completed_trades.append(
                        CompletedTrade(
                            trade_id=f"T_{trade_counter:04d}",
                            symbol=active_position.symbol,
                            entry_timestamp=active_position.entry_timestamp,
                            exit_timestamp=ts,
                            entry_price=entry_price,
                            exit_price=exit_cost.net_price,
                            shares=active_position.shares,
                            gross_pnl=round(gross_pnl, 4),
                            net_pnl=round(net_pnl, 4),
                            return_pct=round(trade_ret, 6),
                            spread_paid=round(exit_cost.spread_cost + (current_trade_entry_fill.spread_cost if current_trade_entry_fill else 0), 4),
                            slippage_paid=round(exit_cost.slippage_cost + (current_trade_entry_fill.slippage_cost if current_trade_entry_fill else 0), 4),
                            commission_paid=round(exit_cost.commission + (current_trade_entry_fill.fee if current_trade_entry_fill else 0), 4),
                            holding_bars=active_position.bars_held,
                            exit_reason=exit_reason,
                            strategy=current_trade_strategy_name,
                        )
                    )

                    active_position = None
                    current_trade_entry_fill = None
                    if symbol_name in portfolio.positions:
                        del portfolio.positions[symbol_name]

            # 3. Check Entries if no active position
            current_signal = signal_map.get(ts)
            if active_position is None and current_signal is not None and current_signal.direction == SignalDirection.BUY:
                # EOD Entry restriction: do not open trades in final 20 minutes of session
                if self.force_eod_liquidation and mins_to_close <= 20.0:
                    rejected_signals_count += 1
                else:
                    # Determine position sizing: 10% max capital
                    available_cash = portfolio.cash
                    max_alloc = portfolio.portfolio_value * self.max_position_pct
                    allocated_capital = min(available_cash, max_alloc)

                    shares_to_buy = int(allocated_capital // close_price)
                    if shares_to_buy > 0:
                        entry_cost = self.cost_model.calculate_fill(
                            side=OrderSide.BUY,
                            price=close_price,
                            shares=shares_to_buy,
                            observed_spread=spread,
                            volume=vol,
                        )
                        total_entry_cost = (shares_to_buy * entry_cost.net_price) + entry_cost.commission

                        if total_entry_cost <= portfolio.cash:
                            portfolio.cash -= total_entry_cost
                            portfolio.total_fees += entry_cost.commission
                            portfolio.total_slippage += entry_cost.slippage_cost
                            total_friction_accum += entry_cost.total_friction

                            # Stop loss / take profit parameters
                            stop_pct = current_signal.metadata.get("stop_loss_pct", 0.005)
                            take_pct = current_signal.metadata.get("take_profit_pct", 0.010)

                            active_position = Position(
                                symbol=symbol_name,
                                shares=shares_to_buy,
                                avg_entry_price=entry_cost.net_price,
                                current_price=close_price,
                                entry_timestamp=ts,
                                stop_loss=round(entry_cost.net_price * (1.0 - stop_pct), 4),
                                take_profit=round(entry_cost.net_price * (1.0 + take_pct), 4),
                                max_holding_bars=current_signal.expected_holding_period,
                                bars_held=0,
                            )
                            portfolio.positions[symbol_name] = active_position

                            current_trade_entry_fill = Fill(
                                fill_id=f"FILL_IN_{trade_counter+1}",
                                order_id=f"ORD_IN_{trade_counter+1}",
                                symbol=symbol_name,
                                side=OrderSide.BUY,
                                quantity=shares_to_buy,
                                price=entry_cost.net_price,
                                slippage_cost=entry_cost.slippage_cost,
                                spread_cost=entry_cost.spread_cost,
                                fee=entry_cost.commission,
                                timestamp=ts,
                            )
                            executed_trades_count += 1
                        else:
                            rejected_signals_count += 1
                    else:
                        rejected_signals_count += 1

            # 4. Record Portfolio State
            portfolio.timestamp = ts
            portfolio.update_metrics()

            equity_records.append({
                "timestamp": ts,
                "portfolio_value": portfolio.portfolio_value,
                "cash": portfolio.cash,
                "drawdown_pct": portfolio.drawdown_pct,
                "in_position": 1 if active_position is not None else 0,
            })

        equity_df = pd.DataFrame(equity_records)
        if not equity_df.empty:
            equity_df["returns"] = equity_df["portfolio_value"].pct_change().fillna(0.0)

        return BacktestResult(
            strategy_name=strategy.name,
            initial_capital=self.initial_capital,
            final_capital=round(portfolio.portfolio_value, 4),
            equity_curve=equity_df,
            trades=completed_trades,
            portfolio_states=portfolio_states,
            total_signals=total_signals_count,
            executed_trades=executed_trades_count,
            rejected_signals=rejected_signals_count,
            total_friction_cost=round(total_friction_accum, 4),
        )
