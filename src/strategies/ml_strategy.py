"""ML-driven systematic strategy with economic threshold filtering and friction awareness."""

from __future__ import annotations

from typing import List, Optional
import numpy as np
import pandas as pd

from src.core.types import Signal, SignalDirection
from src.models.base import BaseMLModel
from src.models.calibration import ProbabilityCalibrator
from src.strategies.base import BaseStrategy


class MLSignalStrategy(BaseStrategy):
    """
    Translates statistical machine-learning predictions into actionable trading signals
    with strict confidence and economic friction filters.
    """

    def __init__(
        self,
        model: BaseMLModel,
        calibrator: Optional[ProbabilityCalibrator] = None,
        min_confidence: float = 0.55,           # 55% min calibrated probability threshold
        min_expected_return_bps: float = 15.0,  # 0.15% min edge before costs
        stop_loss_pct: float = 0.005,           # 0.50%
        take_profit_pct: float = 0.010,         # 1.00%
        expected_holding_bars: int = 12,        # 60 minutes
        name: str = "ml_signal_strategy",
        version: str = "v1.0",
    ) -> None:
        super().__init__(name=name, version=version)
        self.model = model
        self.calibrator = calibrator
        self.min_confidence = min_confidence
        self.min_expected_return_bps = min_expected_return_bps
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.expected_holding_bars = expected_holding_bars

    def generate_signals(self, features_df: pd.DataFrame) -> List[Signal]:
        if features_df.empty:
            return []

        # Extract only permissible feature columns (prevent passing targets or raw metadata)
        feature_cols = [c for c in features_df.columns if c.startswith("feature_")]
        X_features = features_df[feature_cols].copy()

        # Predict probabilities
        if self.calibrator is not None:
            probs = self.calibrator.predict_proba(self.model, X_features)
        else:
            probs = self.model.predict_proba(X_features)

        p_up = probs[:, 1] if probs.ndim > 1 and probs.shape[1] > 1 else probs.flatten()

        signals: List[Signal] = []
        for idx, (_, row) in enumerate(features_df.iterrows()):
            symbol = str(row["symbol"])
            ts = row["timestamp"]
            prob = float(p_up[idx])

            # Edge estimation based on probability skew
            # e.g. prob = 0.60 -> expected movement = (0.60 - 0.50) * 2 * target_reward
            edge_bps = max(0.0, (prob - 0.50) * 10000.0 * 0.02)
            exp_ret = edge_bps / 10000.0

            if prob >= self.min_confidence and edge_bps >= self.min_expected_return_bps:
                direction = SignalDirection.BUY
                strength = min(1.0, max(0.1, (prob - 0.50) * 2.0))
            else:
                direction = SignalDirection.NO_TRADE
                strength = 0.0
                exp_ret = 0.0

            signals.append(
                Signal(
                    symbol=symbol,
                    timestamp=ts,
                    direction=direction,
                    signal_strength=strength,
                    expected_return=exp_ret,
                    confidence=prob,
                    expected_holding_period=self.expected_holding_bars,
                    model_version=f"{self.model.model_id}_{self.version}",
                    metadata={
                        "p_up": prob,
                        "min_confidence": self.min_confidence,
                        "stop_loss_pct": self.stop_loss_pct,
                        "take_profit_pct": self.take_profit_pct,
                    },
                )
            )
        return signals
