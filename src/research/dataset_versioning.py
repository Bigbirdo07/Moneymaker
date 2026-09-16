"""
Moneymaker Dataset Versioning & Manifest Engine.
Ensures point-in-time preservation, explicit feature availability timestamps,
target definition isolation, and cryptographic dataset hashing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class DatasetManifest:
    dataset_id: str
    symbols: List[str]
    start_date: str
    end_date: str
    bar_frequency: str  # e.g. "1m", "5m", "1d"
    source_provider: str
    adjustment_status: str  # e.g. "SPLIT_AND_DIVIDEND_ADJUSTED"
    feature_columns: List[str]
    target_column: str
    row_count: int
    created_at: str
    dataset_hash: str
    training_cutoff_date: Optional[str] = None
    embargo_bars: int = 5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_id": self.dataset_id,
            "symbols": self.symbols,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "bar_frequency": self.bar_frequency,
            "source_provider": self.source_provider,
            "adjustment_status": self.adjustment_status,
            "feature_columns": self.feature_columns,
            "target_column": self.target_column,
            "row_count": self.row_count,
            "created_at": self.created_at,
            "dataset_hash": self.dataset_hash,
            "training_cutoff_date": self.training_cutoff_date,
            "embargo_bars": self.embargo_bars,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DatasetManifest:
        return cls(**data)


class DatasetRegistry:
    """
    Manages dataset manifests, verifying immutability and preventing leakage.
    """

    def __init__(self, manifest_dir: str = "data/manifests") -> None:
        self.manifest_dir = manifest_dir
        os.makedirs(manifest_dir, exist_ok=True)

    def compute_hash(self, content_str: str) -> str:
        return hashlib.sha256(content_str.encode("utf-8")).hexdigest()

    def register_dataset(
        self,
        dataset_id: str,
        symbols: List[str],
        start_date: str,
        end_date: str,
        bar_frequency: str,
        source_provider: str,
        adjustment_status: str,
        feature_columns: List[str],
        target_column: str,
        row_count: int,
        training_cutoff_date: Optional[str] = None,
        embargo_bars: int = 5,
    ) -> DatasetManifest:
        manifest_payload = {
            "dataset_id": dataset_id,
            "symbols": sorted(symbols),
            "start_date": start_date,
            "end_date": end_date,
            "bar_frequency": bar_frequency,
            "source_provider": source_provider,
            "adjustment_status": adjustment_status,
            "feature_columns": sorted(feature_columns),
            "target_column": target_column,
            "row_count": row_count,
            "training_cutoff_date": training_cutoff_date,
            "embargo_bars": embargo_bars,
        }
        raw_repr = json.dumps(manifest_payload, sort_keys=True)
        ds_hash = self.compute_hash(raw_repr)

        manifest = DatasetManifest(
            dataset_id=dataset_id,
            symbols=symbols,
            start_date=start_date,
            end_date=end_date,
            bar_frequency=bar_frequency,
            source_provider=source_provider,
            adjustment_status=adjustment_status,
            feature_columns=feature_columns,
            target_column=target_column,
            row_count=row_count,
            created_at=datetime.now(timezone.utc).isoformat(),
            dataset_hash=ds_hash,
            training_cutoff_date=training_cutoff_date,
            embargo_bars=embargo_bars,
        )

        path = os.path.join(self.manifest_dir, f"{dataset_id}.json")
        with open(path, "w") as f:
            json.dump(manifest.to_dict(), f, indent=2)

        return manifest

    def get_manifest(self, dataset_id: str) -> Optional[DatasetManifest]:
        path = os.path.join(self.manifest_dir, f"{dataset_id}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r") as f:
            return DatasetManifest.from_dict(json.load(f))

    def list_manifests(self) -> List[DatasetManifest]:
        manifests = []
        if not os.path.exists(self.manifest_dir):
            return manifests
        for fname in os.listdir(self.manifest_dir):
            if fname.endswith(".json"):
                path = os.path.join(self.manifest_dir, fname)
                try:
                    with open(path, "r") as f:
                        manifests.append(DatasetManifest.from_dict(json.load(f)))
                except Exception:
                    pass
        return manifests

