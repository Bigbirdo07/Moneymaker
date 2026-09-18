# Intraday Time-of-Day Performance & P&L Attribution Report

## 1. Executive Summary

This report segments trading performance across five distinct intraday trading windows to evaluate the interaction between market microstructure regimes and strategy profitability.

---

## 2. Intraday Performance Breakdown

| Time Bucket | ET Hours | Trade Count | Win Rate (%) | Gross P&L ($) | Friction ($) | Net P&L ($) | Net Expectancy / Trade ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Market Open Rush** | 09:30 – 10:30 | 218 | 28.4% | -$26.40 | $14.20 | -$40.60 | -$0.1862 |
| **Morning Trend** | 10:30 – 11:30 | 142 | 33.1% | -$12.10 | $9.30 | -$21.40 | -$0.1507 |
| **Midday Lull** | 11:30 – 14:00 | 164 | 30.5% | -$18.20 | $10.70 | -$28.90 | -$0.1762 |
| **Afternoon Power** | 14:00 – 15:30 | 108 | 38.9% | -$2.52 | $7.10 | -$9.62 | -$0.0891 |
| **Market Close** | 15:30 – 16:00 | 26 | 34.6% | $0.00 | $1.70 | -$1.72 | -$0.0662 |
| **Total Session** | **09:30 – 16:00** | **658** | **32.4%** | **-$59.24** | **$43.00** | **-$102.24** | **-$0.1809** |

```
Net Loss by Time of Day ($):
09:30 - 10:30  ████████████████████ (-$40.60, 39.7% of total losses)
10:30 - 11:30  ██████████ (-$21.40, 20.9% of total losses)
11:30 - 14:00  ██████████████ (-$28.90, 28.3% of total losses)
14:00 - 15:30  █████ (-$9.62, 9.4% of total losses)
15:30 - 16:00  █ (-$1.72, 1.7% of total losses)
```

---

## 3. Forensic Analysis by Window

### 1. Market Open Rush (09:30–10:30 ET) — *Severe Underperformance*:
- **Loss Contribution**: 39.7% of all strategy losses occurred in the first 60 minutes.
- **Microstructure Mechanics**: Bid-ask spreads and volatility are widest at open. The model entered 218 trades immediately upon market open with low edge thresholds (4.0 bps), suffering wide fill slippage and rapid morning whip-saws.

### 2. Midday Lull (11:30–14:00 ET) — *Choppy Churn*:
- **Loss Contribution**: 28.3% of total losses.
- **Microstructure Mechanics**: Low volume and range-bound chop caused false momentum signals, leading to 164 trades that decayed into stops.

### 3. Afternoon Window (14:00–15:30 ET) — *Relative Stability*:
- Higher win rate (38.9%) and lowest gross loss per trade (-$0.0233 gross), as institutional block flows establish clearer directional trends.

---

## 4. Policy Updates for Engine V1.1

1. **Morning Spread Buffer**: Restrict entries in the 09:30–09:45 open window unless net edge exceeds $\ge 15.0\text{ bps}$ and spread is $\le 8.0\text{ bps}$.
2. **Midday Participation Filter**: Reduce max concurrent positions during 11:30–13:30 to 1 position unless high-confidence volume confirmation is present.
