"""
Capital Scale & Nonlinear Market Impact Engine for Phase 4.
Evaluates strategy capacity, participation rates, and square-root market impact across portfolio sizes.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


@dataclass
class CapitalScaleResult:
    portfolio_capital_usd: float
    position_notional_usd: float
    avg_shares_nvda: float
    avg_participation_rate_pct: float
    base_spread_bps: float
    nonlinear_impact_bps: float
    total_roundtrip_friction_bps: float
    gross_expectancy_bps: float
    net_expectancy_bps: float
    annualized_net_pnl_usd: float
    annualized_sharpe: float
    capacity_status: str  # "OPTIMAL", "VIABLE", "CAPACITY_CONSTRAINED", "UNPROFITABLE"


class CapacityEngine:
    """Simulates capital scaling under conservative nonlinear square-root market impact."""

    def __init__(
        self,
        gamma_impact_coeff: float = 0.10,
        gross_alpha_bps: float = 4.80,
        base_spread_bps: float = 2.00,
        base_slippage_bps: float = 0.50,
        trades_per_day: float = 8.5,
        annual_trading_days: int = 252,
    ):
        self.gamma = gamma_impact_coeff
        self.gross_alpha_bps = gross_alpha_bps
        self.base_spread_bps = base_spread_bps
        self.base_slippage_bps = base_slippage_bps
        self.trades_per_day = trades_per_day
        self.annual_trading_days = annual_trading_days

    def evaluate_scale(
        self,
        capital_levels: List[float],
        symbol_price: float = 120.0,
        avg_5m_bar_volume: float = 250000.0,
        avg_5m_volatility_bps: float = 25.0,
    ) -> List[CapitalScaleResult]:
        """
        Evaluate performance across capital tiers.
        """
        results = []
        for cap in capital_levels:
            pos_notional = cap * 0.10  # 10% position allocation
            shares = pos_notional / symbol_price
            participation_rate = (shares / avg_5m_bar_volume) * 100.0

            # Square-Root Market Impact Model: I = gamma * sigma * sqrt(Q / V)
            impact_fraction = np.sqrt(shares / avg_5m_bar_volume) if avg_5m_bar_volume > 0 else 0.0
            nonlinear_impact_bps = self.gamma * avg_5m_volatility_bps * impact_fraction

            # Round-trip friction = 2 * (half-spread + slippage + impact) + commission
            roundtrip_friction = self.base_spread_bps + (2.0 * self.base_slippage_bps) + (2.0 * nonlinear_impact_bps) + 0.20
            net_expectancy = self.gross_alpha_bps - roundtrip_friction

            total_annual_trades = self.trades_per_day * self.annual_trading_days
            annual_volume = total_annual_trades * pos_notional
            annual_net_pnl = annual_volume * (net_expectancy / 10000.0)

            # Estimate Sharpe decay with net expectancy
            base_sharpe = 1.60
            sharpe = max(0.0, base_sharpe * (net_expectancy / 1.58)) if net_expectancy > 0 else 0.0

            if net_expectancy >= 1.0:
                status = "OPTIMAL"
            elif net_expectancy >= 0.5:
                status = "VIABLE"
            elif net_expectancy > 0.0:
                status = "CAPACITY_CONSTRAINED"
            else:
                status = "UNPROFITABLE"

            results.append(
                CapitalScaleResult(
                    portfolio_capital_usd=cap,
                    position_notional_usd=pos_notional,
                    avg_shares_nvda=shares,
                    avg_participation_rate_pct=participation_rate,
                    base_spread_bps=self.base_spread_bps,
                    nonlinear_impact_bps=nonlinear_impact_bps,
                    total_roundtrip_friction_bps=roundtrip_friction,
                    gross_expectancy_bps=self.gross_alpha_bps,
                    net_expectancy_bps=net_expectancy,
                    annualized_net_pnl_usd=annual_net_pnl,
                    annualized_sharpe=sharpe,
                    capacity_status=status,
                )
            )

        return results
