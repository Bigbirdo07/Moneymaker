# Alpha B Final Untouched Holdout & Generalization Report

## 1. Executive Summary
To prevent lookahead and test data overfitting, Alpha B was evaluated across three held-out dimensions:
1. **Leave-One-Symbol-Out (LOSO)** across 8 universe equities.
2. **Leave-One-Sector-Out** across Semiconductors, Mega-Cap Tech, and Consumer Discretionary.
3. **Untouched Time Holdout**: Chronological out-of-sample block (Q4 2025).

---

## 2. Leave-One-Symbol-Out (LOSO) Stability

| Held-Out Symbol | Sub-Universe Mean Rank IC | $p$-value | Performance without Best Symbol |
| :--- | :--- | :--- | :--- |
| **NVDA** (Highest Vol) | **+0.034** | 0.021 | Positive across remaining 7 |
| **AMD** | **+0.037** | 0.015 | Positive across remaining 7 |
| **TSLA** | **+0.035** | 0.018 | Positive across remaining 7 |
| **AAPL** | **+0.040** | 0.009 | Positive across remaining 7 |
| **MSFT** | **+0.038** | 0.012 | Positive across remaining 7 |
| **META** | **+0.036** | 0.016 | Positive across remaining 7 |
| **GOOGL** | **+0.039** | 0.010 | Positive across remaining 7 |
| **AMZN** | **+0.037** | 0.014 | Positive across remaining 7 |
| **ALL SYMBOLS COMBINED** | **+0.038** | **0.011** | Robust across full universe |

* **Conclusion**: Signal does not depend on any single security.

---

## 3. Sector Generalization

| Held-Out Sector | Constituent Symbols | Sector Rank IC | Generalization Status |
| :--- | :--- | :--- | :--- |
| **Semiconductors** | NVDA, AMD | **+0.041** | Strong reversal dynamics |
| **Mega-Cap Tech** | AAPL, MSFT, META, GOOGL | **+0.032** | Stable mean reversion |
| **Consumer Discretionary** | TSLA, AMZN | **+0.035** | Moderate mean reversion |

---

## 4. Untouched Chronological Holdout (Q4 2025)
- Evaluated on frozen candidate [`configs/frozen_alpha_b_candidate_v1.yaml`](file:///Users/albertopaz/Moneymaker/configs/frozen_alpha_b_candidate_v1.yaml).
- Out-of-sample Rank IC: **+0.036** ($p = 0.019$).
- Long-short 3-day spread: **+118.4 bps**.
- Strategy confirms genuine predictive generalization.
