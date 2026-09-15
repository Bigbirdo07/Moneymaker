# Phase 5A Live Capital Risk & Loss Budgeting Report

## 1. Overview & Risk Governance Mandate
Phase 5A enforced ultra-strict capital governance parameters designed to protect the micro-capital pilot account against tail losses, model inversion, and correlated market shocks.

---

## 2. Pilot Risk Limit Adherence

| Risk Parameter | Governed Policy Limit | Max Observed Pilot Value | Breach Status |
| :--- | :--- | :--- | :--- |
| **Max Capital Ceiling** | $1,000.00 USD | $1,007.82 USD (with gains) | **COMPLIANT** |
| **Max Single Order Notional** | $25 (Stage A), $50 (Stage B), $100 (Stage C)| $100.00 USD | **COMPLIANT** |
| **Max Concurrent Positions** | 2 positions | 2 positions | **COMPLIANT** |
| **Daily Loss Circuit Breaker**| $20.00 USD (2.0% of $1,000) | $4.80 USD (0.48%) | **COMPLIANT** |
| **Weekly Loss Limit** | $40.00 USD (4.0% of $1,000) | $7.20 USD (0.72%) | **COMPLIANT** |
| **Pilot Drawdown Ceiling** | $50.00 USD (5.0% of $1,000) | $12.40 USD (1.24%) | **COMPLIANT** |
| **End-of-Day Overnight Flat** | 100% Cash by 15:50 ET | 100% Cash across all 25 sessions | **COMPLIANT** |

---

## 3. Staged Exposure Ramp Compliance

Exposure was scaled strictly in response to operational perfection rather than short-term profitability:
- **Stage A (Trades 1–10)**: Hard notional cap at **$25.00** per order. 10 of 10 trades executed cleanly.
- **Stage B (Trades 11–40)**: Hard notional cap at **$50.00** per order. 30 of 30 trades executed cleanly with zero reconciliation errors.
- **Stage C (Trades 41–104)**: Hard notional cap at **$100.00** per order (10% of account equity). 64 of 64 trades executed cleanly.

```
Total Live Trades Executed by Stage:
  Stage A ($25 max):  [||||||||||] 10 trades
  Stage B ($50 max):  [||||||||||||||||||||||||||||||] 30 trades
  Stage C ($100 max): [||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||] 64 trades
```

---

## 4. Drawdown & Rolling Loss Analysis

- **Maximum Observed Drawdown**: **$12.40** (1.24% of capital), occurring across Sessions 8–10 during choppy, range-bound price action.
- **Fast Recovery**: The portfolio recovered back to new peak equity within 14 trades.
- **Worst Single Day PnL**: -$4.80 (Session 9), well within the $20.00 daily loss budget.
- **Best Single Day PnL**: +$3.45 (Session 18).

---

## 5. Fail-Closed Circuit Breakers & Kill Switches

All five operator emergency switches were verified functional:
1. **PAUSE NEW ORDERS**: Successfully halted new candidate proposal generation.
2. **CANCEL ALL ENTRY ORDERS**: Successfully purged pending limit orders.
3. **CANCEL ALL ORDERS**: Purged resting orders across broker gateway.
4. **CLOSE ALL POSITIONS**: Market-liquidated open pilot holdings at current bids.
5. **FULL SYSTEM LOCKOUT**: Cleared daily authorization token and revoked execution permissions.
