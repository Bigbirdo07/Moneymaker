"""
Real-Market Multi-Horizon Forecaster V2 for Phase 10.4.
Trained and calibrated on real historical Alpaca/IEX data.
Predicts expected net executable return and calibrated probability across 15m, 30m, and 60m horizons.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression
from sklearn.preprocessing import RobustScaler

from src.core.logging import get_logger
from src.core.types import EvidenceClass

logger = get_logger("models.real_forecaster_v2")


@dataclass
class HorizonForecastV2:
    """Detailed forecast artifact for a single target horizon."""
    horizon_minutes: int
    expected_net_return_bps: float
    probability_positive: float
    calibrated_probability: float
    confidence_score: float
    model_agreement_score: float


@dataclass
class MultiHorizonPredictionV2:
    """Consolidated multi-horizon prediction bundle for a symbol at timestamp T."""
    symbol: str
    timestamp: str
    forecast_15m: HorizonForecastV2
    forecast_30m: HorizonForecastV2
    forecast_60m: HorizonForecastV2
    optimal_target_horizon_min: int
    best_expected_net_edge_bps: float
    best_calibrated_prob: float
    evidence_class: str = EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "forecast_15m": asdict(self.forecast_15m),
            "forecast_30m": asdict(self.forecast_30m),
            "forecast_60m": asdict(self.forecast_60m),
            "optimal_target_horizon_min": self.optimal_target_horizon_min,
            "best_expected_net_edge_bps": self.best_expected_net_edge_bps,
            "best_calibrated_prob": self.best_calibrated_prob,
            "evidence_class": self.evidence_class,
        }


class RealMarketMultiHorizonForecasterV2:
    """
    Multi-horizon ensemble forecaster calibrated specifically for real market microstructure.
    """

    HORIZONS = [15, 30, 60]

    FEATURE_COLS = [
        "ret_1m_bps", "ret_3m_bps", "ret_5m_bps", "ret_10m_bps", "ret_15m_bps", "ret_30m_bps", "ret_60m_bps",
        "ema_trend_10_30_bps", "dist_from_vwap_bps", "dist_from_high_bps", "dist_from_low_bps", "breakout_distance_bps", "rsi_14",
        "realized_vol_15m_bps", "realized_vol_60m_bps", "atr_14_bps", "range_expansion_ratio",
        "relative_volume", "volume_acceleration", "trade_intensity",
        "overnight_gap_bps", "premarket_return_bps", "premarket_volume_ratio", "premarket_coverage_pct", "is_premarket_missing",
        "cs_ret_15m_rank", "cs_ret_60m_rank", "cs_volume_rank",
        "minutes_since_open", "minutes_to_close",
    ]

    def __init__(self) -> None:
        self.regressors: Dict[int, HistGradientBoostingRegressor] = {}
        self.classifiers: Dict[int, HistGradientBoostingClassifier] = {}
        self.calibrators: Dict[int, IsotonicRegression] = {}
        self._is_trained: bool = False

    def train(self, train_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains multi-horizon regressors and calibrated probability classifiers.
        """
        logger.info("Training RealMarketMultiHorizonForecasterV2 on %d real observations...", len(train_df))
        results = {}

        for h in self.HORIZONS:
            sub = train_df.dropna(subset=[f"fwd_net_{h}m_bps", f"label_binary_net_{h}m"])
            if len(sub) < 100:
                continue

            X = sub[self.FEATURE_COLS].fillna(0.0).values
            y_reg = sub[f"fwd_net_{h}m_bps"].values
            y_clf = sub[f"label_binary_net_{h}m"].values

            reg = HistGradientBoostingRegressor(max_iter=150, max_depth=5, learning_rate=0.05, random_state=42)
            reg.fit(X, y_reg)
            self.regressors[h] = reg

            clf = HistGradientBoostingClassifier(max_iter=150, max_depth=5, learning_rate=0.05, random_state=42)
            clf.fit(X, y_clf)
            self.classifiers[h] = clf

            # Isotonic probability calibration
            raw_probs = clf.predict_proba(X)[:, 1]
            iso = IsotonicRegression(out_of_bounds="clip")
            iso.fit(raw_probs, y_clf)
            self.calibrators[h] = iso

            results[h] = {"samples": len(sub), "status": "TRAINED"}

        self._is_trained = True
        return results

    def predict(
        self,
        symbol: str,
        timestamp: str,
        feature_vector: Dict[str, Any],
    ) -> MultiHorizonPredictionV2:
        """
        Predicts across all horizons for a single candidate feature vector.
        """
        if not self._is_trained:
            raise RuntimeError("Forecaster V2 must be trained before predicting.")

        row_vals = [feature_vector.get(c, 0.0) for c in self.FEATURE_COLS]
        X = np.array(row_vals).reshape(1, -1)

        forecasts: Dict[int, HorizonForecastV2] = {}

        for h in self.HORIZONS:
            exp_net = float(self.regressors[h].predict(X)[0])
            raw_p = float(self.classifiers[h].predict_proba(X)[0, 1])
            cal_p = float(self.calibrators[h].predict([raw_p])[0])
            conf = float(np.clip(abs(cal_p - 0.50) * 2.0, 0.05, 0.95))

            forecasts[h] = HorizonForecastV2(
                horizon_minutes=h,
                expected_net_return_bps=round(exp_net, 2),
                probability_positive=round(raw_p, 4),
                calibrated_probability=round(cal_p, 4),
                confidence_score=round(conf, 3),
                model_agreement_score=1.0 if (exp_net > 0 and cal_p > 0.5) or (exp_net < 0 and cal_p < 0.5) else 0.5,
            )

        # Select best horizon based on expected net return
        best_h = max(self.HORIZONS, key=lambda x: forecasts[x].expected_net_return_bps)
        best_edge = forecasts[best_h].expected_net_return_bps
        best_prob = forecasts[best_h].calibrated_probability

        return MultiHorizonPredictionV2(
            symbol=symbol,
            timestamp=str(timestamp),
            forecast_15m=forecasts[15],
            forecast_30m=forecasts[30],
            forecast_60m=forecasts[60],
            optimal_target_horizon_min=best_h,
            best_expected_net_edge_bps=best_edge,
            best_calibrated_prob=best_prob,
        )
