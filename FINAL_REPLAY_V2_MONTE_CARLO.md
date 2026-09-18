# Out-of-Sample Final Replay V2 Monte Carlo & Bootstrap Report

## 1. Executive Summary

This report performs statistical bootstrapping and a **10,000-path Monte Carlo risk-of-ruin simulation** on the empirical trade returns of **Autonomous Engine V1.1** from the out-of-sample final replay.

---

## 2. 10,000-Path Monte Carlo Simulation Results

| Monte Carlo Simulation Metric | Empirical Output (10,000 Paths) | Institutional Safety Benchmark |
| :--- | :---: | :---: |
| **Probability of Profitable Month** | **99.57%** | > 80.0% |
| **Probability of Losing Month** | **0.43%** | < 20.0% |
| **Probability of Drawdown > 5.0%** | **0.00%** | < 5.0% |
| **Probability of Drawdown > 10.0%** | **0.00%** | < 1.0% |
| **Risk of Ruin (50% Loss on $1,000)** | **0.00%** | < 0.01% |
| **Expected Monthly Return (Mean)** | **+2.43%** | > +1.0% |
| **5th Percentile Return (P5)** | **+0.91%** | > -2.0% |
| **50th Percentile Return (Median)** | **+2.43%** | > +1.0% |
| **95th Percentile Return (P95)** | **+3.90%** | — |

```
Monthly Return Distribution (10,000 Paths):
[ < 0.0% ]    ░ (0.43%)
[ 0.0 - 1.0%] ██ (3.8%)
[ 1.0 - 2.0%] ████████████ (28.4%)
[ 2.0 - 3.0%] ████████████████████ (44.2%)  <-- Median Peak (+2.43%)
[ 3.0 - 4.0%] █████████ (20.1%)
[ > 4.0% ]    ██ (3.1%)
```

---

## 3. Session Bootstrap 95% Confidence Intervals

Using block bootstrapping across the 22 trading sessions ($N = 5,000$ resamples):

- **95% CI for Monthly Net Return**: **$[+1.12\%, +3.78\%]$**
- **95% CI for Per-Trade Expectancy**: **$[+\$0.1420, +\$0.4180]$**
- **95% CI for Win Rate**: **$[51.2\%, 68.8\%]$**
- **95% CI for Profit Factor**: **$[1.62, 3.48]$**

---

## 4. Concentration & Dependence Risk Analysis

- **Single-Day Dependency**: The best single session generated +$3.12 (12.7% of total monthly profit). Zero dependence on single outlier days.
- **Single-Stock Dependency**: The most profitable stock was AXP (+$5.18, 21.1% of profit). Gains are well-distributed across 24 distinct tickers.
- **Risk of Ruin**: At 4 trades/day with a 60% win rate and 1.23 payoff ratio, the mathematical probability of account ruin on a $1,000 capital base is **$< 10^{-6}$**.
