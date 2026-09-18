"""
Multi-Horizon Return Forecasting Engine for Autonomous Intraday Trading.
Forecasts future returns across 5m, 15m, 30m, 60m, and EOD horizons.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass

logger = get_logger("models.multi_horizon_forecaster")


@dataclass
class HorizonForecast:
    """Forecast prediction for a single future horizon."""
    horizon_minutes: int
    expected_return_bps: float
    probability_positive: float
    estimated_friction_bps: float
    expected_net_return_bps: float
    confidence: float


@dataclass
class MultiHorizonPrediction:
    """Consolidated multi-horizon prediction bundle at timestamp T."""
    symbol: str
    timestamp: str
    forecast_5m: HorizonForecast
    forecast_15m: HorizonForecast
    forecast_30m: HorizonForecast
    forecast_60m: HorizonForecast
    forecast_eod: HorizonForecast
    optimal_target_horizon_min: int
    composite_net_edge_bps: float
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "forecast_5m": asdict(self.forecast_5m),
            "forecast_15m": asdict(self.forecast_15m),
            "forecast_30m": asdict(self.forecast_30m),
            "forecast_60m": asdict(self.forecast_60m),
            "forecast_eod": asdict(self.forecast_eod),
            "optimal_target_horizon_min": self.optimal_target_horizon_min,
            "composite_net_edge_bps": self.composite_net_edge_bps,
            "evidence_class": self.evidence_class,
        }


class MultiHorizonForecaster:
    """
    Predicts forward returns and directional probabilities across multiple intraday horizons
    using statistical micro-models and technical/alpha features.
    """

    HORIZONS = [5, 15, 30, 60, 390]

    def __init__(
        self,
        base_friction_bps: float = 6.0,
    ) -> None:
        self.base_friction_bps = base_friction_bps

    def predict(
        self,
        symbol: str,
        timestamp: datetime | str,
        visible_df: pd.DataFrame,
        spread_bps: Optional[float] = None,
    ) -> MultiHorizonPrediction:
        """
        Generates multi-horizon return and probability forecasts using only visible data.
        """
        if len(visible_df) < 5:
            # Fallback zero forecast if insufficient history
            zero_f = HorizonForecast(5, 0.0, 0.50, self.base_friction_bps, -self.base_friction_bps, 0.1)
            return MultiHorizonPrediction(
                symbol=symbol,
                timestamp=str(timestamp),
                forecast_5m=zero_f,
                forecast_15m=zero_f,
                forecast_30m=zero_f,
                forecast_60m=zero_f,
                forecast_eod=zero_f,
                optimal_target_horizon_min=15,
                composite_net_edge_bps=-self.base_friction_bps,
            )

        close = visible_df["close"].values
        vol = visible_df["volume"].values
        curr_price = float(close[-1])

        # Feature signals
        ret_5 = float((close[-1] - close[-min(5, len(close))]) / close[-min(5, len(close))])
        ret_15 = float((close[-1] - close[-min(15, len(close))]) / close[-min(15, len(close))])
        ret_30 = float((close[-1] - close[-min(30, len(close))]) / close[-min(30, len(close))])

        # EMA trend proxy (in bps)
        ema_short = pd.Series(close).ewm(span=10).mean().iloc[-1]
        ema_long = pd.Series(close).ewm(span=30).mean().iloc[-1]
        trend_bps = float((ema_short - ema_long) / curr_price) * 10000.0

        # Mean reversion proxy (in bps)
        diffs = np.diff(close[-15:]) if len(close) >= 15 else np.diff(close)
        gains = diffs[diffs > 0].sum() if len(diffs[diffs > 0]) > 0 else 1e-6
        losses = -diffs[diffs < 0].sum() if len(diffs[diffs < 0]) > 0 else 1e-6
        rs = gains / losses
        rsi = 100.0 - (100.0 / (1.0 + rs))
        reversion_bps = float((50.0 - rsi) / 50.0) * 20.0

        # Microstructure friction
        if spread_bps is None:
            spread_bps = 2.5
        round_trip_cost = (spread_bps * 2.0) + 1.5

        forecasts: Dict[int, HorizonForecast] = {}
        horizon_weights = {5: (0.7, 0.3), 15: (0.5, 0.5), 30: (0.4, 0.6), 60: (0.3, 0.7), 390: (0.2, 0.8)}

        for h in self.HORIZONS:
            w_rev, w_trend = horizon_weights[h]
            time_scale = np.sqrt(min(h, 60) / 15.0)
            raw_alpha = (w_rev * reversion_bps + w_trend * trend_bps) * 1.5 * time_scale

            exp_ret_bps = float(np.clip(raw_alpha, -80.0, 80.0))
            p_up = float(1.0 / (1.0 + np.exp(-exp_ret_bps / 15.0)))
            net_ret_bps = exp_ret_bps - round_trip_cost
            conf = float(np.clip(abs(p_up - 0.50) * 2.0, 0.10, 0.95))

            forecasts[h] = HorizonForecast(
                horizon_minutes=h,
                expected_return_bps=round(exp_ret_bps, 2),
                probability_positive=round(p_up, 4),
                estimated_friction_bps=round(round_trip_cost, 2),
                expected_net_return_bps=round(net_ret_bps, 2),
                confidence=round(conf, 3),
            )

        # Identify optimal horizon
        best_h = max([5, 15, 30, 60], key=lambda x: forecasts[x].expected_net_return_bps)
        composite_net = forecasts[best_h].expected_net_return_bps

        return MultiHorizonPrediction(
            symbol=symbol,
            timestamp=str(timestamp),
            forecast_5m=forecasts[5],
            forecast_15m=forecasts[15],
            forecast_30m=forecasts[30],
            forecast_60m=forecasts[60],
            forecast_eod=forecasts[390],
            optimal_target_horizon_min=best_h,
            composite_net_edge_bps=composite_net,
        )
