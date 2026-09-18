# Event Provider Interface Specification

## Abstract Interface Definition
All event providers implement `EventProvider` with strict point-in-time semantics:
```python
class EventProvider(ABC):
    def get_events_for_symbol(self, symbol: str, start_ts: str, end_ts: str) -> List[EventRecord]: ...
    def get_all_active_events(self, as_of_ts: str) -> List[EventRecord]: ...
```

## Specialized Implementations
1. `EarningsCalendarProvider`: Ingests company reporting schedules and timestamps.
2. `TradingHaltProvider`: Subscribes to exchange halt/resumption feeds.
3. `RegulatoryEventProvider`: Tracks scheduled FDA PDUFA dates and AdCom meetings.
4. `CorporateActionsProvider`: Monitors SEC filings for offerings, M&A, and restructuring.