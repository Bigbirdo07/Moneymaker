# Alpha A Explicit Capacity Retention Thresholds Report

## 1. Multi-Threshold Taxonomy
Rather than quoting a single subjective "practical capacity" figure, this report establishes explicit retention thresholds based on the calibrated empirical Square-Root Sublinear Impact model:

$$\text{Retention Ratio} = \frac{\text{Projected Net Expectancy}}{\text{Tier 0 Net Expectancy (+1.57 bps)}}$$

---

## 2. Explicit Thresholds Matrix

| Retention Tier | Target Retention % | Net Expectancy Target | Projected Capital Threshold | Evidence Status | Operational Significance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`CAPACITY_90_RETENTION`** | **90.0%** | $+1.413$ bps | **$3,450 USD** | `PROJECTED_MODEL` | Minimum edge decay; institutional grade efficiency |
| **`CAPACITY_80_RETENTION`** | **80.0%** | $+1.256$ bps | **$6,380 USD** | `PROJECTED_MODEL` | Formal `HEALTHY_CAPACITY` boundary |
| **`CAPACITY_70_RETENTION`** | **70.0%** | $+1.099$ bps | **$11,200 USD** | `PROJECTED_MODEL` | `WATCH_CAPACITY` midpoint; encompasses Tier 3 ($10k) |
| **`CAPACITY_50_RETENTION`** | **50.0%** | $+0.785$ bps | **$25,400 USD** | `PROJECTED_MODEL` | Previous "practical capacity" actually represents 50% retention |
| **`CAPACITY_30_RETENTION`** | **30.0%** | $+0.471$ bps | **$48,900 USD** | `PROJECTED_MODEL` | `DEGRADED_CAPACITY` floor |
| **`CAPACITY_BREAK_EVEN`** | **0.0%** | $0.000$ bps | **$71,800 - $86,200 USD** | `PROJECTED_MODEL` | Friction fully consumes gross alpha |

---

## 3. Key Governance Insights
1. **Tier 2 ($5,000 USD) Observed**: Net expectancy $+1.31$ bps (83.4% retention). Fits comfortably within `HEALTHY_CAPACITY` ($> 80\%$).
2. **Tier 3 ($10,000 USD) Projected**: Net expectancy $+1.14$ bps (72.6% retention). Falls into `WATCH_CAPACITY` (60%–80%).
3. **The $25,000 Myth**: Operating at $25,000 will yield approximately $+0.73$ to $+0.80$ bps (half of original edge). While still profitable under base costs, it leaves a narrow buffer against adverse regime shifts.
