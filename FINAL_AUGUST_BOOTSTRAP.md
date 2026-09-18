# Final August 2026 Holdout Statistical Uncertainty & Bootstrap Report

## 1. Overview & Methodological Caveats
August 2026 comprises a single 21-session calendar month (28 executed trades).
Standard annualized Sharpe ratios calculated from a single month are subject to extreme small-sample noise and estimation bias.
To quantify the statistical uncertainty of the observed results, we employ:
1. **Trade-Level Non-Parametric Bootstrap** (10,000 iterations with replacement).
2. **Session-Level Non-Parametric Bootstrap** (10,000 iterations with replacement).

## 2. Bootstrap Uncertainty Estimates

| Metric | Point Estimate | 95% Confidence Interval (Low) | 95% Confidence Interval (High) | Standard Error |
| :--- | :---: | :---: | :---: | :---: |
| **Monthly Net P&L ($)** | **+$51.25** | **-$45.38** | **+$147.24** | $48.82 |
| **Net Return (%)** | **+5.12%** | **-4.54%** | **+14.72%** | 4.88% |
| **Per-Trade Expectancy ($)** | **+$1.84** | **-$1.62** | **+$5.26** | $1.74 |
| **Win Rate (%)** | **57.1%** | **39.3%** | **75.0%** | 9.1% |
| **Profit Factor** | **1.75** | **0.62** | **3.84** | 0.81 |

## 3. Probability Distribution Analysis
- **Probability of Net Positive Month ($P(PnL > 0)$)**: **84.8%** based on 10,000 trade-level resamples.
- **Probability of Severe Loss ($P(PnL < -10\%)$)**: **< 1.2%** under frozen risk controls.

## 4. Scientific Disclosures & Limitations
1. **Wide Confidence Interval**: Because the sample size is N=28 trades across 21 sessions, the 95% CI for monthly P&L spans from -$45.38 to +$147.24. While the central tendency is clearly positive (+5.12%), zero-profitability cannot be ruled out at the 95% confidence level.
2. **No Claim of Guaranteed Returns**: This single out-of-sample month does not guarantee future profitability, true forward win rate, or asymptotic risk of ruin.
3. **Requirement for Forward Multi-Month Validation**: Definitive statistical convergence requires multi-month forward paper trading across diverse macroeconomic regimes.
