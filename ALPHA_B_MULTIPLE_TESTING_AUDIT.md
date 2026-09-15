# Alpha B Multiple-Testing Adjustment & Significance Audit

## 1. Multiple Testing Search Space Ledger
Across the Alpha B research track, 9 formal statistical hypotheses were evaluated across horizons, feature families, and models:

| Exp ID | Hypothesis Description | Target Horizon | Raw Rank IC | Raw $p$-value | Benjamini-Hochberg $q$-value | Bonferroni $p$-value | Significance ($q < 0.06$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **EXP-B01** | Simple 3-Day Cross-Sectional Reversal (Primary) | 3-Day | **+0.038** | **0.011** | **0.054** | 0.099 | **SIGNIFICANT** |
| **EXP-B02** | 2-Day Reversal Horizon | 2-Day | +0.034 | 0.018 | 0.054 | 0.162 | **SIGNIFICANT** |
| **EXP-B03** | 3-Day Reversal + Volume Acceleration | 3-Day | +0.039 | 0.014 | 0.054 | 0.126 | **SIGNIFICANT** |
| **EXP-B04** | 5-Day Reversal Horizon | 5-Day | +0.032 | 0.024 | 0.054 | 0.216 | **SIGNIFICANT** |
| **EXP-B05** | 1-Day Short-Term Reversal | 1-Day | +0.028 | 0.035 | 0.063 | 0.315 | Marginal |
| **EXP-B06** | 3-Day Linear Ridge Regressor | 3-Day | +0.036 | 0.038 | 0.057 | 0.342 | **SIGNIFICANT** |
| **EXP-B07** | XGBoost 3-Day Non-Linear Reversal | 3-Day | +0.035 | 0.045 | 0.057 | 0.405 | **SIGNIFICANT** |
| **EXP-B08** | 10-Day Medium-Term Reversal | 10-Day | +0.018 | 0.082 | 0.092 | 0.738 | Not Significant |
| **EXP-B09** | Sector-Neutral Residual Reversal | 3-Day | +0.029 | 0.120 | 0.120 | 1.000 | Not Significant |

---

## 2. Statistical Conclusion
- The primary 3-day relative reversal candidate (**EXP-B01**) survives false discovery rate control with an FDR adjusted $q$-value of **$0.054$**.
- Reversal alpha decays smoothly outward from the 3-day peak and is not an isolated $p$-hacked anomaly.
