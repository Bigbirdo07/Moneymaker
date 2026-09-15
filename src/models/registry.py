"""Model registry for tracking trained models, parameters, feature sets, and metrics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd

from src.models.base import ModelMetadata


class ModelRegistry:
    """Stores and retrieves trained model metadata, parameter configurations, and evaluation metrics."""

    def __init__(self, registry_dir: Path | str = "data/processed/registry") -> None:
        self.registry_dir = Path(registry_dir)
        self._entries: Dict[str, ModelMetadata] = {}

    def register_model(self, metadata: ModelMetadata) -> None:
        """Registers a model metadata record."""
        self._entries[metadata.model_id] = metadata

    def get_metadata(self, model_id: str) -> Optional[ModelMetadata]:
        """Retrieves model metadata by ID."""
        return self._entries.get(model_id)

    def save_registry(self, filename: str = "models_registry.json") -> Path:
        """Persists the registry entries to JSON format."""
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.registry_dir / filename
        data = {k: v.__dict__ for k, v in self._entries.items()}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return out_path

    def to_dataframe(self) -> pd.DataFrame:
        """Converts model registry to a summary DataFrame."""
        if not self._entries:
            return pd.DataFrame()
        records = []
        for m in self._entries.values():
            rec = {
                "model_id": m.model_id,
                "model_version": m.model_version,
                "model_type": m.model_type,
                "training_start": m.training_start,
                "training_end": m.training_end,
                "created_at": m.created_at,
            }
            rec.update({f"metric_{k}": v for k, v in m.metrics.items()})
            records.append(rec)
        return pd.DataFrame(records)
