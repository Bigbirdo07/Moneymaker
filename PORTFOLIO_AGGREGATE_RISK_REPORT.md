# Portfolio Aggregate Risk & Hierarchical Governance Report (Phase 7B)

**Engine**: `PortfolioRiskAggregator` (4-Tier Deterministic Risk Hierarchy)  
**Total Account Scope**: **$11,000.00 USD** ($10,000 Alpha A + $1,000 Alpha B)

---

## 1. 4-Tier Hierarchical Deterministic Risk Engine

```mermaid
graph TD
    Order["Incoming Strategy Order Request"] --> T1["<b>TIER 1: ACCOUNT RISK</b><br/>Account Capital ($11k) & Daily Loss ($230)"]
    T1 -- "Pass" --> T2["<b>TIER 2: STRATEGY RISK</b><br/>Strategy Partition ($10k / $1k) & Strategy Daily Loss"]
    T2 -- "Pass" --> T3["<b>TIER 3: SYMBOL RISK</b><br/>Combined Cross-Strategy Symbol Cap ($3.5k)"]
    T3 -- "Pass" --> T4["<b>TIER 4: ORDER RISK</b><br/>Single Order Cap ($1k / $333.33) & Long-Only Check"]
    T4 -- "Pass" --> App["<b>APPROVED FOR BROKER ROUTING</b>"]
    T1 -- "Fail" --> Rej["<b>REJECTED WITH TIER REASON CODE</b>"]
    T2 -- "Fail" --> Rej
    T3 -- "Fail" --> Rej
    T4 -- "Fail" --> Rej
```

---

## 2. Risk Budget & Concentration Summary

| Risk Dimension | Authorized Limit | Maximum Observed Live Value | Utilization (%) | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Total Account Capital** | $11,000.00 USD | $11,000.00 USD | 100.0% | `HEALTHY` |
| **Alpha A Capital Partition** | $10,000.00 USD | $10,000.00 USD | 100.0% | `COMPLIANT` |
| **Alpha B Capital Partition** | $1,000.00 USD | $1,000.00 USD | 100.0% | `COMPLIANT` |
| **Account Daily Loss Limit** | $230.00 USD | $48.50 USD | 21.1% | `HEALTHY` |
| **Single Symbol Combined Cap** | $3,500.00 USD | $1,333.33 USD | 38.1% | `HEALTHY` |
| **High-Beta Cluster Weight** | $\le 75.0\%$ | 62.5% | 83.3% | `WATCH` |
| **Overnight Exposure Cap** | $1,000.00 USD (Alpha B only)| $1,000.00 USD | 100.0% | `HEALTHY` |

---

## 3. Governance Boundaries

The Portfolio Risk Aggregator acts strictly as a **deterministic risk veto barrier**. It possesses zero authorization to dynamically rebalance capital weights, optimize strategy sizes, or route live orders.
