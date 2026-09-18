# MONEYMAKER GOVERNANCE & PROVENANCE SPECIFICATION

## 1. Evidence Classification Hierarchy

Every experiment, backtest, simulation, and execution session in Moneymaker must be stamped with a strict evidence classification:

| Evidence Class | Definition | Counts Toward Forward Block? |
|---|---|:---:|
| **`FORWARD_PAPER_TRADING`** | Real-time paper execution on genuinely unseen market sessions where the future was unknowable at runtime start, using a frozen policy and live broker responses. | **`TRUE`** |
| **`PAPER_TRADING`** | Generic paper broker execution, integration testing, or un-governed live observation. | `FALSE` |
| **`BLIND_HISTORICAL_WALK_FORWARD_DIAGNOSTIC`** | Out-of-sample historical simulation where test dates were strictly excluded from model training, selected deterministically without prior inspection of profitability, and stepped bar-by-bar. | `FALSE` |
| **`HISTORICAL_OPERATIONAL_REHEARSAL`** | Replaying past historical market days through the forward runtime to verify software pipelines, reconciliation, and Slurm operational readiness. | `FALSE` |
| **`POST_HOC_HISTORICAL_DIAGNOSTIC`** | Retrospective counterfactual analysis on historical logs (e.g. evaluating the rejected candidate pool). | `FALSE` |
| **`SIMULATED_EXECUTION_ON_REAL_MARKET_DATA`** | Standard backtesting using historical OHLCV data with simulated execution fills. | `FALSE` |
| **`REAL_HISTORICAL_MARKET_DATA`** | Raw or cleaned historical bar archives stored in the database. | `FALSE` |

---

## 2. Forward Session Qualification Standard

A trading session qualifies to increment the 20-session forward block (`COUNTS_TOWARD_FORWARD_BLOCK = TRUE`) **if and only if all seven criteria are satisfied**:

1. **Unknowable Future**: The market outcome was in the future when the runtime session initialized.
2. **Pre-Session Freeze**: The candidate model weights, ranking logic, and policy YAML were cryptographically frozen prior to market open.
3. **Live Market Data**: Real incoming market quotes/bars from the broker or data provider were ingested sequentially as they occurred.
4. **Zero Historical Substitution**: No historical replay, pre-loaded day files, or retrospective summaries were substituted for live market flow.
5. **Zero Interim Retuning**: No model hyperparameters, thresholds, or feature definitions were tuned using knowledge from the active session.
6. **Paper Execution Mode**: The session executed in `PAPER` mode against the authorized broker adapter.
7. **Verifiable Broker Provenance**: Authentic broker response IDs, order intents, fills (if any), and reconciliation snapshots were persisted to immutable session ledgers.

---

## 3. Strict Provenance Invariants

- **Zero Fabrication**: It is strictly forbidden to fabricate broker IDs, fill prices, Slurm job IDs, compute node hostnames, sha256 checksums, provider timestamps, execution slippage, or backtest metrics.
- **Pass $\neq$ Validated**: Unit/integration tests passing proves software correctness, not economic edge or statistical validation.
- **Backtest $\neq$ Forward Edge**: Historical backtest profitability does not constitute forward evidence.
- **Single Session Invariance**: One profitable session does not validate a strategy; one losing session or zero-trade session does not invalidate it.
- **Cash Is Valid**: Zero-trade sessions where no candidate clears the net hurdle are first-class valid decisions.

---

## 4. Policy Freeze Break Protocol

During the active 20-session forward paper testing block, the strategy policy and model weights are **strictly frozen**.

### Permissible Freeze-Break Triggers:
1. **Critical Software Bug**: Code crash, fatal exception, unhandled edge case, or deadlock.
2. **Safety / Risk Bug**: Failure of the strategy capital firewall ($1,000 limit), loss limit breach, or position limit failure.
3. **Data Integrity Defect**: Silent data feed corruption, stale quote ingestion, or missing bar processing.
4. **Broker Integration Failure**: Alpaca API breaking changes, order rejection loops, or persistent reconciliation mismatch.
5. **Severe Operational Issue**: Slurm scheduler failure or hardware failure requiring runtime logic changes.

### Prohibited Triggers (Do NOT Break Freeze For):
- A losing trade or series of losing trades.
- A profitable trade.
- A missed opportunity or "leaving money on the table".
- Consecutive zero-trade sessions.
- Dislike of model candidate selection or market regime assessment.

### Required Actions If Freeze Is Broken:
1. Document the exact root-cause justification in `artifacts/forward/FREEZE_BREAK_AUDIT.md`.
2. Compute and record old vs. new SHA-256 hashes of all modified files.
3. Increment policy version (e.g. `FORWARD_PAPER_POLICY_V1_1`).
4. Formally reset the 20-session forward counter (`0 / 20`) or document explicit governance handling.
