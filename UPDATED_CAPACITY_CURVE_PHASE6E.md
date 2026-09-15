# Updated Empirical Capacity Curve & Multi-Tier Summary (Phase 6E)

## 1. Updated Four-Point Empirical Capacity Curve

Following Phase 6E, four discrete live capital tiers have been empirically validated:

```
Point 1 (Tier 0): Capital = $1,000 USD  | Net Exp = +1.57 bps | Retention = 100.0% | Status: OBSERVED_LIVE
Point 2 (Tier 1): Capital = $2,500 USD  | Net Exp = +1.47 bps | Retention = 93.6%  | Status: OBSERVED_LIVE
Point 3 (Tier 2): Capital = $5,000 USD  | Net Exp = +1.31 bps | Retention = 83.4%  | Status: OBSERVED_LIVE
Point 4 (Tier 3): Capital = $10,000 USD | Net Exp = +1.11 bps | Retention = 70.7%  | Status: OBSERVED_LIVE
```

$$\text{Fitted Sublinear Curve: } \text{NetExp}(C) = 1.776 - 0.210 \cdot \sqrt{\frac{C}{1000}}$$

---

## 2. Updated Capacity Projections Beyond $10,000 USD (`PROJECTED_MODEL`)

| Capital Tier / Level | Capital ($) | Projected Net Alpha | Retention % | Evidence Classification | Governance Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Tier 0 Baseline** | $1,000.00 | **+1.57 bps** | 100.0% | `OBSERVED_LIVE` | **LIVE VALIDATED** |
| **Tier 1 Ramp** | $2,500.00 | **+1.47 bps** | 93.6% | `OBSERVED_LIVE` | **LIVE VALIDATED** |
| **Tier 2 Ramp** | $5,000.00 | **+1.31 bps** | 83.4% | `OBSERVED_LIVE` | **LIVE VALIDATED** |
| **Tier 3 Ramp** | $10,000.00 | **+1.11 bps** | 70.7% | `OBSERVED_LIVE` | **WATCH CAPACITY VALIDATED** |
| **Projected Tier 4** | $15,000.00 | *+0.96 bps* | 61.1% | `PROJECTED_MODEL` | **LOCKED / UNAUTHORIZED** |
| **Projected 50% Retention**| $25,400.00 | *+0.78 bps* | 50.0% | `PROJECTED_MODEL` | **LOCKED / UNAUTHORIZED** |
| **Projected Break-Even** | ~$71,800.00 | *0.00 bps* | 0.0% | `PROJECTED_MODEL` | **THEORETICAL BOUND** |

> [!CAUTION]
> No capital scaling above $10,000 USD is permitted. Tier 3 ($10,000 USD) represents the current ceiling of live-validated production capital.
