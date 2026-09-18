# MONEYMAKER ARCHITECTURE GUIDE

## 1. High-Level Architecture Diagram

```
[ Real Market Data / Alpaca Paper Streams ]
                     │
                     ▼
       1. Market Ingestion & Data Quality
       (src/data/ingestion.py, market_data_quality_policy.py)
                     │
                     ▼
       2. Dynamic Universe & Liquidity Filtering
       (src/data/universe_manager.py, security_eligibility_policy.py)
                     │
                     ▼
       3. FastScanner & Cross-Sectional Ranking
       (src/signals/fast_scanner.py, src/models/ranking.py)
                     │
       ┌─────────────┴────────────────────────┐
       ▼                                      ▼
4. Feature Pipeline & Regressors       5. Macro/Event Risk & Regime
(src/features/, src/models/regressors)  (src/events/, src/intelligence/)
       │                                      │
       └─────────────┬────────────────────────┘
                     ▼
       6. SessionGate (GO / CAUTION / NO_GO)
       (src/intelligence/session_gate.py)
                     │
       ┌─────────────┴────────────────────────┐
       ▼                                      ▼
7. Execution Cost Model                8. MMRM Advisory Layer (LLM)
(src/cost/expected_execution_cost.py)   (src/llm/mmrm_client.py)
       │                               (Non-executable explanations)
       └─────────────┬────────────────────────┘
                     ▼
       9. Sizing & Capacity (RiskPositionSizer & CapacityModel)
       (src/risk/risk_position_sizer.py, src/capacity/capacity_model.py)
                     │
                     ▼
       10. Strategy Capital Ledger & Real-Money Firewall
       (src/broker/strategy_capital_ledger.py, execution_environment.py)
                     │
                     ▼
       11. Order Intent & Execution Authorization
       (src/broker/order_intent.py, broker_adapter.py)
                     │
                     ▼
       12. Broker Execution & Reconciliation
       (src/broker/alpaca_paper_broker.py, reconciliation.py)
                     │
                     ▼
       13. Post-Close Journal & Provenance Archive
       (src/post_close/post_close_journal.py, artifacts/forward/)
```

---

## 2. Comprehensive Component Catalog

