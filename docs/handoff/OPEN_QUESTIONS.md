# MONEYMAKER OPEN RESEARCH & TECHNICAL QUESTIONS

This document tracks prioritized open questions, technical risks, and empirical uncertainties for the platform.

---

## 1. Prioritized Research & Empirical Questions

### Q1: Does `PAPER_CANDIDATE_V1` produce positive net expectancy out-of-sample?
- **Context**: The candidate demonstrated promising rolling OOS performance in 2025 (+8.97%, PF 1.31) and fresh 2023 replication (+5.95%), but blind May 2026 week was slightly negative (-0.20%, PF 0.76).
- **Target**: Evaluate net P&L, win rate, and profit factor over the 20-session forward paper testing block.

### Q2: What will the actual forward trade accumulation rate be?
- **Context**: Under CAUTION market regime gates, the 30.0 bps net edge hurdle filters aggressively. Session 1 yielded 0 trades (CASH), while blind May 2026 week yielded 4 trades across 5 days.
- **Target**: Observe how many trades accumulate across the 20 forward sessions.

### Q3: Is single-symbol concentration structurally persistent?
- **Context**:
  - August 2026 holdout: ORCL generated 68.8% of profit.
  - 2023 holdout: TSLA generated 93.3% of profit.
  - Blind May 2026 week: INTC accounted for 75% of executed trades.
- **Target**: Track top-1 and top-3 symbol P&L contribution in forward trading to determine if alpha is idiosyncratic to a few mega-caps or broadly distributed.

### Q4: What is the empirical implementation shortfall on Alpaca Paper fills?
- **Context**: Backtests and simulations model half-spread + slippage buffer. True live execution will reveal actual latency-driven slippage ($IS = P_{fill} - P_{decision}$).
- **Target**: Measure implementation shortfall on every completed paper fill.

### Q5: Dynamic Universe Ingestion Discrepancy (299 vs. 103 symbols)
- **Context**: The historical dress rehearsal ingested 299 listed equities from historical files, whereas Session 1 live run reported 103 listed securities passing the initial dynamic screener.
- **Analysis**: This is caused by live API query constraints (Alpaca asset listing vs. cached historical symbol universe).
- **Action**: Verify whether expanding the initial dynamic query pool increases opportunity capture without degrading scanner latency.

### Q6: Gate Strictness Evolution (30 bps vs. 25 bps vs. 20 bps)
- **Context**: Blind week analysis showed that lowering to 25 bps added a losing trade (-$0.84), while lowering to 20 bps added a small winning trade (+$1.04). The 30 bps gate successfully saved capital on Day 4.
- **Action**: Maintain the 30.0 bps hurdle strictly during the 20-session forward block. Do not retune without a statistically sufficient trade sample.

### Q7: Point-in-Time News Ingestion & Real-Time Event Risk
- **Context**: In historical simulation, archived point-in-time news was marked `POINT_IN_TIME_NEWS_UNAVAILABLE` to avoid post-hoc bias.
- **Action**: Ensure that live forward sessions accurately capture contemporaneous earnings/macro calendar feeds via `EventRiskPolicy`.

### Q8: MMRM Non-Execution Boundary Integrity
- **Context**: Language models generate senior quant commentary and MorningBrief summaries.
- **Action**: Ensure MMRM remains strictly decoupled from order execution and risk sizing.

### Q9: Unity HPC Slurm Scheduling & Resource Optimization
- **Context**: Running 6.5-hour trading sessions on an HPC cluster requires careful scheduling to avoid holding idle compute nodes overnight.
- **Action**: Use `schedule_morning_launch.py` with `wait_and_submit` to trigger batch jobs precisely at 08:25 ET.

### Q10: Statistical Sufficiency Beyond the 20-Session Freeze Block
- **Context**: 20 calendar sessions is an operational freeze block designed to prove runtime stability, zero lookahead, and reconciliation. Depending on market volatility, 20 sessions may yield anywhere from 5 to 25 trades.
- **Guideline**: A statistical sample of ~30–50+ completed trades will be required before declaring formal economic validation or considering capital scaling.

### Q11: Future Long-Term Production Runtime
- **Context**: Unity HPC is used for forward paper validation by user preference.
- **Target**: Evaluate whether long-term production execution should remain on Slurm or migrate to a dedicated low-latency server.
