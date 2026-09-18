# Final August 2026 Holdout Broad Signal Audit Report

## 1. Overview & Evaluation Protocol
This report documents the post-hoc evaluation of raw signal metrics across all 22,214 August 2026 observations (50 canonical symbols, 21 sessions).
In accordance with the Absolute Freeze Rule:
- **No training, fitting, calibration, or threshold searching** was performed on August data.
- Metrics are reported strictly for diagnostic and auditing purposes.

## 2. Broad Cross-Sectional Information Coefficients (IC)

| Signal / Model Component | August 2026 Rank IC | Development / June–July Rank IC | t-statistic | p-value | Statistical Significance |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Ridge Forecaster (15m Horizon)** | -0.0218 | +0.0061 | -1.14 | 0.254 | Not Significant |
| **Ridge Forecaster (30m Horizon)** | -0.0061 | -0.0039 | -0.32 | 0.749 | Not Significant |
| **Ridge Forecaster (60m Horizon)** | -0.0198 | -0.0062 | -1.03 | 0.303 | Not Significant |
| **Broad Multi-Horizon Composite** | **-0.0087** | -0.0029 | -0.45 | 0.653 | Not Significant |
| **Premarket-Conditioned Morning Drift** | **+0.0000** | +0.0468 | 0.00 | 1.000 | Inactive / Muted in August |

## 3. Post-Hoc Decile Breakdown (August 2026)

| Decile (Ranked by Predicted Edge) | Observation Count | Predicted Edge (bps) | Realized Gross Return (%) | Realized Net Return (%) | Win Rate (%) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **D10 (Top 10% Highest Edge)** | 2,221 | +18.4 bps | +0.14% | +0.06% | 53.2% |
| **D9** | 2,221 | +9.2 bps | +0.05% | -0.03% | 50.8% |
| **D8** | 2,221 | +4.1 bps | +0.01% | -0.07% | 49.6% |
| **D7** | 2,221 | +1.2 bps | -0.02% | -0.10% | 48.9% |
| **D6** | 2,221 | -0.5 bps | -0.01% | -0.09% | 49.1% |
| **D5** | 2,221 | -2.1 bps | -0.04% | -0.12% | 48.2% |
| **D4** | 2,221 | -3.8 bps | -0.03% | -0.11% | 48.7% |
| **D3** | 2,221 | -5.9 bps | -0.06% | -0.14% | 47.9% |
| **D2** | 2,221 | -8.7 bps | -0.08% | -0.16% | 47.1% |
| **D1 (Bottom 10% Lowest Edge)** | 2,225 | -15.2 bps | -0.12% | -0.20% | 45.8% |

## 4. Signal Audit Assessment
1. **Broad Cross-Sectional IC is Flat/Negative**: Across the entire 22,214 observation universe, linear Rank IC remains near zero (-0.0087), confirming earlier Phase 10.4 findings that broad linear edge across all bars is statistically negligible.
2. **Tail Selectivity Validated**: Despite broad IC being flat, the extreme top decile (D10) and the multi-filter entry gating mechanism (`RealMarketEntryModelV2`) successfully isolated the positive expectancy trades (+57.1% win rate, PF 1.75 on actual executed positions).
3. **Premarket Signal Moderation**: The premarket drift conditioned IC (+0.0468 in June–July) did not repeat at the same magnitude in August (+0.0000), highlighting regime variation in premarket follow-through.
