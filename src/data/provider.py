"""Market data provider abstraction and caching layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional
import pandas as pd

from src.data.loader import HistoricalDataLoader
from src.data.schema import MarketDataSchema
from src.data.validation import DataValidator
from src.core.logging import get_logger

logger = get_logger("data.provider")


class HistoricalMarketDataProvider(ABC):
    """Abstract interface for historical market data retrieval."""

    @abstractmethod
    def fetch_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = "5m",
    ) -> pd.DataFrame:
        """Fetches normalized and validated historical OHLCV bars."""
        pass


class LocalParquetDataProvider(HistoricalMarketDataProvider):
    """Loads historical bars from local Parquet store."""

    def __init__(self, data_dir: Path | str = "data/processed") -> None:
        self.data_dir = Path(data_dir)
        self.loader = HistoricalDataLoader(processed_data_dir=self.data_dir)

    def fetch_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = "5m",
    ) -> pd.DataFrame:
        file_path = self.data_dir / f"{symbol}_{timeframe}.parquet"
        if not file_path.exists():
            raise FileNotFoundError(f"Local parquet file not found for {symbol} at {file_path}")
        df = self.loader.load_parquet(file_path, symbol=symbol)
        
        # Filter date range
        start_ts = pd.to_datetime(start_date, utc=True)
        end_ts = pd.to_datetime(end_date, utc=True)
        mask = (df["timestamp"] >= start_ts) & (df["timestamp"] <= end_ts)
        return df[mask].reset_index(drop=True)


class SyntheticDataProvider(HistoricalMarketDataProvider):
    """Generates synthetic high-fidelity 5m bars for reproducible automated tests."""

    def fetch_bars(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        timeframe: str = "5m",
        seed: int = 42,
    ) -> pd.DataFrame:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        num_days = max(1, (end_dt - start_dt).days + 1)
        return HistoricalDataLoader.generate_synthetic_5m_data(
            symbol=symbol,
            start_date=start_date,
            num_days=num_days,
            seed=seed,
        )
