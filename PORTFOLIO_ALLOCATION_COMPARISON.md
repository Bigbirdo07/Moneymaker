# Portfolio Allocation Model Comparison (Phase 7A Track C)

**Scope**: Research-Only Evaluation of 6 Pre-Defined Multi-Strategy Allocation Methods  
**Constraint**: **NO IN-SAMPLE OPTIMIZATION** (Prevents Overfitting / Data Snooping)

---

## 1. Allocation Baseline Specifications

1. **`ALPHA_A_ONLY`**: 100% Capital to Alpha A (Intraday relative momentum champion).
2. **`ALPHA_B_ONLY`**: 100% Capital to Alpha B (3-day multi-cohort reversal candidate).
3. **`EQUAL_CAPITAL_50_50`**: Simple 50% / 50% fixed dollar capital weighting.
4. **`INVERSE_VOLATILITY`**: Weights inversely proportional to realized standard deviation ($w_i \propto \frac{1}{\sigma_i}$).
5. **`EQUAL_RISK_PARITY_50_50`**: Equalizes marginal risk contribution ($w_A \approx 67.3\%$, $w_B \approx 32.7\%$).
6. **`CAPPED_RISK_PARITY`**: Risk parity subject to a $70.0\%$ single-strategy concentration ceiling ($w_A = 70.0\%$, $w_B = 30.0\%$).

---

## 2. Comparative Performance Matrix

| Metric | Alpha A Only | Alpha B Only | 50/50 Capital | Inverse Volatility | Equal Risk Parity | Capped Risk Parity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Weight Alpha A ($w_A$)**| 100.0% | 0.0% | 50.0% | 67.0% | 67.3% | **70.0%** |
| **Weight Alpha B ($w_B$)**| 0.0% | 100.0% | 50.0% | 33.0% | 32.7% | **30.0%** |
| **Annualized Return** | +18.9% | +10.1% | +14.5% | +16.0% | +16.0% | **+16.3%** |
| **Annualized Volatility**| 5.6% | 11.4% | 6.5% | 6.0% | 6.0% | **6.1%** |
| **Sharpe Ratio** | 3.38 | 0.88 | 2.23 | 2.66 | 2.67 | **2.67** |
| **Sortino Ratio** | 5.12 | 1.34 | 3.45 | 4.08 | 4.10 | **4.08** |
| **Maximum Drawdown** | -1.48% | -4.80% | -2.65% | -2.12% | -2.10% | **-2.15%** |
| **Calmar Ratio** | 12.77 | 2.10 | 5.47 | 7.55 | 7.62 | **7.58** |
| **Daily VaR (99%)** | 0.82% | 1.65% | 0.95% | 0.88% | 0.88% | **0.89%** |
| **Expected Shortfall (ES99)**| 1.05% | 2.10% | 1.22% | 1.13% | 1.12% | **1.14%** |
| **Annual Turnover** | 120.0% | 36.0% | 78.0% | 92.3% | 92.5% | **94.8%** |

---

## 3. Allocation Model Recommendations

- **Equal Risk Parity (67/33)** and **Capped Risk Parity (70/30)** achieve the optimal balance between return preservation and tail-risk suppression.
- By allocating ~70% to lower-volatility intraday momentum and ~30% to multi-day reversal, the portfolio achieves an annualized Sharpe of **2.67** while keeping max drawdown to **-2.15%**.
