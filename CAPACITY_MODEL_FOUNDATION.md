# Scalable Capacity & Market Impact Model Foundation (Phase B)

## 1. Capital Scaling & Liquidity Constraints
As Moneymaker scales capital from $\$1,000$ to $\$100,000+$, order sizes must remain invisible to market participants to prevent predatory adverse selection and excessive implementation shortfall.

---

## 2. Invariant Capacity Invariants

| Capital Tier | Representative Portfolio Equity | Typical 50% Position Size | Max % ADV Constraint ($\le 1.0\%$) | Min Dollar Volume Required |
| :--- | :---: | :---: | :---: | :---: |
| **Tier 1: Proving Ground** | **$1,000** | $500 | $0.002\%$ of $\$25\text{M}$ ADV | $\$25\text{M}$ |
| **Tier 2: Micro-Capital** | **$5,000** | $2,500 | $0.010\%$ of $\$25\text{M}$ ADV | $\$25\text{M}$ |
| **Tier 3: Core Strategy** | **$25,000** | $12,500 | $0.050\%$ of $\$25\text{M}$ ADV | $\$25\text{M}$ |
| **Tier 4: Scaled Strategy** | **$100,000** | $50,000 | $0.200\%$ of $\$25\text{M}$ ADV | $\$50\text{M}$ |
| **Tier 5: Institutional** | **$1,000,000** | $500,000 | $0.500\%$ of $\$100\text{M}$ ADV | $\$100\text{M}$ |

---

## 3. Market Impact Modeling (Square Root Law)

$$\text{Impact Cost (bps)} = 5.0 \times \sqrt{\frac{\text{Order Size (\$)}}{\text{1-Minute Dollar Volume (\$)}}}$$

At $\$1,000$ proving capital ($500 position), market impact is negligible ($<0.5\text{ bps}$). At $\$100,000$ capital ($50,000 position), impact adds $\approx 3.5\text{ bps}$ of one-way friction, which is factored into candidate selection.
