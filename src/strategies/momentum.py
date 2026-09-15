"""Baseline momentum strategy for intraday 5-minute bars."""

from __future__ import annotations

from typing import List
import pandas as pd

from src.core.types import Signal, SignalDirection
from src.strategies.base import BaseStrategy


class BaselineMomentumStrategy(BaseStrategy):
    """
    Systematic trend & momentum baseline strategy.
    
    Entry Conditions:
    1. Short EMA (9) > Long EMA (21)
    2. RSI (14) between 52 and 68 (momentum expansion without extreme overbought)
    3. Relative Volume (20) > 1.10 (volume expansion)
    4. Price > VWAP (or VWAP deviation > 0)
    """

    def __init__(
        self,
        name: str = "baseline_momentum",
        version: str = "v1.0",
        min_rsi: float = 52.0,
        max_rsi: float = 68.0,
        min_rvol: float = 1.10,
        expected_holding_bars: int = 12,  # 60 minutes
        stop_loss_pct: float = 0.005,     # 0.50%
        take_profit_pct: float = 0.010,   # 1.00%
    ) -> None:
        super().__init__(name=name, version=version)
        self.min_rsi = min_rsi
        self.max_rsi = max_rsi
        self.min_rvol = min_rvol
        self.expected_holding_bars = expected_holding_bars
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct

    def generate_signals(self, features_df: pd.DataFrame) -> List[Signal]:
        signals: List[Signal] = []
        for _, row in features_df.iterrows():
            symbol = str(row["symbol"])
            ts = row["timestamp"]

            # Feature lookups with safe fallbacks
            rsi = row.get("feature_rsi_14", 50.0)
            ema_cross = row.get("feature_ema_cross_9_21", 0.0)
            rvol = row.get("feature_relative_volume_20b", 1.0)
            vwap_dev = row.get("feature_vwap_deviation", 0.0)
            return_1b = row.get("feature_return_1b", 0.0)

            # Signal logic
            is_bullish_trend = ema_cross > 0.0005
            is_healthy_momentum = self.min_rsi <= rsi <= self.max_rsi
            is_volume_confirmed = rvol >= self.min_rvol
            is_above_vwap = vwap_dev >= 0.0

            if is_bullish_trend and is_healthy_momentum and is_volume_confirmed and is_above_vwap:
                direction = SignalDirection.BUY
                strength = min(1.0, max(0.5, float(rvol / 2.0)))
                expected_return = max(0.003, float(ema_cross * 2.0 + 0.004))
                confidence = min(0.85, 0.55 + (rsi - 50.0) / 100.0)
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
                        "rsi": rsi,
                        "ema_cross": ema_cross,
                        "rvol": rvol,
                        "stop_loss_pct": self.stop_loss_pct,
                        "take_profit_pct": self.take_profit_pct,
                    },
                )
            )
        return signals
