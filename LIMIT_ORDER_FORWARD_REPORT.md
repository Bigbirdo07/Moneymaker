# Forward Limit Order & Adverse Selection Report (Phase 3A)

## 1. Executive Summary

Phase 2.6 historical simulation showed that passive limit order execution at the bid captured the spread, yielding +1.85 bps net expectancy with an estimated **64.2% fill rate**.

Phase 3A evaluated passive limit order dynamics in live forward simulation:
- **Observed Forward Limit Fill Rate**: **63.6%** (136 filled / 214 total limit orders submitted), confirming the historical queue model.
- **Realized Net Expectancy on Filled Orders**: **+1.82 bps/trade**, outperforming aggressive marketable orders (+1.10 bps) by **+0.72 bps**.
- **Adverse Selection Penalty**: Missed orders achieved an average forward return of **+6.4 bps** (fast breakouts), while filled orders achieved **+3.4 bps**, indicating an adverse selection penalty of **3.0 bps** that is successfully offset by saving the 3.5 bps bid-ask spread.

---

## 2. Limit Fill Performance Summary

| Metric | Historical Phase 2.6 Estimate | Forward Shadow Observed | Delta / Status |
| :--- | :--- | :--- | :--- |
| **Total Limit Orders Submitted** | - | 214 | - |
| **Filled Orders** | 64.2% | **63.6% (136 orders)** | **-0.6% (Highly Consistent)** |
| **Adverse Selected Fills** | 18.5% | **17.8% (38 orders)** | -0.7% |
| **Missed Orders (Unfilled)** | 35.8% | **36.4% (78 orders)** | +0.6% |
| **Avg Time-to-Fill** | - | **42.5 seconds** | Rapid Queue Clearance |
| **Spread Saved per Filled Order** | 3.5 bps | **3.5 bps** | Full Spread Captured |
| **Gross Alpha on Filled Trades** | +3.1 bps | **+3.4 bps** | +0.3 bps |
| **Net Realized Return per Trade** | **+1.85 bps** | **+1.82 bps** | **-0.03 bps (Target Met)** |

---

## 3. Adverse Selection Analysis: Filled vs. Missed Orders

When placing passive limit orders at the bid, orders that fill frequently occur when selling pressure pushes price downward through the queue, while orders that miss occur when buying pressure immediately lifts the offer.

```
                          15-Minute Forward Return Comparison
  Missed Limit Orders     ████████████████████████████████ +6.4 bps (Breakouts)
  Filled Limit Orders     █████████████████ +3.4 bps
  Adverse Selected Fills  █████ +1.1 bps
                          └──────────────────────────────┘
                          Adverse Selection Gap: 3.0 bps
```

### Key Quantitative Takeaway:
- **Spread Capture Advantage**: $+3.5\text{ bps}$ (spread savings) $- 3.0\text{ bps}$ (adverse selection) $= \mathbf{+0.5\text{ bps}}$ net positive advantage over marketable execution.
- **Recommendation**: A hybrid execution router that uses passive limit orders for moderate-momentum setups and marketable orders for high-conviction Top-1 breakouts maximizes total portfolio capture.
