# Allocation Research Stress Testing Report

## 1. Executive Summary

This report evaluates the resilience of the candidate `CAPPED_RISK_PARITY` allocation policy under severe macroeconomic, structural, and single-strategy failure stress regimes.

---

## 2. Stress Scenario Results Matrix

| Stress Scenario ID | Stress Description & Injection | Baseline Sharpe | Stressed Sharpe | Baseline MaxDD (%) | Stressed MaxDD (%) | Cash Cushion (%) | Resilience Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`ALPHA_A_ZERO_EXPECTANCY`** | Alpha A net returns shifted to 0 bps | 7.17 | **1.85** | 1.44% | **2.45%** | 4.5% | **Pass** (B sustains portfolio) |
| **`ALPHA_B_ZERO_EXPECTANCY`** | Alpha B net returns shifted to 0 bps | 7.17 | **4.20** | 1.44% | **1.58%** | 4.5% | **Pass** (A sustains portfolio) |
| **`CORRELATION_SPIKE_POS_80`**| Cross-strategy correlation pushed to +0.80 | 7.17 | **4.85** | 1.44% | **2.15%** | 4.5% | **Pass** (Drawdown contained) |
| **`ALPHA_A_FRICTION_PLUS_50PCT`**| Alpha A friction surges by +50% (+1.88 bps)| 7.17 | **5.45** | 1.44% | **1.52%** | 4.5% | **Pass** (Edge preserved) |
| **`ALPHA_B_OVERNIGHT_GAP_SHOCK_2PCT`**| Repeated -2.0% gap down shocks on B | 7.17 | **4.60** | 1.44% | **2.65%** | 4.5% | **Pass** (Drawdown < 3.0%) |

---

## 3. Structural Robustness Diagnosis

1. **Dual-Engine Redundancy**:
   If either Alpha A or Alpha B experiences complete edge decay (zero net expectancy), the remaining strategy preserves positive account-level Sharpe (>1.85) and prevents severe capital drawdowns.
2. **Correlation Surge Absorption**:
   Even if cross-asset correlations spike to +0.80 during a market-wide liquidity event, combined max drawdown remains contained at 2.15% (well below the 5.0% account threshold).
