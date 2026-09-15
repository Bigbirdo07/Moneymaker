"""Tests for trading calendar session awareness and timezone normalization."""

from datetime import datetime, timezone
import pandas as pd
import pytest

from src.core.types import SessionType
from src.data.calendar import TradingCalendar


def test_session_type_determination() -> None:
    cal = TradingCalendar()

    # Wednesday 2026-01-07 10:00 AM ET = 15:00 UTC (Regular Session)
    dt_regular = datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc)
    assert cal.get_session_type(dt_regular) == SessionType.REGULAR
    assert cal.is_regular_session(dt_regular) is True

    # Wednesday 2026-01-07 08:00 AM ET = 13:00 UTC (Premarket)
    dt_pre = datetime(2026, 1, 7, 13, 0, tzinfo=timezone.utc)
    assert cal.get_session_type(dt_pre) == SessionType.PREMARKET
    assert cal.is_regular_session(dt_pre) is False

    # Wednesday 2026-01-07 17:00 PM ET = 22:00 UTC (Postmarket)
    dt_post = datetime(2026, 1, 7, 22, 0, tzinfo=timezone.utc)
    assert cal.get_session_type(dt_post) == SessionType.POSTMARKET

    # Saturday 2026-01-10 12:00 PM ET (Closed)
    dt_weekend = datetime(2026, 1, 10, 17, 0, tzinfo=timezone.utc)
    assert cal.get_session_type(dt_weekend) == SessionType.CLOSED


def test_minutes_from_open_and_close() -> None:
    cal = TradingCalendar()
    # Wednesday 10:00 ET (30 mins from open, 360 mins to close)
    dt = datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc)
    assert cal.get_minutes_from_open(dt) == pytest.approx(30.0)
    assert cal.get_minutes_to_close(dt) == pytest.approx(360.0)


def test_filter_regular_hours() -> None:
    cal = TradingCalendar()
    # Create 3 timestamps: premarket, regular, weekend
    timestamps = [
        datetime(2026, 1, 7, 13, 0, tzinfo=timezone.utc), # 8:00 ET (pre)
        datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc), # 10:00 ET (regular)
        datetime(2026, 1, 10, 15, 0, tzinfo=timezone.utc), # Weekend
    ]
    df = pd.DataFrame({"timestamp": timestamps, "close": [100.0, 101.0, 102.0]})
    filtered = cal.filter_regular_hours(df)
    assert len(filtered) == 1
    assert filtered.iloc[0]["close"] == 101.0
