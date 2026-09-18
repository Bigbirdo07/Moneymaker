"""
Real-Market Statistical and Machine Learning Baseline Models for Phase 10.4.
Provides leakage-safe Ridge, Logistic, Random Forest, and Gradient Boosting baselines.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor, HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, roc_auc_score, brier_score_loss


class RealMarketBaselines:
    """
    Leakage-safe baseline model training and evaluation suite for real market data.
    """

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
        self.scaler = StandardScaler()
        self.ridge_model = Ridge(alpha=100.0)
        self.logistic_model = LogisticRegression(C=0.1, max_iter=1000)
        self.rf_model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42, n_jobs=-1)
        self.gbr_model = HistGradientBoostingRegressor(max_iter=100, max_depth=5, random_state=42)
        self.gbc_model = HistGradientBoostingClassifier(max_iter=100, max_depth=5, random_state=42)
        self._is_fitted = False

    def fit(self, train_df: pd.DataFrame, target_horizon: int = 15) -> Dict[str, Any]:
        """
        Fits all baselines on training partition.
        """
        valid_df = train_df.dropna(subset=[f"fwd_net_{target_horizon}m_bps", f"label_binary_net_{target_horizon}m"])
        if len(valid_df) < 100:
            raise ValueError("Insufficient training observations.")

        X = valid_df[self.FEATURE_COLS].fillna(0.0).values
        y_reg = valid_df[f"fwd_net_{target_horizon}m_bps"].values
        y_clf = valid_df[f"label_binary_net_{target_horizon}m"].values

        # Scale features
        X_scaled = self.scaler.fit_transform(X)

        # Train models
        self.ridge_model.fit(X_scaled, y_reg)
        self.logistic_model.fit(X_scaled, y_clf)
        self.rf_model.fit(X, y_reg)
        self.gbr_model.fit(X, y_reg)
        self.gbc_model.fit(X, y_clf)

        self._is_fitted = True
        return {
            "train_samples": len(valid_df),
            "target_horizon_min": target_horizon,
            "status": "TRAINED",
        }

    def predict_all(self, test_df: pd.DataFrame, target_horizon: int = 15) -> Dict[str, np.ndarray]:
        """
        Generates predictions across all fitted baseline models.
        """
        if not self._is_fitted:
            raise RuntimeError("Models must be fitted before predicting.")

        X = test_df[self.FEATURE_COLS].fillna(0.0).values
        X_scaled = self.scaler.transform(X)

        pred_ridge = self.ridge_model.predict(X_scaled)
        prob_logistic = self.logistic_model.predict_proba(X_scaled)[:, 1]
        pred_rf = self.rf_model.predict(X)
        pred_gbr = self.gbr_model.predict(X)
        prob_gbc = self.gbc_model.predict_proba(X)[:, 1]

        return {
            "ridge_exp_net_bps": pred_ridge,
            "logistic_p_up": prob_logistic,
            "rf_exp_net_bps": pred_rf,
            "gbr_exp_net_bps": pred_gbr,
            "gbc_p_up": prob_gbc,
        }