| # | Component Name | File Path | Core Responsibility | Deterministic vs. LLM | Forward Freeze Status |
|---|---|---|---|---|---|
| **1** | **Market Data Ingestion** | `src/data/ingestion.py`, `src/data/tick_aggregator.py`, `src/data/market_data_quality_policy.py` | Ingests live/historical 1-min OHLCV bars, validates staleness, gaps, and zero-volume flags. | Deterministic | **FROZEN** |
| **2** | **Dynamic Universe Manager** | `src/data/universe_manager.py`, `src/safety/security_eligibility_policy.py` | Filters raw listed equities by price ($5–$1,000), minimum volume (500k shares), dollar volume ($10M+), and spreads. | Deterministic | **FROZEN** |
| **3** | **FastScanner & Ranking** | `src/signals/fast_scanner.py`, `src/models/ranking.py`, `src/signals/premarket_scanner.py` | Rapidly filters broad universe to Top 15 candidates by RVOL, gap momentum, and relative strength. | Deterministic | **FROZEN** |
| **4** | **Feature & Regressor Layer** | `src/features/real_market_features.py`, `src/features/technical.py`, `src/models/regressors.py` | Computes rolling VWAP, multi-horizon returns, volatility, order imbalance, and regression edge estimates. | Deterministic | **FROZEN** |
| **5** | **Market Regime Engine** | `src/intelligence/market_regime_engine.py` | Analyzes SPY / market breadth, volatility (VIX proxy), sector dispersion, and determines market regime. | Deterministic | **FROZEN** |
| **6** | **SessionGate** | `src/intelligence/session_gate.py` | Emits `GO` (normal risk), `CAUTION` (halved risk, 30 bps hurdle), or `NO_GO` (cash only). | Deterministic | **FROZEN** |
| **7** | **Event Risk Policy** | `src/events/event_risk_policy.py`, `src/events/macro_event_schedule.py` | Freezes trading [-15m, +15m] around CPI/FOMC/NFP/PPI and issues earnings vetoes. | Deterministic | **FROZEN** |
| **8** | **Expected Execution Cost** | `src/cost/expected_execution_cost.py` | Estimates round-trip friction = half-spread + volatility slippage + exchange fees. | Deterministic | **FROZEN** |
| **9** | **Risk Position Sizer** | `src/risk/risk_position_sizer.py`, `src/risk/risk_budget.py` | Calculates exact share quantity from equity, risk fraction (0.75%), stop distance, and sizing ceiling ($750 normal, $375 caution). | Deterministic | **FROZEN** |
| **10** | **Capacity Model** | `src/capacity/capacity_model.py`, `src/stress/capacity_engine.py` | Enforces participation rate caps (<1% of 5-min ADV) to prevent market impact. | Deterministic | **FROZEN** |
| **11** | **Portfolio Risk State** | `src/risk/portfolio_risk_state.py`, `src/risk/drawdown_state.py`, `src/risk/capital_tiers.py` | Tracks intraday cumulative P&L, daily loss limit (1.5% / $15), and peak equity drawdown. | Deterministic | **FROZEN** |
| **12** | **Strategy Capital Ledger** | `src/broker/strategy_capital_ledger.py`, `src/broker/execution_environment.py` | Maintains strategy equity ($1,000 firewall) and blocks real-money execution (`RealMoneyAuthorizationError`). | Deterministic | **FROZEN** |
| **13** | **Broker Adapter Interface** | `src/broker/broker_adapter.py`, `src/broker/order_intent.py` | Abstract broker interface handling order intents, state transitions, fills, and cancellations. | Deterministic | **FROZEN** |
| **14** | **Alpaca Paper Broker** | `src/broker/alpaca_paper_broker.py` | Concrete REST/WebSocket client executing paper orders against Alpaca Paper API. | Deterministic | **FROZEN** |
| **15** | **Simulation Broker** | `src/broker/simulation_broker.py` | Offline deterministic execution simulator applying realistic spread, slippage, and latencies. | Deterministic | **FROZEN** |
| **16** | **Runtime State Machine** | `src/runtime/runtime_state.py`, `src/runtime/paper_trading_runtime.py` | Controls session states: `PRE_MARKET` -> `OPEN_COOLDOWN` -> `TRADING` -> `FLATTENING` -> `CLOSED`. | Deterministic | **FROZEN** |
| **17** | **Market Clock & Calendar** | `src/runtime/market_clock.py`, `src/data/calendar.py` | Enforces strict Eastern Time (ET) market hours, early closes, and trading holidays. | Deterministic | **FROZEN** |
| **18** | **Reconciliation Engine** | `src/broker/reconciliation.py` | Continuously verifies that internal strategy positions match broker-reported positions. | Deterministic | **FROZEN** |
| **19** | **Event Store** | `src/runtime/event_store.py` | Immutable append-only store recording all decisions, quotes, order intents, fills, and state changes. | Deterministic | **FROZEN** |
| **20** | **Post-Close Journal** | `src/post_close/post_close_journal.py` | Generates end-of-day Markdown summaries, performance metrics, and Parquet ledgers. | Deterministic | **FROZEN** |
| **21** | **MMRM Advisory Layer** | `src/llm/mmrm_client.py`, `src/llm/rag_retrieval.py`, `src/intelligence/morning_brief.py` | Generates MorningBrief narratives and post-trade qualitative audits. Zero execution authority. | **LLM (Advisory)** | Non-Executable |
| **22** | **Unity Slurm Runtime** | `jobs/true_forward_paper_session.slurm`, `scripts/unity/*.sh`, `schedule_morning_launch.py` | Submits, schedules, and monitors headless forward paper trading jobs on Unity HPC. | Shell / Python | Operational |
| **23** | **Artifact & Provenance Storage** | `src/workstation/provenance.py`, `artifacts/forward/`, `artifacts/research/` | Records SHA-256 hashes, Slurm IDs, node names, and immutable session bundles. | Deterministic | **FROZEN** |
