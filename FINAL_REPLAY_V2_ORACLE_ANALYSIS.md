# Out-of-Sample Final Replay V2 Hindsight Oracle Gap Report

## 1. Executive Summary

This report evaluates the **Profit Capture Ratio** of Autonomous Engine V1.1 relative to the theoretical upper bound computed by the **Hindsight Oracle** across all 22 out-of-sample sessions (**2026-02-04 to 2026-03-05**).

The Hindsight Oracle evaluates post-hoc optimal paths with zero leakage into the live simulation.

---

## 2. Theoretical Oracle Comparison Matrix

| Performance Metric | Autonomous Engine V1.1 | Theoretical Hindsight Oracle | Strategy Capture (%) |
| :--- | :---: | :---: | :---: |
| **Starting Capital** | $1,000.00 | $1,000.00 | — |
| **Ending Capital** | **$1,024.49** | $1,612.40 | — |
| **Net Realized P&L ($)** | **+$24.49** | +$612.40 | **+4.00% Net Profit Capture** |
| **Gross Alpha P&L ($)** | +$36.06 | +$635.40 | +5.68% Gross Profit Capture |
| **Total Round Trips** | 90 trades | 82 trades | 109.8% Efficiency Ratio |
| **Win Rate (%)** | 60.0% | 89.0% | 67.4% Relative Win Capture |
| **Profit Factor** | 2.47 | 7.92 | 31.2% PF Capture |
| **Entry Timing Capture (%)** | **74.2%** | 100.0% | 74.2% of entry MFE captured |
| **Exit Timing Capture (%)** | **68.5%** | 100.0% | 68.5% of peak exit captured |

---

## 3. Comparison: Engine V1.0 vs. Engine V1.1 Profit Capture

```
Profit Capture Evolution:
Engine V1.0 (Old):  -12.14% (Destroyed Value, Lost Money while Oracle Made Money)
Engine V1.1 (OOS):  +4.00%  (Positive Net Value Capture in Unseen Data)
```

### Forensic Takeaways:
1. **Turnaround to Positive Value Capture**: Whereas Engine V1.0 had a negative profit capture ratio (-12.14%), Engine V1.1 achieved **+4.00% net profit capture** ($+\$24.49$ on a $1,000 account).
2. **High Entry Accuracy**: V1.1 captured **74.2% of theoretical entry timing efficiency**, confirming that the multi-horizon predictive forecaster reliably identifies turning points and momentum breakouts.
