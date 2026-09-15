"""Expected return regression models (Linear, Random Forest, XGBoost)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import xgboost as xgb

from src.features.contracts import FeatureContractValidator


@dataclass
class RegressionMetrics:
    """Standardized performance evaluation for return forecasting regressors."""
    mae_bps: float
    rmse_bps: float
    pearson_corr: float
    spearman_rank_ic: float
    directional_accuracy_pct: float
    sample_count: int


class BaseRegressor:
    """Base interface for return regression models."""

    def __init__(self, model_id: str) -> None:
        self.model_id = model_id
        self.feature_names: List[str] = []
        self.is_fitted = False

    def validate_inputs(self, X: pd.DataFrame) -> pd.DataFrame:
        valid_cols = FeatureContractValidator.validate_features(X.columns)
        if self.is_fitted:
            return X[self.feature_names].copy()
        return X[valid_cols].copy()


class LinearRegressionModel(BaseRegressor):
    """L2-regularized linear return forecasting model."""

    def __init__(self, model_id: str = "ridge_reg", alpha: float = 1.0) -> None:
        super().__init__(model_id=model_id)
        self.alpha = alpha
        self.pipeline: Optional[Pipeline] = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series | np.ndarray) -> "LinearRegressionModel":
        X_clean = self.validate_inputs(X_train)
        self.feature_names = list(X_clean.columns)
        y_arr = np.asarray(y_train)

        scaler = StandardScaler()
        reg = Ridge(alpha=self.alpha)
        self.pipeline = Pipeline([("scaler", scaler), ("regressor", reg)])
        self.pipeline.fit(X_clean, y_arr)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.pipeline is None:
            raise ValueError("Model must be fitted.")
        X_clean = self.validate_inputs(X)
        return self.pipeline.predict(X_clean)


class RandomForestRegressorModel(BaseRegressor):
    """Random Forest regressor for non-linear return forecasting."""

    def __init__(self, model_id: str = "rf_reg", n_estimators: int = 50, max_depth: int = 4, random_state: int = 42) -> None:
        super().__init__(model_id=model_id)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.random_state = random_state
        self.model: Optional[RandomForestRegressor] = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series | np.ndarray) -> "RandomForestRegressorModel":
        X_clean = self.validate_inputs(X_train)
        self.feature_names = list(X_clean.columns)
        self.model = RandomForestRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(X_clean, np.asarray(y_train))
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be fitted.")
        X_clean = self.validate_inputs(X)
        return self.model.predict(X_clean)


class XGBoostRegressorModel(BaseRegressor):
    """XGBoost gradient-boosted return regressor."""

    def __init__(
        self,
        model_id: str = "xgb_reg",
        n_estimators: int = 50,
        max_depth: int = 3,
        learning_rate: float = 0.05,
        random_state: int = 42,
    ) -> None:
        super().__init__(model_id=model_id)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model: Optional[xgb.XGBRegressor] = None

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series | np.ndarray) -> "XGBoostRegressorModel":
        X_clean = self.validate_inputs(X_train)
        self.feature_names = list(X_clean.columns)
        self.model = xgb.XGBRegressor(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.model.fit(X_clean, np.asarray(y_train))
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted or self.model is None:
            raise ValueError("Model must be fitted.")
        X_clean = self.validate_inputs(X)
        return self.model.predict(X_clean)


def evaluate_regression_predictions(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray | pd.Series,
) -> RegressionMetrics:
    """Evaluates MAE, RMSE, Pearson/Spearman correlation, and directional sign accuracy."""
    y_t = np.asarray(y_true)
    y_p = np.asarray(y_pred)
    n = len(y_t)

    errors_bps = (y_p - y_t) * 10000.0
    mae = float(np.mean(np.abs(errors_bps)))
    rmse = float(np.sqrt(np.mean(errors_bps ** 2)))

    p_corr = float(pearsonr(y_p, y_t)[0]) if np.std(y_p) > 1e-8 and np.std(y_t) > 1e-8 else 0.0
    s_corr = float(spearmanr(y_p, y_t)[0]) if np.std(y_p) > 1e-8 and np.std(y_t) > 1e-8 else 0.0

    dir_acc = float(np.mean(np.sign(y_p) == np.sign(y_t))) * 100.0

    return RegressionMetrics(
        mae_bps=round(mae, 2),
        rmse_bps=round(rmse, 2),
        pearson_corr=round(p_corr, 4),
        spearman_rank_ic=round(s_corr, 4),
        directional_accuracy_pct=round(dir_acc, 2),
        sample_count=n,
    )
