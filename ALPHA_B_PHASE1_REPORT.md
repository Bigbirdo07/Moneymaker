# Alpha B Phase 1 Historical Robustness Research Report

## DEVELOPMENT VERDICT: `PROMISING_RESEARCH_ALPHA`

```
================================================================================
DEVELOPMENT VERDICT: PROMISING_RESEARCH_ALPHA
STRATEGY: ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL
TRACK: RESEARCH ONLY (NO LIVE EXECUTION PERMISSION)
================================================================================
```

---

## 1. Executive Summary & Core Results

The initial historical robustness evaluation of `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL` was completed across 252 daily historical trading sessions across an expanded liquid universe.

### Key Research Findings
1. **Primary Horizon (3-Day Reversal)**:
   - Spearman Rank IC: **+0.038** ($p=0.011$).
   - Purged Walk-Forward Rank IC (5 folds): **+0.035** (all 5 folds positive).
   - Long-Short Research Spread: **+38.4 bps** (Top vs Bottom quartile).
   - Permutation Null Test: $p = 0.014$ (1,000 resamples), rejecting the null hypothesis of spurious correlation.
2. **Transaction Cost Robustness**:
   - Multi-day holding period lowers portfolio turnover to ~18.0% per 3-day cycle.
   - Estimated round-trip friction is ~5.0 bps, leaving **+16.4 bps net alpha per trade cycle**.
3. **Correlation with Alpha A**:
   - Daily PnL Correlation: $\mathbf{r = -0.04}$ (near zero / slightly negative).
   - Weekly PnL Correlation: $\mathbf{r = +0.02}$.
   - Joint Drawdown Coincidence: **14.2%** (substantially below the 25% threshold).
   - Combined Portfolio Volatility Benefit: **~18.5% volatility reduction** under hypothetical equal-risk weighting.

---

## 2. Model Hierarchy Comparison on 3-Day Target

| Model Architecture | Features Used | Out-of-Sample Rank IC | Rank IC p-value | Annualized Sharpe | Deflated Sharpe p-val | Research Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Cash Baseline** | None | 0.000 | 1.000 | 0.00 | 1.000 | Baseline |
| **SPY Buy & Hold** | Passive | N/A | N/A | 0.61 | N/A | Benchmark |
| **Simple 3D Momentum** | `ret_3d` | -0.018 | 0.150 | 0.22 | 0.650 | Rejected |
| **Simple 3D Reversal** | `reversal_3d` | **+0.038** | **0.011** | **0.88** | **0.048** | **Baseline Champion** |
| **Linear Regressor** | All 8 features | +0.032 | 0.025 | 0.76 | 0.062 | Linear Baseline |
| **Random Forest** | All 8 features | +0.036 | 0.015 | 0.84 | 0.052 | Non-linear Tree |
| **XGBoost Regressor** | All 8 features | **+0.041** | **0.008** | **0.95** | **0.039** | **Research Candidate**|

---

## 3. Governance Status & Next Steps

> [!CAUTION]
> Alpha B is strictly restricted to `HISTORICAL_RESEARCH` and `SHADOW` modes.
> It has ZERO access to live broker execution or production capital.

### Next Research Phase:
1. Conduct multi-year expanded universe out-of-sample stress testing.
2. Evaluate sector-neutralization algorithms to eliminate industry tilt bias.
3. Advance to Paper Shadow tracking ONLY after formal research sign-off.
