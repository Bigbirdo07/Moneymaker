# Multi-Tier Capital Scale Replay Analysis

## 1. Performance Across Account Capital Tiers

| Capital Tier | Starting Equity | Max Positions | Max Position (%) | Avg Size ($) | Capital Util (%) | Constrained (%) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| TIER_PAPER_1000 | $1,000 | 1 | 75% | $281.60 | 28.2% | 65.5% | HIGHLY_SCALABLE |
| TIER_5000 | $5,000 | 2 | 50% | $1,660.85 | 33.2% | 33.3% | HIGHLY_SCALABLE |
| TIER_25000 | $25,000 | 3 | 35% | $7,138.67 | 28.6% | 40.0% | HIGHLY_SCALABLE |
| TIER_100000 | $100,000 | 5 | 25% | $12,781.82 | 12.8% | 83.3% | CAPACITY_MANAGED |

## 2. Key Findings
- **$1,000 Proving Tier**: Single-position limit ($750 max allocation) provides optimal proof-of-concept capital density.
- **$25,000+ PDT Tier**: Seamlessly transitions to 3 simultaneous positions without violating 1% ADV participation limits.