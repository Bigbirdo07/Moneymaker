"""Abstract base class for all machine learning directional prediction models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.features.contracts import FeatureContractValidator


@dataclass
class ModelMetadata:
    """Immutable audit metadata for a trained model artifact."""
    model_id: str
    model_version: str
    model_type: str
    feature_names: List[str]
    target_name: str
    training_start: str
    training_end: str
    validation_start: Optional[str] = None
    validation_end: Optional[str] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, float] = field(default_factory=dict)
    feature_importances: Dict[str, float] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BaseMLModel(ABC):
    """Abstract interface defining the lifecycle of a financial machine learning model."""

    def __init__(self, model_id: str, model_version: str = "v1.0") -> None:
        self.model_id = model_id
        self.model_version = model_version
        self.feature_names: List[str] = []
        self._is_fitted: bool = False
        self._metadata: Optional[ModelMetadata] = None

    @property
    def is_fitted(self) -> bool:
        return self._is_fitted

    @abstractmethod
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series | np.ndarray,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series | np.ndarray] = None,
    ) -> "BaseMLModel":
        """Fits the model using strictly training data (with optional validation for early stopping)."""
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts discrete target classes (e.g. 0, 1 or -1, 0, 1)."""
        pass

    @abstractmethod
    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """Predicts probability distributions over target classes (n_samples, n_classes)."""
        pass

    @abstractmethod
    def get_feature_importances(self) -> Dict[str, float]:
        """Returns normalized feature importance scores."""
        pass

    def validate_inputs(self, X: pd.DataFrame) -> pd.DataFrame:
        """Validates feature columns against leakage rules and enforces training column order."""
        valid_cols = FeatureContractValidator.validate_features(X.columns)
        if self._is_fitted:
            missing = [col for col in self.feature_names if col not in X.columns]
            if missing:
                raise ValueError(f"Missing required model features at inference: {missing}")
            return X[self.feature_names].copy()
        return X[valid_cols].copy()

    def metadata(self) -> ModelMetadata:
        """Returns the audit metadata for this model."""
        if not self._is_fitted or self._metadata is None:
            raise ValueError("Model must be fitted before metadata is available.")
        return self._metadata
