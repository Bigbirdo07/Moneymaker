# Event Service Health & Degradation Policy

## 1. Feed Health State Machine
- **`EVENT_SERVICE_HEALTHY`**: All upstream feeds operational. Standard policy execution.
- **`EVENT_SERVICE_DEGRADED`**: Intermittent heartbeat delays. Action: `REDUCE_RISK` (50% size limit) with operational warning.
- **`EVENT_SERVICE_UNAVAILABLE`**: Complete upstream provider outage. Action: **`STRICT_VETO`** (No new positions authorized).

## 2. Fail-Safe Principle
> **Safety > Coverage**: In the event of event feed failure, the system NEVER assumes a clean state.