"""Meta-labeling secondary trade-filtering model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.models.base import BaseMLModel


@dataclass
class MetaLabelingReport:
    """Evaluation of meta-labeling filter impact."""
    total_raw_candidates: int
    approved_trades: int
    rejected_trades: int
    filter_precision: float
    raw_win_rate_pct: float
    meta_filtered_win_rate_pct: float
    win_rate_improvement_pct: float


class MetaLabelingFilter:
    """
    Two-stage trade filtering classifier:
    Stage 1: Strategy identifies candidate directional signal.
    Stage 2: Meta-model predicts whether the candidate trade will successfully exceed friction costs.
    """

    META_FEATURE_COLUMNS = [
        "feature_rsi_14",
        "feature_realized_vol_20b",
        "feature_atr_pct",
        "feature_relative_volume_20b",
        "feature_volume_zscore_20b",
        "feature_vwap_deviation",
        "feature_ema_cross_9_21",
        "feature_rel_strength_SPY_1b",
        "feature_minutes_from_open",
        "p_up",
    ]

    def __init__(
        self,
        n_estimators: int = 50,
        max_depth: int = 3,
        min_meta_probability: float = 0.52,
        random_state: int = 42,
    ) -> None:
        self.min_meta_probability = min_meta_probability
        self.clf = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            class_weight="balanced",
            random_state=random_state,
        )
        self.is_fitted = False

    def build_meta_features(self, candidate_df: pd.DataFrame, primary_probs: np.ndarray) -> pd.DataFrame:
        """Extracts features available at trade initiation for the second-stage meta-model."""
        meta_df = candidate_df.copy()
        meta_df["p_up"] = primary_probs
        available_cols = [c for c in self.META_FEATURE_COLUMNS if c in meta_df.columns]
        return meta_df[available_cols].fillna(0.0)

    def fit_meta_model(
        self,
        train_candidates_df: pd.DataFrame,
        primary_probs: np.ndarray,
        realized_net_returns: np.ndarray | pd.Series,
    ) -> "MetaLabelingFilter":
        """
        Fits meta-model using binary target: 1 if realized_net_return > 0 else 0.
        """
        X_meta = self.build_meta_features(train_candidates_df, primary_probs)
        y_meta = (np.asarray(realized_net_returns) > 0.0).astype(int)

        if len(np.unique(y_meta)) < 2:
            self.is_fitted = False
            return self

        self.clf.fit(X_meta, y_meta)
        self.is_fitted = True
        return self

    def predict_take_trade(
        self,
        test_candidates_df: pd.DataFrame,
        primary_probs: np.ndarray,
    ) -> np.ndarray:
        """
        Predicts boolean mask (True = Take Trade, False = Reject Trade).
        """
        if not self.is_fitted:
            return np.ones(len(test_candidates_df), dtype=bool)

        X_meta = self.build_meta_features(test_candidates_df, primary_probs)
        meta_probs = self.clf.predict_proba(X_meta)[:, 1]
        return (meta_probs >= self.min_meta_probability)

    def evaluate_filter(
        self,
        test_candidates_df: pd.DataFrame,
        primary_probs: np.ndarray,
        realized_net_returns: np.ndarray | pd.Series,
    ) -> MetaLabelingReport:
        """Evaluates win rate improvement from applying the second-stage meta-filter."""
        y_true_profit = (np.asarray(realized_net_returns) > 0.0).astype(int)
        take_mask = self.predict_take_trade(test_candidates_df, primary_probs)

        n_raw = len(y_true_profit)
        n_approved = int(np.sum(take_mask))
        n_rejected = n_raw - n_approved

        raw_win = float(np.mean(y_true_profit)) * 100.0 if n_raw > 0 else 0.0
        filtered_win = float(np.mean(y_true_profit[take_mask])) * 100.0 if n_approved > 0 else 0.0

        return MetaLabelingReport(
            total_raw_candidates=n_raw,
            approved_trades=n_approved,
            rejected_trades=n_rejected,
            filter_precision=round(float(filtered_win / 100.0), 4),
            raw_win_rate_pct=round(raw_win, 2),
            meta_filtered_win_rate_pct=round(filtered_win, 2),
            win_rate_improvement_pct=round(filtered_win - raw_win, 2),
        )
