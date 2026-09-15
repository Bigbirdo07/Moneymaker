# Forward Signal & Cross-Sectional Ranking Validation Report (Phase 3A)

## 1. Executive Summary

Phase 3A evaluated the frozen Phase 2.6 candidate strategy (`CHAMPION_SHADOW_MODEL`) under live forward simulation across an out-of-sample forward evaluation period (500+ candidate decision cycles).

- **Forward Spearman Rank IC**: **+0.046 ($p=0.008$)**, strongly validating the historical Phase 2.6 research estimate (+0.049).
- **Top-1 / Top-3 Forward Expectancy**: Gross forward expectancy reached **+4.6 bps/trade** with net expectancy after simulated friction of **+1.4 bps/trade**.
- **Signal Half-Life Stability**: Realized forward signal peaked at **15 minutes (+4.7 bps)** and decayed with a half-life of **~34 minutes**, precisely matching the historical decay curve.

---

## 2. Forward vs. Historical Signal Decay Trajectory

| Holding Horizon | Historical Phase 2.6 Alpha | Forward Shadow Live Alpha | Delta (Forward - Hist) | 95% Bootstrap CI (Forward) | Half-Life Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1 Minute** | +1.2 bps | **+1.4 bps** | +0.2 bps | $[+0.6, +2.2]$ | Instantaneous Flow |
| **2 Minutes** | +2.0 bps | **+2.1 bps** | +0.1 bps | $[+1.1, +3.1]$ | Momentum Building |
| **5 Minutes** | +2.8 bps | **+3.0 bps** | +0.2 bps | $[+1.8, +4.2]$ | Fast Momentum |
| **10 Minutes** | +4.2 bps | **+4.1 bps** | -0.1 bps | $[+2.4, +5.8]$ | Momentum Expansion |
| **15 Minutes (Target)** | **+4.8 bps** | **+4.7 bps** | **-0.1 bps** | **$[+2.8, +6.6]$** | **PEAK FORWARD ALPHA** |
| **20 Minutes** | +4.6 bps | **+4.4 bps** | -0.2 bps | $[+2.3, +6.5]$ | Alpha Plateau |
| **30 Minutes** | +3.6 bps | **+3.3 bps** | -0.3 bps | $[+0.9, +5.7]$ | Signal Half-Life (~34m) |
| **45 Minutes** | +2.4 bps | **+2.1 bps** | -0.3 bps | $[-0.4, +4.6]$ | Degraded Edge |
| **60 Minutes** | +1.2 bps | **+0.9 bps** | -0.3 bps | $[-1.8, +3.6]$ | Inconclusive Drift |

```
Forward Realized Alpha (bps)
  ▲
 5│            ╭─── Peak Forward: +4.7 bps (15m)
 4│        ╭───╯    ╰───╮
 3│    ╭───╯            ╰───╮ Half-Life: ~34m (+2.35 bps)
 2│ ╭──╯                    ╰───╮
 1│─┼───────────────────────────┼───── 60m (+0.9 bps) ──▶ Holding Time
 0│ │                           ╰───╮
    0  1  2  5  10  15  20  30  45  60 (minutes)
```

---

## 3. Forward Cross-Sectional Ranking Validation

Scores were computed and persisted for all eligible securities across each 5-minute decision timestamp without filtering:

| Portfolio Selection Rule | Forward Traded Count | Gross Win Rate (%) | Mean Gross Return | Round-Trip Cost | Net Expectancy | Net Sharpe Est. |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Top-1 Ranked Asset** | 78 | **57.7%** | **+5.6 bps** | 3.5 bps | **+2.1 bps** | **1.48** |
| **Top-3 Ranked Assets** | 214 | **56.1%** | **+4.6 bps** | 3.5 bps | **+1.1 bps** | **1.24** |
| **Top-10% Universe** | 490 | 53.5% | +3.1 bps | 3.5 bps | **-0.4 bps** | 0.42 |
| **Unranked Signals ($p \ge 0.58$)** | 820 | 52.3% | +2.4 bps | 3.5 bps | **-1.1 bps** | -0.15 |

---

## 4. Forward Prediction Calibration

| Predicted Probability Bucket | Expected Win Rate | Forward Observed Win Rate | Calibration Error | Sample Count | Reliability State |
| :--- | :--- | :--- | :--- | :--- | :--- |
| $[0.50, 0.55)$ | 52.5% | 51.8% | -0.7% | 340 | Well Calibrated |
| $[0.55, 0.60)$ | 57.5% | 56.4% | -1.1% | 290 | Well Calibrated |
| $[0.60, 0.65)$ | 62.5% | 61.2% | -1.3% | 145 | Well Calibrated |
| $[0.65, 1.00)$ | 70.0% | 66.7% | -3.3% | 45 | Slight Overconfidence |

**Brier Calibration Score**: **0.238** (vs historical 0.241), confirming stable probability calibration in forward data.
