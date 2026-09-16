# Moneymaker Workstation Architecture Document (Phase 8A)

## 1. System Overview & Architectural Topology
Moneymaker Workstation V1 is a local-first, low-latency trading and quantitative research application built on top of the validated multi-strategy quantitative execution engine.

```
+-------------------------------------------------------------------------+
|                       Moneymaker Workstation UI                         |
|   (React 18 + TypeScript + Vite + Tailwind/Custom CSS - Dark Glass)     |
|   Screens: Dashboard | Markets | Portfolio | Strategies | Trades |      |
|            Risk | AI Copilot | System / Provenance Audit               |
+-------------------------------------------------------------------------+
                                    |  REST / WebSocket (/ws/stream)
                                    v
+-------------------------------------------------------------------------+
|                       Workstation API & Services                        |
|   (FastAPI Router | WorkstationService | DataProvenanceEngine)          |
+-------------------------------------------------------------------------+
          |                                        |
          | Read-Only Invocations                  | Authoritative Telemetry
          v                                        v
+------------------------------------+   +--------------------------------+
|       Moneymaker AI Copilot        |   |    Quantitative Core Engine    |
|   (23 Explicit Structured Tools)   |   |  - Alpha A ($10k Hold)         |
|   - Execution Firewall Barrier     |   |  - Alpha B ($5k Tier 2 Valid)  |
|   - Zero Broker Execution Rights   |   |  - PortfolioRiskAggregator     |
|   - Evidence-Grounded Reasoning    |   |  - Allocator (Shadow Only)     |
|   - Trade Explanations & Briefs    |   |  - Broker Adapter & Ledger     |
+------------------------------------+   +--------------------------------+
```

---

## 2. Core Subsystems

### A. Backend API Layer (`src/workstation/`)
- **`models.py`**: Defines typed Pydantic models for account equity, strategy cards, open positions, trade records, candlestick bars, risk metrics, daily briefs, and audit records.
- **`provenance.py`**: Implements the `DataProvenanceEngine` and `audit_live_evidence()` function to audit empirical provenance across all database and ledger rows.
- **`service.py`**: Central platform orchestrator that maintains real-time position mark-to-market, trade journals, opportunity rankings, and system health.
- **`copilot_tools.py`**: 23 explicit structured tools for conversational analysis, guarded by the `CopilotExecutionFirewallViolation` barrier.
- **`copilot_engine.py`**: Natural language reasoning engine that synthesizes tool outputs into grounded explanations with evidence badges.
- **`streaming.py`**: Broadcasts live ticks and risk events via WebSocket connections without aggressive frontend polling.
- **`api.py`**: Exposes REST and WebSocket endpoints.

### B. Frontend Workstation (`workstation/`)
- **Stack**: React 18, TypeScript, Vite, Tailwind/Custom CSS, Lucide icons.
- **Navigation (8 Screens)**:
  1. **Dashboard**: Top KPI bar, Strategy Cards, SVG Equity Curve, Daily P&L breakdown, and Live Activity Feed.
  2. **Markets**: Live Watchlist, Candlestick + VWAP Chart (1m, 5m, 15m, 1h, 1D), Strategy Signals, and Risk Flags.
  3. **Portfolio**: Positions Table with explicit `ALPHA_A` / `ALPHA_B` ownership, Cohort IDs, Exposure distributions, and Risk Telemetry.
  4. **Strategies**: Alpha A and Alpha B dedicated pages, Ranked Opportunity Scanner, and 3-point Empirical Capacity Curves.
  5. **Trades**: Complete Trade Journal with interactive **"WHY? (Explain Trade)"** drawer.
  6. **Risk**: Multi-tier Risk Dashboard, Realized Drawdown (1.30%), Tail Risk (VaR/ES), Veto Log, and Macro Stress Simulations.
  7. **AI Copilot**: Conversational assistant with suggested prompt chips, tool invocation logs, and Morning/Midday/Closing Daily Briefs.
  8. **System / Audit**: Broker Connection Status, Reconciliation Status (`BROKER MATCHED`), Kill Switch Visibility, and Data Provenance Audit Inspector.

---

## 3. Governance & Firewall Invariants
1. **Zero LLM Execution Authority**: The AI Copilot is restricted to read-only tool calls. Any attempt to route orders, mutate budgets, or alter configs raises a fatal `PermissionError`.
2. **Capital Isolation**: Alpha A ($10,000 USD) and Alpha B ($5,000 USD) maintain strictly separate capital partitions.
3. **Data Provenance**: Every statistic displayed in the UI is tagged with its empirical evidence origin (`BROKER_LIVE`, `BROKER_PAPER`, `FORWARD_SHADOW`, `HISTORICAL`, `SIMULATED`, `PROJECTED`).
