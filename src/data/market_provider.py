"""
Provider-neutral Live and Replay Market Data Provider Architecture for Phase 3A.
Ensures strict timestamp integrity, multi-timeframe streaming, staleness detection, and fail-closed safety.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass(frozen=True)
class QuoteEvent:
    """Live top-of-book quote event with complete timestamp attribution."""
    symbol: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    exchange_timestamp: pd.Timestamp
    provider_timestamp: pd.Timestamp
    received_timestamp: pd.Timestamp
    processing_timestamp: pd.Timestamp = field(default_factory=lambda: pd.Timestamp.now(tz=timezone.utc))

    @property
    def mid_price(self) -> float:
        return (self.bid + self.ask) / 2.0

    @property
    def spread_bps(self) -> float:
        if self.mid_price <= 0:
            return 0.0
        return ((self.ask - self.bid) / self.mid_price) * 10000.0


@dataclass(frozen=True)
class TradeEvent:
    """Individual market trade print with complete timestamp attribution."""
    symbol: str
    price: float
    size: float
    exchange_timestamp: pd.Timestamp
    provider_timestamp: pd.Timestamp
    received_timestamp: pd.Timestamp
    processing_timestamp: pd.Timestamp = field(default_factory=lambda: pd.Timestamp.now(tz=timezone.utc))


@dataclass(frozen=True)
class BarEvent:
    """Standardized OHLCV bar with start, close, and ingestion timestamps."""
    symbol: str
    timeframe: str  # e.g. "1m", "5m"
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float
    bar_start_timestamp: pd.Timestamp
    bar_close_timestamp: pd.Timestamp  # The exact moment the bar finalized
    provider_timestamp: pd.Timestamp
    received_timestamp: pd.Timestamp
    processing_timestamp: pd.Timestamp = field(default_factory=lambda: pd.Timestamp.now(tz=timezone.utc))


class LiveMarketDataProvider(ABC):
    """Abstract Base Class for live/forward market data feeds."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to market data provider."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect safely from market data provider."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check current connection health."""
        pass

    @abstractmethod
    def subscribe(self, symbols: List[str]) -> None:
        """Subscribe to live updates for target universe."""
        pass

    @abstractmethod
    def get_latest_quote(self, symbol: str) -> Optional[QuoteEvent]:
        """Fetch latest top-of-book quote."""
        pass

    @abstractmethod
    def get_latest_trade(self, symbol: str) -> Optional[TradeEvent]:
        """Fetch latest executed trade print."""
        pass

    @abstractmethod
    def get_latest_bar(self, symbol: str, timeframe: str = "5m") -> Optional[BarEvent]:
        """Fetch latest completed OHLCV bar."""
        pass

    @abstractmethod
    def get_bar_history(self, symbol: str, timeframe: str = "5m", count: int = 50) -> List[BarEvent]:
        """Fetch historical completed bars strictly up to the latest received timestamp."""
        pass

    def check_staleness(
        self,
        symbol: str,
        current_time: pd.Timestamp,
        max_quote_staleness_sec: float = 30.0,
        max_bar_staleness_sec: float = 330.0,  # 5m + 30s buffer
    ) -> Tuple[bool, str]:
        """
        Validate data feed freshness.
        Returns: (is_valid, reason)
        """
        if not self.is_connected():
            return False, "PROVIDER_DISCONNECTED"

        quote = self.get_latest_quote(symbol)
        if quote is None:
            return False, f"MISSING_QUOTE_{symbol}"

        quote_age_sec = (current_time - quote.received_timestamp).total_seconds()
        if quote_age_sec > max_quote_staleness_sec:
            return False, f"STALE_QUOTE_{symbol}_{quote_age_sec:.1f}s"

        bar = self.get_latest_bar(symbol, timeframe="5m")
        if bar is None:
            return False, f"MISSING_5M_BAR_{symbol}"

        bar_age_sec = (current_time - bar.received_timestamp).total_seconds()
        if bar_age_sec > max_bar_staleness_sec:
            return False, f"STALE_BAR_{symbol}_{bar_age_sec:.1f}s"

        if quote.bid <= 0 or quote.ask <= 0 or quote.ask < quote.bid:
            return False, f"INVALID_QUOTE_PRICES_{symbol}_{quote.bid}x{quote.ask}"

        return True, "FRESH"


class ReplayMarketDataProvider(LiveMarketDataProvider):
    """
    High-fidelity replay adapter for forward validation and shadow simulation.
    Feeds bars and quotes chronologically without lookahead.
    """

    def __init__(self, simulated_network_latency_ms: float = 25.0):
        self._connected = False
        self._subscribed_symbols: List[str] = []
        self._quotes: Dict[str, QuoteEvent] = {}
        self._trades: Dict[str, TradeEvent] = {}
        self._bars: Dict[str, Dict[str, List[BarEvent]]] = {}  # symbol -> timeframe -> list
        self.simulated_network_latency_ms = simulated_network_latency_ms

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def subscribe(self, symbols: List[str]) -> None:
        self._subscribed_symbols.extend([s for s in symbols if s not in self._subscribed_symbols])
        for s in symbols:
            if s not in self._bars:
                self._bars[s] = {"1m": [], "5m": []}

    def ingest_quote(self, quote: QuoteEvent) -> None:
        """Feed a new quote event."""
        if self._connected:
            self._quotes[quote.symbol] = quote

    def ingest_trade(self, trade: TradeEvent) -> None:
        """Feed a new trade event."""
        if self._connected:
            self._trades[trade.symbol] = trade

    def ingest_bar(self, bar: BarEvent) -> None:
        """Feed a finalized bar event."""
        if self._connected:
            if bar.symbol not in self._bars:
                self._bars[bar.symbol] = {"1m": [], "5m": []}
            if bar.timeframe not in self._bars[bar.symbol]:
                self._bars[bar.symbol][bar.timeframe] = []
            self._bars[bar.symbol][bar.timeframe].append(bar)

    def get_latest_quote(self, symbol: str) -> Optional[QuoteEvent]:
        return self._quotes.get(symbol)

    def get_latest_trade(self, symbol: str) -> Optional[TradeEvent]:
        return self._trades.get(symbol)

    def get_latest_bar(self, symbol: str, timeframe: str = "5m") -> Optional[BarEvent]:
        symbol_bars = self._bars.get(symbol, {}).get(timeframe, [])
        return symbol_bars[-1] if symbol_bars else None

    def get_bar_history(self, symbol: str, timeframe: str = "5m", count: int = 50) -> List[BarEvent]:
        symbol_bars = self._bars.get(symbol, {}).get(timeframe, [])
        return symbol_bars[-count:] if symbol_bars else []
