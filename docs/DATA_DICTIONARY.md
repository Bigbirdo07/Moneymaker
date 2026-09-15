# Data Dictionary

## Market Observation Schema
All market datasets ingested into the platform conform to the following schema:

| Column | Type | Description | Mandatory |
| :--- | :--- | :--- | :--- |
| `timestamp` | `datetime (UTC)` | Timestamp representing the start of the observation interval | YES |
| `symbol` | `string` | Ticker symbol (e.g. `AAPL`, `SPY`) | YES |
| `open` | `float64` | Opening traded price during the bar | YES |
| `high` | `float64` | Maximum traded price during the bar | YES |
| `low` | `float64` | Minimum traded price during the bar | YES |
| `close` | `float64` | Closing traded price during the bar | YES |
| `volume` | `float64` | Total traded share volume during the bar | YES |
| `vwap` | `float64` | Volume-weighted average price (if available) | NO |
| `bid` | `float64` | Best bid price at bar close | NO |
| `ask` | `float64` | Best ask price at bar close | NO |
| `spread` | `float64` | Bid-Ask spread (`ask - bid`) | NO |
| `trade_count` | `int64` | Number of distinct trades in bar | NO |

## Timestamp Conventions
- **Internal Timezone**: All internal timestamps are strictly stored and computed in **UTC**.
- **Market Session Mapping**: Converted to `America/New_York` to determine regular trading hours (`09:30:00` - `16:00:00` ET), premarket (`04:00:00` - `09:30:00` ET), or postmarket (`16:00:00` - `20:00:00` ET).
