# Moneymaker Research Director: Challenger Proposals & Research Queue Report

## 1. Overview & Research Queue Governance
To prevent research stagnation without destabilizing the frozen live champion, the Research Director formulates structured `ChallengerProposal` objects and appends them to the `RESEARCH_QUEUE`.

**Governance Rule**: No proposal in the `RESEARCH_QUEUE` may be merged, trained, or deployed into live execution without separate formal backtesting, Purged Walk-Forward verification, Deflated Sharpe testing, and human authorization.

---

## 2. Active Queued Challenger Proposals

### Proposal CHALL-001: Time-of-Day Morning Spread Restriction Filter
- **Hypothesis**: Restricting new order entries to the core liquid regular session window (10:00 - 15:30 ET) will reduce implementation shortfall by avoiding opening 30-minute spread expansion.
- **Motivation**: Live telemetry indicated that 62% of spread gate rejections ($>3.0\text{ bps}$) occurred during the first 30 minutes of trading (09:30 - 10:00 ET).
- **Experimental Design**: 5-fold Purged Cross-Validation across 2026 5m bar data comparing Champion with/without 10:00-15:30 ET filter.
- **Primary Metric**: Net Expectancy (bps/trade) after 3.5 bps transaction friction.
- **Null Hypothesis**: Net expectancy is unchanged or reduced ($p \ge 0.05$).
- **Risk of Overfitting**: Low (broad 30-minute market opening block filter).
- **Promotion Threshold**: Net alpha gain of $\ge +0.30\text{ bps}$ with Deflated Sharpe Ratio $p < 0.05$.

### Proposal CHALL-002: Dynamic Spread-Adjusted Limit Order Offset
- **Hypothesis**: Placing passive limit orders 0.25 bps inside the bid when spread $< 2.0\text{ bps}$ will increase passive fill rates from 65.3% to $> 72.0\%$ without increasing adverse selection.
- **Motivation**: Short-horizon momentum alpha peaks at 15 minutes; improving queue priority will increase fill efficiency.
- **Experimental Design**: High-fidelity tick queue simulation on Level 2 order book replay data.
- **Primary Metric**: Passive Limit Fill Rate & 15m Realized Net Return.
- **Promotion Threshold**: Passive fill rate increase of $\ge +5.0\%$ with no decrease in 15m post-fill alpha.
