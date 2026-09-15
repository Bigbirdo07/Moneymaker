# Allocation Risk Contribution & Capital Attribution Report

## 1. Executive Summary

This report presents the Euler marginal risk decomposition for the candidate `CAPPED_RISK_PARITY` allocation policy compared against static weighting benchmarks on the Phase 7E dataset.

---

## 2. Volatility & Expected Shortfall Contribution

| Allocation Model | Alpha A Capital Share (%) | Alpha B Capital Share (%) | Cash Share (%) | Alpha A Vol Contribution (%) | Alpha B Vol Contribution (%) | Alpha A ES95 Contribution (%) | Alpha B ES95 Contribution (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`STATIC_90_10`** | 90.0% | 10.0% | 0.0% | 85.2% | 14.8% | 86.4% | 13.6% |
| **`STATIC_80_20` (Live)** | **80.0%** | **20.0%** | **0.0%** | **74.6%** | **25.4%** | **75.8%** | **24.2%** |
| **`STATIC_70_30`** | 70.0% | 30.0% | 0.0% | 63.8% | 36.2% | 65.1% | 34.9% |
| **`STATIC_50_50`** | 50.0% | 50.0% | 0.0% | 42.1% | 57.9% | 43.5% | 56.5% |
| **`CAPPED_RISK_PARITY`**| **76.5%** | **19.0%** | **4.5%** | **72.1%** | **27.9%** | **73.4%** | **26.6%** |

---

## 3. Analysis of Risk Balance

1. **Near-Parity Risk Balance**:
   Under `STATIC_80_20` and `CAPPED_RISK_PARITY`, Alpha A accounts for ~75% of portfolio volatility and Alpha B accounts for ~25%.
   Because Alpha B's standalone volatility (8.20%) is higher than Alpha A's (5.48%), a 4:1 capital ratio ($10k / $2.5k) achieves an effective 3:1 risk balance, heavily stabilizing portfolio return distribution without overloading the multi-day overnight inventory.
2. **Tail Contribution Match**:
   Expected Shortfall (ES95) contributions closely track volatility contributions, demonstrating that neither strategy introduces hidden, asymmetric tail risk into the joint equity curve.
