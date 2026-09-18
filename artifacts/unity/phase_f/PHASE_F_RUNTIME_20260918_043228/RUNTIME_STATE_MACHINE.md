# Runtime State Machine Specification (Phase F2)

## 1. Canonical State Flow
`BOOTING` → `PREMARKET_INITIALIZING` → `PREMARKET_READY` → `WAITING_FOR_OPEN` → `MARKET_OPEN` → `TRADING_ACTIVE` → `FLATTENING` → `POST_CLOSE_RECONCILIATION` → `POST_CLOSE_JOURNAL` → `SESSION_COMPLETE`

## 2. Fail-Safe States
- `REDUCED_RISK`: SessionGate is CAUTION; 50% position sizing multiplier.
- `CASH_PRESERVATION`: SessionGate is NO_GO or daily loss limit hit; 0 new entries.
- `HALTED`: Triggered by operator kill switch, data outage, or unresolvable reconciliation failure.
