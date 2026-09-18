# Broker Reconciliation Design (Phases F28, F35)

## 1. Reconciliation Intervals
Reconciliation executes at three critical intervals:
1. **Startup**: Verifies paper account status and initial flat portfolio.
2. **Intraday Periodic**: Compares internal position counts against broker open positions.
3. **Post-Close**: Validates 100% flat portfolio and final cash/equity balance.

## 2. Mismatch Action
Any unexplained position or order mismatch forces `ReconciliationStatus.FAILED` and halts further trading.
