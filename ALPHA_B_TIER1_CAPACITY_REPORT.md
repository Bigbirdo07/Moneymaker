# Alpha B Tier 1 Capacity & Deployable Alpha Report

## 1. Executive Summary

This report analyzes the capacity boundaries, symbol-level stacking limits, capital utilization, and deployable alpha for `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1` operating at **$2,500 USD** capital.

---

## 2. Model Alpha vs Deployable Alpha

Due to discrete capital constraints, risk limits, and same-symbol stacking caps, not all raw model opportunity translates into live execution:

| Alpha Accounting Dimension | Dollar Value ($) | bps / Cycle Equivalent | Percentage of Model Alpha |
| :--- | :--- | :--- | :--- |
| **Gross Model Opportunity (Unconstrained)** | **$478.50 USD** | +16.02 bps | 100.00% |
| **Missed Alpha (Symbol & Sector Cap Resizing)**| -$9.80 USD | -0.33 bps | -2.05% |
| **Missed Alpha (Portfolio Vetoes)** | -$7.50 USD | -0.25 bps | -1.57% |
| **Realized Gross Deployable Alpha** | **$461.20 USD** | +15.44 bps | 96.38% |
| **Canonical Friction Subtraction** | -$163.80 USD | -5.46 bps | -34.23% |
| **Net Deployable Alpha Realized** | **+$297.40 USD** | **+9.98 bps eq.** | **62.15% of Gross** |

---

## 3. Same-Symbol Cohort Stacking & Capacity Rejections

When consecutive daily signals rank a symbol that is already held in an active cohort from the prior session, `AlphaBCapacityManager` deterministically applies the `CAP_AT_MAX_SYMBOL_EXPOSURE` policy:

### Observed Capacity Events (60 Sessions):
- **Total Rebalance Events**: 60
- **Same-Symbol Rebalance Instances**: 8 instances
- **`CAPACITY_RESIZED`**: 6 instances (orders downsized to enforce the $833.33 single symbol limit).
- **`CAPACITY_REJECTED` / `SYMBOL_CAP_REJECTED`**: 2 instances (orders blocked entirely due to fully saturated symbol exposure).
- **`PORTFOLIO_VETOED`**: 1 instance (cross-strategy combined sector limit).
- **`INSUFFICIENT_CAPITAL`**: 0 instances (capital utilization always remained $\le 98.2\%$).

### Counterfactual Impact:
- Counterfactual return of downsized / rejected quantity: +8.40 bps average.
- Total missed gross alpha: **$17.30 USD**.
- Risk benefit: Symbol concentration never exceeded the hard 33.33% ($833.33 USD) ceiling, protecting against idiosyncratic gap downs.

---

## 4. Multi-Point Capacity Model & Extrapolation Caution

With empirical validation completed at two discrete capital tiers ($1,000 USD and $2,500 USD), the initial empirical capacity trajectory is established:

```
Net Expectancy vs Capital:
$1,000 USD (B-Tier 0) : +10.67 bps (Observed Live)
$2,500 USD (B-Tier 1) : +10.56 bps (Observed Live, Retention 98.97%)
$5,000 USD (B-Tier 2) : +10.15 bps (PROJECTED MODEL ONLY - LOCKED)
$10,000 USD (B-Tier 3): +9.20 bps  (PROJECTED MODEL ONLY - LOCKED)
```

> [!CAUTION]
> Any capacity claims above $2,500 USD remain **PROJECTED MODEL ONLY**. Higher tiers (B-Tier 2 @ $5,000 USD and B-Tier 3 @ $10,000 USD) remain strictly locked and unauthorized until future authorized ramp phases.
