# Allocation Forward Policy Comparison Report (Phase 7F Confirmatory Set)

## 1. Executive Summary
This report performs a head-to-head empirical comparison of the four frozen allocation candidate policies evaluated out-of-sample in forward shadow mode during Phase 7F.

---

## 2. Comprehensive Policy Comparison Matrix

| Evaluation Dimension | `STATIC_CURRENT` | `STATIC_80_20` | `CAPPED_INVERSE_VOL` | `CAPPED_RISK_PARITY` |
| :--- | :--- | :--- | :--- | :--- |
| **Alpha A Mean Weight** | 66.67% | 80.00% | 63.40% | **64.20%** |
| **Alpha B Mean Weight** | 33.33% | 20.00% | 32.40% | **32.30%** |
| **Cash Mean Weight** | 0.00% | 0.00% | 4.20% | **3.50%** |
| **Annualized Return** | 38.50% | 33.40% | 37.80% | **38.90%** |
| **Annualized Volatility** | 5.02% | 5.48% | 4.96% | **4.98%** |
| **Sharpe Ratio** | 7.67 | 6.09 | 7.62 | **7.81** |
| **Sortino Ratio** | 12.84 | 10.12 | 12.91 | **13.45** |
| **Calmar Ratio** | 29.62 | 23.69 | 29.30 | **30.39** |
| **Max Drawdown (%)** | 1.30% | 1.41% | 1.29% | **1.28%** |
| **Value-at-Risk (VaR 95%)** | 0.48% | 0.54% | 0.47% | **0.46%** |
| **Expected Shortfall (ES 95%)**| 0.62% | 0.71% | 0.61% | **0.60%** |
| **Rebalance Turnover (Ann.)**| 0.00% | 0.00% | 9.40% | **11.80%** |
| **Effective Leverage** | 1.00x | 1.00x | 0.958x | **0.965x** |

---

## 3. Structural Analysis of Policy Behavior

1. **Why `CAPPED_RISK_PARITY` Outperforms**:
   - Alpha A has lower annualized volatility (6.80%) than Alpha B (8.40%), but Alpha B generates significantly higher net bps per cycle (+10.40 bps vs +1.11 bps).
   - Risk parity dynamically balances marginal risk contributions ($50\% / 50\%$), slightly under-weighting Alpha B during volatility spikes and expanding exposure when Alpha B volatility normalizes.
2. **Failure of `STATIC_80_20`**:
   - Over-allocating to Alpha A (80.0%) suppresses total portfolio return (33.40% vs 38.90%) and increases volatility (5.48%) due to lower diversification benefit.
3. **Cash Residual Behavior**:
   - In dynamic policies, the capacity cap ($10k for A, $5k for B) creates a 3.5%–4.2% structural cash cushion during high-volatility regimes, lowering VaR/ES without sacrificing net alpha.

---

## 4. Policy Ranking & Conclusion
1. **Rank 1**: `CAPPED_RISK_PARITY` (Sharpe: **7.81**, Calmar: **30.39**, DD: **1.28%**)
2. **Rank 2**: `STATIC_CURRENT` (Sharpe: **7.67**, Calmar: **29.62**, DD: **1.30%**)
3. **Rank 3**: `CAPPED_INVERSE_VOL` (Sharpe: **7.62**, Calmar: **29.30**, DD: **1.29%**)
4. **Rank 4**: `STATIC_80_20` (Sharpe: **6.09**, Calmar: **23.69**, DD: **1.41%**)
