"""Historical market data ingestion, loading, and synthetic generation."""

from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import pandas as pd

from src.data.calendar import TradingCalendar, REGULAR_OPEN, REGULAR_CLOSE
from src.data.schema import MarketDataSchema
from src.data.validation import DataValidator, DataValidationReport
from src.core.logging import get_logger

logger = get_logger("data.loader")


class HistoricalDataLoader:
    """Loads, processes, and validates historical market data from local files or storage."""

    def __init__(
        self,
        raw_data_dir: Path | str = "data/raw",
        processed_data_dir: Path | str = "data/processed",
        validator: Optional[DataValidator] = None,
        calendar: Optional[TradingCalendar] = None,
    ) -> None:
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        self.validator = validator or DataValidator()
        self.calendar = calendar or TradingCalendar()

    def load_csv(self, file_path: Path | str, symbol: Optional[str] = None, filter_regular_hours: bool = True) -> pd.DataFrame:
        """Loads a CSV file into standard market data format."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Market data file not found: {path}")

        df = pd.read_csv(path)
        df = MarketDataSchema.enforce_types(df)
        if "symbol" not in df.columns and symbol:
            df["symbol"] = symbol

        if filter_regular_hours:
            df = self.calendar.filter_regular_hours(df)

        report = self.validator.validate(df, symbol=symbol)
        if not report.is_valid:
            logger.warning(f"Data validation issues for {symbol or path.stem}:\n{report.summary()}")
        return df

    def load_parquet(self, file_path: Path | str, symbol: Optional[str] = None, filter_regular_hours: bool = True) -> pd.DataFrame:
        """Loads a Parquet file into standard market data format."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Market data file not found: {path}")

        df = pd.read_parquet(path)
        df = MarketDataSchema.enforce_types(df)
        if "symbol" not in df.columns and symbol:
            df["symbol"] = symbol

        if filter_regular_hours:
            df = self.calendar.filter_regular_hours(df)

        report = self.validator.validate(df, symbol=symbol)
        if not report.is_valid:
            logger.warning(f"Data validation issues for {symbol or path.stem}:\n{report.summary()}")
        return df

    def save_processed_parquet(self, df: pd.DataFrame, symbol: str) -> Path:
        """Saves a validated dataset into the processed parquet store."""
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        out_path = self.processed_data_dir / f"{symbol}_5m.parquet"
        clean_df = MarketDataSchema.enforce_types(df)
        clean_df.to_parquet(out_path, index=False)
        return out_path

    @staticmethod
    def generate_synthetic_5m_data(
        symbol: str = "AAPL",
        start_date: str = "2026-01-05",
        num_days: int = 10,
        initial_price: float = 180.0,
        annualized_volatility: float = 0.25,
        seed: int = 42,
    ) -> pd.DataFrame:
        """Generates high-fidelity 5-minute intraday bars with realistic U-shaped volume curves and spreads."""
        np.random.seed(seed)
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        
        # 5-minute bars in regular session (09:30 to 16:00 is 6.5 hours = 78 bars/day)
        bars_per_day = 78
        dt_minutes = 5
        dt_annual = (5.0 / (252.0 * 6.5 * 60.0))
        bar_vol = annualized_volatility * np.sqrt(dt_annual)

        all_bars: List[dict] = []
        current_price = initial_price

        for day_idx in range(num_days):
            current_day = start_dt + timedelta(days=day_idx)
            # Skip weekends
            if current_day.weekday() >= 5:
                continue

            session_open = current_day.replace(hour=9, minute=30, second=0, microsecond=0, tzinfo=timezone.utc)

            for bar_idx in range(bars_per_day):
                bar_time = session_open + timedelta(minutes=bar_idx * dt_minutes)
                
                # U-shaped intraday volume profile
                u_factor = 1.0 + 2.0 * ((bar_idx / (bars_per_day - 1) - 0.5) ** 2)
                base_volume = np.random.normal(loc=15000 * u_factor, scale=2000 * u_factor)
                volume = max(100.0, float(base_volume))

                # Geometric Brownian Motion step
                ret = np.random.normal(loc=0.0, scale=bar_vol)
                open_p = current_price
                close_p = open_p * np.exp(ret)
                
                # High and Low with realistic intra-bar fluctuations
                intra_noise = np.abs(np.random.normal(loc=0.0, scale=bar_vol * 0.75, size=2))
                high_p = max(open_p, close_p) * (1.0 + float(intra_noise[0]))
                low_p = min(open_p, close_p) * (1.0 - float(intra_noise[1]))
                low_p = max(0.01, low_p)

                # Microstructure proxies
                vwap_p = (open_p + high_p + low_p + 2.0 * close_p) / 5.0
                spread = max(0.01, round(close_p * 0.0003, 4))
                bid = round(close_p - spread / 2.0, 4)
                ask = round(close_p + spread / 2.0, 4)
                trade_count = int(volume / np.random.uniform(50, 150))

                all_bars.append({
                    "timestamp": bar_time,
                    "symbol": symbol,
                    "open": round(open_p, 4),
                    "high": round(high_p, 4),
                    "low": round(low_p, 4),
                    "close": round(close_p, 4),
                    "volume": round(volume, 2),
                    "vwap": round(vwap_p, 4),
                    "bid": bid,
                    "ask": ask,
                    "spread": spread,
                    "trade_count": trade_count,
                })
                current_price = close_p

        df = pd.DataFrame(all_bars)
        return MarketDataSchema.enforce_types(df)
