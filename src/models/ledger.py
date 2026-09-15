"""Immutable out-of-sample prediction ledger for research auditing and backtesting."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd


@dataclass(frozen=True)
class PredictionRecord:
    """A single out-of-sample prediction record."""
    prediction_id: str
    timestamp: datetime
    symbol: str
    model_id: str
    fold_id: int
    features_version: str
    p_up: float
    p_down: float
    predicted_label: int
    actual_label: Optional[int] = None
    expected_return: Optional[float] = None
    regime: str = "UNKNOWN"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class PredictionLedger:
    """Immutable in-memory and persistent storage for out-of-sample prediction records."""

    def __init__(self, ledger_dir: Path | str = "data/processed/predictions") -> None:
        self.ledger_dir = Path(ledger_dir)
        self._records: List[PredictionRecord] = []

    def record_prediction(self, record: PredictionRecord) -> None:
        """Appends a new prediction record to the ledger."""
        self._records.append(record)

    def record_batch(self, records: List[PredictionRecord]) -> None:
        """Appends multiple prediction records."""
        self._records.extend(records)

    def to_dataframe(self) -> pd.DataFrame:
        """Converts all recorded predictions to a DataFrame."""
        if not self._records:
            return pd.DataFrame()
        data = [asdict(r) for r in self._records]
        df = pd.DataFrame(data)
        return df

    def save_parquet(self, filename: str = "prediction_ledger.parquet") -> Path:
        """Persists the ledger to Parquet format."""
        self.ledger_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.ledger_dir / filename
        df = self.to_dataframe()
        if not df.empty:
            df.to_parquet(out_path, index=False)
        return out_path
