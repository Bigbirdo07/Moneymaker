"""Tree-based quantitative signal models (Random Forest & XGBoost)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb

from src.models.base import BaseMLModel, ModelMetadata


class RandomForestModel(BaseMLModel):
    """Random Forest ensemble classifier for non-linear feature interactions."""

    def __init__(
        self,
        model_id: str = "rf_baseline",
        model_version: str = "v1.0",
        n_estimators: int = 100,
        max_depth: int = 5,
        min_samples_leaf: int = 20,
        class_weight: str | Dict[int, float] = "balanced",
        random_state: int = 42,
    ) -> None:
        super().__init__(model_id=model_id, model_version=model_version)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.class_weight = class_weight
        self.random_state = random_state
        self.clf: Optional[RandomForestClassifier] = None

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series | np.ndarray,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series | np.ndarray] = None,
    ) -> "RandomForestModel":
        X_clean = self.validate_inputs(X_train)
        self.feature_names = list(X_clean.columns)
        y_arr = np.asarray(y_train)

        self.clf = RandomForestClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            min_samples_leaf=self.min_samples_leaf,
            class_weight=self.class_weight,
            random_state=self.random_state,
            n_jobs=-1,
        )
        self.clf.fit(X_clean, y_arr)
        self._is_fitted = True

        raw_importances = self.clf.feature_importances_
        norm_importances = {name: float(raw_importances[i]) for i, name in enumerate(self.feature_names)}

        self._metadata = ModelMetadata(
            model_id=self.model_id,
            model_version=self.model_version,
            model_type="RandomForest",
            feature_names=self.feature_names,
            target_name="target_class_up_60m",
            training_start=str(X_train.index[0]) if hasattr(X_train, "index") else "",
            training_end=str(X_train.index[-1]) if hasattr(X_train, "index") else "",
            hyperparameters={
                "n_estimators": self.n_estimators,
                "max_depth": self.max_depth,
                "min_samples_leaf": self.min_samples_leaf,
                "class_weight": str(self.class_weight),
            },
            feature_importances=norm_importances,
        )
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fitted or self.clf is None:
            raise ValueError("Model must be fitted before predict.")
        X_clean = self.validate_inputs(X)
        return self.clf.predict(X_clean)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fitted or self.clf is None:
            raise ValueError("Model must be fitted before predict_proba.")
        X_clean = self.validate_inputs(X)
        return self.clf.predict_proba(X_clean)

    def get_feature_importances(self) -> Dict[str, float]:
        if not self._is_fitted or self._metadata is None:
            raise ValueError("Model must be fitted to retrieve feature importances.")
        return self._metadata.feature_importances


class XGBoostModel(BaseMLModel):
    """Gradient Boosted Decision Trees classifier using XGBoost."""

    def __init__(
        self,
        model_id: str = "xgb_baseline",
        model_version: str = "v1.0",
        n_estimators: int = 100,
        max_depth: int = 4,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        scale_pos_weight: Optional[float] = None,
        random_state: int = 42,
    ) -> None:
        super().__init__(model_id=model_id, model_version=model_version)
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.learning_rate = learning_rate
        self.subsample = subsample
        self.colsample_bytree = colsample_bytree
        self.scale_pos_weight = scale_pos_weight
        self.random_state = random_state
        self.clf: Optional[xgb.XGBClassifier] = None

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series | np.ndarray,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series | np.ndarray] = None,
    ) -> "XGBoostModel":
        X_clean = self.validate_inputs(X_train)
        self.feature_names = list(X_clean.columns)
        y_arr = np.asarray(y_train)

        # Compute class balance weight if not explicitly provided
        pos_weight = self.scale_pos_weight
        if pos_weight is None and len(np.unique(y_arr)) == 2:
            n_neg = np.sum(y_arr == 0)
            n_pos = np.sum(y_arr == 1)
            pos_weight = float(n_neg / max(1, n_pos))

        self.clf = xgb.XGBClassifier(
            n_estimators=self.n_estimators,
            max_depth=self.max_depth,
            learning_rate=self.learning_rate,
            subsample=self.subsample,
            colsample_bytree=self.colsample_bytree,
            scale_pos_weight=pos_weight,
            random_state=self.random_state,
            eval_metric="logloss",
            n_jobs=-1,
        )

        eval_set = None
        if X_val is not None and y_val is not None:
            X_val_clean = self.validate_inputs(X_val)
            eval_set = [(X_val_clean, np.asarray(y_val))]

        self.clf.fit(X_clean, y_arr, eval_set=eval_set, verbose=False)
        self._is_fitted = True

        raw_importances = self.clf.feature_importances_
        norm_importances = {name: float(raw_importances[i]) for i, name in enumerate(self.feature_names)}

        self._metadata = ModelMetadata(
            model_id=self.model_id,
            model_version=self.model_version,
            model_type="XGBoost",
            feature_names=self.feature_names,
            target_name="target_class_up_60m",
            training_start=str(X_train.index[0]) if hasattr(X_train, "index") else "",
            training_end=str(X_train.index[-1]) if hasattr(X_train, "index") else "",
            hyperparameters={
                "n_estimators": self.n_estimators,
                "max_depth": self.max_depth,
                "learning_rate": self.learning_rate,
                "subsample": self.subsample,
                "colsample_bytree": self.colsample_bytree,
                "scale_pos_weight": pos_weight,
            },
            feature_importances=norm_importances,
        )
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fitted or self.clf is None:
            raise ValueError("Model must be fitted before predict.")
        X_clean = self.validate_inputs(X)
        return self.clf.predict(X_clean)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        if not self._is_fitted or self.clf is None:
            raise ValueError("Model must be fitted before predict_proba.")
        X_clean = self.validate_inputs(X)
        return self.clf.predict_proba(X_clean)

    def get_feature_importances(self) -> Dict[str, float]:
        if not self._is_fitted or self._metadata is None:
            raise ValueError("Model must be fitted to retrieve feature importances.")
        return self._metadata.feature_importances
