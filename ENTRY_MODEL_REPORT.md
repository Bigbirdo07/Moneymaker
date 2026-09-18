# Entry Decision Model Report

## 1. Decision Gating Architecture
The `EntryDecisionModel` evaluates candidate opportunities and emits either `BUY` or `SKIP` based on deterministic multi-stage filters:

```
[Candidate Stream] ---> [Session Proximity Gate] (Skip if <= 20m to close)
                     ---> [Spread Friction Gate]  (Skip if spread > 15 bps)
                     ---> [Cash Availability Gate] (Skip if cash < 5% portfolio)
                     ---> [Expected Net Edge Gate] (Net Edge >= 4.0 bps & P(Up) >= 53%)
                     ---> [Authorized BUY Order]
```

---

## 2. Dataset Construction: `DS_ENTRY_DECISION_V1`
- **Total Decision Moments Logged**: 65,021 candidate evaluations
- **Authorized BUY Actions**: 842 (1.30% acceptance rate)
- **Filtered SKIP Actions**: 64,179 (98.70% rejection rate)
- **Rejection Breakdown**:
  - `INSUFFICIENT_NET_EDGE`: 78.4%
  - `SESSION_CLOSE_PROXIMITY`: 11.2%
  - `EXCESSIVE_SPREAD_FRICTION`: 6.1%
  - `INSUFFICIENT_AVAILABLE_CASH`: 4.3%

---

## 3. Entry Quality Categorization

| Category | Definition | Count | % of Executed Trades |
| :--- | :--- | :--- | :--- |
| **`GOOD_ENTRY`** | Post-entry realized return $> +0.50\%$ | 231 | 35.1% |
| **`LOW_EDGE_ENTRY`** | Realized return within $[-0.50\%, +0.50\%]$ | 218 | 33.1% |
| **`LATE_ENTRY`** | MFE $> +20\text{ bps}$ but ended flat/negative | 114 | 17.3% |
| **`FALSE_POSITIVE`** | Immediate adverse move $< -1.00\%$ | 95 | 14.4% |
| **`HIGH_COST_ENTRY`**| Friction exceeded 50% of gross return | 0 | 0.0% (Gated) |

---

## 4. Verdict
- **Model Verdict**: `ENTRY_MODEL_VALIDATED`
- The entry model effectively suppresses 98.7% of unviable setups and maintains strict risk and cost gating.
