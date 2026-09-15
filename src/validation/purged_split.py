"""Purged time-series splitting and embargo logic for overlapping financial return targets."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class SplitInterval:
    """Explicit time boundary interval for a fold component."""
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    indices: np.ndarray


class PurgedTimeSeriesSplitter:
    """
    Purges samples whose forward label horizons overlap subsequent evaluation sets,
    and applies embargo intervals after evaluation sets.
    """

    def __init__(
        self,
        label_duration: timedelta = timedelta(minutes=60),
        embargo_duration: timedelta = timedelta(minutes=60),
    ) -> None:
        self.label_duration = label_duration
        self.embargo_duration = embargo_duration

    def purge_train_set(
        self,
        train_indices: np.ndarray,
        timestamps: pd.Series,
        eval_start_time: pd.Timestamp,
    ) -> np.ndarray:
        """
        Removes any training observation whose forward label horizon (t + label_duration)
        extends into or beyond the evaluation period start (eval_start_time).
        """
        train_ts = timestamps.iloc[train_indices]
        # An observation t has label horizon ending at t + label_duration
        label_end = train_ts + self.label_duration
        # Keep only samples where label_end <= eval_start_time
        valid_mask = (label_end <= eval_start_time).values
        return train_indices[valid_mask]

    def apply_embargo(
        self,
        eval_indices: np.ndarray,
        timestamps: pd.Series,
        prior_eval_end_time: pd.Timestamp,
    ) -> np.ndarray:
        """
        Removes observations that occur within the embargo duration immediately
        following a prior evaluation period (to prevent auto-regressive leakage).
        """
        if len(eval_indices) == 0:
            return eval_indices
        eval_ts = timestamps.iloc[eval_indices]
        embargo_end = prior_eval_end_time + self.embargo_duration
        valid_mask = (eval_ts >= embargo_end).values
        return eval_indices[valid_mask]
