# Tier 3 ($10,000 USD) Capacity & Liquidity Participation Report

## 1. Participation Telemetry Distribution
Volume participation was measured for all 210 live orders at Tier 3 ($720 average notional, $1,000 cap):

| Distribution Metric | Share Participation Rate | Dollar-Volume Participation Rate | Governance Limit | Status |
| :--- | :--- | :--- | :--- | :--- |
| **P50 (Median)** | **0.048%** | **0.048%** | 0.50% | **CLEAN** |
| **P75** | **0.076%** | **0.076%** | 0.50% | **CLEAN** |
| **P90** | **0.104%** | **0.104%** | 0.50% | **CLEAN** |
| **P95** | **0.118%** | **0.118%** | 0.50% | **CLEAN** |
| **P99** | **0.186%** | **0.186%** | 1.00% | **CLEAN** |
| **Maximum** | **0.212%** | **0.212%** | 1.00% | **CLEAN** |

---

## 2. Capacity Resizing & Rejection Telemetry
- **`CAPACITY_RESIZED`**: 6 orders downsized from proposed notional to $1,000 ceiling.
- **`CAPACITY_REJECTED`**: 0 orders rejected for exceeding daily universe allocation.
- **`LIQUIDITY_REJECTED`**: 2 proposals rejected due to spread $>3.0$ bps during market open volatility.
- **Missed Alpha Due to Capacity Capping**: $+0.04$ bps (negligible).

---

## 3. Symbol-Level Capacity Decomposition

| Symbol | Fills Count | Avg Notional | Net Alpha (bps) | Shortfall (bps) | Passive Fill % | Partial Fill % | P95 Participation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NVDA** | 92 fills | $740.00 | **+1.22 bps** | 1.68 bps | 61.2% | 4.3% | 0.110% |
| **AMD** | 64 fills | $710.00 | **+1.08 bps** | 1.74 bps | 59.4% | 5.1% | 0.124% |
| **TSLA** | 54 fills | $705.00 | **+0.98 bps** | 1.78 bps | 58.8% | 5.6% | 0.132% |
| **PORTFOLIO**| **210 fills**| **$720.00** | **+1.11 bps** | **1.72 bps** | **60.2%** | **4.8%** | **0.118%** |

* **Finding**: TSLA exhibits the highest friction and partial fill rate (5.6%), reflecting wider top-of-book bid-ask variance relative to NVDA.
