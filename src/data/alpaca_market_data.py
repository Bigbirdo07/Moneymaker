"""
Alpaca Historical Market Data Client & Ingestion Engine.
Fetches real 1-minute OHLCV bars via Alpaca Stocks Historical Bars API (IEX Feed),
enforces symbol normalization, rate limits, pagination, and SHA-256 provenance.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from dotenv import load_dotenv

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from src.core.logging import get_logger
from src.core.types import EvidenceClass
from src.data.calendar import ET_TZ, UTC_TZ, TradingCalendar

# Load environment variables safely
load_dotenv()
load_dotenv(Path.home() / ".env")

logger = get_logger("data.alpaca_market_data")


class RealDataContaminationError(Exception):
    """Raised if synthetic data generation is detected in real market data pipelines."""
    pass


@dataclass
class AlpacaBarRecord:
    """Canonical 1-minute bar record from Alpaca."""
    timestamp_utc: str
    timestamp_et: str
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    trade_count: Optional[int] = None
    feed: str = "IEX"
    provider: str = "ALPACA"
    evidence_class: str = EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AlpacaHistoricalDataClient:
    """
    Client for downloading and normalizing real historical 1-minute bars from Alpaca.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        raw_data_dir: Path | str = "data/raw/alpaca",
        processed_data_dir: Path | str = "data/processed/alpaca_1m",
        manifest_path: Path | str = "artifacts/provenance/alpaca_data_manifest.json",
    ) -> None:
        self.api_key = api_key or os.environ.get("APCA_API_KEY_ID")
        self.secret_key = secret_key or os.environ.get("APCA_API_SECRET_KEY")

        if not self.api_key or not self.secret_key:
            raise ValueError("Alpaca API credentials missing. Set APCA_API_KEY_ID and APCA_API_SECRET_KEY.")

        self.client = StockHistoricalDataClient(self.api_key, self.secret_key)
        self.raw_dir = Path(raw_data_dir)
        self.processed_dir = Path(processed_data_dir)
        self.manifest_path = Path(manifest_path)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.calendar = TradingCalendar()

        # Symbol mapping dictionary
        self.symbol_mapping: Dict[str, str] = {
            "BRK.B": "BRK.B",  # Alpaca IEX supports BRK.B directly
        }

    def get_provider_symbol(self, canonical_symbol: str) -> str:
        """Returns the Alpaca-compatible ticker symbol."""
        return self.symbol_mapping.get(canonical_symbol, canonical_symbol)

    def save_symbol_mapping(self, output_path: Path | str = "ALPACA_SYMBOL_MAPPING.json") -> None:
        """Saves canonical to provider symbol mapping JSON."""
        mapping_data = {
            "provider": "ALPACA",
            "feed": "IEX",
            "mappings": {
                "AAPL": "AAPL", "MSFT": "MSFT", "NVDA": "NVDA", "AMZN": "AMZN", "GOOGL": "GOOGL",
                "META": "META", "TSLA": "TSLA", "BRK.B": "BRK.B", "UNH": "UNH", "JNJ": "JNJ",
                "XOM": "XOM", "JPM": "JPM", "V": "V", "PG": "PG", "MA": "MA",
                "HD": "HD", "CVX": "CVX", "ABBV": "ABBV", "MRK": "MRK", "COST": "COST",
                "PEP": "PEP", "KO": "KO", "AVGO": "AVGO", "ADBE": "ADBE", "WMT": "WMT",
                "CSCO": "CSCO", "MCD": "MCD", "CRM": "CRM", "BAC": "BAC", "ACN": "ACN",
                "TMO": "TMO", "LIN": "LIN", "NFLX": "NFLX", "AMD": "AMD", "DIS": "DIS",
                "ABT": "ABT", "ORCL": "ORCL", "INTC": "INTC", "CMCSA": "CMCSA", "VZ": "VZ",
                "QCOM": "QCOM", "TXN": "TXN", "DHR": "DHR", "PM": "PM", "CAT": "CAT",
                "NKE": "NKE", "IBM": "IBM", "UNP": "UNP", "LOW": "LOW", "SPY": "SPY",
            },
            "special_handling": {
                "BRK.B": "Verified working with dot notation on Alpaca IEX"
            }
        }
        with open(output_path, "w") as f:
            json.dump(mapping_data, f, indent=2)

    def download_bars_for_symbol(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        feed: str = "iex",
        max_retries: int = 5,
        backoff_factor: float = 1.5,
    ) -> pd.DataFrame:
        """
        Downloads real 1-minute historical bars for a single symbol across date range.
        Handles pagination, rate-limiting, and retries.
        """
        provider_sym = self.get_provider_symbol(symbol)
        logger.info("Fetching real bars for %s (provider symbol: %s) from %s to %s",
                    symbol, provider_sym, start_date.isoformat(), end_date.isoformat())

        request = StockBarsRequest(
            symbol_or_symbols=[provider_sym],
            timeframe=TimeFrame.Minute,
            start=start_date,
            end=end_date,
            feed=feed,
        )

        for attempt in range(max_retries):
            try:
                bar_set = self.client.get_stock_bars(request)
                df = bar_set.df
                if df.empty:
                    logger.warning("Empty bars returned for %s", symbol)
                    return pd.DataFrame()

                # Reset multi-index if returned as (symbol, timestamp)
                if isinstance(df.index, pd.MultiIndex):
                    df = df.reset_index()
                elif df.index.name == "timestamp":
                    df = df.reset_index()

                # Add canonical metadata
                df["canonical_symbol"] = symbol
                df["feed"] = feed.upper()
                df["provider"] = "ALPACA"
                df["evidence_class"] = EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value

                return df

            except Exception as e:
                wait_time = backoff_factor ** attempt
                logger.warning("Attempt %s failed for %s: %s. Retrying in %ss...", attempt + 1, symbol, e, wait_time)
                time.sleep(wait_time)

        logger.error("Failed to download bars for %s after %s retries.", symbol, max_retries)
        return pd.DataFrame()

    def process_and_save_symbol_data(
        self,
        symbol: str,
        df: pd.DataFrame,
    ) -> Tuple[Path, str, int]:
        """
        Normalizes raw bars into standard schema, computes SHA-256 hash, and saves Parquet.
        """
        if df.empty:
            return Path(""), "", 0

        # Timestamp normalization
        if "timestamp" in df.columns:
            ts_utc = pd.to_datetime(df["timestamp"], utc=True)
            df["timestamp_utc"] = ts_utc.dt.strftime("%Y-%m-%d %H:%M:%S+00:00")
            df["timestamp_et"] = ts_utc.dt.tz_convert(ET_TZ).dt.strftime("%Y-%m-%d %H:%M:%S")
            df["timestamp"] = ts_utc.dt.tz_convert(ET_TZ).dt.tz_localize(None)

        # Ensure required columns
        for col in ["vwap", "trade_count"]:
            if col not in df.columns:
                df[col] = np.nan

        # Sort and deduplicate
        df = df.sort_values(by="timestamp_utc").drop_duplicates(subset=["timestamp_utc"]).reset_index(drop=True)

        # Save clean processed Parquet
        out_path = self.processed_dir / f"{symbol}_1m.parquet"
        df.to_parquet(out_path, index=False)

        raw_bytes = out_path.read_bytes()
        sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

        return out_path, sha256_hash, len(df)
