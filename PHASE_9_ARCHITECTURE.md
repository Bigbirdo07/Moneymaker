# Moneymaker Phase 9 Architecture: Shadow A/B Dual-Model Infrastructure

## 1. Executive Summary & Core Objective

Moneymaker Phase 9 deploys **`MMRM-0.2-REAL + RAG`** (verified QLoRA adapter on Qwen-2.5-14B-Instruct) inside the Moneymaker Workstation in **Shadow A/B Mode** alongside the production control model **`BASE-QWEN-2.5-14B`**.

The objective is **not synthetic benchmark evaluation** (which was completed in Phase 8D.1 with a strict accuracy of 86.25% and semantic accuracy of 95.62%), but **empirical validation on real user interactions** across live workstation usage.

```
+---------------------------------------------------------------------------------------------------+
|                                     MONEYMAKER WORKSTATION UI                                     |
|                                                                                                   |
|   User Query: "What happened today? Explain today's P&L and why NVDA was vetoed."                  |
|                                                                                                   |
|   +-------------------------------------------------------------------------------------------+   |
|   | Snapshot Telemetry Pinning: snapshot_id="SNAP_20260916_205600", timestamp="2026-09-16T..."|   |
|   +-------------------------------------------------------------------------------------------+   |
|                 |                                                             |                   |
|                 v                                                             v                   |
|   +---------------------------+                                 +---------------------------+     |
|   |          CONTROL          |                                 |          SHADOW           |     |
|   |    BASE-QWEN-2.5-14B      |                                 |    MMRM-0.2-REAL + RAG    |     |
|   |      [PRODUCTION]         |                                 |       [CHALLENGER]        |     |
|   +---------------------------+                                 +---------------------------+     |
|                 |                                                             |                   |
|                 +-----------------------------+-------------------------------+                   |
|                                               |                                                   |
|                                               v                                                   |
|                       +-----------------------------------------------+                           |
|                       |        23 Read-Only Telemetry Tools           |                           |
|                       |  (get_today_pnl, get_portfolio_risk, etc.)    |                           |
|                       +-----------------------------------------------+                           |
|                                               |                                                   |
|                                               v                                                   |
|                       +-----------------------------------------------+                           |
|                       |          STRICT EXECUTION FIREWALL            |                           |
|                       |   Zero Broker Order / Capital Modification    |                           |
|                       +-----------------------------------------------+                           |
|                                               |                                                   |
|                                               v                                                   |
|                       +-----------------------------------------------+                           |
|                       |             outputs/copilot_ab/               |                           |
|                       |   interaction_log.jsonl & incidents.jsonl     |                           |
|                       +-----------------------------------------------+                           |
+---------------------------------------------------------------------------------------------------+
```

---

## 2. Strict Safety & Execution Firewall

Both models operate under unconditional **READ-ONLY** constraints:
1. **Zero Broker Execution**: Neither model has access to order placement, order modification, or account transfer functions.
2. **Zero Capital or Risk Alteration**: Neither model can alter strategy budgets ($10,000 Alpha A, $5,000 Alpha B), portfolio risk parameters, position limits, or kill switch states.
3. **Execution Path Invariance**: The deterministic trading and execution engine remains 100% decoupled from LLM inference:
   $$\text{Alpha Numeric Models} \longrightarrow \text{Deterministic PortfolioRiskAggregator} \longrightarrow \text{Execution Engine} \longrightarrow \text{Broker}$$

---

## 3. Dual-Model Routing & Snapshot Pinning Engine

When a user submits a query to the Workstation Copilot:
1. **Snapshot Creation**: The engine generates a pinned telemetry state with a unique `snapshot_id` and ISO timestamp.
2. **Synchronous/Parallel Dispatch**: The exact same query, system prompt, tool definitions, retrieval policy, and pinned state are dispatched to both:
   - **Control**: `BASE-QWEN-2.5-14B` (default production response).
   - **Challenger**: `MMRM-0.2-REAL + RAG` (background shadow response).
3. **Tool Access Equivalence**: Both models interact with identical read-only tool signatures:
   - `get_account_summary`, `get_today_pnl`, `get_portfolio`, `get_open_positions`, `get_position`, `get_trade_history`, `get_trade`, `get_live_quote`, `get_market_snapshot`, `get_watchlist`, `get_alpha_a_signals`, `get_alpha_b_signals`, `get_strategy_status`, `get_strategy_health`, `get_strategy_capacity`, `get_portfolio_risk`, `get_recent_risk_vetoes`, `get_market_regime`, `get_system_health`, `get_validation_state`, `explain_trade`, `compare_strategies`, `get_daily_summary`.
4. **Evidence Preservation**: Tool outputs explicitly preserve evidence classes: `BROKER_LIVE`, `BROKER_PAPER`, `FORWARD_SHADOW`, `HISTORICAL`, `SIMULATED`, `PROJECTED`.

---

## 4. Workstation User Experience & Blind A/B Evaluation

1. **Default View**: Active production responses are presented immediately from `BASE-QWEN-2.5-14B`.
2. **Challenger Reveal ("Compare with MMRM")**: Users can expand a side-by-side comparison drawer.
3. **Blind A/B Mode**: When enabled, models are labeled neutrally as **Response A** and **Response B** to eliminate brand/model bias.
4. **Human Evaluation Interface**:
   - Preferences: **Better (A / B / Base / Challenger)**, **Equal / Tie**, **Worse**.
   - Reason Tags: `More accurate`, `Better explanation`, `Better tool use`, `More concise`, `More complete`, `Better grounded`, `Wrong data`, `Hallucination`, `Too verbose`, `Too slow`.
   - Free-form feedback notes.
5. **Research Proposal Integration**: Operators can ask Copilot to generate structured Unity experiment specifications (hypothesis, dataset, parameters, compute class) with an explicit Approve/Reject human review gate prior to Slurm dispatch.

---

## 5. Storage & Privacy Safeguards

Interaction records are stored in `outputs/copilot_ab/interaction_log.jsonl`.
- **Zero Secrets**: API keys, broker tokens, passwords, and private authentication headers are stripped prior to serialization.
- **Incident Quarantine**: Detected anomalies (wrong tools, hallucinated trades, unsupported numeric assertions) are quarantined in `outputs/copilot_ab/incidents.jsonl`.
- **Feedback Candidates**: Problematic examples are appended to `outputs/copilot_ab/feedback_candidates.jsonl` for offline curation and future MMRM-0.3 fine-tuning.
