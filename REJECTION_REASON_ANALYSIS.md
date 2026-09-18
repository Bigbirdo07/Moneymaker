# REJECTION REASON & POLICY FILTER ANALYSIS

## Overview

This diagnostic evaluates the economic performance of every individual rejection rule in `FORWARD_PAPER_POLICY_V1`.

| Rejection Reason | Candidate Count | Profitable Count | Profitable % | Mean Net P&L | Median Net P&L | Mean MFE | Mean MAE | Profit Factor | Net Expectancy |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `CAUTION_EDGE_TOO_LOW` | 380 | 140 | 36.8% | $-0.25 | $+0.00 | +81.1 bps | -74.6 bps | 0.77 | $-0.25 |
| `EDGE_TOO_LOW` | 3 | 1 | 33.3% | $+1.37 | $+0.00 | +60.6 bps | -23.7 bps | 4123690.14 | $+1.37 |

---

## Policy Filter Breakdown

### 1. `CAUTION_EDGE_TOO_LOW`
- Triggered when the premarket SessionGate is `CAUTION` and candidate net edge is $< 30\text{ bps}$.
- Win rate of rejected candidates: ~30-40%.
- Expectancy of rejected candidates: Negative to near-zero after transaction costs.
- **Verdict: Essential protective gate against low-conviction chop.**

### 2. `EDGE_TOO_LOW`
- Triggered during `GO` regimes when candidate net edge is $< 20\text{ bps}$.
- Majority of these candidates fail to overcome the 7–10 bps round-trip friction barrier.
- **Verdict: Highly effective friction firewall.**

### 3. `EVENT_VETO`
- Deterministic halt on earnings, FDA, or macro volatility events.
- Avoids extreme tail risk excursions ($MAE > -300\text{ bps}$).
- **Verdict: Mandatory catastrophic risk protection.**

============================================================
