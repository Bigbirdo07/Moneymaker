# Multi-Strategy Allocation Baseline Comparison Report

## 1. Executive Summary

This report compares the offline simulated performance of 8 allocation policies over the 60-session Phase 7E return dataset ($12,500 total capital basis).

---

## 2. Quantitative Performance Matrix

| Allocation Policy | Ann. Return (%) | Ann. Volatility (%) | Sharpe Ratio | Sortino Ratio | Calmar Ratio | Max Drawdown (%) | Max Drawdown ($) | Avg Cash Weight (%) | Ann. Turnover (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`STATIC_90_10`** | 30.52% | 5.24% | 5.82 | 7.85 | 20.48 | 1.49% | $186.25 | 0.0% | 0.0% |
| **`STATIC_80_20` (Current Live)**| **35.80%** | **5.08%** | **7.05** | **9.62** | **24.69** | **1.45%** | **$181.25** | **0.0%** | **0.0%** |
| **`STATIC_70_30`** | 39.45% | 5.42% | 7.28 | 10.05 | 24.18 | 1.63% | $203.75 | 0.0% | 0.0% |
| **`STATIC_60_40`** | 44.10% | 6.05% | 7.29 | 10.12 | 23.45 | 1.88% | $235.00 | 0.0% | 0.0% |
| **`STATIC_50_50`** | 48.75% | 6.88% | 7.08 | 9.85 | 22.06 | 2.21% | $276.25 | 0.0% | 0.0% |
| **`EQUAL_RISK`** | 34.12% | 5.15% | 6.62 | 9.15 | 23.21 | 1.47% | $183.75 | 2.5% | 18.5% |
| **`CAPPED_INVERSE_VOL`**| 34.85% | 5.12% | 6.81 | 9.38 | 23.87 | 1.46% | $182.50 | 3.0% | 15.8% |
| **`CAPPED_RISK_PARITY`**| **36.20%** | **5.05%** | **7.17** | **9.80** | **25.14** | **1.44%** | **$180.00** | **4.5%** | **14.2%** |

---

## 3. Analysis & Comparative Insights

1. **Static 80/20 vs Dynamic Risk Parity**:
   The current static live partition (80% Alpha A @ $10k, 20% Alpha B @ $2.5k) performs remarkably close to dynamic capped risk parity (Sharpe 7.05 vs 7.17), while incurring **zero rebalancing turnover**.
2. **Turnover Friction Drag**:
   Dynamic rebalancing generates 14.2% to 18.5% annualized weight turnover, which would incur minor transaction friction in live execution.
3. **Capacity Constraints**:
   Policies attempting >20% allocation to Alpha B (`STATIC_70_30`, `STATIC_60_40`, `STATIC_50_50`) breach Alpha B's validated capacity limit ($2,500 USD) unless excess is converted to cash.
