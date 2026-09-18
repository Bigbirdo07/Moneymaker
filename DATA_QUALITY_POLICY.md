# Market Data Quality Policy Specification (Phase B)

## 1. Objective & Scope
The **Market Data Quality Policy** acts as an empirical firewall against corrupted, stale, or malformed 1-minute market feeds before data enters feature engineering or cross-sectional ranking pipelines.

---

## 2. Mandatory Data Quality Invariants

| Invariant | Quality Test | Rejection Threshold | Violation Code |
| :--- | :--- | :--- | :--- |
| **Strict Monotonicity** | Ascending UTC timestamps | Non-increasing timestamps detected | `NON_MONOTONIC_TIMESTAMPS` |
| **Zero Duplication** | Unique timestamp per symbol | Duplicate timestamp found | `DUPLICATE_TIMESTAMPS` |
| **Valid Price Bounds** | $P > 0$ for all OHLC | Any price $\le \$0.00$ | `NEGATIVE_OR_ZERO_PRICE` |
| **OHLC Consistency** | $H \ge \max(O, C)$ and $L \le \min(O, C)$ | Inverted high/low vs open/close | `INVERTED_OHLC` |
| **Continuous Activity** | Zero-volume bar fraction | Zero-volume bars $> 50\%$ of regular session | `EXCESSIVE_ZERO_VOLUME` |
| **Tick Freshness** | Maximum consecutive identical closes | Stale price sequence $> 15$ bars | `STALE_PRICE_SEQUENCE` |
| **Session Completeness**| Valid regular-session bars | Total session bars $< 200$ bars | `INSUFFICIENT_BAR_COUNT` |

---

## 3. Governance Principle
> [!IMPORTANT]
> **Safety Over Coverage**: If a symbol's feed exhibits data anomalies on session $T$, the entire symbol is disqualified for session $T$. The platform never attempts synthetic bar interpolation or forward-filling during live or validation replays.
