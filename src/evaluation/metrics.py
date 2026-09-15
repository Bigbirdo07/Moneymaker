"""Comprehensive financial performance and risk metrics engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.backtest.engine import BacktestResult, CompletedTrade


@dataclass
class PerformanceSummary:
    """Comprehensive statistical performance teardown."""
    strategy_name: str
    initial_capital: float
    final_capital: float
    total_return_pct: float
    cagr_pct: float
    annualized_volatility_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    calmar_ratio: float
    
    # Trade Statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    loss_rate_pct: float
    profit_factor: float
    expectancy: float
    avg_win_dollar: float
    avg_loss_dollar: float
    avg_trade_pnl: float
    avg_holding_bars: float
    
    # Cost & Friction
    total_friction_cost: float
    total_slippage: float
    total_spread: float
    total_commissions: float
    gross_pnl: float
    net_pnl: float

    # Market Sensitivity
    alpha_annualized: float = 0.0
    beta_to_benchmark: float = 0.0
    benchmark_correlation: float = 0.0


class MetricsCalculator:
    """Calculates professional quantitative performance metrics from backtest results."""

    def __init__(
        self,
        risk_free_rate: float = 0.04,  # 4% annual risk-free rate
        intraday_annualization_factor: float = 252.0 * 78.0,  # 252 days * 78 5-min bars
    ) -> None:
        self.risk_free_rate = risk_free_rate
        self.annualization_factor = intraday_annualization_factor

    def compute_summary(
        self,
        result: BacktestResult,
        benchmark_equity_curve: Optional[pd.DataFrame] = None,
    ) -> PerformanceSummary:
        """Calculates the complete performance summary."""
        eq = result.equity_curve
        trades = result.trades

        init_cap = result.initial_capital
        fin_cap = result.final_capital
        tot_ret = (fin_cap - init_cap) / init_cap if init_cap > 0 else 0.0

        # Bar returns
        returns = eq["returns"].values if not eq.empty and "returns" in eq else np.array([])
        n_bars = len(returns)

        # CAGR approximation based on trading days (78 bars = 1 day)
        trading_days = max(1.0, n_bars / 78.0)
        years = trading_days / 252.0
        if years > 0 and fin_cap > 0:
            cagr = (fin_cap / init_cap) ** (1.0 / years) - 1.0
        else:
            cagr = 0.0

        # Volatility
        if len(returns) > 1:
            bar_std = float(np.std(returns, ddof=1))
            ann_vol = bar_std * np.sqrt(self.annualization_factor)
        else:
            bar_std = 0.0
            ann_vol = 0.0

        # Sharpe Ratio
        rf_per_bar = self.risk_free_rate / self.annualization_factor
        excess_returns = returns - rf_per_bar
        if bar_std > 1e-9:
            sharpe = (float(np.mean(excess_returns)) / bar_std) * np.sqrt(self.annualization_factor)
        else:
            sharpe = 0.0

        # Sortino Ratio (downside deviation)
        downside_returns = returns[returns < rf_per_bar]
        if len(downside_returns) > 1:
            downside_std = float(np.std(downside_returns, ddof=1))
            sortino = (float(np.mean(excess_returns)) / downside_std) * np.sqrt(self.annualization_factor) if downside_std > 1e-9 else 0.0
        else:
            sortino = 0.0

        # Max Drawdown
        max_dd = float(eq["drawdown_pct"].max()) if not eq.empty and "drawdown_pct" in eq else 0.0

        # Calmar Ratio
        calmar = (tot_ret / max_dd) if max_dd > 1e-4 else 0.0

        # Trade metrics
        tot_trades = len(trades)
        if tot_trades > 0:
            trade_pnls = np.array([t.net_pnl for t in trades])
            gross_pnls = np.array([t.gross_pnl for t in trades])
            wins = trade_pnls[trade_pnls > 0]
            losses = trade_pnls[trade_pnls < 0]

            win_count = len(wins)
            loss_count = len(losses)
            win_rate = win_count / tot_trades
            loss_rate = loss_count / tot_trades

            gross_win_sum = float(np.sum(wins)) if len(wins) > 0 else 0.0
            gross_loss_sum = abs(float(np.sum(losses))) if len(losses) > 0 else 0.0

            profit_factor = (gross_win_sum / gross_loss_sum) if gross_loss_sum > 1e-6 else (99.0 if gross_win_sum > 0 else 0.0)
            avg_win = float(np.mean(wins)) if len(wins) > 0 else 0.0
            avg_loss = float(np.mean(losses)) if len(losses) > 0 else 0.0
            avg_trade_pnl = float(np.mean(trade_pnls))
            expectancy = (win_rate * avg_win) + (loss_rate * avg_loss)
            avg_holding = float(np.mean([t.holding_bars for t in trades]))

            tot_slip = float(np.sum([t.slippage_paid for t in trades]))
            tot_sprd = float(np.sum([t.spread_paid for t in trades]))
            tot_comm = float(np.sum([t.commission_paid for t in trades]))
            tot_gross = float(np.sum(gross_pnls))
            tot_net = float(np.sum(trade_pnls))
        else:
            win_count = 0
            loss_count = 0
            win_rate = 0.0
            loss_rate = 0.0
            profit_factor = 0.0
            avg_win = 0.0
            avg_loss = 0.0
            avg_trade_pnl = 0.0
            expectancy = 0.0
            avg_holding = 0.0
            tot_slip = 0.0
            tot_sprd = 0.0
            tot_comm = 0.0
            tot_gross = 0.0
            tot_net = 0.0

        # Alpha / Beta to benchmark if provided
        alpha = 0.0
        beta = 0.0
        corr = 0.0
        if benchmark_equity_curve is not None and not benchmark_equity_curve.empty:
            bench_ret = benchmark_equity_curve["returns"].values
            min_len = min(len(returns), len(bench_ret))
            if min_len > 10:
                r_strat = returns[:min_len]
                r_bench = bench_ret[:min_len]
                cov_mat = np.cov(r_strat, r_bench)
                cov_sb = cov_mat[0, 1]
                var_b = cov_mat[1, 1]
                beta = float(cov_sb / var_b) if var_b > 1e-9 else 0.0
                corr = float(np.corrcoef(r_strat, r_bench)[0, 1]) if np.std(r_strat) > 1e-9 and np.std(r_bench) > 1e-9 else 0.0
                alpha = (tot_ret - (self.risk_free_rate * years + beta * (benchmark_equity_curve["portfolio_value"].iloc[-1] / benchmark_equity_curve["portfolio_value"].iloc[0] - 1.0)))

        return PerformanceSummary(
            strategy_name=result.strategy_name,
            initial_capital=init_cap,
            final_capital=fin_cap,
            total_return_pct=round(tot_ret * 100.0, 3),
            cagr_pct=round(cagr * 100.0, 3),
            annualized_volatility_pct=round(ann_vol * 100.0, 3),
            sharpe_ratio=round(sharpe, 3),
            sortino_ratio=round(sortino, 3),
            max_drawdown_pct=round(max_dd * 100.0, 3),
            calmar_ratio=round(calmar, 3),
            total_trades=tot_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate_pct=round(win_rate * 100.0, 2),
            loss_rate_pct=round(loss_rate * 100.0, 2),
            profit_factor=round(profit_factor, 3),
            expectancy=round(expectancy, 4),
            avg_win_dollar=round(avg_win, 4),
            avg_loss_dollar=round(avg_loss, 4),
            avg_trade_pnl=round(avg_trade_pnl, 4),
            avg_holding_bars=round(avg_holding, 1),
            total_friction_cost=result.total_friction_cost,
            total_slippage=round(tot_slip, 4),
            total_spread=round(tot_sprd, 4),
            total_commissions=round(tot_comm, 4),
            gross_pnl=round(tot_gross, 4),
            net_pnl=round(tot_net, 4),
            alpha_annualized=round(alpha, 4),
            beta_to_benchmark=round(beta, 4),
            benchmark_correlation=round(corr, 4),
        )
