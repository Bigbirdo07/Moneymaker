"""
Monte Carlo Simulation, Block Bootstrap, Value at Risk (VaR), Expected Shortfall (ES),
and Fractional Kelly Research for Phase 4 Capital Risk Audit.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


@dataclass
class MonteCarloSimulationResult:
    num_paths: int
    trades_per_path: int
    median_return_pct: float
    p05_return_pct: float
    p01_return_pct: float
    max_drawdown_median_pct: float
    p95_max_drawdown_pct: float
    p99_max_drawdown_pct: float
    prob_drawdown_5pct: float
    prob_drawdown_10pct: float
    prob_drawdown_15pct: float
    prob_ruin_25pct: float
    prob_ruin_50pct: float
    prob_ruin_75pct: float
    daily_var_95_pct: float
    daily_var_99_pct: float
    daily_es_95_pct: float
    daily_es_99_pct: float


@dataclass
class KellyAnalysisResult:
    win_rate: float
    win_loss_ratio: float
    full_kelly_fraction: float
    fractional_kelly_10pct: float
    fractional_kelly_25pct: float
    fractional_kelly_50pct: float
    current_fixed_cap: float
    recommendation: str


class MonteCarloRiskEngine:
    """Executes block-bootstrap Monte Carlo risk simulations across 10,000 paths."""

    def __init__(
        self,
        num_paths: int = 10000,
        trades_per_path: int = 250,
        block_size: int = 8,
        random_state: int = 42,
    ):
        self.num_paths = num_paths
        self.trades_per_path = trades_per_path
        self.block_size = block_size
        self.rng = np.random.RandomState(random_state)

    def run_simulation(
        self,
        empirical_trade_returns_bps: List[float],
        position_allocation_pct: float = 0.10,
    ) -> MonteCarloSimulationResult:
        """
        Run 10,000 block-bootstrap portfolio trajectory simulations.
        """
        arr = np.array(empirical_trade_returns_bps)
        if len(arr) < self.block_size:
            raise ValueError(f"Insufficient empirical trades for block bootstrap: {len(arr)}")

        n_blocks = self.trades_per_path // self.block_size
        total_trades = n_blocks * self.block_size

        # Pre-generate blocks
        num_possible_blocks = len(arr) - self.block_size + 1
        blocks = np.array([arr[i : i + self.block_size] for i in range(num_possible_blocks)])

        final_returns = []
        max_drawdowns = []
        daily_losses = []

        for _ in range(self.num_paths):
            sampled_block_indices = self.rng.randint(0, num_possible_blocks, size=n_blocks)
            sampled_trade_returns = blocks[sampled_block_indices].flatten()

            # Portfolio equity curve starting at 1.0
            equity = 1.0
            peak = 1.0
            max_dd = 0.0

            # Daily grouping (approx 8.5 trades/day)
            daily_pnl = 0.0
            day_counter = 0

            for trade_ret_bps in sampled_trade_returns:
                trade_ret = (trade_ret_bps / 10000.0) * position_allocation_pct
                equity *= (1.0 + trade_ret)
                if equity > peak:
                    peak = equity
                dd = (peak - equity) / peak
                if dd > max_dd:
                    max_dd = dd

                daily_pnl += trade_ret
                day_counter += 1
                if day_counter >= 8:
                    daily_losses.append(-daily_pnl)
                    daily_pnl = 0.0
                    day_counter = 0

            final_returns.append((equity - 1.0) * 100.0)
            max_drawdowns.append(max_dd * 100.0)

        final_returns = np.array(final_returns)
        max_drawdowns = np.array(max_drawdowns)
        daily_losses = np.array(daily_losses)

        # VaR and Expected Shortfall
        var_95 = float(np.percentile(daily_losses, 95)) * 100.0
        var_99 = float(np.percentile(daily_losses, 99)) * 100.0
        es_95 = float(np.mean(daily_losses[daily_losses >= np.percentile(daily_losses, 95)])) * 100.0
        es_99 = float(np.mean(daily_losses[daily_losses >= np.percentile(daily_losses, 99)])) * 100.0

        return MonteCarloSimulationResult(
            num_paths=self.num_paths,
            trades_per_path=total_trades,
            median_return_pct=float(np.median(final_returns)),
            p05_return_pct=float(np.percentile(final_returns, 5)),
            p01_return_pct=float(np.percentile(final_returns, 1)),
            max_drawdown_median_pct=float(np.median(max_drawdowns)),
            p95_max_drawdown_pct=float(np.percentile(max_drawdowns, 95)),
            p99_max_drawdown_pct=float(np.percentile(max_drawdowns, 99)),
            prob_drawdown_5pct=float(np.mean(max_drawdowns >= 5.0) * 100.0),
            prob_drawdown_10pct=float(np.mean(max_drawdowns >= 10.0) * 100.0),
            prob_drawdown_15pct=float(np.mean(max_drawdowns >= 15.0) * 100.0),
            prob_ruin_25pct=float(np.mean(final_returns <= -25.0) * 100.0),
            prob_ruin_50pct=float(np.mean(final_returns <= -50.0) * 100.0),
            prob_ruin_75pct=float(np.mean(final_returns <= -75.0) * 100.0),
            daily_var_95_pct=var_95,
            daily_var_99_pct=var_99,
            daily_es_95_pct=es_95,
            daily_es_99_pct=es_99,
        )

    def evaluate_kelly_criterion(
        self,
        win_rate: float = 0.574,
        avg_win_bps: float = 16.5,
        avg_loss_bps: float = 14.8,
    ) -> KellyAnalysisResult:
        """
        Compute theoretical Full Kelly fraction and Fractional Kelly bounds.
        f* = (p * b - q) / b where b = avg_win / avg_loss, p = win_rate, q = 1 - p
        """
        b = avg_win_bps / avg_loss_bps
        p = win_rate
        q = 1.0 - p
        full_kelly = (p * b - q) / b if b > 0 else 0.0

        return KellyAnalysisResult(
            win_rate=p,
            win_loss_ratio=b,
            full_kelly_fraction=full_kelly,
            fractional_kelly_10pct=full_kelly * 0.10,
            fractional_kelly_25pct=full_kelly * 0.25,
            fractional_kelly_50pct=full_kelly * 0.50,
            current_fixed_cap=0.10,
            recommendation="0.25 Fractional Kelly (~4.5% to 6.0%) or 10% hard cap ensures tail risk protection.",
        )
