# Drawdown Throttling State Machine

## 1. State Transitions
| Account State | Daily DD Trigger | Rolling DD Trigger | Risk Budget Multiplier | Trading Allowed |
| :--- | :--- | :--- | :--- | :--- |
| **`NORMAL`** | < 1.0% | < 4.0% | 1.00x | Yes |
| **`REDUCED_RISK`** | >= 1.0% | >= 4.0% | 0.50x | Yes |
| **`CASH_PRESERVATION`** | >= 1.5% | >= 7.0% | 0.00x | No |
| **`HALTED`** | - | >= 10.0% | 0.00x | No |