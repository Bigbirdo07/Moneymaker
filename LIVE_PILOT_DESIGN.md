# Micro-Capital Live Pilot Design & Capital Ramp Plan (Phase 4)

## 1. Executive Summary

This document specifies the conceptual design for a **Hypothetical Tier-1 Micro-Capital Pilot ($1,000 USD)**, establishing formal staging tiers, capital ramp rules, and automatic scale-down triggers.

> [!WARNING]
> This design document is a **governance blueprint only**. ExecutionMode.LIVE remains strictly disabled and fatal-blocked. Real capital deployment requires explicit stakeholder authorization.

---

## 2. Micro-Capital Pilot Architecture (Tier 1)

```
                            TIER 1 PILOT SPECIFICATION
┌───────────────────────────────┬────────────────────────────────────────┐
│ Parameter                     │ Pilot Setting                          │
├───────────────────────────────┼────────────────────────────────────────┤
│ Initial Approved Capital      │ $1,000.00 USD                          │
│ Maximum Single Position       │ 10.0% ($100.00 USD)                    │
│ Maximum Concurrent Positions  │ 3 positions ($300.00 USD max notional) │
│ Eligible Universe             │ NVDA, AMD, TSLA (Strict Allow-List)    │
│ Target Holding Period         │ 15 Minutes (3 bars)                    │
│ Trade Cooldown                │ 4 Bars (20 Minutes)                    │
│ Maximum Daily Loss Cap        │ $30.00 USD (3.0%)                      │
│ Strategy Drawdown Ceiling     │ $150.00 USD (15.0%)                    │
│ Execution Routing             │ Passive Limit Order (Queue Priority)   │
│ Live Arming Mode              │ Multi-Factor Human Arming + Daily Auth │
└───────────────────────────────┴────────────────────────────────────────┘
```

---

## 3. Staged Capital Ramp Progression Framework

Capital progression must follow strict empirical milestones. Scaling is never permitted based on short-term dollar profits alone:

| Progression Stage | Capital Cap | Duration Requirement | Sample Size Requirement | Promotion Criteria |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 0: Broker Paper** | Virtual $1k | 25 trading days | $\ge 200$ trades | Net Exp $\ge 1.0\text{ bps}$, Max DD $< 5\%$, Recon $100\%$ |
| **Tier 1: Micro-Pilot** | **$1,000 USD** | **30 trading days** | **$\ge 200$ trades** | **Positive Realized Alpha, Max DD $< 3\%$, 0 Violations** |
| **Tier 2: Small Scale** | **$2,500 USD** | **60 trading days** | **$\ge 400$ trades** | **Sharpe $\ge 1.25$, Shortfall $< 2.0\text{ bps}$, 0 Violations** |
| **Tier 3: Expanded Scale** | **$5,000 USD** | **90 trading days** | **$\ge 600$ trades** | **Consistent Multi-Asset Edge, 0 Lockouts** |

---

## 4. Automatic Capital Scale-Down & Revocation Rules

Scaling operates symmetrically in both directions. If performance or risk deteriorates, the system automatically downscales capital:

1. **Drawdown Degradation**: If Tier-2 ($2,500) suffers a **5% drawdown ($125)**, capital is automatically cut back to Tier-1 ($1,000).
2. **Expectancy Collapse**: If rolling 50-trade net expectancy drops below **0.0 bps**, trading is instantly suspended pending human risk review.
3. **Reconciliation Incident**: Any single unresolved reconciliation discrepancy triggers immediate pilot revocation.
