# Allocation Capacity Constraints & Cash Buffer Report

## 1. Executive Summary

A fundamental vulnerability of classic mean-variance or risk-parity allocators is the unconstrained assignment of capital into low-capacity strategies.

The Moneymaker **Capacity-Aware Allocation Framework** enforces hard ceiling bounds tied strictly to empirical validation tiers, routing any excess unallocated capital to a **CASH** buffer.

---

## 2. Capacity Bounding Formulation & Cash Residual Dynamics

Let $W^*_A$ and $W^*_B$ be the unconstrained target strategy weights for total portfolio capital $C$.
The capacity-aware allocations are:

$$C_A = \min(W^*_A \cdot C, \ \text{Cap}_A^{\text{validated}})$$
$$C_B = \min(W^*_B \cdot C, \ \text{Cap}_B^{\text{validated}})$$
$$C_{\text{Cash}} = C - (C_A + C_B)$$

$$\text{Effective Weights: } w_A = \frac{C_A}{C}, \quad w_B = \frac{C_B}{C}, \quad w_{\text{Cash}} = \frac{C_{\text{Cash}}}{C}$$

Where $\sum w_i = 1.0$ (Zero leverage, Cash $\ge 0$).

---

## 3. Account Capital Scaling Simulation ($10k to $50k)

| Portfolio Capital ($) | Validated Cap A ($) | Validated Cap B ($) | Deployed Capital ($) | Cash Residual ($ / %) | Effective Alpha A (%) | Effective Alpha B (%) | Max Drawdown Dampening (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **$11,000 USD** | $10,000 | $1,000 (Tier 0) | $11,000 | $0.00 (0.0%) | 90.91% | 9.09% | Baseline |
| **$12,500 USD** | $10,000 | $2,500 (Tier 1) | $12,500 | $0.00 (0.0%) | 80.00% | 20.00% | Baseline |
| **$15,000 USD** | $10,000 | $2,500 (Tier 1) | $12,500 | **$2,500 (16.7%)** | 66.67% | 16.67% | -16.7% MaxDD |
| **$20,000 USD** | $10,000 | $2,500 (Tier 1) | $12,500 | **$7,500 (37.5%)** | 50.00% | 12.50% | -37.5% MaxDD |
| **$25,000 USD** | $10,000 | $2,500 (Tier 1) | $12,500 | **$12,500 (50.0%)** | 40.00% | 10.00% | -50.0% MaxDD |
| **$50,000 USD** | $10,000 | $2,500 (Tier 1) | $12,500 | **$37,500 (75.0%)** | 20.00% | 5.00% | -75.0% MaxDD |

---

## 4. Key Takeaway

Unallocated cash acts as an automatic, volatility-dampening shock absorber. Rather than forcing larger order sizes that degrade fill quality and push strategies past their capacity limits, the account safely preserves liquidity until higher strategy capacity tiers are empirically validated.
