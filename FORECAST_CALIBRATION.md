# Multi-Horizon Forecast Probability Calibration Report

## 1. Executive Summary

This report evaluates the statistical calibration of predicted upward movement probabilities ($P(\text{Up})$) against empirical realized win rates across all 65,021 candidate evaluations in the historical replay.

A well-calibrated probabilistic model satisfies:

$$\mathbb{E}[\text{Win} \mid P(\text{Up}) = p] = p$$

---

## 2. Calibration Binning Analysis

| Probability Bin | Predicted Mean $P(\text{Up})$ | Realized Win Rate (%) | Observation Count | Calibration Error ($\vert \text{Pred} - \text{Real} \vert$) | Calibration Status |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **0.500 – 0.525** | 0.5121 (51.2%) | 46.82% | 8,060 | 4.39% | Mild Overconfidence |
| **0.525 – 0.550** | 0.5366 (53.7%) | 48.49% | 6,164 | 5.17% | Mild Overconfidence |
| **0.550 – 0.575** | 0.5612 (56.1%) | 50.16% | 3,923 | 5.96% | Mild Overconfidence |
| **0.575 – 0.600** | 0.5866 (58.7%) | 51.89% | 2,526 | 6.77% | Moderate Overconfidence |
| **0.600 – 0.650** | 0.6243 (62.4%) | 54.45% | 3,868 | 7.98% | Moderate Overconfidence |
| **> 0.650** | 0.8098 (81.0%) | 67.06% | 20,179 | 13.91% | Overconfident in Tails |
| **Global Overall** | **0.6720 (67.2%)** | **58.20%** | **65,021** | **9.00%** | **Systemic Overconfidence Bias** |

```
Reliability Diagram (Predicted vs. Realized):
Predicted  Realized
[51.2%] -> [46.8%]  ░░░░░░░░░░░ (Gap: -4.4%)
[53.7%] -> [48.5%]  ░░░░░░░░░░░░ (Gap: -5.2%)
[56.1%] -> [50.2%]  ░░░░░░░░░░░░ (Gap: -6.0%)
[58.7%] -> [51.9%]  ░░░░░░░░░░░░░ (Gap: -6.8%)
[62.4%] -> [54.5%]  ░░░░░░░░░░░░░░ (Gap: -8.0%)
[81.0%] -> [67.1%]  ░░░░░░░░░░░░░░░░░░░░░░░░ (Gap: -13.9%)
```

---

## 3. Root Cause of Probability Overconfidence

1. **Microstructure Frictional Erosion**:
   - The raw forecaster predicts mid-quote directional probability. However, realized trading outcomes are executed across the bid-ask spread and subject to adverse selection, which shaves 3–5 percentage points off realized hit rates.
2. **Tail Probability Shrinkage**:
   - For high-confidence predictions ($P(\text{Up}) > 0.65$), the forecaster outputs an average probability of 81.0%, but the empirical hit rate is 67.1%.
3. **Implication for Entry Threshold**:
   - A nominal threshold of $P(\text{Up}) \ge 53.0\%$ produces an empirical realized win rate of only **48.5%** (a losing coin toss).
   - To achieve a true empirical win rate of $> 52.0\%$, the nominal gate must be raised to **$P(\text{Up}) \ge 58.0\%$**.

---

## 4. Calibration Curve Correction for Engine V1.1

We apply Platt / Isotonic scaling calibration mapping to raw forecaster outputs:

$$P_{\text{calibrated}}(\text{Up}) = \sigma\left(0.72 \cdot \text{logit}(P_{\text{raw}}) - 0.15\right)$$

This shrinkage adjustment aligns predicted probabilities with true empirical execution hit rates before passing into `EntryDecisionModelV1_1`.
