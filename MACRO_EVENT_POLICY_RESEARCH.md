# Macroeconomic Event Policy & Calendar Risk (Phases E7, E8)

## 1. Scheduled High-Impact Releases
The `MacroEventProvider` monitors high-importance economic releases:
- Consumer Price Index (CPI)
- Producer Price Index (PPI)
- FOMC Rate Decisions & Press Conferences
- Non-Farm Payrolls (Jobs Report)
- GDP Releases

## 2. Macro Release Window Throttling Policy
When a high-importance macro release is scheduled within 15 minutes of session evaluation:
- Session Gate is deterministically downgraded to **CAUTION** or **NO_GO**.
- Position sizing risk multiplier is automatically scaled down to 0.50x.
- Prevents catastrophic slippage and spread widening during headline news releases.
