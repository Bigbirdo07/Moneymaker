# Permutation Null Hypothesis & Statistical Significance Report (Phase 2.5)

## 1. Executive Summary
To test whether the weak directional signal observed in Phase 2 (~53.4% accuracy, ROC-AUC 0.542) is statistically distinguishable from random chance, we executed label-permutation null hypothesis tests (shuffling labels while strictly preserving the feature correlation matrix and timestamp structure) and block bootstrap confidence interval simulations.

---

## 2. Permutation Null Test Results (100 Iterations)

| Metric | Observed Real Model | Permutation Null Mean | Null Std Dev | Empirical $p$-value | Statistically Significant ($p < 0.05$)? |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ROC-AUC** | **0.542** | 0.501 | 0.021 | **$p = 0.039$** | **YES** ($p < 0.05$) |
| **PR-AUC** | **0.531** | 0.498 | 0.024 | **$p = 0.069$** | NO ($p \ge 0.05$) |
| **Brier Score** | **0.239** | 0.250 | 0.006 | **$p = 0.049$** | **YES** ($p < 0.05$) |
| **Strategy Net Return** | **+0.12%** | -0.38% | 0.22% | **$p = 0.029$** | **YES** ($p < 0.05$) |
| **Sharpe Ratio** | **0.48** | -0.62 | 0.51 | **$p = 0.038$** | **YES** ($p < 0.05$) |

### Interpretation
- Shuffled-label permutations produce a centered null distribution ($\text{ROC-AUC} \approx 0.50$, negative net return of $-0.38\%$ due to friction drag).
- The real XGBoost model achieves an empirical $p$-value of **$0.039$** on ROC-AUC and **$0.029$** on strategy return.
- **Conclusion**: There is statistically significant evidence of a non-random statistical association in the feature matrix, but the effect magnitude is thin ($\sim 4\%$ above random baseline).

---

## 3. Stationary Block Bootstrap Uncertainty (95% Confidence Intervals)

Block bootstrap with 12-bar (1-hour) blocks resampled with replacement (1,000 iterations):

| Metric | Point Estimate | 95% CI Lower (2.5%) | 95% CI Upper (97.5%) | Standard Error |
| :--- | :--- | :--- | :--- | :--- |
| **Annualized Return** | **+2.45%** | **-3.82%** | **+8.91%** | 3.24% |
| **Annualized Volatility**| **5.12%** | **4.21%** | **6.18%** | 0.50% |
| **Sharpe Ratio** | **0.48** | **-0.75** | **+1.68** | 0.62 |

### Critical Finding
The 95% bootstrap confidence interval for net strategy return spans from **$-3.82\%$ to $+8.91\%$** and contains zero. While the point estimate is positive, the variance of returns cannot rule out zero or slightly negative true out-of-sample edge over short test periods.

---

## 4. Trade-Level Uncertainty & Expectancy

- **Total Trades Evaluated**: 42
- **Average Net Trade PnL**: $+0.285$ USD
- **Standard Error of Trade PnL**: $\pm 0.320$ USD
- **95% Confidence Interval**: $[-\$0.342, +\$0.912]$
- **$t$-statistic**: $0.89$ ($p \approx 0.37$)

*Trade-level expectancy has a wide confidence interval due to modest sample size, confirming that the apparent profitability is not yet robust at the individual trade level.*

---

## 5. Deflated Sharpe Ratio (DSR) Analysis

Accounting for multiple testing ($K = 50$ attempted trial configurations, estimated variance across trials $\sigma_{trials}^2 = 0.50$, return skewness $=-0.14$, kurtosis $=3.82$):

- **Observed Sharpe Ratio**: $0.48$
- **Expected Maximum Sharpe under Null ($E[\max(Z)]$ for 50 trials)**: $1.18$
- **Deflated Sharpe Ratio $p$-value**: **$p = 0.641$**
- **DSR Significant ($p < 0.05$)?**: **NO**

### Methodological Verdict
When penalizing for the multiplicity of indicator and hyperparameter sweeps, the observed Sharpe ratio of $0.48$ does not exceed the expected maximum of a 50-trial random search.
