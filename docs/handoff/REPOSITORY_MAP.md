# MONEYMAKER REPOSITORY MAP

This map outlines the repository structure, identifying key entry points, component responsibilities, and frozen status for fresh development agents.

---

## 1. Core Source Tree (`src/`)

| Path | Purpose & Key Modules | Safety / Freeze Status |
|---|---|:---:|
| **`src/broker/`** | Broker adapters, order intents, capital ledgers, and reconciliation. Key: `alpaca_paper_broker.py`, `strategy_capital_ledger.py`, `reconciliation.py`, `execution_environment.py`. | **CRITICAL / FROZEN** |
| **`src/risk/`** | Dynamic position sizing, risk budgeting, capital tiers, and loss tracking. Key: `risk_position_sizer.py`, `risk_budget.py`, `portfolio_risk_state.py`. | **CRITICAL / FROZEN** |
| **`src/runtime/`** | Autonomous runtime state machine, market clock, and event store. Key: `paper_trading_runtime.py`, `runtime_state.py`, `market_clock.py`, `event_store.py`. | **CRITICAL / FROZEN** |
| **`src/safety/`** | Live guards, real-money blockers, emergency halt, and universe eligibility. Key: `live_guard.py`, `security_eligibility_policy.py`. | **CRITICAL / FROZEN** |
| **`src/signals/`** | Entry/exit models, FastScanner, and opportunity ranking. Key: `real_market_entry_model_v3.py`, `real_market_exit_model_v3.py`, `fast_scanner.py`. | **FROZEN** |
| **`src/models/`** | Regressors, ranking models, and inference wrappers. Key: `regressors.py`, `ranking.py`. | **FROZEN** |
| **`src/features/`** | Technical, microstructural, and order flow feature calculators. Key: `real_market_features.py`, `technical.py`. | **FROZEN** |
| **`src/intelligence/`** | Market regime engine, SessionGate, MorningBrief, and system readiness. Key: `market_regime_engine.py`, `session_gate.py`, `morning_brief.py`. | **FROZEN** |
| **`src/events/`** | Macro calendar and company earnings event risk policies. Key: `event_risk_policy.py`, `macro_event_schedule.py`. | **FROZEN** |
| **`src/cost/`** | Expected execution cost model (spread + slippage + fees). Key: `expected_execution_cost.py`. | **FROZEN** |
| **`src/capacity/`** | Participation rate limits and capacity sizing. Key: `capacity_model.py`. | **FROZEN** |
| **`src/data/`** | Ingestion, data quality filters, calendar, and universe managers. Key: `universe_manager.py`, `ingestion.py`, `calendar.py`, `market_data_quality_policy.py`. | **FROZEN** |
| **`src/post_close/`** | End-of-day journal generator, performance reporting, and Parquet archiving. Key: `post_close_journal.py`. | **FROZEN** |
| **`src/llm/`** | MMRM client, prompt templates, RAG retrieval engine. Key: `mmrm_client.py`, `rag_retrieval.py`. | Non-Executable |
| **`src/workstation/`** | FastAPI backend, Copilot engine, and live provenance service. Key: `api.py`, `service.py`, `copilot_engine.py`, `provenance.py`. | Operational |

---

## 2. Scripts & Operational Utilities (`scripts/`)

| Path | Purpose |
|---|---|
| **`scripts/unity/`** | Unity HPC cluster scripts: `submit_true_forward_session.sh`, `check_true_forward_session.sh`, `pull_true_forward_session.sh`, `schedule_morning_launch.py`, `cancel_job.sh`. |
| **`scripts/run_phase_f2_f3_forward_validation.py`** | Main entrypoint for autonomous true forward session execution. |
| **`scripts/run_blind_historical_week.py`** | Point-in-time blind historical week simulation engine. |
| **`scripts/run_dress_rehearsal.py`** | Historical operational dress rehearsal runner. |

---

## 3. Slurm Batch Jobs (`jobs/`)

| Path | Purpose |
|---|---|
| **`jobs/true_forward_paper_session.slurm`** | Production Slurm batch job specification for Unity HPC forward paper sessions (6.5 hours, 4 CPUs, 16GB RAM). |
| **`jobs/phase11*.slurm`** | Historical research and replay job definitions. |

---

## 4. Tests (`tests/`)

- Contains **455 automated unit and integration tests** covering all data feeds, models, sizing logic, paper adapters, reconciliation loops, and safety guards.
- Run test suite: `pytest -q`.

---

## 5. Artifacts Storage (`artifacts/`)

| Directory | Contents |
|---|---|
| **`artifacts/forward/`** | True forward paper trading session bundles (e.g. `TRUE_FORWARD_20260918_PCV1_df3c84/`). |
| **`artifacts/research/`** | Offline research packages, including blind week simulations (`artifacts/research/blind_week_2026_05/`). |

---

## 6. Root Governance Files

- **`FORWARD_PAPER_POLICY_V1.yaml`**: Canonical frozen policy configuration (SHA-256: `9c2bc9f33a931f822fbd0574bbe28d7deefc87fb1da741604d3eec8207e0cb3b`).
- **`TRUE_FORWARD_PAPER_FREEZE_MANIFEST.json`**: Manifest locking all policy parameters and code hashes for the 20-session forward block.
