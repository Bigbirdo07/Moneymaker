# Alpaca Connection & Provider Symbol Audit

## 1. Authentication Status
- **Authentication**: `ALPACA_AUTHENTICATED=true`
- **Primary Endpoint**: Alpaca Stocks Historical Bars v2 (`https://data.alpaca.markets/v2/stocks/bars`)
- **Feed**: `IEX` (`ALPACA_IEX`)
- **Timeframe**: `1Min`

## 2. Connectivity Test Results
- **AAPL Test Rows**: 396 rows returned
- **BRK.B Test Rows**: 298 rows returned (verified using `BRK.B` symbol notation)
- **Status**: **PASS - READY FOR BULK INGESTION**
