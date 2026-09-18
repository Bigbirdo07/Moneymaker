# PROMPT TO INITIALIZE FRESH CODEX SESSION

*Copy and paste the entire block below into the new Codex session:*

```markdown
======================================================================
MONEYMAKER QUANTITATIVE RESEARCH PLATFORM — INITIALIZATION
======================================================================

You are taking over an existing quantitative research and paper trading platform named Moneymaker.

You have zero prior conversational context. Do NOT guess or hallucinate past events.

Do NOT modify any code, configuration, or policies yet.

Your immediate task is to independently read the canonical handoff documentation and inspect the actual repository code, tests, and manifests to establish your own grounded understanding of the system.

======================================================================
STEP 1: READ THE CANONICAL HANDOFF PACKAGE
======================================================================

Read the following 10 core handoff documents in order:

1. docs/handoff/CODEX_BOOTSTRAP.md
2. docs/handoff/CURRENT_SYSTEM_STATE.md
3. docs/handoff/ARCHITECTURE.md
4. docs/handoff/EMPIRICAL_HISTORY.md
5. docs/handoff/GOVERNANCE_AND_PROVENANCE.md
6. docs/handoff/FORWARD_PAPER_RUNBOOK.md
7. docs/handoff/OPEN_QUESTIONS.md
8. docs/handoff/REPOSITORY_MAP.md
9. FORWARD_PAPER_POLICY_V1.yaml
10. TRUE_FORWARD_PAPER_FREEZE_MANIFEST.json

======================================================================
STEP 2: INDEPENDENT REPOSITORY INSPECTION
======================================================================

Do NOT rely solely on documentation summaries. Cross-check the docs against the actual repository:

1. Check git status and recent commit history:
   `git status`
   `git log -n 15 --oneline`

2. Inspect key subsystem modules in `src/`:
   - `src/broker/` (alpaca_paper_broker.py, strategy_capital_ledger.py, reconciliation.py)
   - `src/risk/` (risk_position_sizer.py, risk_budget.py, portfolio_risk_state.py)
   - `src/runtime/` (paper_trading_runtime.py, market_clock.py, event_store.py)
   - `src/intelligence/` (market_regime_engine.py, session_gate.py)
   - `src/signals/` (real_market_entry_model_v3.py, real_market_exit_model_v3.py, fast_scanner.py)
   - `src/events/` (event_risk_policy.py, macro_event_schedule.py)
   - `src/cost/` (expected_execution_cost.py)
   - `src/safety/` (live_guard.py, security_eligibility_policy.py)

3. Inspect runtime scripts & Slurm jobs:
   - `scripts/unity/` (submit_true_forward_session.sh, check_true_forward_session.sh, pull_true_forward_session.sh, schedule_morning_launch.py)
   - `scripts/run_phase_f2_f3_forward_validation.py`
   - `jobs/true_forward_paper_session.slurm`

4. Inspect forward artifacts and research diagnostics:
   - `artifacts/forward/` (Session 1 ledger: `TRUE_FORWARD_20260918_PCV1_df3c84`)
   - `artifacts/research/blind_week_2026_05/` (Blind May 2026 week diagnostic)

5. Verify test suite:
   `pytest -q`

======================================================================
STEP 3: INITIALIZATION RESPONSE
======================================================================

After completing your inspection, return ONLY a concise structured summary containing:

1. **Architecture Understanding**: Brief summary of the core control flow and MMRM advisory boundary.
2. **Current System State**: Current candidate, policy SHA-256 hash, capital tier, and runtime environment.
3. **Frozen Components**: List of components strictly locked during the active forward block.
4. **Evidence & Provenance Standards**: Summary of what qualifies as true forward evidence vs. historical simulation.
5. **Current Forward Block Progress**: Verified session count (e.g. 1 / 20) and latest session verdict.
6. **Top Technical & Empirical Risks**: Major vulnerabilities (e.g. concentration risk, turnover friction).
7. **Code / Documentation Inconsistencies**: Any discrepancies found between docs and code.
8. **Open Questions**: Key operational or research questions before next steps.

Then STOP.

Do NOT propose architecture rewrites, new phases, threshold tweaks, or code modifications.
======================================================================
```
