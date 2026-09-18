# Daily Loss Limit & Cash Preservation Analysis

## 1. Deterministic Daily Circuit Breaker
- **Caution Threshold (1.0% loss)**: Triggers `REDUCED_RISK` (50% risk budget multiplier).
- **Hard Stop Threshold (1.5% loss)**: Triggers `CASH_PRESERVATION` (0 new trades permitted for rest of session).
- Successfully truncates catastrophic intraday loss streaks with zero overnight risk.