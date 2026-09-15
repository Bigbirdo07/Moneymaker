"""Multiple-testing accounting, trial tracking ledger, and Family-Wise Error Rate controls."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class TrialRecord:
    """Record of a single experimental strategy or parameter evaluation."""
    trial_id: str
    horizon_minutes: int
    target_name: str
    model_type: str
    threshold_value: float
    features_count: int
    gross_return_pct: float
    net_return_pct: float
    sharpe_ratio: float
    profit_factor: float
    p_value: float
    is_bonferroni_significant: bool = False
    is_fdr_significant: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class MultipleTestingLedger:
    """Tracks cumulative hypothesis tests and calculates multiple-testing corrections."""

    def __init__(self, alpha: float = 0.05) -> None:
        self.alpha = alpha
        self.trials: List[TrialRecord] = []

    def record_trial(self, trial: TrialRecord) -> None:
        """Appends a new trial record."""
        self.trials.append(trial)

    def apply_corrections(self) -> None:
        """Computes Bonferroni and Benjamini-Hochberg False Discovery Rate (FDR) adjustments."""
        k = len(self.trials)
        if k == 0:
            return

        bonferroni_thresh = self.alpha / k

        # Sort trials by p-value ascending for BH FDR
        sorted_indices = np.argsort([t.p_value for t in self.trials])
        m = len(self.trials)

        for rank, idx in enumerate(sorted_indices):
            p = self.trials[idx].p_value
            bh_thresh = (rank + 1) / m * self.alpha
            self.trials[idx].is_bonferroni_significant = (p <= bonferroni_thresh)
            self.trials[idx].is_fdr_significant = (p <= bh_thresh)

    def to_dataframe(self) -> pd.DataFrame:
        """Converts trial records to a summary DataFrame."""
        if not self.trials:
            return pd.DataFrame()
        return pd.DataFrame([asdict(t) for t in self.trials])
