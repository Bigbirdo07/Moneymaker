"""
Real-Market Ranking Forecaster V3 for Phase 11B / Engine V3.
Two-stage ranking model integrating market regime gating, cross-sectional relative strength,
and multi-horizon expected net edge prediction (30m, 60m, 120m).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.isotonic import IsotonicRegression

from src.core.logging import get_logger
from src.core.types import EvidenceClass

logger = get_logger("models.real_forecaster_v3")


@dataclass
class HorizonForecastV3:
    """Forecast for a single horizon."""
    horizon_minutes: int
    expected_net_return_bps: float
    probability_positive: float
    calibrated_probability: float
    confidence_score: float


@dataclass
class MultiHorizonPredictionV3:
    """Consolidated prediction bundle for a symbol at timestamp T."""
    symbol: str
    timestamp: str
    forecast_30m: HorizonForecastV3
    forecast_60m: HorizonForecastV3
    forecast_120m: HorizonForecastV3
    optimal_target_horizon_min: int
    best_expected_net_edge_bps: float
    best_calibrated_prob: float
    is_tradable_regime: bool
    evidence_class: str = EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "forecast_30m": asdict(self.forecast_30m),
            "forecast_60m": asdict(self.forecast_60m),
            "forecast_120m": asdict(self.forecast_120m),
            "optimal_target_horizon_min": self.optimal_target_horizon_min,
            "best_expected_net_edge_bps": self.best_expected_net_edge_bps,
            "best_calibrated_prob": self.best_calibrated_prob,
            "is_tradable_regime": self.is_tradable_regime,
            "evidence_class": self.evidence_class,
        }


class RealMarketRankingForecasterV3:
    """
    Engine V3 Two-Stage Ranking & Multi-Horizon Forecaster.
    """

    HORIZONS = [30, 60, 120]

    FEATURE_COLS = [
        "ret_1m_bps", "ret_3m_bps", "ret_5m_bps", "ret_10m_bps", "ret_15m_bps", "ret_30m_bps", "ret_60m_bps",
        "ema_trend_10_30_bps", "dist_from_vwap_bps", "dist_from_high_bps", "dist_from_low_bps", "breakout_distance_bps", "rsi_14",
        "realized_vol_15m_bps", "realized_vol_60m_bps", "atr_14_bps", "range_expansion_ratio",
        "relative_volume", "volume_acceleration", "trade_intensity",
        "overnight_gap_bps",
        "cs_return_rank_15m", "cs_return_rank_60m", "cs_vwap_rank", "cs_volume_rank",
        "market_breadth_above_vwap", "market_mean_ret_15m_bps", "market_mean_ret_60m_bps",
        "rel_strength_15m_bps", "rel_strength_60m_bps",
        "minutes_since_open", "minutes_to_close",
    ]

    def __init__(self) -> None:
        self.regressors: Dict[int, HistGradientBoostingRegressor] = {}
        self.classifiers: Dict[int, HistGradientBoostingClassifier] = {}
        self.calibrators: Dict[int, IsotonicRegression] = {}
        self._is_trained: bool = False

    def train(self, train_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Trains multi-horizon regressors and probability classifiers on historical data.
        """
        logger.info("Training RealMarketRankingForecasterV3 on %d observations...", len(train_df))
        results = {}

        # Available feature columns
        avail_features = [f for f in self.FEATURE_COLS if f in train_df.columns]

        for h in self.HORIZONS:
            net_col = f"fwd_net_{h}m_bps"
            lbl_col = f"label_binary_net_{h}m"
            if net_col not in train_df.columns or lbl_col not in train_df.columns:
                continue

            sub = train_df.dropna(subset=[net_col, lbl_col])
            if len(sub) < 100:
                continue

            X = sub[avail_features].fillna(0.0).values
            y_reg = sub[net_col].values
            y_clf = sub[lbl_col].values

            reg = HistGradientBoostingRegressor(max_iter=150, max_depth=5, learning_rate=0.03, random_state=42)
            reg.fit(X, y_reg)
            self.regressors[h] = reg

            clf = HistGradientBoostingClassifier(max_iter=150, max_depth=5, learning_rate=0.03, random_state=42)
            clf.fit(X, y_clf)
            self.classifiers[h] = clf

            raw_probs = clf.predict_proba(X)[:, 1]
            iso = IsotonicRegression(out_of_bounds="clip")
            iso.fit(raw_probs, y_clf)
            self.calibrators[h] = iso

            results[h] = {"samples": len(sub), "status": "TRAINED"}

        self._is_trained = True
        return results

    def predict_batch(self, df: pd.DataFrame) -> List[MultiHorizonPredictionV3]:
        """
        Generates predictions for a batch of candidate observations at timestamp T.
        """
        if not self._is_trained or df.empty:
            return []

        avail_features = [f for f in self.FEATURE_COLS if f in df.columns]
        X = df[avail_features].fillna(0.0).values

        preds_reg: Dict[int, np.ndarray] = {}
        probs_cal: Dict[int, np.ndarray] = {}

        for h in self.HORIZONS:
            if h in self.regressors:
                preds_reg[h] = self.regressors[h].predict(X)
                raw_p = self.classifiers[h].predict_proba(X)[:, 1]
                probs_cal[h] = self.calibrators[h].predict(raw_p)
            else:
                preds_reg[h] = np.zeros(len(df))
                probs_cal[h] = np.full(len(df), 0.50)

        predictions: List[MultiHorizonPredictionV3] = []
        for i in range(len(df)):
            row = df.iloc[i]
            sym = str(row["symbol"])
            ts = str(row["timestamp_et"]) if "timestamp_et" in row else str(row.get("dt_et", ""))

            # Stage 1: Market Regime Check
            tradable_regime = bool(row.get("market_regime_tradable", 1))

            f_30 = HorizonForecastV3(
                horizon_minutes=30,
                expected_net_return_bps=float(preds_reg[30][i]),
                probability_positive=float(probs_cal[30][i]),
                calibrated_probability=float(probs_cal[30][i]),
                confidence_score=float(probs_cal[30][i]),
            )
            f_60 = HorizonForecastV3(
                horizon_minutes=60,
                expected_net_return_bps=float(preds_reg[60][i]),
                probability_positive=float(probs_cal[60][i]),
                calibrated_probability=float(probs_cal[60][i]),
                confidence_score=float(probs_cal[60][i]),
            )
            f_120 = HorizonForecastV3(
                horizon_minutes=120,
                expected_net_return_bps=float(preds_reg[120][i]),
                probability_positive=float(probs_cal[120][i]),
                calibrated_probability=float(probs_cal[120][i]),
                confidence_score=float(probs_cal[120][i]),
            )

            # Select optimal horizon
            forecasts = [f_30, f_60, f_120]
            best_f = max(forecasts, key=lambda f: f.expected_net_return_bps)

            pred = MultiHorizonPredictionV3(
                symbol=sym,
                timestamp=ts,
                forecast_30m=f_30,
                forecast_60m=f_60,
                forecast_120m=f_120,
                optimal_target_horizon_min=best_f.horizon_minutes,
                best_expected_net_edge_bps=best_f.expected_net_return_bps,
                best_calibrated_prob=best_f.calibrated_probability,
                is_tradable_regime=tradable_regime,
            )
            predictions.append(pred)

        return predictions
