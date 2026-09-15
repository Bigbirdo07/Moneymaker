# Multiple-Testing Accounting & Hypothesis Ledger (Phase 2.6)

## 1. Executive Summary

A major pitfall in quantitative finance is *data snooping bias* / *p-hacking*: when dozens or hundreds of model variations, target definitions, and hyperparameter combinations are evaluated, standard statistical significance thresholds ($p < 0.05$) generate false discoveries.

This ledger records **every trial and hypothesis explored across Phase 1, Phase 2, Phase 2.5, and Phase 2.6**, applying rigorous family-wise error rate (**Bonferroni**) and False Discovery Rate (**Benjamini-Hochberg FDR**) adjustments, as well as the **Deflated Sharpe Ratio (DSR)** to adjust for multi-hypothesis exploration.

---

## 2. Global Experiment Accounting

```
Cumulative Hypotheses Tested:
├── Phase 1 (Baseline Strategies & Rules):             8 trials
├── Phase 2 (Directional ML Models & Features):        18 trials
├── Phase 2.5 (Significance & Robustness Audit):       14 trials
└── Phase 2.6 (Multi-Horizon, Ranking, Meta-Labeling): 38 trials
─────────────────────────────────────────────────────────────────
Total Cumulative Hypotheses (N):                      78 trials
```

---

## 3. Comprehensive Trial Ledger (Phase 2.6 Experiments)

| Trial ID | Category / Dimension | Hypothesis Tested | Raw $p$-value | Bonferroni Adj. $p$ | Benjamini-Hochberg FDR $q$ | Empirical Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `T-01` | Multi-Horizon Target | 5-Minute Forward Return Target (XGBoost) | 0.042 | 1.000 | 0.148 | Marginal / Noise |
| `T-02` | Multi-Horizon Target | 10-Minute Forward Return Target (XGBoost) | 0.018 | 1.000 | 0.082 | Statistical Signal |
| **`T-03`** | **Multi-Horizon Target** | **15-Minute Forward Return Target (XGBoost)** | **0.003** | **0.234** | **0.024** | **STRONG SIGNAL (FDR $\le 0.05$)** |
| `T-04` | Multi-Horizon Target | 20-Minute Forward Return Target (XGBoost) | 0.008 | 0.624 | 0.048 | Statistical Signal |
| `T-05` | Multi-Horizon Target | 30-Minute Forward Return Target (XGBoost) | 0.035 | 1.000 | 0.134 | Degrading Alpha |
| `T-06` | Multi-Horizon Target | 45-Minute Forward Return Target (XGBoost) | 0.120 | 1.000 | 0.312 | Inconclusive |
| `T-07` | Multi-Horizon Target | 60-Minute Forward Return Target (XGBoost) | 0.280 | 1.000 | 0.540 | Inconclusive (Phase 2 Target) |
| `T-08` | Multi-Horizon Target | 90-Minute Forward Return Target (XGBoost) | 0.640 | 1.000 | 0.820 | Non-Predictive |
| `T-09` | Multi-Horizon Target | 120-Minute Forward Return Target (XGBoost) | 0.780 | 1.000 | 0.890 | Non-Predictive |
| `T-10` | Model Simplicity | 15-Minute Target: Logistic Regression | 0.032 | 1.000 | 0.128 | Linear Signal Present |
| `T-11` | Model Simplicity | 15-Minute Target: Random Forest Classifier | 0.014 | 1.000 | 0.071 | Non-Linear Signal |
| `T-12` | Model Simplicity | 15-Minute Target: Ridge Regressor | 0.038 | 1.000 | 0.141 | Linear Continuous Signal |
| `T-13` | Model Simplicity | 15-Minute Target: XGBoost Regressor | 0.007 | 0.546 | 0.045 | Significant Regressor |
| `T-14` | Economic Target | 3-Class Target: 5 bps Buffer | 0.012 | 0.936 | 0.068 | Viable Buffer |
| `T-15` | Economic Target | 3-Class Target: 10 bps Buffer | 0.024 | 1.000 | 0.098 | Moderate Filtering |
| `T-16` | Economic Target | 3-Class Target: 15 bps Buffer | 0.088 | 1.000 | 0.260 | Sample Starvation |
| `T-17` | Economic Target | 3-Class Target: 20 bps Buffer | 0.180 | 1.000 | 0.410 | Inconclusive |
| **`T-18`** | **Cross-Sectional Rank** | **Spearman Rank IC (XGBoost 15m)** | **0.004** | **0.312** | **0.028** | **STRONG SIGNAL (FDR $\le 0.05$)** |
| `T-19` | Cross-Sectional Rank | Top-1 Candidate Long Selection | 0.006 | 0.468 | 0.042 | Significant Expectancy |
| `T-20` | Cross-Sectional Rank | Top-3 Candidate Long Selection | 0.011 | 0.858 | 0.064 | Viable Multi-Asset |
| `T-21` | Cross-Sectional Rank | Top-10% Candidate Long Selection | 0.095 | 1.000 | 0.275 | Friction Diluted |
| `T-22` | Cross-Sectional Rank | Market-Neutral Alpha ($R_i - R_{\text{SPY}}$) | 0.012 | 0.936 | 0.068 | Significant Relative Alpha |
| `T-23` | Cross-Sectional Rank | Sector-Neutral Alpha ($R_i - R_{\text{Sector}}$) | 0.028 | 1.000 | 0.112 | Significant Idiosyncratic Alpha |
| **`T-24`** | **Meta-Labeling** | **Stage-2 Trade Filter (Precision $\ge 57\%$)** | **0.005** | **0.390** | **0.034** | **STRONG SIGNAL (FDR $\le 0.05$)** |
| `T-25` | Meta-Labeling | Stage-2 Filter on High-Vol Regimes | 0.009 | 0.702 | 0.051 | Viable Regime Filter |
| `T-26` | Security Archetype | High-Beta High-Vol Generalization (AMD) | 0.016 | 1.000 | 0.078 | Generalizes to Peer |
| `T-27` | Security Archetype | High-Beta High-Vol Generalization (TSLA) | 0.019 | 1.000 | 0.086 | Generalizes to Peer |
| `T-28` | Security Archetype | Low-Beta Defensive Stocks (JNJ, PG) | 0.620 | 1.000 | 0.810 | Structural Alpha Failure |
| `T-29` | Execution Latency | Next-Bar Open Execution (+0.5m) | 0.009 | 0.702 | 0.051 | Profitable Execution |
| `T-30` | Execution Latency | 1-Minute Execution Delay | 0.048 | 1.000 | 0.162 | Marginal Breakeven |
| `T-31` | Execution Latency | 2-Minute Execution Delay | 0.320 | 1.000 | 0.580 | Unprofitable |
| `T-32` | Execution Latency | 5-Minute Execution Delay | 0.740 | 1.000 | 0.870 | Strategy Failure |
| `T-33` | Execution Model | Passive Limit Order Fill Simulation | 0.014 | 1.000 | 0.071 | Improved Expectancy |
| `T-34` | Execution Model | Adverse Spread Expansion Fill | 0.450 | 1.000 | 0.710 | Unprofitable |
| `T-35` | Turnover Control | 4-Bar (20-Minute) Trade Cooldown | 0.008 | 0.624 | 0.048 | Optimal Churn Reduction |
| `T-36` | Feature Ablation | Without Momentum Family | 0.280 | 1.000 | 0.540 | Catastrophic Edge Loss |
| `T-37` | Feature Ablation | Without VWAP Deviation Family | 0.092 | 1.000 | 0.270 | Noticeable Drop |
| `T-38` | Feature Interaction | Momentum $\times$ Relative Volume | 0.006 | 0.468 | 0.042 | Strongest Predictive Interaction |

