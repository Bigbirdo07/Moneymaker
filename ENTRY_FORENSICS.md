# Entry Decision Model Forensics Report

## 1. Executive Summary

This report analyzes all 65,021 entry evaluations and 658 executed entries produced by `EntryDecisionModel` during the Phase 10 historical replay test.

The goal is to determine why trades were accepted, whether entry criteria filtered noise effectively, and what structural changes are required in `EntryDecisionModelV1_1`.

---

## 2. Global Evaluation Breakdown

Across all 65,021 candidate evaluations:

| Evaluation Result | Count | Percentage | Primary Rejection / Acceptance Reason |
| :--- | :--- | :--- | :--- |
| **BUY (Executed / Authorized)** | 658 | 1.01% | `POSITIVE_NET_EDGE_CONFIRMED` |
| **SKIP: Sub-Threshold Edge** | 48,214 | 74.15% | `INSUFFICIENT_NET_EDGE` (Edge < 4.0 bps or P(Up) < 53%) |
| **SKIP: Portfolio Cash Throttling** | 11,432 | 17.58% | `INSUFFICIENT_AVAILABLE_CASH` (Cash < 5% of Portfolio Value) |
| **SKIP: Session Close Buffer** | 3,420 | 5.26% | `SESSION_CLOSE_PROXIMITY` (Last 20 minutes of session) |
| **SKIP: Spread / Liquidity Filter** | 1,297 | 2.00% | `EXCESSIVE_SPREAD_FRICTION` (Spread > 15.0 bps) |

---

## 3. Dissection of Executed Entries ($N = 658$)

Examining the 658 trades that passed the V1.0 entry filter:

### Edge Distribution of Accepted Entries:
- **Low Edge (4.0 to 8.0 bps)**: 404 trades (61.4%) — *Average Net Return: -5.82 bps*
- **Medium Edge (8.0 to 15.0 bps)**: 168 trades (25.5%) — *Average Net Return: +1.14 bps*
- **High Edge (> 15.0 bps)**: 86 trades (13.1%) — *Average Net Return: +14.22 bps*

### Root Cause Diagnosis:
1. **Low-Edge Sub-Threshold Contamination**: Over 60% of all executed trades were entered with expected edges between 4.0 and 8.0 bps. In real execution with slippage and half-spread costs averaging 6.5 bps, these trades suffered negative expected value from inception.
2. **Lack of Re-Entry Cooldown**: After exiting a symbol on signal decay, the model frequently re-entered the exact same symbol 2–5 minutes later upon a minor tick update, generating repetitive commissions and spreads.
3. **Absence of Daily Velocity Throttling**: On volatile days, the model executed up to 48 trades in a single session, overloading the portfolio with transaction friction.

---

## 4. Entry Engine V1.1 Enhancements

The newly constructed `EntryDecisionModelV1_1` incorporates four institutional guardrails:

```python
# V1.1 Entry Guardrails
min_net_edge_bps = 10.0           # Up from 4.0 bps (filters out Decile 8 noise)
min_probability_positive = 0.58   # Up from 0.53 (requires 58%+ conviction)
max_spread_bps = 10.0             # Down from 15.0 bps (stricter liquidity gate)
re_entry_cooldown_bars = 30       # 30-bar mandatory lockout per symbol
max_daily_trades = 8              # Hard cap to eliminate churning
max_concurrent_positions = 3      # Limits simultaneous risk
```

These enhancements ensure that only high-conviction opportunities (Deciles 9 and 10) are authorized for capital allocation.
