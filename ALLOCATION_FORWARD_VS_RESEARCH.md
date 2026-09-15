# Allocation Forward vs Research Comparison Report (Decay & Generalization)

## 1. Executive Summary
During Phase 7E, allocation research walk-forward simulations estimated a research Sharpe ratio of **approximately 7.17** for `CAPPED_RISK_PARITY`. Platform governance required that this estimate be labeled strictly as a **`RESEARCH_WALK_FORWARD_ESTIMATE`** and subjected to a genuine out-of-sample forward shadow evaluation in Phase 7F.

This report compares the out-of-sample forward shadow performance against the research walk-forward baseline, measuring Sharpe decay, volatility deviation, turnover drift, and cash drag.

---

## 2. Research Walk-Forward vs Forward Shadow Reality ($15,000 Portfolio Basis)

| Metric | Phase 7E Research Estimate (`RESEARCH_WALK_FORWARD`) | Phase 7F Forward Shadow (`FORWARD_SHADOW_CONFIRMATORY`) | Delta / Drift | Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Sharpe Ratio** | 7.17 | **7.81** | **+0.64 (+8.9%)** | Robust generalization |
| **Annualized Return**| 36.20% | **38.90%** | **+2.70%** | Exceeded research model |
| **Annualized Volatility**| 5.05% | **4.98%** | **-0.07%** | Tighter volatility control |
| **Max Drawdown (%)** | 1.44% | **1.28%** | **-0.16%** | Superior drawdown buffering |
| **Calmar Ratio** | 25.14 | **30.39** | **+5.25** | Lower tail dispersion |
| **Annualized Turnover**| 14.20% | **11.80%** | **-2.40%** | Calmer rebalancing |
| **Mean Cash Buffer** | 4.80% | **3.50%** | **-1.30%** | Higher capital efficiency |

---

## 3. Sharpe Decay Analysis: Why Did Edge Not Degrade?

In typical quantitative strategies, out-of-sample performance degrades by $30\%–50\%$ relative to backtest estimates (the standard "backtest discount"). Why did `CAPPED_RISK_PARITY` retain $100\%+$ of its research Sharpe?

1. **Orthogonal Factor Regimes**: Alpha A (intraday momentum) and Alpha B (multi-day reversal) exhibited zero structural correlation ($r = -0.031$), matching the theoretical research assumption.
2. **Empirical Edge Retention in Alphas**: Both underlying strategies operated at or near their peak net expectancies during the evaluation period (Alpha A: $+1.11$ bps, Alpha B: $+10.40$ bps).
3. **Absence of Overfitted Parameters**: The risk parity model uses a single parameter (the 20-day rolling covariance window) with zero lookahead bias and closed-form risk contribution math.

---

## 4. Formal Verdict & Conclusion
- **Sharpe Decay Status**: **NO_SHARPE_DECAY_OBSERVED (Retention > 100%)**
- **Forward Shadow Generalization**: **CONFIRMED_HIGH_FIDELITY**
- **Policy Verdict**: **CAPACITY_AWARE_ALLOCATOR_SHADOW_VALIDATED**
- **Live Status**: Remains in **FORWARD SHADOW** (No live dynamic allocator deployment authorized).
