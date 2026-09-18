# Moneymaker — Canonical Product, Research, System, and Autonomy Spec

## 1. Project Overview & Product Vision
- **Project Name**: Moneymaker Quantitative Research Platform
- **Product Vision**: Autonomous, Risk-First, Intraday Quantitative Portfolio Manager
- **Initial Proving Capital**: $1,000 (Proving ground, not permanent strategy capacity)
- **Long-Term Scaling Path**:
  $$\$1,000 \longrightarrow \$5,000 \longrightarrow \$25,000 \longrightarrow \$100,000+$$
- **Capital Scaling Law**: Scaling must **never** be accomplished by simply multiplying order quantities. As capital scales, the system must account for liquidity, bid-ask spread, slippage, market impact, participation rate (% ADV / minute volume), volatility, concentration, sector exposure, fill probability, and implementation shortfall.

---

## 2. The Product We Are Actually Building

Moneymaker is **NOT**:
- A stock predictor or stock-picking chatbot
- A generic LLM financial assistant
- A high-frequency trading bot
- An unconstrained backtesting toy
- An LLM with direct brokerage order authority

Moneymaker **IS**:
**An Autonomous, Risk-First, Intraday Quantitative Portfolio Manager** that executes the following 20-step lifecycle:
1. Wakes up before U.S. market open (8:45 AM ET).
2. Quantifies the broad market environment (SPY trend, breadth, volatility regime).
3. Scans hundreds of liquid U.S. equities dynamically.
4. Filters the market down to liquid, tradable candidates.
5. Identifies and removes securities subject to deterministic event/risk vetoes (earnings, halts, binary trials).
6. Ranks remaining candidates using cross-sectional relative momentum & valuation metrics.
7. Forecasts expected **EXECUTABLE NET edge** after realistic spread, slippage, and commissions.
8. Decides whether any candidate exceeds the validated net-edge hurdle.
9. Frequently and successfully chooses **100% CASH** when no setup clears the hurdle.
10. Sizes positions via risk budgeting ($ risk / stop distance), liquidity, and capacity limits.
11. Autonomously executes paper orders without requiring interactive human confirmation.
12. Continuously monitors open positions in real time.
13. Evaluates HOLD / REDUCE / EXIT based on expected continuation value and trailing gain protection.
14. Re-ranks opportunities dynamically as intraday cross-sectional market state shifts.
15. Enforces deterministic account-level stop-loss firewalls and daily loss limits.
16. Closes 100% of open positions before 4:00 PM ET (target flattening: 3:45–3:55 PM ET).
17. Finishes every trading day with **zero intentional overnight equity exposure**.
18. Generates a comprehensive post-close research, trade, and audit journal.
19. Learns strictly **OFFLINE** through governed, versioned, and audited research.
20. **Never silently retrains or alters parameters intraday**.

---

## 3. Core Operating Philosophy & Priority Hierarchy

$$\text{Capital Preservation} \longrightarrow \text{Positive Net Expectancy} \longrightarrow \text{Controlled Drawdown} \longrightarrow \text{Cost-Awareness} \longrightarrow \text{Selectivity} \longrightarrow \text{Return Maximization}$$

The persona resembles a **Disciplined Quantitative Portfolio Manager + Research Analyst + Chief Risk Officer + Automated Execution Engine**.

---

## 4. LLM Role & Strict Separation from Money Path

```
                    ┌──────────────────────────────────────────┐
                    │               LLM / MMRM                 │
                    │  (Research / Explanation / Struct Context│
                    └─────────────────────┬────────────────────┘
                                          │ Advisory Flags / Metadata
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │    DETERMINISTIC QUANTITATIVE SYSTEM     │
                    │ (Data, Features, Cross-Sectional Ranking)│
                    └─────────────────────┬────────────────────┘
                                          │ Candidate Ranking & Edge
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │         DETERMINISTIC RISK ENGINE        │
                    │ (Capacity, Loss Limits, Event Vetoes)    │
                    └─────────────────────┬────────────────────┘
                                          │ Authorized Orders Only
                                          ▼
                    ┌──────────────────────────────────────────┐
                    │      DETERMINISTIC EXECUTION ENGINE      │
                    │   (Fills, Sizing, Routing, Slippage)     │
                    └─────────────────────┬────────────────────┘
                                          │ Verified Executable Orders
                                          ▼
                                     [ BROKER ]
```

### Invariant Rules:
1. The LLM sits **BESIDE** the money path, **NEVER INSIDE** the direct execution authorization path.
2. The LLM has **ZERO** direct brokerage authority to submit orders, modify stops, alter share quantities, change strategy parameters, or bypass risk limits.
3. MMRM produces structured context (e.g. `EventRiskPolicy` triggers, morning briefs, trade explanations, post-close journals). All executable actions must pass through deterministic mathematical rules.

---

## 5. Multi-Stage Decision Pipeline

```
STAGE 0: Data Quality & Monotonic Clock Assertion
   ↓
STAGE 1: Market Regime & Macro Gate (SPY Trend, Breadth >= 40%, Volatility)
   ↓
STAGE 2: Universe Eligibility (Price > $10, Daily Volume, Spreads)
   ↓
STAGE 3: Deterministic Event Vetoes (Earnings today, Halts, Binary corporate actions)
   ↓
STAGE 4: Fast Market Scanner (Premarket Gap, Volume acceleration)
   ↓
STAGE 5: Contemporaneous Cross-Sectional Ranking
   ↓
STAGE 6: Multi-Horizon Predicted Net Edge Evaluation (Hurdle >= 25 bps)
   ↓
STAGE 7: Risk-Budgeted Sizing & Capacity Allocation ($ Risk / Stop Distance)
   ↓
STAGE 8: Autonomous Entry or 100% Cash Decision
   ↓
STAGE 9: Intraday Position Monitoring & Trailing Gain Protection
   ↓
STAGE 10: Exit Execution & Daily Flattening (3:45–3:55 PM ET)
```

---

## 6. Key Quantitative & Operational Policies

| Dimension | Initial Proving Ground ($1,000) | Long-Term Scaled ($25,000–$100,000+) |
| :--- | :--- | :--- |
| **Max Concurrent Positions** | **1 position** (Clean attribution & sizing) | Dynamic $2–5$ based on correlation & risk budget |
| **Trading Frequency** | **0–2 trades/day** (Average ~0.3–0.8 trades/day) | $1–4$ trades/day strictly bounded by net edge hurdles |
| **Holding Domain** | **30–120 minutes** (Micro 5–15m avoided) | Multi-horizon dynamic (30m, 60m, 120m) |
| **Max Defined Risk / Trade** | **0.75% – 1.00%** ($7.50 – $10.00 on $1,000) | 0.50% – 0.75% of total portfolio equity |
| **Daily Loss Limit** | **1.50%** (-$15.00 on $1,000 $\rightarrow$ Cash mode) | 1.00% – 1.50% account-level circuit breaker |
| **Overnight Exposure** | **0.00% (100% Cash by 3:55 PM ET)** | Strictly 0.00% overnight equity exposure |
| **Instrument Types** | Liquid U.S. Common Equities + SPY | Liquid U.S. Common Equities + Sector ETFs |
| **Forbidden Assets** | Penny stocks, <$10 stocks, meme stocks, 3x ETFs | Microcaps, illiquid OTC, binary trial biotechs |
| **Friction Modeling** | Spread (5 bps) + Slippage (2.5 bps) + Commission | Impact model + ADV % cap + Slippage curve |
| **Promotion Gate** | Multi-month forward paper positive expectancy | Micro-capital pilot $\rightarrow$ Scaled production |
