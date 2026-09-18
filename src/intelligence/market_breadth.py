"""
Market Breadth & Cross-Sectional Dispersion Engine (Phase E).

Computes percentage of universe above VWAP, premarket advancers/decliners,
and cross-sectional return dispersion.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd

from src.intelligence.morning_market_state import MarketBreadthSnapshot, DispersionState


class MarketBreadthEngine:
    """
    Computes breadth and dispersion snapshots from contemporaneous premarket quotes.
    """
    def __init__(
        self,
        low_dispersion_threshold_bps: float = 40.0,
        high_dispersion_threshold_bps: float = 120.0,
        extreme_dispersion_threshold_bps: float = 250.0,
    ):
        self.low_dispersion_threshold_bps = low_dispersion_threshold_bps
        self.high_dispersion_threshold_bps = high_dispersion_threshold_bps
        self.extreme_dispersion_threshold_bps = extreme_dispersion_threshold_bps

    def compute_breadth(
        self,
        symbol_returns_pct: Dict[str, float],
        symbol_vwap_distances_pct: Dict[str, float],
    ) -> MarketBreadthSnapshot:
        """
        Evaluates point-in-time universe breadth metrics.
        """
        if not symbol_returns_pct:
            return MarketBreadthSnapshot(
                pct_above_vwap=50.0,
                pct_positive_premarket=50.0,
                cross_sectional_dispersion_bps=80.0,
                dispersion_state=DispersionState.NORMAL,
                advancers_count=0,
                decliners_count=0,
                total_evaluated=0,
            )

        returns = list(symbol_returns_pct.values())
        vwap_dists = list(symbol_vwap_distances_pct.values()) if symbol_vwap_distances_pct else returns

        n = len(returns)
        advancers = sum(1 for r in returns if r > 0.0)
        decliners = sum(1 for r in returns if r < 0.0)
        above_vwap = sum(1 for v in vwap_dists if v > 0.0)

        pct_pos = (advancers / n) * 100.0 if n > 0 else 50.0
        pct_vwap = (above_vwap / len(vwap_dists)) * 100.0 if vwap_dists else 50.0

        # Cross-sectional standard deviation in bps
        std_ret = float(np.std(returns)) * 100.0  # 1% = 100 bps
        disp_bps = max(10.0, std_ret)

        if disp_bps < self.low_dispersion_threshold_bps:
            disp_state = DispersionState.LOW
        elif disp_bps < self.high_dispersion_threshold_bps:
            disp_state = DispersionState.NORMAL
        elif disp_bps < self.extreme_dispersion_threshold_bps:
            disp_state = DispersionState.HIGH
        else:
            disp_state = DispersionState.EXTREME

        return MarketBreadthSnapshot(
            pct_above_vwap=pct_vwap,
            pct_positive_premarket=pct_pos,
            cross_sectional_dispersion_bps=disp_bps,
            dispersion_state=disp_state,
            advancers_count=advancers,
            decliners_count=decliners,
            total_evaluated=n,
        )
