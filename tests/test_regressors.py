"""Tests for expected return regression models (Linear, RF, XGBoost)."""

import numpy as np
import pandas as pd
import pytest

from src.models.regressors import (
    LinearRegressionModel,
    RandomForestRegressorModel,
    XGBoostRegressorModel,
    evaluate_regression_predictions,
)


@pytest.fixture
def regression_data() -> tuple[pd.DataFrame, pd.Series]:
    np.random.seed(42)
    n = 100
    X = pd.DataFrame({
        "feature_rsi_14": np.random.uniform(30, 70, size=n),
        "feature_return_1b": np.random.normal(0, 0.005, size=n),
        "feature_relative_volume_20b": np.random.uniform(0.8, 2.0, size=n),
    })
    y = X["feature_return_1b"] * 0.5 + np.random.normal(0, 0.002, size=n)
    return X, y


def test_linear_regressor(regression_data: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = regression_data
    model = LinearRegressionModel()
    model.fit(X.iloc[:70], y.iloc[:70])
    preds = model.predict(X.iloc[70:])
    metrics = evaluate_regression_predictions(y.iloc[70:], preds)
    assert metrics.mae_bps >= 0.0
    assert metrics.sample_count == 30


def test_xgboost_regressor(regression_data: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = regression_data
    model = XGBoostRegressorModel(n_estimators=20, max_depth=3)
    model.fit(X.iloc[:70], y.iloc[:70])
    preds = model.predict(X.iloc[70:])
    metrics = evaluate_regression_predictions(y.iloc[70:], preds)
    assert metrics.rmse_bps >= 0.0
