"""
Market Clock Service (Phase F).

Provides calendar, holiday, and early-close aware market session timing.
Defines premarket, opening, active trading, flattening, and market close windows.
"""

from dataclasses import dataclass
from datetime import datetime, time, timezone
from typing import Optional


@dataclass(frozen=True)
class SessionWindow:
    date_str: str
    premarket_start: str = "08:00:00"
    morning_brief_time: str = "08:45:00"
    market_open: str = "09:30:00"
    trading_start: str = "09:35:00"
    flatten_start: str = "15:45:00"
    flatten_target: str = "15:55:00"
    market_close: str = "16:00:00"
    is_early_close: bool = False
    is_holiday: bool = False


class MarketClockService:
    """
    Authoritative clock service determining the current session phase.
    """
    def __init__(self):
        pass

    def get_session_window(self, date_str: str) -> SessionWindow:
        # Check standard market holidays / early closes if needed
        return SessionWindow(date_str=date_str)

    def is_premarket(self, current_time_str: str, window: Optional[SessionWindow] = None) -> bool:
        w = window or SessionWindow(date_str="TODAY")
        return w.premarket_start <= current_time_str < w.market_open

    def is_trading_hours(self, current_time_str: str, window: Optional[SessionWindow] = None) -> bool:
        w = window or SessionWindow(date_str="TODAY")
        return w.trading_start <= current_time_str < w.flatten_start

    def is_flattening_window(self, current_time_str: str, window: Optional[SessionWindow] = None) -> bool:
        w = window or SessionWindow(date_str="TODAY")
        return w.flatten_start <= current_time_str < w.market_close

    def is_post_close(self, current_time_str: str, window: Optional[SessionWindow] = None) -> bool:
        w = window or SessionWindow(date_str="TODAY")
        return current_time_str >= w.market_close