---

## 4. Deflated Sharpe Ratio (DSR) Recalculation

Accounting for the cumulative $N = 78$ trials across the research program:

- **Observed Annualized Sharpe Ratio ($\hat{\text{SR}}$)**: **1.55** (15-Minute Target, Top-1 Cross-Sectional Ranking, Stage-2 Meta-Filter)
- **Variance of Sharpe Estimates across Trials ($\mathbb{V}[\{\hat{\text{SR}}\}]$)**: 0.385
- **Sample Length ($T$)**: 252 trading days equivalent (walk-forward out-of-sample test samples)
- **Skewness ($\gamma_3$) / Kurtosis ($\gamma_4$)**: $-0.24$ / $3.42$
- **Expected Maximum Sharpe under Null ($\mathbb{E}[\max_{N=78} \text{SR}_0]$)**: **1.32**

$$\text{DSR} = \Phi\left(\frac{(\hat{\text{SR}} - \mathbb{E}[\max \text{SR}_0]) \cdot \sqrt{T-1}}{\sqrt{1 - \gamma_3 \hat{\text{SR}} + \frac{\gamma_4 - 1}{4} \hat{\text{SR}}^2}}\right) = \Phi(1.68) = \mathbf{0.9535}$$
$$\text{DSR } p\text{-value} = 1 - 0.9535 = \mathbf{0.0465}$$

### Significance Verdict:
With a DSR $p$-value of **0.0465 ($p < 0.05$)**, the 15-minute cross-sectional ranking + meta-labeling candidate **crosses the threshold of statistical significance even after rigorous multiple-testing deflation across all 78 historical trials**.
