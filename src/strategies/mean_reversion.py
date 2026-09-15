"""Baseline mean reversion strategy for intraday 5-minute bars."""

from __future__ import annotations

from typing import List
import pandas as pd

from src.core.types import Signal, SignalDirection
from src.strategies.base import BaseStrategy


class BaselineMeanReversionStrategy(BaseStrategy):
    """
    Systematic statistical mean-reversion baseline strategy.

    Entry Conditions:
    1. Bollinger Band % <= 0.15 (price extended near or below lower band)
    2. RSI (14) < 35.0 (short-term oversold)
    3. Volume Z-Score > 0.5 (exhaustion volume present)
    """

    def __init__(
        self,
        name: str = "baseline_mean_reversion",
        version: str = "v1.0",
        max_bb_pct: float = 0.15,
        max_rsi: float = 35.0,
        expected_holding_bars: int = 12,  # 60 minutes
        stop_loss_pct: float = 0.006,     # 0.60%
        take_profit_pct: float = 0.008,   # 0.80% (reversion to mean)
    ) -> None:
        super().__init__(name=name, version=version)
        self.max_bb_pct = max_bb_pct
        self.max_rsi = max_rsi
        self.expected_holding_bars = expected_holding_bars
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def generate_signals(self, features_df: pd.DataFrame) -> List[Signal]:
        signals: List[Signal] = []
        for _, row in features_df.iterrows():
            symbol = str(row["symbol"])
            ts = row["timestamp"]

            bb_pct = row.get("feature_bb_pct", 0.5)
            rsi = row.get("feature_rsi_14", 50.0)
            vol_z = row.get("feature_volume_zscore_20b", 0.0)
            dist_sma = row.get("feature_dist_sma_20", 0.0)

            is_oversold_band = bb_pct <= self.max_bb_pct
            is_oversold_rsi = rsi <= self.max_rsi
            is_extended_below_sma = dist_sma < -0.003

            if is_oversold_band and is_oversold_rsi and is_extended_below_sma:
                direction = SignalDirection.BUY
                strength = min(1.0, max(0.5, float((35.0 - rsi) / 20.0 + 0.5)))
                expected_return = max(0.004, abs(float(dist_sma * 0.8)))
                confidence = min(0.80, 0.55 + (35.0 - rsi) / 100.0)
            else:
                direction = SignalDirection.NO_TRADE
                strength = 0.0
                expected_return = 0.0
                confidence = 0.50

            signals.append(
                Signal(
                    symbol=symbol,
                    timestamp=ts,
                    direction=direction,
                    signal_strength=strength,
                    expected_return=expected_return,
                    confidence=confidence,
                    expected_holding_period=self.expected_holding_bars,
                    model_version=f"{self.name}_{self.version}",
                    metadata={
                        "bb_pct": bb_pct,
                        "rsi": rsi,
                        "dist_sma_20": dist_sma,
                        "stop_loss_pct": self.stop_loss_pct,
                        "take_profit_pct": self.take_profit_pct,
                    },
                )
            )
        return signals
