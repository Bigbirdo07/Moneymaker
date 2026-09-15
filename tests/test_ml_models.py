"""Tests for baseline machine learning models and feature preprocessing."""

import numpy as np
import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.features.contracts import FeatureContractValidator
from src.models.logistic import LogisticRegressionModel
from src.models.trees import RandomForestModel, XGBoostModel
from src.models.metrics import compute_classification_metrics


@pytest.fixture
def sample_feature_data() -> tuple[pd.DataFrame, pd.Series]:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=5, seed=42)
    engine = FeatureEngine(include_targets=True)
    feats = engine.compute_all_features(df)
    
    # Filter out warmup NaNs and target NaNs
    valid = feats.dropna().reset_index(drop=True)
    X = valid[[c for c in valid.columns if c.startswith("feature_")]]
    y = valid["target_class_up_60m"]
    return X, y


def test_logistic_regression_fit_predict(sample_feature_data: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = sample_feature_data
    split = len(X) // 2
    X_train, y_train = X.iloc[:split], y.iloc[:split]
    X_test, y_test = X.iloc[split:], y.iloc[split:]

    model = LogisticRegressionModel(model_id="log_test", C=1.0)
    model.fit(X_train, y_train)

    assert model.is_fitted is True
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)

    assert len(preds) == len(X_test)
    assert probs.shape == (len(X_test), 2)
    assert np.all(probs >= 0.0) and np.all(probs <= 1.0)

    importances = model.get_feature_importances()
    assert len(importances) == len(model.feature_names)
    assert sum(importances.values()) == pytest.approx(1.0, abs=1e-3)


def test_random_forest_fit_predict(sample_feature_data: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = sample_feature_data
    split = len(X) // 2
    X_train, y_train = X.iloc[:split], y.iloc[:split]
    X_test, y_test = X.iloc[split:], y.iloc[split:]

    model = RandomForestModel(model_id="rf_test", n_estimators=50, max_depth=3)
    model.fit(X_train, y_train)

    assert model.is_fitted is True
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)

    assert len(preds) == len(X_test)
    assert probs.shape == (len(X_test), 2)
    assert len(model.get_feature_importances()) > 0


def test_xgboost_fit_predict(sample_feature_data: tuple[pd.DataFrame, pd.Series]) -> None:
    X, y = sample_feature_data
    split = len(X) // 2
    X_train, y_train = X.iloc[:split], y.iloc[:split]
    X_test, y_test = X.iloc[split:], y.iloc[split:]

    model = XGBoostModel(model_id="xgb_test", n_estimators=50, max_depth=3)
    model.fit(X_train, y_train, X_val=X_test, y_val=y_test)

    assert model.is_fitted is True
    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)

    assert len(preds) == len(X_test)
    assert probs.shape == (len(X_test), 2)
    metrics = compute_classification_metrics(y_test, preds, probs)
    assert 0.0 <= metrics.accuracy <= 1.0


def test_scaler_leakage_invariance() -> None:
    """
    Verifies that test/validation observations do not leak into StandardScaler fitted inside Pipeline.
    """
    X_train = pd.DataFrame({"feature_rsi_14": [40.0, 50.0, 60.0]})
    y_train = pd.Series([0, 1, 1])

    model = LogisticRegressionModel(model_id="leakage_test")
    model.fit(X_train, y_train)

    # Scaler mean & scale should be exactly based on [40, 50, 60] -> mean=50.0
    scaler = model.pipeline.named_steps["scaler"]
    assert scaler.mean_[0] == pytest.approx(50.0)

    # Calling predict on test data with huge outliers should NOT change scaler mean
    X_test_outlier = pd.DataFrame({"feature_rsi_14": [99999.0, 100000.0]})
    model.predict(X_test_outlier)
    assert scaler.mean_[0] == pytest.approx(50.0)
