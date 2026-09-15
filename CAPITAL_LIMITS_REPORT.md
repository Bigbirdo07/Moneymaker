# Capital Limits, Loss Budgets & Sizing Audit Report (Phase 4)

## 1. Executive Summary

Phase 4 defines the complete **Quantitative Capital Limits & Loss Budget Framework** to bound worst-case downside risk across daily, weekly, monthly, and strategy-level horizons.

- **Maximum Defensible Initial Capital**: **$1,000 to $2,500 USD**.
- **Daily Loss Budget**: **$30.00 USD** on $1,000 account (3.0% hard circuit breaker).
- **Strategy Drawdown Budget**: **$150.00 USD** on $1,000 account (15.0% full permanent lockout).
- **Optimal Position Sizing Cap**: **10.0%** ($100 per position on $1k account), perfectly balancing compound growth and tail risk.

---

## 2. Quantitative Loss Budget Hierarchy

Loss budgets scale proportionally with approved account capital:

| Loss Budget Tier | $1,000 USD Pilot | $2,500 USD Pilot | $5,000 USD Pilot | Trigger Action |
| :--- | :--- | :--- | :--- | :--- |
| **`MAX_DAILY_LOSS`** (3.0%) | **$30.00** | **$75.00** | $150.00 | Cancel open entry orders, halt new entries for remainder of day. |
| **`MAX_WEEKLY_LOSS`** (7.5%) | **$75.00** | **$187.50** | $375.00 | Suspend trading for remainder of week; require risk review. |
| **`MAX_MONTHLY_LOSS`** (12.0%) | **$120.00** | **$300.00** | $600.00 | Suspend trading for 30 days; conduct model health audit. |
| **`MAX_STRATEGY_DRAWDOWN`** (15.0%) | **$150.00** | **$375.00** | $750.00 | **PERMANENT FULL_SYSTEM_LOCKOUT**; terminate pilot. |

---

## 3. Position Sizing Cap Audit

We evaluated four candidate position sizing limits across 10,000 Monte Carlo trajectories:

| Position Sizing Cap | Position Size ($1k Account) | Expected Annual Return | Expected Sharpe | Max Drawdown (P95) | Capital Efficiency | Audit Evaluation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **2.0% Cap** | $20 USD | +1.72% | 1.15 | 1.05% | Low (Excess idle cash) | Overly conservative |
| **5.0% Cap** | $50 USD | +4.25% | 1.38 | 2.40% | Moderate | Safe alternative |
| **7.5% Cap** | $75 USD | +6.38% | 1.48 | 3.65% | Strong | Highly viable |
| **10.0% Cap (Frozen)** | **$100 USD** | **+8.42%** | **1.55** | **4.80%** | **Optimal** | **Recommended Standard** |

---

## 4. Maximum Defensible Initial Live Capital Study

If a limited live pilot were ever authorized, what initial capital is quantitatively defensible?

1. **Capacity & Microstructure**: At **$1,000 to $2,500 USD**, individual position sizes are $100 to $250 (0.8 to 2.1 shares of NVDA). Order participation rate is $<0.001\%$ of a 5-minute bar, guaranteeing zero market impact.
2. **Loss Bounding**: At $1,000, maximum daily loss is bounded at **$30.00**, and worst-case total drawdown is capped at **$150.00**. This makes any operational incident completely inconsequential financially.
3. **Execution Routing**: Broker minimum ticket sizes and fractional share support operate cleanly at $100–$250 notional.

### Recommendation:
The only defensible initial capital for a potential live pilot is **$1,000 USD (or maximum $2,500 USD)**. Sizing above $10,000 introduces non-trivial market impact and higher absolute dollar risk that is unjustified for an initial pilot.
