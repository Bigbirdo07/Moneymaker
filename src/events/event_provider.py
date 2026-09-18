"""
Event Provider Abstractions and Implementations.

Defines the core interfaces for event ingestion:
- EventProvider (Base)
- EarningsCalendarProvider
- TradingHaltProvider
- CorporateActionsProvider
- RegulatoryEventProvider
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import hashlib

from src.events.event_types import EventRecord, EventFamily, EventSeverity


class EventProvider(ABC):
    """
    Abstract base interface for event data providers.
    """
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    def get_events_for_symbol(self, symbol: str, start_timestamp: str, end_timestamp: str) -> List[EventRecord]:
        """
        Retrieves events for a specific symbol within the timestamp window.
        """
        pass

    @abstractmethod
    def get_all_active_events(self, as_of_timestamp: str) -> List[EventRecord]:
        """
        Retrieves all currently active events point-in-time.
        """
        pass


class EarningsCalendarProvider(EventProvider):
    """
    Provider specialized for corporate earnings release schedules.
    """
    def __init__(self, earnings_records: Optional[List[Dict[str, Any]]] = None):
        self._records = earnings_records or []

    @property
    def provider_name(self) -> str:
        return "EARNINGS_CALENDAR_PROVIDER"

    def get_events_for_symbol(self, symbol: str, start_timestamp: str, end_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            if rec.get("symbol") == symbol:
                src_ts = rec.get("source_timestamp", "")
                if start_timestamp <= src_ts <= end_timestamp:
                    results.append(self._parse_record(rec))
        return results

    def get_all_active_events(self, as_of_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            ev = self._parse_record(rec)
            if ev.is_active_at(as_of_timestamp):
                results.append(ev)
        return results

    def _parse_record(self, r: Dict[str, Any]) -> EventRecord:
        raw_hash = hashlib.sha256(f"{r.get('symbol')}_{r.get('date')}_{r.get('timing')}".encode()).hexdigest()[:16]
        return EventRecord(
            event_id=r.get("event_id", f"EARN_{r.get('symbol')}_{r.get('date')}"),
            symbol=r["symbol"],
            event_type=EventFamily.EARNINGS,
            event_subtype=r.get("timing", "BEFORE_OPEN"),
            source=self.provider_name,
            source_timestamp=r.get("source_timestamp", f"{r.get('date')}T00:00:00Z"),
            effective_timestamp=r.get("effective_timestamp", f"{r.get('date')}T09:30:00Z"),
            expiry_timestamp=r.get("expiry_timestamp", f"{r.get('date')}T16:00:00Z"),
            severity=EventSeverity.HIGH,
            confidence=float(r.get("confidence", 0.98)),
            known_before_open=r.get("timing") in ("BEFORE_OPEN", "PREMARKET"),
            raw_reference_hash=raw_hash,
            metadata=r,
        )


class TradingHaltProvider(EventProvider):
    """
    Provider specialized for exchange trading halts (LULD, regulatory, etc.).
    """
    def __init__(self, halt_records: Optional[List[Dict[str, Any]]] = None):
        self._records = halt_records or []

    @property
    def provider_name(self) -> str:
        return "EXCHANGE_TRADING_HALT_PROVIDER"

    def get_events_for_symbol(self, symbol: str, start_timestamp: str, end_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            if rec.get("symbol") == symbol:
                src_ts = rec.get("source_timestamp", "")
                if start_timestamp <= src_ts <= end_timestamp:
                    results.append(self._parse_record(rec))
        return results

    def get_all_active_events(self, as_of_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            ev = self._parse_record(rec)
            if ev.is_active_at(as_of_timestamp):
                results.append(ev)
        return results

    def _parse_record(self, r: Dict[str, Any]) -> EventRecord:
        raw_hash = hashlib.sha256(f"{r.get('symbol')}_{r.get('halt_time')}".encode()).hexdigest()[:16]
        return EventRecord(
            event_id=r.get("event_id", f"HALT_{r.get('symbol')}_{r.get('halt_time')}"),
            symbol=r["symbol"],
            event_type=EventFamily.TRADING_HALT,
            event_subtype=r.get("halt_reason", "HALT_ACTIVE"),
            source=self.provider_name,
            source_timestamp=r.get("source_timestamp", r.get("halt_time", "")),
            effective_timestamp=r.get("halt_time", ""),
            expiry_timestamp=r.get("resumption_time", "2099-12-31T23:59:59Z"),
            severity=EventSeverity.CRITICAL,
            confidence=1.0,
            known_before_open=False,
            raw_reference_hash=raw_hash,
            metadata=r,
        )


class RegulatoryEventProvider(EventProvider):
    """
    Provider for FDA PDUFA dates, Advisory Committee meetings, and regulatory rulings.
    """
    def __init__(self, reg_records: Optional[List[Dict[str, Any]]] = None):
        self._records = reg_records or []

    @property
    def provider_name(self) -> str:
        return "REGULATORY_FDA_PROVIDER"

    def get_events_for_symbol(self, symbol: str, start_timestamp: str, end_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            if rec.get("symbol") == symbol:
                src_ts = rec.get("source_timestamp", "")
                if start_timestamp <= src_ts <= end_timestamp:
                    results.append(self._parse_record(rec))
        return results

    def get_all_active_events(self, as_of_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            ev = self._parse_record(rec)
            if ev.is_active_at(as_of_timestamp):
                results.append(ev)
        return results

    def _parse_record(self, r: Dict[str, Any]) -> EventRecord:
        raw_hash = hashlib.sha256(f"{r.get('symbol')}_{r.get('event_type')}_{r.get('date')}".encode()).hexdigest()[:16]
        return EventRecord(
            event_id=r.get("event_id", f"REG_{r.get('symbol')}_{r.get('date')}"),
            symbol=r["symbol"],
            event_type=EventFamily.CLINICAL_FDA_BINARY if "FDA" in r.get("event_type", "") else EventFamily.REGULATORY_DECISION,
            event_subtype=r.get("event_subtype", "PDUFA_DECISION"),
            source=self.provider_name,
            source_timestamp=r.get("source_timestamp", f"{r.get('date')}T00:00:00Z"),
            effective_timestamp=r.get("effective_timestamp", f"{r.get('date')}T09:30:00Z"),
            expiry_timestamp=r.get("expiry_timestamp", f"{r.get('date')}T20:00:00Z"),
            severity=EventSeverity.CRITICAL if "FDA" in r.get("event_type", "") else EventSeverity.HIGH,
            confidence=float(r.get("confidence", 0.95)),
            known_before_open=True,
            raw_reference_hash=raw_hash,
            metadata=r,
        )


class CorporateActionsProvider(EventProvider):
    """
    Provider for corporate restructuring, offerings, M&A, and bankruptcy filings.
    """
    def __init__(self, action_records: Optional[List[Dict[str, Any]]] = None):
        self._records = action_records or []

    @property
    def provider_name(self) -> str:
        return "CORPORATE_ACTIONS_PROVIDER"

    def get_events_for_symbol(self, symbol: str, start_timestamp: str, end_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            if rec.get("symbol") == symbol:
                src_ts = rec.get("source_timestamp", "")
                if start_timestamp <= src_ts <= end_timestamp:
                    results.append(self._parse_record(rec))
        return results

    def get_all_active_events(self, as_of_timestamp: str) -> List[EventRecord]:
        results = []
        for rec in self._records:
            ev = self._parse_record(rec)
            if ev.is_active_at(as_of_timestamp):
                results.append(ev)
        return results

    def _parse_record(self, r: Dict[str, Any]) -> EventRecord:
        family_str = r.get("event_family", "MERGER_ACQUISITION")
        fam = EventFamily(family_str) if family_str in EventFamily.__members__ else EventFamily.MATERIAL_CORPORATE_ACTION
        raw_hash = hashlib.sha256(f"{r.get('symbol')}_{family_str}_{r.get('date')}".encode()).hexdigest()[:16]
        return EventRecord(
            event_id=r.get("event_id", f"CORP_{r.get('symbol')}_{r.get('date')}"),
            symbol=r["symbol"],
            event_type=fam,
            event_subtype=r.get("event_subtype", "DEFINITIVE_AGREEMENT"),
            source=self.provider_name,
            source_timestamp=r.get("source_timestamp", f"{r.get('date')}T08:00:00Z"),
            effective_timestamp=r.get("effective_timestamp", f"{r.get('date')}T09:30:00Z"),
            expiry_timestamp=r.get("expiry_timestamp", f"{r.get('date')}T16:00:00Z"),
            severity=EventSeverity.CRITICAL if fam == EventFamily.BANKRUPTCY_DISTRESS else EventSeverity.HIGH,
            confidence=float(r.get("confidence", 0.99)),
            known_before_open=True,
            raw_reference_hash=raw_hash,
            metadata=r,
        )
