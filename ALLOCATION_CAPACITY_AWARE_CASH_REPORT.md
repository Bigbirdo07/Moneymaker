# Capacity-Aware Allocator Cash & Scalability Report ($15k / $20k / $25k Scenarios)

## 1. Executive Summary
This report analyzes the capacity-aware cash residual behavior of `CAPPED_RISK_PARITY` across three hypothetical portfolio capital tiers: **$15,000 USD**, **$20,000 USD**, and **$25,000 USD**.

Under strict platform governance, the allocator is constrained to **empirically validated strategy capacity limits**:
- **Alpha A Maximum Authorized Capital**: **$10,000 USD** (Frozen at Hold)
- **Alpha B Maximum Authorized Capital**: **$5,000 USD** (Tier 2 Validated)
- **Any capital beyond validated strategy capacity MUST be held as CASH ($0\% \text{ risk, } 0\% \text{ alpha}$)**.

---

## 2. Portfolio Scalability & Mandatory Cash Allocation Matrix

| Hypothetical Portfolio Capital | Alpha A Allocation ($) | Alpha B Allocation ($) | Idle Cash Allocation ($) | Cash Share (%) | Projected Sharpe | Projected Ann Return (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$15,000 USD (Baseline)** | $9,630.00 | $4,845.00 | **$525.00 USD** | **3.50%** | **7.81** | **38.90%** |
| **$20,000 USD (Expansion)** | $10,000.00 (Cap) | $5,000.00 (Cap) | **$5,000.00 USD** | **25.00%** | **5.86** | **29.18%** |
| **$25,000 USD (Expansion)** | $10,000.00 (Cap) | $5,000.00 (Cap) | **$10,000.00 USD**| **40.00%** | **4.69** | **23.34%** |

---

## 3. Capacity Bound Mechanics & Cash Drag Analysis

1. **Why Cash Expands Beyond $15,000 USD**:
   - Because Alpha A cannot exceed $10,000 USD and Alpha B cannot exceed $5,000 USD, total deployable strategy capacity is strictly capped at **$15,000 USD**.
   - Any portfolio scale beyond $15,000 USD cannot be absorbed by the current two strategies without violating frozen capacity ceilings.
2. **Sharpe & Return Dilution**:
   - At $20,000 USD portfolio scale, holding $5,000 USD in cash dilutes portfolio annualized return from $38.90\%$ to $29.18\%$.
   - At $25,000 USD portfolio scale, holding $10,000 USD in cash dilutes portfolio annualized return to $23.34\%$.
3. **Prohibition of Projected Capacity Allocation**:
   - The allocator strictly refuses to allocate capital based on unvalidated higher tiers (e.g. theoretical $10k Alpha B). Cash buffers remain un-invested until empirical validation is achieved.

---

## 4. Key Recommendations
- Current validated platform capacity ceiling across Alpha A and Alpha B is **$15,000 USD**.
- Expanding total portfolio deployment beyond $15,000 USD requires either:
  1. Empirical capacity validation of Alpha B Tier 3 ($10,000 USD) in a future phase, or
  2. Introduction and validation of an orthogonal Alpha C strategy.
