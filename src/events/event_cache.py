"""
Point-in-Time Event Cache & Lookahead Firewall.

Maintains an in-memory or indexed cache of market events with strict
point-in-time publication checks to guarantee zero lookahead bias.
"""

from typing import Dict, List, Optional, Set
from collections import defaultdict
import bisect

from src.events.event_types import EventRecord, EventFamily


class PointInTimeEventCache:
    """
    Guarantees that queries as of timestamp T only expose events where:
        source_timestamp <= T < expiry_timestamp
    """
    def __init__(self):
        # Symbol -> list of EventRecords
        self._events_by_symbol: Dict[str, List[EventRecord]] = defaultdict(list)
        # Event ID set for deduplication
        self._seen_event_ids: Set[str] = set()

    def add_event(self, event: EventRecord) -> bool:
        """
        Adds an event record to the cache if not already present.
        Returns True if added, False if duplicate.
        """
        if event.event_id in self._seen_event_ids:
            return False
        self._seen_event_ids.add(event.event_id)
        self._events_by_symbol[event.symbol].append(event)
        # Keep sorted by source_timestamp
        self._events_by_symbol[event.symbol].sort(key=lambda x: x.source_timestamp)
        return True

    def add_events(self, events: List[EventRecord]) -> int:
        added = 0
        for ev in events:
            if self.add_event(ev):
                added += 1
        return added

    def get_active_events(self, symbol: str, as_of_timestamp: str) -> List[EventRecord]:
        """
        Returns all active events for symbol visible strictly as of as_of_timestamp.
        Guarantees source_timestamp <= as_of_timestamp < expiry_timestamp.
        """
        if symbol not in self._events_by_symbol:
            return []

        active = []
        for ev in self._events_by_symbol[symbol]:
            # Lookahead check: cannot observe event before its publication
            if ev.source_timestamp > as_of_timestamp:
                continue
            # Expiration check: event must still be active
            if as_of_timestamp < ev.expiry_timestamp:
                active.append(ev)
        return active

    def get_all_active_events(self, as_of_timestamp: str) -> Dict[str, List[EventRecord]]:
        """
        Returns all active events across all symbols as of as_of_timestamp.
        """
        result = {}
        for sym in self._events_by_symbol.keys():
            acts = self.get_active_events(sym, as_of_timestamp)
            if acts:
                result[sym] = acts
        return result

    def get_market_wide_events(self, as_of_timestamp: str) -> List[EventRecord]:
        """
        Returns market-wide active events (symbol == 'MARKET' or 'SPY' or 'ALL').
        """
        market_events = []
        for sym in ["MARKET", "SPY", "ALL", "GLOBAL"]:
            market_events.extend(self.get_active_events(sym, as_of_timestamp))
        return market_events

    def clear(self) -> None:
        self._events_by_symbol.clear()
        self._seen_event_ids.clear()
