# Milestone Report: Phase 2.5 — Statistical Significance, Robustness & Generalization Audit

## 1. Executive Summary & Required Final Verdict

- **Final Verdict**: **`WEAK_EVIDENCE`**
- **Core Scientific Conclusion**:
  1. **Statistically Distinguishable From Random Noise**: In permutation null tests (100 shuffles), the real XGBoost model achieved an empirical $p$-value of **$p = 0.039$** on ROC-AUC and **$p = 0.029$** on net return, demonstrating that the technical momentum and relative-strength features carry a genuine, non-random statistical association with short-term price direction.
  2. **Economically Fragile & Vulnerable to Friction**: The break-even transaction cost is **`7.82 bps`** round-trip (only $+0.82\text{ bps}$ buffer above the 7.0 bps baseline). At $1.5\times$ base friction, the net return turns negative ($-0.23\%$).
  3. **Severe Stock & Regime Concentration**: Over **65% of net profit originates from a single high-beta technology stock (NVDA)**. Performance collapses to $+0.02\%$ when NVDA is excluded. Furthermore, predictive edge is concentrated almost exclusively in `BULL_LOW_VOL` regimes and degrades in Energy and Industrials.
  4. **Rapid Signal Decay**: Peak accumulated alpha occurs at **15–30 minutes** (+4.5 bps), after which decay and mean-reversion erode edge. Execution delays of even 1 bar (5 min) flip the net strategy return negative.
  5. **Deflated Sharpe Ratio (DSR)**: After correcting for trial multiplicity ($K = 50$), the DSR $p$-value is **$p = 0.641$** ($\text{not significant}$), indicating that the observed Sharpe of $0.48$ is within the expected maximum of a multi-configuration search.

---

## 2. Frozen Phase 2 Configuration Artifact
The Phase 2 hypothesis was frozen in [`configs/frozen_phase2.yaml`](file:///Users/albertopaz/Moneymaker/configs/frozen_phase2.yaml) and evaluated without in-sample tuning:
- **Model**: XGBoost (100 trees, depth 4, learning rate 0.05, subsample 0.80)
- **Target**: 60-minute forward return binary direction ($\text{UP} \ge +0.10\%$)
- **Calibrator**: Platt sigmoid calibration on validation fold
- **Decision Filter**: Frozen threshold $p \ge 0.58$, min expected return 15 bps
- **Friction**: 1.5 bps half-spread + 2.0 bps slippage per trade

---

## 3. Multi-Fold Walk-Forward Performance Across 5 Folds

| Fold ID | Train Period | Val Period | Test Period | Train Samples | Test Samples | Test Accuracy | Net Return | Net Sharpe | Max DD |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Fold 1** | Days 1–6 | Days 7–9 | Days 10–12 | 390 | 185 | 53.8% | +0.18% | 0.68 | 0.35% |
| **Fold 2** | Days 1–7 | Days 8–10 | Days 11–13 | 468 | 185 | 52.4% | +0.06% | 0.22 | 0.48% |
| **Fold 3** | Days 1–8 | Days 9–11 | Days 12–14 | 546 | 185 | 51.9% | -0.04% | -0.14 | 0.62% |
| **Fold 4** | Days 1–9 | Days 10–12 | Days 13–15 | 624 | 185 | 54.1% | +0.22% | 0.84 | 0.38% |
| **Fold 5** | Days 1–10 | Days 11–13 | Days 14–16 | 702 | 185 | 53.0% | +0.10% | 0.38 | 0.52% |
| **Aggregate**| — | — | — | **2,730** | **925** | **53.0%** | **+0.10%** | **0.40** | **0.62%** |

*Observation: Fold 3 exhibited negative net return ($-0.04\%$) due to regime transition into higher volatility, confirming that performance is non-uniform across time folds.*

---

## 4. Key Diagnostic Summary Tables

### A. Permutation Null Test ($N = 100$)
- **Observed ROC-AUC**: $0.542$ vs Null Mean $0.501$ ($p = 0.039$ — Significant)
- **Observed Net Return**: $+0.12\%$ vs Null Mean $-0.38\%$ ($p = 0.029$ — Significant)
- **Deflated Sharpe Ratio (DSR)**: $p = 0.641$ (Not significant under 50-trial penalty)

### B. Stress Testing & Friction Break-Even
- **Break-Even Friction**: **`7.82 bps`** total round-trip.
- **Execution Delay**: 0-delay $= +0.12\%$, +5 min delay $= -0.08\%$, +10 min delay $= -0.34\%$.
- **Peak Signal Horizon**: 15–30 minutes (+4.5 bps forward drift).

### C. Cross-Sectional Generalization & Concentration
- **Sector Generalization**: Works in Tech ($+0.22\%$), Consumer ($+0.14\%$), Healthcare ($+0.08\%$); fails in Energy ($-0.21\%$) and Industrials ($-0.12\%$).
- **Concentration**: **NVDA accounts for 65% of total net profits**. Ex-NVDA return is $+0.02\%$.

---

## 5. Promotion Criteria Audit for Phase 3

| Promotion Criterion | Status | Audit Result & Notes |
| :--- | :--- | :--- |
| 1. Exceeds permutation-null | **PASS** | $p = 0.039$ on ROC-AUC, $p = 0.029$ on return |
| 2. Positive expectancy after base costs | **PASS** | $+0.12\%$ net return after 7.0 bps friction |
| 3. Independent of single symbol | **FAIL** | 65% of profit driven by NVDA alone |
| 4. Persists across multiple folds | **MARGINAL** | 4 of 5 folds positive; Fold 3 negative ($-0.04\%$) |
| 5. Survives execution delay | **FAIL** | Turns negative at +1 bar (5 min) execution delay |
| 6. Bootstrap CI compatible with positive edge | **MARGINAL** | 95% CI spans $[-3.82\%, +8.91\%]$ (contains zero) |
| 7. Robust across market regimes | **FAIL** | Fails in sideways and high-volatility regimes |
| 8. Survives cost stress testing | **FAIL** | Fails at $1.5\times$ base cost (break-even is 7.82 bps) |

---

## 6. Research Recommendations

**Do NOT proceed to autonomous paper-forward deployment yet.**

Before deploying paper capital, the following research expansions are strictly recommended:
1. **Shorter Holding Horizons (15–30 min Target)**:
   - Since the signal decay curve peaks at 15–30 minutes (+4.5 bps), retrain targets on 15m/30m holding periods rather than 60m to avoid holding through decay.
2. **Cross-Sectional Dynamic Universe Filtering**:
   - Filter universe dynamically to trade only high-RVOL / high-liquidity stocks in active trend regimes, eliminating low-edge trades in sluggish sectors.
3. **Volatility & Regime-Gated Execution**:
   - Strictly prohibit trade entries when market regime is `SIDEWAYS` or `BEAR_HIGH_VOL`.
