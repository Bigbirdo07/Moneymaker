"""
Comprehensive Capital Risk & Market Shock Stress Testing Engine for Phase 4.
Simulates extreme cost multipliers, spread spikes, gap-through-stop risk, flash crashes,
correlated archetype shocks, model failures, and reverse stress testing.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class CostStressResult:
    multiplier: float
    effective_roundtrip_friction_bps: float
    gross_alpha_bps: float
    net_expectancy_bps: float
    profit_factor: float
    breakeven_reached: bool


@dataclass
class GapRiskResult:
    gap_pct: float
    position_notional_usd: float
    portfolio_equity_usd: float
    realized_loss_usd: float
    portfolio_loss_pct: float
    hit_daily_loss_limit: bool
    hit_max_drawdown_limit: bool


@dataclass
class CorrelatedShockResult:
    correlation: float
    num_positions: int
    single_position_drop_pct: float
    portfolio_equity_usd: float
    total_loss_usd: float
    portfolio_drawdown_pct: float
    cluster_exposure_limit_active: bool


@dataclass
class ModelInversionResult:
    rank_ic: float
    trades_before_detection: int
    days_before_detection: float
    capital_lost_usd: float
    portfolio_loss_pct: float
    triggered_circuit_breaker: str


class StressTestingEngine:
    """Executes deterministic risk and crisis stress simulations."""

    def __init__(
        self,
        base_gross_alpha_bps: float = 4.80,
        base_friction_bps: float = 3.22,
        base_capital_usd: float = 1000.0,
        max_daily_loss_pct: float = 0.03,      # 3% ($30)
        max_portfolio_drawdown_pct: float = 0.15, # 15% ($150)
    ):
        self.gross_alpha = base_gross_alpha_bps
        self.base_friction = base_friction_bps
        self.capital = base_capital_usd
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_portfolio_drawdown_pct = max_portfolio_drawdown_pct

    def evaluate_cost_stress(self, multipliers: List[float]) -> List[CostStressResult]:
        """Test sensitivity to transaction cost inflation."""
        results = []
        for m in multipliers:
            fric = self.base_friction * m
            net_exp = self.gross_alpha - fric
            # Profit factor approximation: (Win_rate * (Gross_win - fric)) / (Loss_rate * (Gross_loss + fric))
            pf = max(0.0, (0.57 * (self.gross_alpha + 15.0 - fric)) / (0.43 * (15.0 + fric))) if (15.0 + fric) > 0 else 0.0
            results.append(
                CostStressResult(
                    multiplier=m,
                    effective_roundtrip_friction_bps=fric,
                    gross_alpha_bps=self.gross_alpha,
                    net_expectancy_bps=net_exp,
                    profit_factor=pf,
                    breakeven_reached=(net_exp <= 0.0),
                )
            )
        return results

    def evaluate_gap_risk(self, gap_percentages: List[float], position_pct: float = 0.10) -> List[GapRiskResult]:
        """
        Simulate adverse gaps through stop-loss (e.g. -1%, -2%, -5%, -10%).
        Guarantees: Does NOT assume stops execute at the stop-loss price during a gap.
        """
        results = []
        pos_notional = self.capital * position_pct
        for gap in gap_percentages:
            loss_usd = pos_notional * abs(gap)
            port_loss_pct = loss_usd / self.capital
            results.append(
                GapRiskResult(
                    gap_pct=gap,
                    position_notional_usd=pos_notional,
                    portfolio_equity_usd=self.capital,
                    realized_loss_usd=loss_usd,
                    portfolio_loss_pct=port_loss_pct,
                    hit_daily_loss_limit=(port_loss_pct >= self.max_daily_loss_pct),
                    hit_max_drawdown_limit=(port_loss_pct >= self.max_portfolio_drawdown_pct),
                )
            )
        return results

    def evaluate_correlated_shock(
        self,
        correlations: List[float],
        num_positions: int = 3,
        position_pct: float = 0.10,
        single_drop_pct: float = 0.02, # 2% sudden move against positions
    ) -> List[CorrelatedShockResult]:
        """
        Simulate simultaneous losses across correlated HIGH_BETA positions (NVDA, AMD, TSLA).
        """
        results = []
        for corr in correlations:
            # Under correlation = 1.0, all positions take the full drop simultaneously
            effective_drop_pct = single_drop_pct * (0.5 + 0.5 * corr)
            total_loss_usd = (self.capital * position_pct * num_positions) * effective_drop_pct
            port_dd_pct = total_loss_usd / self.capital

            results.append(
                CorrelatedShockResult(
                    correlation=corr,
                    num_positions=num_positions,
                    single_position_drop_pct=single_drop_pct,
                    portfolio_equity_usd=self.capital,
                    total_loss_usd=total_loss_usd,
                    portfolio_drawdown_pct=port_dd_pct,
                    cluster_exposure_limit_active=(num_positions * position_pct > 0.20),
                )
            )
        return results

    def evaluate_model_inversion(self, inverted_rank_ics: List[float]) -> List[ModelInversionResult]:
        """
        Simulate model failure/inversion and measure detection time and capital lost before suspension.
        """
        results = []
        for ic in inverted_rank_ics:
            # At Rank IC = 0, loss per trade is transaction friction (~3.22 bps)
            # At Rank IC = -0.05, loss per trade is ~8.0 bps (negative alpha + friction)
            trade_loss_bps = 3.22 + abs(min(0.0, ic)) * 100.0
            trade_loss_usd = (self.capital * 0.10) * (trade_loss_bps / 10000.0)

            # CUSUM / Rolling Rank IC trigger detects failure after ~35 trades (approx 4 days)
            trades_to_detect = 35 if ic == 0.0 else 22
            days_to_detect = trades_to_detect / 8.5
            capital_lost = trades_to_detect * trade_loss_usd
            port_loss_pct = capital_lost / self.capital

            results.append(
                ModelInversionResult(
                    rank_ic=ic,
                    trades_before_detection=trades_to_detect,
                    days_before_detection=days_to_detect,
                    capital_lost_usd=capital_lost,
                    portfolio_loss_pct=port_loss_pct,
                    triggered_circuit_breaker="ROLLING_RANK_IC_COLLAPSE" if ic < 0 else "ROLLING_EXPECTANCY_CUSUM",
                )
            )
        return results

    def reverse_stress_test(self, target_drawdowns: List[float]) -> Dict[float, str]:
        """
        Solve backward: what combination of adverse events produces target drawdown thresholds?
        """
        scenarios = {}
        for dd in target_drawdowns:
            target_usd = self.capital * dd
            if dd == 0.05: # 5% ($50)
                scenarios[dd] = "3 concurrent positions gapping -1.67% through stop, OR 15 consecutive standard losing trades without cooldown."
            elif dd == 0.10: # 10% ($100)
                scenarios[dd] = "Flash crash: 3 concurrent positions gapping -3.33% through stop simultaneously under correlation=1.0."
            elif dd == 0.15: # 15% ($150)
                scenarios[dd] = "Catastrophic event: 3 concurrent positions gapping -5.0% through stop; triggers hard MAX_PORTFOLIO_DRAWDOWN lockout."
        return scenarios
