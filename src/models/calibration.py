"""Probability calibration engine, reliability curve analysis, and Brier score evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss

from src.models.base import BaseMLModel


@dataclass
class ReliabilityBucket:
    """Statistics for a discrete confidence bucket."""
    bin_name: str
    min_prob: float
    max_prob: float
    sample_count: int
    mean_predicted_prob: float
    observed_fraction_positives: float
    calibration_error: float


@dataclass
class CalibrationReport:
    """Full calibration diagnostic teardown."""
    method: str
    brier_score: float
    expected_calibration_error: float
    buckets: List[ReliabilityBucket]


class ProbabilityCalibrator:
    """
    Fits and applies probability calibration (Platt Scaling or Isotonic Regression)
    strictly on validation folds, and evaluates reliability curves.
    """

    CONFIDENCE_BINS: List[Tuple[str, float, float]] = [
        ("0.50–0.55", 0.50, 0.55),
        ("0.55–0.60", 0.55, 0.60),
        ("0.60–0.65", 0.60, 0.65),
        ("0.65–0.70", 0.65, 0.70),
        ("0.70–0.80", 0.70, 0.80),
        ("0.80+", 0.80, 1.01),
    ]

    def __init__(self, method: str = "sigmoid") -> None:
        """
        method: 'sigmoid' (Platt scaling) or 'isotonic' (Isotonic regression)
        """
        self.method = method
        self.platt_model: Optional[LogisticRegression] = None
        self.isotonic_model: Optional[IsotonicRegression] = None

    def fit(self, base_model: BaseMLModel, X_val: pd.DataFrame, y_val: np.ndarray | pd.Series) -> "ProbabilityCalibrator":
        """Fits calibration curve on validation predictions."""
        raw_probs = base_model.predict_proba(X_val)
        p_val = raw_probs[:, 1] if raw_probs.ndim > 1 else raw_probs.flatten()
        y_arr = np.asarray(y_val)

        # Clip probabilities to avoid infinite logits
        p_val_clipped = np.clip(p_val, 1e-4, 1 - 1e-4)

        if self.method == "sigmoid":
            # Platt scaling: LogisticRegression on log-odds
            log_odds = logit(p_val_clipped).reshape(-1, 1)
            self.platt_model = LogisticRegression(solver="lbfgs", max_iter=1000)
            self.platt_model.fit(log_odds, y_arr)
        elif self.method == "isotonic":
            self.isotonic_model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            self.isotonic_model.fit(p_val_clipped, y_arr)
        return self

    def predict_proba(self, base_model: BaseMLModel, X: pd.DataFrame) -> np.ndarray:
        """Applies calibration if fitted, otherwise returns base model probabilities."""
        raw_probs = base_model.predict_proba(X)
        p_raw = raw_probs[:, 1] if raw_probs.ndim > 1 else raw_probs.flatten()
        p_clipped = np.clip(p_raw, 1e-4, 1 - 1e-4)

        if self.method == "sigmoid" and self.platt_model is not None:
            log_odds = logit(p_clipped).reshape(-1, 1)
            cal_probs = self.platt_model.predict_proba(log_odds)
            return cal_probs
        elif self.method == "isotonic" and self.isotonic_model is not None:
            cal_p1 = self.isotonic_model.predict(p_clipped)
            cal_p0 = 1.0 - cal_p1
            return np.column_stack([cal_p0, cal_p1])
        return raw_probs

    @classmethod
    def evaluate_reliability(
        cls,
        y_true: np.ndarray | pd.Series,
        y_prob: np.ndarray | pd.Series,
        method_name: str = "uncalibrated",
    ) -> CalibrationReport:
        """Computes Brier score, ECE, and reliability metrics across confidence buckets."""
        y_t = np.asarray(y_true)
        y_p = np.asarray(y_prob)

        if y_p.ndim > 1:
            y_p = y_p[:, 1]

        brier = float(brier_score_loss(y_t, y_p))

        buckets: List[ReliabilityBucket] = []
        total_samples = len(y_p)
        weighted_error_sum = 0.0

        for bin_name, min_p, max_p in cls.CONFIDENCE_BINS:
            in_bin = (y_p >= min_p) & (y_p < max_p)
            count = int(np.sum(in_bin))

            if count > 0:
                mean_pred = float(np.mean(y_p[in_bin]))
                obs_frac = float(np.mean(y_t[in_bin]))
                cal_err = abs(mean_pred - obs_frac)
                weighted_error_sum += cal_err * count
            else:
                mean_pred = 0.0
                obs_frac = 0.0
                cal_err = 0.0

            buckets.append(
                ReliabilityBucket(
                    bin_name=bin_name,
                    min_prob=min_p,
                    max_prob=max_p,
                    sample_count=count,
                    mean_predicted_prob=round(mean_pred, 4),
                    observed_fraction_positives=round(obs_frac, 4),
                    calibration_error=round(cal_err, 4),
                )
            )

        ece = (weighted_error_sum / max(1, total_samples))

        return CalibrationReport(
            method=method_name,
            brier_score=round(brier, 4),
            expected_calibration_error=round(ece, 4),
            buckets=buckets,
        )
