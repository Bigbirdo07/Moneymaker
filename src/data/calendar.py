"""Trading calendar and market session management for US Equities."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional, Set
import zoneinfo
import pandas as pd

from src.core.types import SessionType

ET_TZ = zoneinfo.ZoneInfo("America/New_York")
UTC_TZ = zoneinfo.ZoneInfo("UTC")

# Standard US Equity Session Times (Eastern Time)
PREMARKET_OPEN = time(4, 0)
REGULAR_OPEN = time(9, 30)
REGULAR_CLOSE = time(16, 0)
POSTMARKET_CLOSE = time(20, 0)


class TradingCalendar:
    """Session-aware US equity trading calendar."""

    def __init__(self, holidays: Optional[Set[date]] = None) -> None:
        self.holidays = holidays or set()

    @staticmethod
    def to_eastern(ts: datetime | pd.Timestamp) -> datetime:
        """Converts any timestamp to Eastern Time."""
        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime()
        if ts.tzinfo is None:
            # Assume UTC if naive
            ts = ts.replace(tzinfo=UTC_TZ)
        return ts.astimezone(ET_TZ)

    @staticmethod
    def to_utc(ts: datetime | pd.Timestamp) -> datetime:
        """Converts any timestamp to UTC."""
        if isinstance(ts, pd.Timestamp):
            ts = ts.to_pydatetime()
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC_TZ)
        return ts.astimezone(UTC_TZ)

    def is_trading_day(self, dt: date | datetime | pd.Timestamp) -> bool:
        """Checks if a date is a weekday and not a known holiday."""
        if isinstance(dt, (datetime, pd.Timestamp)):
            dt = self.to_eastern(dt).date()
        if dt.weekday() >= 5:  # Saturday or Sunday
            return False
        if dt in self.holidays:
            return False
        return True

    def get_session_type(self, ts: datetime | pd.Timestamp) -> SessionType:
        """Determines the market session type for a given timestamp."""
        et_dt = self.to_eastern(ts)
        if not self.is_trading_day(et_dt.date()):
            return SessionType.CLOSED

        t = et_dt.time()
        if PREMARKET_OPEN <= t < REGULAR_OPEN:
            return SessionType.PREMARKET
        elif REGULAR_OPEN <= t < REGULAR_CLOSE:
            return SessionType.REGULAR
        elif REGULAR_CLOSE <= t < POSTMARKET_CLOSE:
            return SessionType.POSTMARKET
        else:
            return SessionType.CLOSED

    def is_regular_session(self, ts: datetime | pd.Timestamp) -> bool:
        """Checks if the timestamp is during regular market hours (09:30 - 16:00 ET)."""
        return self.get_session_type(ts) == SessionType.REGULAR

    def filter_regular_hours(self, df: pd.DataFrame, timestamp_col: str = "timestamp") -> pd.DataFrame:
        """Filters DataFrame to include only regular session bars (09:30 to 16:00 ET)."""
        if df.empty:
            return df
        
        # Ensure UTC datetime index or series
        ts_series = df[timestamp_col]
        if not pd.api.types.is_datetime64_any_dtype(ts_series):
            ts_series = pd.to_datetime(ts_series, utc=True)
        elif ts_series.dt.tz is None:
            ts_series = ts_series.dt.tz_localize("UTC")
        else:
            ts_series = ts_series.dt.tz_convert("UTC")

        et_series = ts_series.dt.tz_convert("America/New_York")
        
        # Weekdays only (Monday=0 ... Friday=4)
        is_weekday = et_series.dt.weekday < 5
        # Regular hours (09:30 <= time < 16:00)
        time_part = et_series.dt.time
        is_regular_time = (time_part >= REGULAR_OPEN) & (time_part < REGULAR_CLOSE)
        
        mask = is_weekday & is_regular_time
        return df[mask].copy()

    @staticmethod
    def get_minutes_from_open(ts: datetime | pd.Timestamp) -> float:
        """Returns the number of minutes elapsed from regular session open (09:30 ET)."""
        et_dt = TradingCalendar.to_eastern(ts)
        open_dt = et_dt.replace(hour=9, minute=30, second=0, microsecond=0)
        delta = (et_dt - open_dt).total_seconds() / 60.0
        return max(0.0, delta)

    @staticmethod
    def get_minutes_to_close(ts: datetime | pd.Timestamp) -> float:
        """Returns the number of minutes remaining until regular session close (16:00 ET)."""
        et_dt = TradingCalendar.to_eastern(ts)
        close_dt = et_dt.replace(hour=16, minute=0, second=0, microsecond=0)
        delta = (close_dt - et_dt).total_seconds() / 60.0
        return max(0.0, delta)
