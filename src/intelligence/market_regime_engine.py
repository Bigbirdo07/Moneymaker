"""
Deterministic Market Regime Classifier (Phase E).

Evaluates premarket index momentum, breadth, realized volatility,
cross-sectional dispersion, and overnight gap behavior.
"""

from typing import Dict, Any, Optional
import numpy as np

from src.intelligence.morning_market_state import MarketRegime, MarketBreadthSnapshot, DispersionState


class MarketRegimeEngine:
    """
    Deterministic regime classifier for the morning intelligence briefing.
    """
    def __init__(
        self,
        bullish_breadth_threshold: float = 60.0,
        bearish_breadth_threshold: float = 40.0,
        high_vol_shock_threshold_bps: float = 220.0,
        low_vol_chop_threshold_bps: float = 60.0,
    ):
        self.bullish_breadth_threshold = bullish_breadth_threshold
        self.bearish_breadth_threshold = bearish_breadth_threshold
        self.high_vol_shock_threshold_bps = high_vol_shock_threshold_bps
        self.low_vol_chop_threshold_bps = low_vol_chop_threshold_bps

    def classify_regime(
        self,
        spy_premarket_return_pct: float,
        spy_overnight_return_pct: float,
        breadth: MarketBreadthSnapshot,
        market_realized_vol_bps: float = 90.0,
    ) -> MarketRegime:
        """
        Maps premarket index, breadth, and volatility metrics to deterministic MarketRegime.
        """
        # 1. High Volatility Shock Check
        if market_realized_vol_bps >= self.high_vol_shock_threshold_bps or breadth.dispersion_state == DispersionState.EXTREME:
            return MarketRegime.HIGH_VOL_SHOCK

        # 2. Bullish Continuation
        # Positive SPY premarket + broad participation (>60% above VWAP / positive)
        if spy_premarket_return_pct >= 0.15 and breadth.pct_above_vwap >= self.bullish_breadth_threshold:
            return MarketRegime.BULLISH_CONTINUATION

        # 3. Bearish Continuation
        # Negative SPY premarket + weak breadth (<40% positive)
        if spy_premarket_return_pct <= -0.15 and breadth.pct_above_vwap <= self.bearish_breadth_threshold:
            return MarketRegime.BEARISH_CONTINUATION

        # 4. Low Volatility Chop
        if market_realized_vol_bps <= self.low_vol_chop_threshold_bps and abs(spy_premarket_return_pct) < 0.10:
            return MarketRegime.LOW_VOL_CHOP

        # 5. Mean Reversion / Dispersion Setup
        if (spy_premarket_return_pct >= 0.20 and breadth.pct_above_vwap < 45.0) or \
           (spy_premarket_return_pct <= -0.20 and breadth.pct_above_vwap > 55.0):
            return MarketRegime.MEAN_REVERSION

        # Default fallback
        return MarketRegime.REGIME_UNCERTAIN
