"""Logistic Regression baseline classifier with training-only scaling pipeline."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from src.models.base import BaseMLModel, ModelMetadata


class LogisticRegressionModel(BaseMLModel):
    """
    Linear logistic regression classifier.
    Guarantees feature standard scaling is fitted ONLY on training folds.
    """

    def __init__(
        self,
        model_id: str = "logistic_baseline",
        model_version: str = "v1.0",
        C: float = 1.0,
        penalty: str = "l2",
        class_weight: str | Dict[int, float] = "balanced",
        random_state: int = 42,
    ) -> None:
        super().__init__(model_id=model_id, model_version=model_version)
        self.C = C
        self.penalty = penalty
        self.class_weight = class_weight
        self.random_state = random_state
        self.pipeline: Optional[Pipeline] = None

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series | np.ndarray,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series | np.ndarray] = None,
    ) -> "LogisticRegressionModel":
        X_clean = self.validate_inputs(X_train)
        self.feature_names = list(X_clean.columns)
        y_arr = np.asarray(y_train)

        # Build pipeline ensuring scaler is fit ONLY on training data
        scaler = StandardScaler()
        clf = LogisticRegression(
            C=self.C,
            class_weight=self.class_weight,
            random_state=self.random_state,
            max_iter=1000,
            solver="lbfgs",
        )
        self.pipeline = Pipeline([("scaler", scaler), ("classifier", clf)])
        self.pipeline.fit(X_clean, y_arr)
        self._is_fitted = True

        # Extract coefficients as normalized feature importance
        raw_coefs = np.abs(clf.coef_[0]) if clf.coef_.ndim > 1 else np.abs(clf.coef_)
        total_coef = np.sum(raw_coefs) + 1e-10
        norm_importances = {name: float(raw_coefs[i] / total_coef) for i, name in enumerate(self.feature_names)}

        self._metadata = ModelMetadata(
            model_id=self.model_id,
            model_version=self.model_version,
            model_type="LogisticRegression",
            feature_names=self.feature_names,
            target_name="target_class_up_60m",
            training_start=str(X_train.index[0]) if hasattr(X_train, "index") else "",
            training_end=str(X_train.index[-1]) if hasattr(X_train, "index") else "",
            hyperparameters={"C": self.C, "penalty": self.penalty, "class_weight": str(self.class_weight)},
            feature_importances=norm_importances,
        )
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fitted or self.pipeline is None:
            raise ValueError("Model must be fitted before predict.")
        X_clean = self.validate_inputs(X)
        return self.pipeline.predict(X_clean)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fitted or self.pipeline is None:
            raise ValueError("Model must be fitted before predict_proba.")
        X_clean = self.validate_inputs(X)
        return self.pipeline.predict_proba(X_clean)

    def get_feature_importances(self) -> Dict[str, float]:
        if not self._is_fitted or self._metadata is None:
            raise ValueError("Model must be fitted to retrieve feature importances.")
        return self._metadata.feature_importances
