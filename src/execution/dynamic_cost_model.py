"""
Dynamic Transaction Cost Model & Spread Estimation Engine (Phase B).
Computes symbol-specific, time-of-day-aware, and liquidity-adjusted execution costs
(spread, slippage, commission, market impact) for accurate net edge hurdles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class CostBreakdown:
    """Detailed components of expected round-trip execution friction."""
    symbol: str
    price: float
    shares: int
    half_spread_bps: float
    half_slippage_bps: float
    commission_bps: float
    market_impact_bps: float
    total_one_way_bps: float
    total_round_trip_bps: float
    total_round_trip_dollars: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "price": round(self.price, 2),
            "shares": self.shares,
            "half_spread_bps": round(self.half_spread_bps, 2),
            "half_slippage_bps": round(self.half_slippage_bps, 2),
            "commission_bps": round(self.commission_bps, 2),
            "market_impact_bps": round(self.market_impact_bps, 2),
            "total_one_way_bps": round(self.total_one_way_bps, 2),
            "total_round_trip_bps": round(self.total_round_trip_bps, 2),
            "total_round_trip_dollars": round(self.total_round_trip_dollars, 2),
        }


class ExpectedExecutionCost:
    """
    Dynamic execution cost estimator for point-in-time candidate evaluation.
    """

    def __init__(
        self,
        base_spread_bps: float = 2.5,
        base_slippage_bps: float = 2.0,
        per_share_commission: float = 0.005,
    ) -> None:
        self.base_spread_bps = base_spread_bps
        self.base_slippage_bps = base_slippage_bps
        self.per_share_commission = per_share_commission

    @staticmethod
    def get_time_of_day_multiplier(time_str: str) -> float:
        """
        Microstructure spread multiplier based on intraday U-curve:
        09:30-10:00: High volatility & wider spreads (1.3x)
        10:00-11:30: Prime liquid momentum window (1.0x)
        11:30-14:00: Lunchtime lulls, lower volume (1.1x)
        14:00-15:45: Afternoon institutional volume (1.0x)
        15:45-16:00: MOC imbalance spikes (1.2x)
        """
        if time_str < "10:00:00":
            return 1.30
        elif time_str <= "11:30:00":
            return 1.00
        elif time_str <= "14:00:00":
            return 1.10
        elif time_str <= "15:45:00":
            return 1.00
        else:
            return 1.25

    def compute_cost(
        self,
        symbol: str,
        price: float,
        shares: int,
        median_dollar_volume_30d: float = 100_000_000.0,
        realized_volatility_bps: float = 25.0,
        time_str: str = "10:00:00",
        cost_multiplier: float = 1.0,
    ) -> CostBreakdown:
        """Computes granular round-trip execution cost breakdown."""
        if price <= 0 or shares <= 0:
            return CostBreakdown(
                symbol=symbol, price=max(1.0, price), shares=max(1, shares),
                half_spread_bps=5.0, half_slippage_bps=5.0, commission_bps=1.0,
                market_impact_bps=0.0, total_one_way_bps=11.0,
                total_round_trip_bps=22.0, total_round_trip_dollars=1.0
            )

        tod_mult = self.get_time_of_day_multiplier(time_str)

        # Microstructure half-spread
        penny_spread_bps = (0.01 / price) * 10000.0 / 2.0
        liquidity_factor = max(0.5, 4.0 / np.sqrt(max(1.0, median_dollar_volume_30d / 1_000_000.0)))
        vol_factor = 1.0 + (realized_volatility_bps / 100.0)
        
        half_spread_bps = max(penny_spread_bps, liquidity_factor * vol_factor * tod_mult) * cost_multiplier
        half_slippage_bps = (self.base_slippage_bps * vol_factor * tod_mult) * cost_multiplier

        # Commission in bps
        trade_dollars = price * shares
        one_way_comm = shares * self.per_share_commission * cost_multiplier
        commission_bps = (one_way_comm / trade_dollars) * 10000.0

        # Market impact (Almgren-Chriss square-root proxy)
        participation_rate = trade_dollars / max(100_000.0, median_dollar_volume_30d / 390.0)  # fraction of 1-min volume
        market_impact_bps = 5.0 * np.sqrt(max(0.0001, participation_rate)) * cost_multiplier

        total_one_way = half_spread_bps + half_slippage_bps + commission_bps + market_impact_bps
        total_round_trip_bps = total_one_way * 2.0
        total_round_trip_dollars = (total_round_trip_bps / 10000.0) * trade_dollars

        return CostBreakdown(
            symbol=symbol,
            price=price,
            shares=shares,
            half_spread_bps=half_spread_bps,
            half_slippage_bps=half_slippage_bps,
            commission_bps=commission_bps,
            market_impact_bps=market_impact_bps,
            total_one_way_bps=total_one_way,
            total_round_trip_bps=total_round_trip_bps,
            total_round_trip_dollars=total_round_trip_dollars,
        )
