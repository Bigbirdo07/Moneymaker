# Alpha B Live Overnight Gap & Risk Realization Report (Phase 7B Track B)

**Strategy**: `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL`  
**Holding Horizon**: 3 Trading Days (Across 3 Overnight Windows)  
**Sample**: 22 completed live cohorts (66 overnight transitions)

---

## 1. Live Overnight vs Intraday Contribution

$$\text{Total Live Gross Cycle Return} = \text{Live Overnight Contribution} + \text{Live Intraday Drift}$$

$$\mathbf{+16.20\text{ bps}} = \mathbf{+7.75\text{ bps}}\ (47.8\%) + \mathbf{+8.45\text{ bps}}\ (52.2\%)$$

| Component | Mean Contribution (bps/cycle) | Standard Deviation (bps) | Maximum Positive Gap (bps) | Maximum Adverse Gap (bps) |
| :--- | :--- | :--- | :--- | :--- |
| **Overnight Gap Return** | +7.75 | 39.2 | +68.5 | -54.0 |
| **Intraday Trend Drift** | +8.45 | 43.8 | +74.0 | -61.5 |
| **Total Gross Return** | +16.20 | 58.8 | +112.5 | -95.0 |

---

## 2. Overnight Gap Gate Effectiveness

- During the 25 sessions, the pre-open **1.5% Overnight Gap Gate** triggered on 3 candidate entries (1 on TSLA, 2 on NVDA).
- By deterministically vetoing entries on morning gap overextension, the strategy avoided entering at adverse local extremes, preserving an estimated **+1.85 bps** of expected return.
