"""Walk-forward time-series validation engine with expanding/rolling windows, purging, and embargoes."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any, Dict, Generator, List, Optional
import numpy as np
import pandas as pd

from src.validation.purged_split import PurgedTimeSeriesSplitter


@dataclass
class WalkForwardFold:
    """Represents a single validated chronological fold in walk-forward evaluation."""
    fold_id: int
    train_indices: np.ndarray
    val_indices: np.ndarray
    test_indices: np.ndarray
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    val_start: pd.Timestamp
    val_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    metadata: Dict[str, Any] = field(default_factory=dict)


class WalkForwardEngine:
    """Generates strictly chronological, purged, and embargoed walk-forward evaluation folds."""

    def __init__(
        self,
        n_splits: int = 3,
        train_ratio: float = 0.60,
        val_ratio: float = 0.20,
        test_ratio: float = 0.20,
        window_type: str = "EXPANDING",  # "EXPANDING" or "ROLLING"
        label_duration: timedelta = timedelta(minutes=60),
        embargo_duration: timedelta = timedelta(minutes=60),
    ) -> None:
        if not np.isclose(train_ratio + val_ratio + test_ratio, 1.0):
            raise ValueError("train_ratio + val_ratio + test_ratio must sum to 1.0")
        self.n_splits = n_splits
        self.train_ratio = train_ratio
        self.val_ratio = val_ratio
        self.test_ratio = test_ratio
        self.window_type = window_type.upper()
        self.splitter = PurgedTimeSeriesSplitter(
            label_duration=label_duration,
            embargo_duration=embargo_duration,
        )

    def generate_folds(self, df: pd.DataFrame) -> List[WalkForwardFold]:
        """
        Generates purged chronological walk-forward folds from a time-series dataframe.
        """
        if df.empty:
            return []

        clean_df = df.sort_values("timestamp").reset_index(drop=True)
        timestamps = pd.to_datetime(clean_df["timestamp"], utc=True)
        n_samples = len(clean_df)
        
        # Calculate step size based on test partitions
        # Each split advances the test window chronologically
        test_size = int(n_samples * (self.test_ratio / self.n_splits))
        val_size = int(n_samples * (self.val_ratio / self.n_splits))
        
        if test_size < 10 or val_size < 10:
            raise ValueError(f"Insufficient samples ({n_samples}) for {self.n_splits} splits with purging.")

        folds: List[WalkForwardFold] = []
        base_train_size = int(n_samples * self.train_ratio)

        for fold_idx in range(self.n_splits):
            if self.window_type == "EXPANDING":
                raw_train_start_idx = 0
            else:  # ROLLING
                raw_train_start_idx = fold_idx * test_size

            raw_train_end_idx = base_train_size + (fold_idx * test_size)
            raw_val_start_idx = raw_train_end_idx
            raw_val_end_idx = raw_val_start_idx + val_size
            raw_test_start_idx = raw_val_end_idx
            raw_test_end_idx = min(n_samples, raw_test_start_idx + test_size)

            if raw_test_start_idx >= n_samples or raw_val_start_idx >= n_samples:
                break

            raw_train_idx = np.arange(raw_train_start_idx, raw_train_end_idx)
            raw_val_idx = np.arange(raw_val_start_idx, raw_val_end_idx)
            raw_test_idx = np.arange(raw_test_start_idx, raw_test_end_idx)

            val_start_ts = timestamps.iloc[raw_val_start_idx]
            val_end_ts = timestamps.iloc[raw_val_end_idx - 1]
            test_start_ts = timestamps.iloc[raw_test_start_idx]
            test_end_ts = timestamps.iloc[raw_test_end_idx - 1]

            # 1. Purge training set of observations whose labels reach into validation
            purged_train_idx = self.splitter.purge_train_set(
                train_indices=raw_train_idx,
                timestamps=timestamps,
                eval_start_time=val_start_ts,
            )

            # 2. Apply embargo between validation and test
            embargoed_test_idx = self.splitter.apply_embargo(
                eval_indices=raw_test_idx,
                timestamps=timestamps,
                prior_eval_end_time=val_end_ts,
            )

            if len(purged_train_idx) == 0 or len(raw_val_idx) == 0 or len(embargoed_test_idx) == 0:
                continue

            train_start_ts = timestamps.iloc[purged_train_idx[0]]
            train_end_ts = timestamps.iloc[purged_train_idx[-1]]

            fold = WalkForwardFold(
                fold_id=fold_idx + 1,
                train_indices=purged_train_idx,
                val_indices=raw_val_idx,
                test_indices=embargoed_test_idx,
                train_start=train_start_ts,
                train_end=train_end_ts,
                val_start=val_start_ts,
                val_end=val_end_ts,
                test_start=timestamps.iloc[embargoed_test_idx[0]],
                test_end=test_end_ts,
                metadata={
                    "window_type": self.window_type,
                    "purged_train_count": len(raw_train_idx) - len(purged_train_idx),
                    "embargoed_test_count": len(raw_test_idx) - len(embargoed_test_idx),
                    "train_samples": len(purged_train_idx),
                    "val_samples": len(raw_val_idx),
                    "test_samples": len(embargoed_test_idx),
                },
            )
            folds.append(fold)

        return folds
