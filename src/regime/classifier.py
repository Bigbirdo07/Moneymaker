"""Interpretable rule-based market regime classifier."""

from __future__ import annotations

from typing import Optional
import numpy as np
import pandas as pd

from src.core.types import MarketRegime


class MarketRegimeClassifier:
    """
    Classifies market regime strictly using historical and current market/benchmark metrics.
    No forward-looking indicators are permitted.
    """

    def __init__(
        self,
        vol_threshold_pct: float = 0.18,      # 18% annualized volatility threshold
        trend_threshold_bps: float = 5.0,     # 5 bps EMA spread threshold
    ) -> None:
        self.vol_threshold_pct = vol_threshold_pct
        self.trend_threshold_bps = trend_threshold_bps

    def classify_bar(self, row: pd.Series) -> MarketRegime:
        """Classifies a single market bar row into a MarketRegime."""
        # Check if benchmark or asset trend/volatility metrics exist
        ema_cross = row.get("feature_ema_cross_9_21", 0.0)
        realized_vol = row.get("feature_realized_vol_20b", 0.0)
        dist_sma = row.get("feature_dist_sma_20", 0.0)

        # Approximate annualized vol from 5-min realized vol (sqrt(252 * 78))
        ann_vol = realized_vol * np.sqrt(252.0 * 78.0) if not pd.isna(realized_vol) else 0.15

        if pd.isna(ema_cross) or pd.isna(ann_vol):
            return MarketRegime.UNKNOWN

        is_high_vol = ann_vol > self.vol_threshold_pct
        trend_bps = (ema_cross * 10000.0)

        if trend_bps > self.trend_threshold_bps:
            return MarketRegime.BULL_HIGH_VOL if is_high_vol else MarketRegime.BULL_LOW_VOL
        elif trend_bps < -self.trend_threshold_bps:
            return MarketRegime.BEAR_HIGH_VOL if is_high_vol else MarketRegime.BEAR_LOW_VOL
        else:
            return MarketRegime.SIDEWAYS

    def classify_dataframe(self, df: pd.DataFrame) -> pd.Series:
        """Classifies an entire features dataframe into a series of MarketRegime strings."""
        regimes = [self.classify_bar(row).value for _, row in df.iterrows()]
        return pd.Series(regimes, index=df.index, name="regime")
