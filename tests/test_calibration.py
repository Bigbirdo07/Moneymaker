"""Tests for probability calibration, reliability buckets, and Brier score."""

import numpy as np
import pandas as pd
import pytest

from src.models.trees import RandomForestModel
from src.models.calibration import ProbabilityCalibrator


def test_calibration_and_reliability_evaluation() -> None:
    # Synthetic ground truth and predictions
    np.random.seed(42)
    n = 200
    y_true = np.random.binomial(1, 0.5, size=n)
    # Simulated overconfident probabilities
    y_prob = np.clip(y_true * 0.7 + np.random.uniform(0.1, 0.3, size=n), 0.01, 0.99)

    report = ProbabilityCalibrator.evaluate_reliability(y_true, y_prob, method_name="test_cal")
    assert 0.0 <= report.brier_score <= 1.0
    assert 0.0 <= report.expected_calibration_error <= 1.0
    assert len(report.buckets) == 6


def test_platt_scaling_fit_predict() -> None:
    np.random.seed(42)
    X = pd.DataFrame({
        "feature_rsi_14": np.random.uniform(20, 80, size=100),
        "feature_return_1b": np.random.normal(0, 0.01, size=100),
    })
    y = np.random.binomial(1, 0.5, size=100)

    model = RandomForestModel(model_id="cal_rf", n_estimators=20, max_depth=3)
    model.fit(X.iloc[:60], y[:60])

    calibrator = ProbabilityCalibrator(method="sigmoid")
    calibrator.fit(model, X.iloc[60:80], y[60:80])

    cal_probs = calibrator.predict_proba(model, X.iloc[80:])
    assert cal_probs.shape == (20, 2)
    assert np.all(cal_probs >= 0.0) and np.all(cal_probs <= 1.0)
