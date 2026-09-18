# Trade Frequency & Holding Duration Analysis

## 1. Trade Velocity Overview

Autonomous Engine V1.0 exhibited extreme hyper-turnover relative to its account size and execution horizon:

- **Total Trading Sessions**: 22 sessions
- **Total Completed Trades**: 658 round-trips
- **Daily Average Trade Count**: 29.9 trades/session
- **Max Daily Trade Count**: 48 trades (Session 2026-01-14)
- **Min Daily Trade Count**: 14 trades (Session 2026-01-29)

---

## 2. Empirical Holding Duration Distribution

The holding duration (measured in 1-minute bars) of all 658 closed trades is distributed as follows:

| Metric | Holding Time (Bars / Minutes) | Interpretation |
| :--- | :--- | :--- |
| **Minimum Hold** | 3.0 bars | Immediate stop-out or sudden switching event |
| **25th Percentile (P25)** | 19.0 bars | Over a quarter of trades exited under 20 minutes |
| **Median (P50)** | 28.0 bars | 50% of positions exited within 28 minutes |
| **Mean** | 33.2 bars | Average position lifecycle is ~33 minutes |
| **75th Percentile (P75)** | 43.0 bars | 75% of positions closed before 45 minutes |
| **90th Percentile (P90)** | 61.0 bars | 90% of positions closed within 1 hour |
| **Maximum Hold** | 120.0 bars | Max holding duration time stop |

```
Holding Duration Distribution (Minutes):
[ 0-10m ]   ██ (34 trades)
[10-20m ]   ██████████ (132 trades)
[20-30m ]   ████████████████████ (214 trades)  <-- Median Peak (28m)
[30-45m ]   ████████████ (146 trades)
[45-60m ]   ██████ (74 trades)
[60-120m]   ███ (58 trades)
```

---

## 3. Turnover Velocity vs. Capital Efficiency

For a starting capital pool of **$1,000.00**, executing 658 trades with an average position size of ~$200.00 represents **$131,600.00 in total gross traded volume**—equivalent to **131.6x portfolio turnover** in 22 trading days.

### Negative Compounding Effects of Hyper-Turnover:
1. **Friction Accumulation**: 658 trades $\times$ ~$0.0653 friction/trade = **$43.00 total friction**.
2. **Noise Capture**: The strategy attempted to scalp transient 5-minute microstructure oscillations rather than holding for the stronger 15m/30m forecast alpha.
3. **Capital Lockup & Throttling**: Constant re-allocation caused frequent entry and exit into identical symbols within the same session.

---

## 4. Remediation in Engine V1.1

- **Hard Daily Velocity Limit**: Hard cap of **8 trades per session** (reducing monthly turnover from 658 to ~88 trades).
- **Mandatory Re-Entry Cooldown**: 30-bar cooldown on closed symbols to prevent churning the same ticker.
- **Projected V1.1 Turnover**: ~17.6x monthly portfolio turnover (down 86.6% from V1.0).
