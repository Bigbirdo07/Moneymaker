# Alpha B Human Governance & Selection Effect Report (Phase 7B Track B)

**Scope**: Human-Alpha Decomposition for Alpha B Multi-Day Reversal  
**Sample**: 50 live proposals across 25 sessions (42 approved, 5 safety vetoed, 3 discretionary rejected)

---

## 1. Human Decision Decomposition

Following the methodology established in Phase 5B:

$$\text{Live Observed Alpha} = \text{Model Intrinsic Alpha} + \text{Human Selection Effect} - \text{Human Latency Cost}$$

| Component | Observed Value | Description |
| :--- | :--- | :--- |
| **Model Intrinsic Alpha** | **+10.75 bps / cycle** | Net expectancy of unconstrained autonomous model counterfactual |
| **Human Selection Effect** | **+0.12 bps / cycle** | Incremental edge from discretionary exclusion of low-conviction signals |
| **Human Latency Cost** | **-0.07 bps / cycle** | Opportunity cost of manual overnight approval window |
| **Net Governed Live Expectancy**| **+10.80 bps / cycle** | Actual realized live micro-pilot expectancy |

---

## 2. Statistical Significance of Human Discretion

- **Paired t-test (Approved vs Discretionary Rejected)**: $t = 0.45$, $p = 0.655$ (Not statistically significant).
- **Interpretation**: Human discretionary overrides contribute negligible incremental edge ($+0.12$ bps, $p=0.655$). The strategy edge resides almost entirely in the underlying quantitative feature model.
- **Safety Role**: Human oversight served primarily as an operational failsafe (governing corporate event compliance and hardware status) rather than a market-timing tool.
