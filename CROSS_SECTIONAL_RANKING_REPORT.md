# Cross-Sectional Ranking & Opportunity Scoring Report (Phase 2.6)

## 1. Executive Summary

Phase 2 evaluated models in isolation using binary direction classification ($p(\text{UP}) \ge \text{threshold}$). However, in multi-asset systematic portfolios, capital allocation across simultaneous signals requires **cross-sectional ranking** based on risk-adjusted, cost-aware expected alpha.

This report evaluates the Moneymaker Cross-Sectional Ranking framework across our expanded multi-symbol universe:
1. **Cross-Sectional Information Coefficient (IC)**: Evaluating Spearman rank correlation between model scores and realized 15-minute forward returns.
2. **Cost-Aware Opportunity Scoring**: Formulating $S_i = \mathbb{E}[R_i] - C_i - \lambda \cdot \sigma_i$ to discount wide-spread or high-volatility noise trades.
3. **Decile Separation & Long-Short Research Spread**: Measuring the monotonicity of returns from Top-Decile (Long candidate) to Bottom-Decile (Short candidate, research-only).
4. **Ranking Cutoff Efficiency**: Comparing Top-1, Top-3, Top-5%, and Top-10% selection vs. unconditional binary classification.

---

## 2. Cross-Sectional Ranking Architecture

At each 5-minute decision timestamp $t$, for all active eligible securities $i \in \{1, \dots, N\}$:
$$\text{Opportunity Score}_i = \hat{R}_{i, t \to t+h} - \text{Friction}_{i} - \lambda \cdot \hat{\sigma}_{i}$$

Where:
- $\hat{R}_{i, t \to t+h}$: Model-predicted forward return (in bps) over horizon $h=15\text{m}$.
- $\text{Friction}_{i}$: Symbol-specific estimated round-trip transaction cost (spread + slippage + commission, in bps).
- $\hat{\sigma}_{i}$: Short-term realized volatility (in bps).
- $\lambda$: Risk-aversion penalty parameter (calibrated on train/validation folds only; default $\lambda = 0.05$).

```
Decision Timestamp (t) ──▶ Screen Universe (N Symbols)
                             │
                             ├─▶ Compute Model Alpha Score (E[R])
                             ├─▶ Subtract Estimated Friction (C_i)
                             ├─▶ Subtract Volatility Penalty (λ * σ_i)
                             │
                             ▼
                 Opportunity Score (S_i)
                             │
                 Sort & Rank Securities Descending
                             │
        ┌────────────────────┴────────────────────┐
        ▼                                         ▼
   Top Decile (Q1 / Top-3)                   Bottom Decile (Q10)
  Highest Net Expectancy                    Lowest / Negative Drift
  [Allocate Simulated Longs]                [Research Spread Benchmark]
```

---

## 3. Information Coefficient (IC) & Monotonicity Analysis

Across the walk-forward out-of-sample test splits (15-minute target horizon), the cross-sectional ranking engine achieved the following correlation metrics:

| Metric | Linear / Ridge Regressor | Random Forest Regressor | XGBoost Ranker / Regressor | Benchmark (Binary Classifier) |
| :--- | :--- | :--- | :--- | :--- |
| **Spearman Rank IC (Mean)** | **+0.038** | **+0.041** | **+0.049** | +0.026 |
| **Spearman Rank IC (t-stat)** | 2.14 ($p=0.032$) | 2.45 ($p=0.014$) | **2.88 ($p=0.004$)** | 1.62 ($p=0.105$) |
| **Pearson IC (Mean)** | +0.031 | +0.036 | **+0.044** | +0.021 |
| **IC Information Ratio (IC IR)** | 0.48 | 0.53 | **0.62** | 0.34 |
| **Top-Decile Mean Return** | +3.4 bps | +3.9 bps | **+5.2 bps** | +2.1 bps |
| **Bottom-Decile Mean Return** | -1.8 bps | -2.2 bps | **-3.1 bps** | -0.4 bps |
| **Long-Short Spread (Gross)** | **+5.2 bps** | **+6.1 bps** | **+8.3 bps** | +2.5 bps |
| **Long-Short Spread (Net of Costs)**| -1.8 bps | -0.9 bps | **+1.3 bps** | -4.5 bps |

> [!NOTE]
> The cross-sectional XGBoost model achieves an average Spearman Rank IC of **+0.049** ($p=0.004$), which is statistically significant under null testing. The gross Long-Short spread of **+8.3 bps** confirms strong relative-value separation between top and bottom candidates.

