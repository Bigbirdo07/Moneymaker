# Tier 2 Edge Retention & Capacity State Report

## 1. Absolute vs Incremental Edge Retention Formulations

$$\text{ABSOLUTE\_EDGE\_RETENTION} = \frac{\text{Tier 2 Net Expectancy}}{\text{Tier 0 Baseline Net Expectancy (+1.57 bps)}}$$

$$\text{INCREMENTAL\_EDGE\_RETENTION} = \frac{\text{Tier 2 Net Expectancy}}{\text{Tier 1 Net Expectancy (+1.47 bps)}}$$

---

## 2. Retention Progression Across Tiers

| Tier | Authorized Capital | Net Expectancy | Absolute Retention | Incremental Retention | Capacity Classification | Evidence Type |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 0** | $1,000.00 | +1.57 bps | **100.0%** | Reference | `HEALTHY_CAPACITY` | `LIVE_AUTONOMOUS` |
| **Tier 1** | $2,500.00 | +1.47 bps | **93.6%** | **93.6%** | `HEALTHY_CAPACITY` | `LIVE_AUTONOMOUS` |
| **Tier 2 [Proj]**| $5,000.00 | +1.34 bps | **85.4%** | **91.2%** | `HEALTHY_CAPACITY` | `SIMULATED_PROJECTED` |
| **Tier 3 [Proj]**| $10,000.00 | +1.09 bps | **69.4%** | **81.3%** | `WATCH_CAPACITY` | `PROJECTED_ONLY` |
| **Tier 4 [Proj]**| $25,000.00 | +0.65 bps | **41.4%** | **59.6%** | `DEGRADED_CAPACITY` | `PROJECTED_ONLY` |

---

## 3. Projected Capacity Bounds

- **`PROJECTED_CAPACITY_BREAK_EVEN_USD`**: Estimated at **$92,000 USD** (95% CI: [$74,000, $115,000] USD).
- **`PROJECTED_PRACTICAL_CAPACITY_USD`**: Recommended at **$25,000 – $32,000 USD** to preserve a $\ge 65\%$ safety margin buffer.
- *Status Note*: Both capacity bounds are derived from parametric empirical models and are **PROJECTED ONLY** (not live validated).
