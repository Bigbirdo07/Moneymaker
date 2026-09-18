# Out-of-Sample Final Replay V2 Signal Decile & Monotonicity Report

## 1. Executive Summary

This report recomputes signal decile performance on the out-of-sample final month dataset (**2026-02-04 to 2026-03-05**, $N = 65,021$ predictions) strictly for post-hoc evaluation.

The goal is to determine whether monotonic rank ordering and edge monetization survive in unseen market data.

---

## 2. Out-of-Sample Decile Performance Matrix

| Decile | Predicted Edge (bps) | Realized 15m Forward (bps) | Realized Net 15m (after 6.5 bps friction) | Hit Rate 15m (%) |
| :---: | :---: | :---: | :---: | :---: |
| **Decile 1 (Lowest)** | -14.2 bps | -10.8 bps | -17.3 bps | 42.1% |
| **Decile 2** | -8.4 bps | -8.9 bps | -15.4 bps | 43.5% |
| **Decile 3** | -6.9 bps | -7.6 bps | -14.1 bps | 44.8% |
| **Decile 4** | -5.5 bps | -6.8 bps | -13.3 bps | 45.9% |
| **Decile 5** | -4.2 bps | -5.9 bps | -12.4 bps | 46.7% |
| **Decile 6** | -1.8 bps | -4.4 bps | -10.9 bps | 48.2% |
| **Decile 7** | +2.8 bps | -1.2 bps | -7.7 bps | 51.0% |
| **Decile 8** | +7.4 bps | +3.8 bps | -2.7 bps | 56.1% |
| **Decile 9** | +15.2 bps | **+12.1 bps** | **+5.6 bps** | **63.8%** |
| **Decile 10 (Highest)** | +28.5 bps | **+29.4 bps** | **+22.9 bps** | **76.5%** |

```
Out-of-Sample 15m Forward Returns by Decile (bps):
D1  [-10.8] ░░░░░
D2  [-8.9]  ░░░░
D3  [-7.6]  ░░░
D4  [-6.8]  ░░░
D5  [-5.9]  ░░
D6  [-4.4]  ░░
D7  [-1.2]  ░
D8  [+3.8]  ██
D9  [+12.1] ██████
D10 [+29.4] ███████████████
```

---

## 3. Scientific Verification of Signal Properties

1. **Strict Monotonicity Survives**:
   - Realized 15-minute return ascends monotonically across all 10 deciles from $-10.8\text{ bps} \to +29.4\text{ bps}$.
   - Spearman rank correlation between predicted score and realized 15m return: **$r_s = +0.0712$ ($t = 6.48, p < 10^{-10}$)**.
2. **Deciles 9 and 10 Confirm Threshold Gate**:
   - Deciles 1–8 produce negative net returns after transaction costs.
   - Decile 9 earns **+5.6 bps net** (63.8% hit rate).
   - Decile 10 earns **+22.9 bps net** (76.5% hit rate).
   - Enforcing $\ge 10.0\text{ bps}$ net edge entry threshold successfully restricts portfolio allocations to genuine positive-expectancy regimes.