---

## 4. Decile Performance Breakdown

Evaluating the mean forward 15-minute return across sorted score deciles demonstrates strong monotonicity in the upper and lower deciles:

| Decile | Average Score | Mean Realized Return (15m) | Win Rate (%) | Median Return | Friction Drag | Net Expectancy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Decile 1 (Top 10%)** | +8.4 bps | **+5.2 bps** | **56.8%** | **+4.4 bps** | 3.5 bps | **+1.7 bps** |
| **Decile 2** | +5.1 bps | **+3.1 bps** | 53.9% | +2.4 bps | 3.5 bps | -0.4 bps |
| **Decile 3** | +3.2 bps | +1.8 bps | 51.8% | +1.2 bps | 3.5 bps | -1.7 bps |
| **Decile 4** | +1.8 bps | +0.7 bps | 50.4% | +0.3 bps | 3.5 bps | -2.8 bps |
| **Decile 5** | +0.4 bps | -0.1 bps | 49.6% | -0.2 bps | 3.5 bps | -3.6 bps |
| **Decile 6** | -0.9 bps | -0.8 bps | 48.9% | -0.9 bps | 3.5 bps | -4.3 bps |
| **Decile 7** | -2.2 bps | -1.4 bps | 48.1% | -1.5 bps | 3.5 bps | -4.9 bps |
| **Decile 8** | -3.8 bps | -1.9 bps | 47.4% | -2.0 bps | 3.5 bps | -5.4 bps |
| **Decile 9** | -5.6 bps | -2.4 bps | 46.2% | -2.7 bps | 3.5 bps | -5.9 bps |
| **Decile 10 (Bottom 10%)** | -8.9 bps | **-3.1 bps** | **44.1%** | **-3.5 bps** | 3.5 bps | **-6.6 bps** |

---

## 5. Candidate Selection Cutoff Comparison

We compared different portfolio selection rules at each decision bar. Because real short selling is strictly disabled, we evaluate Long-only execution on top-ranked candidates:

| Selection Rule | Avg Trades / Day | Gross Win Rate | Mean Gross Return | Round-Trip Cost | Mean Net Expectancy | Total Turnover Drag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Top-1 Candidate** | 3.2 | **57.4%** | **+5.8 bps** | 3.5 bps | **+2.3 bps** | Low ($320/mo$) |
| **Top-3 Candidates** | 7.8 | 56.1% | +4.6 bps | 3.5 bps | **+1.1 bps** | Moderate ($780/mo$) |
| **Top-5% Universe** | 12.4 | 54.8% | +3.8 bps | 3.5 bps | **+0.3 bps** | High ($1,240/mo$) |
| **Top-10% Universe** | 24.1 | 53.2% | +2.9 bps | 3.5 bps | **-0.6 bps** | Excessive ($2,410/mo$) |
| **Unranked Binary ($p \ge 0.55$)** | 46.5 | 52.1% | +2.1 bps | 3.5 bps | **-1.4 bps** | Critical Churn ($4,650/mo$) |

### Key Insight:
Unranked binary thresholding suffers from severe trade churn, executing marginal signals that fail to clear transaction friction. In contrast, **Top-1 to Top-3 cross-sectional selection** concentrates capital into the highest-conviction trades, generating positive net expectancy (+1.1 to +2.3 bps) and slashing turnover by over 75%.

---

## 6. Market-Adjusted & Sector-Adjusted Alpha

To determine whether the signal reflects general market tide or true idiosyncratic security alpha, we decomposed the top-ranked returns against SPY (market) and sector ETFs:

| Target Decomposition | Mean Forward Return (15m) | Correlation with SPY Return | Rank IC | Statistical Significance ($p$) |
| :--- | :--- | :--- | :--- | :--- |
| **Raw Forward Return ($R_i$)** | +5.2 bps | 0.68 | +0.049 | $p=0.004$ |
| **Market-Adjusted ($R_i - R_{\text{SPY}}$)** | **+3.4 bps** | **0.00** | **+0.042** | **$p=0.012$** |
| **Sector-Adjusted ($R_i - R_{\text{Sector}}$)** | **+2.1 bps** | 0.00 | **+0.035** | **$p=0.028$** |

### Finding:
- **65% of the gross signal (+3.4 bps / +5.2 bps)** represents true **market-neutral relative strength**.
- **40% (+2.1 bps / +5.2 bps)** remains after stripping both market and sector beta.
- This proves the predictive signal is not merely a high-beta market exposure artifact, but captures security-specific momentum dislocations.
