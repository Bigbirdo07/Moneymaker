# Moneymaker: Current Architecture State & Gap Analysis

Comprehensive audit and gap analysis of the Moneymaker codebase against the **Canonical Product, Research, System, and Autonomy Specification**.

---

## 1. System Component Status Matrix

| Component Layer | Canonical Target Requirement | Current Implementation in Repository | Architectural Status |
| :--- | :--- | :--- | :--- |
| **Market Data Layer** | Multi-vendor abstraction (Alpaca, Polygon, IEX), real-time streaming + historical bars, monotonic timestamps, SHA-256 provenance. | `src/data/alpaca_market_data.py`, `src/data/real_data_firewall.py`. Ingests real 1m IEX bars with SHA-256 hashes. | **PARTIALLY COMPLETE (HISTORICAL ONLY)** |
| **Universe Scanner** | Dynamic multi-stage filtering from 3,000+ US stocks $\rightarrow$ 500–1,500 liquid $\rightarrow$ 100–300 scanned $\rightarrow$ 5–10 top ranked. | Currently fixed to `STANDARD_50_UNIVERSE` (49 equities + SPY). | **GAP / REFACTOR REQUIRED** |
| **Event Risk Veto** | Deterministic `EventRiskPolicy` for same-day earnings, trading halts, binary clinical trials, merger votes. | Calendar checks exist in `src/data/calendar.py`, but no dedicated `EventRiskPolicy` module. | **GAP / BUILD REQUIRED** |
| **Market Regime Gate** | Macro gate evaluating SPY slope, breadth (% above VWAP $\ge 40\%$), and volatility expansion. | Fully implemented in `src/features/real_market_feature_store_v3.py` and `src/models/real_market_ranking_forecaster_v3.py`. | **COMPLETE (VALIDATED IN V3)** |
| **Feature Store** | Contemporaneous cross-sectional ranking (`cs_return_rank_15m`, `cs_vwap_rank`), relative strength, multi-horizon returns. | Fully implemented in `src/features/real_market_feature_store_v3.py`. Zero lookahead, vectorized. | **COMPLETE (VALIDATED IN V3)** |
| **Forecasting & Ranking** | Multi-horizon executable net return estimation (30m, 60m, 120m) with probability calibration. | Fully implemented in `src/models/real_market_ranking_forecaster_v3.py`. | **COMPLETE (VALIDATED IN V3)** |
| **Entry Engine** | Cost-aware net edge hurdle ($\ge 25\text{ bps}$), calibrated prob ($\ge 0.58$), max 1 trade/day, default to CASH. | Fully implemented in `src/signals/real_market_entry_model_v3.py`. | **COMPLETE (VALIDATED IN V3)** |
| **Position Sizing** | Formulaic risk budgeting $f(\text{equity}, \text{risk\_budget}, \text{stop\_dist}, \text{volatility}, \text{capacity})$. | Currently static 50% capital cap in `src/execution/real_market_allocator_v3.py`. | **PARTIAL / REFACTOR REQUIRED** |
| **Exit Engine** | Dynamic expected continuation value, hard stop (-1.5%), take profit (+3.0%), trailing gain lock ($\ge +1.5\%$ MFE). | Fully implemented in `src/signals/real_market_exit_model_v3.py`. | **COMPLETE (VALIDATED IN V3)** |
| **End-of-Day Flattening** | Mandatory 100% cash by 3:55 PM ET. Zero overnight equity risk. | Forced exit at bar 60 or session end in runner. Needs formal 3:45–3:55 PM sweep rule. | **PARTIAL (ENFORCE FORMALLY)** |
| **Account Drawdown Guard** | State machine (`NORMAL`, `REDUCED_RISK`, `CASH_PRESERVATION`, `HALTED`) on daily loss $\ge 1.5\%$. | Hard stop on daily trades in entry model; needs multi-day drawdown state machine. | **PARTIALLY COMPLETE** |
| **Capacity & Impact** | ADV participation %, minute volume %, impact curves for $25k–$100k+ scaling. | Researched in Phase 7/8; needs unified `CapacityModel` module integrated into sizing. | **GAP / BUILD REQUIRED** |
| **LLM / MMRM System** | Beside the money path. Premarket briefs, trade explanations, post-close journals, anomaly alerts. | `src/llm/mmrm_adapter.py`, `src/governance/trade_explanations.py`, Copilot workstation chat. | **PARTIALLY COMPLETE** |
| **Autonomous Paper Runtime** | Always-on forward paper execution loop with live Alpaca paper broker connector. | Simulated replay exists; live always-on paper trading daemon not yet wired to live websockets. | **GAP / BUILD REQUIRED** |
| **Post-Close Journaling** | Automated EOD research journal generating P&L attribution, MFE/MAE, skipped opportunities. | Script-based reporting in research; needs automated daily journal service for paper trading. | **PARTIAL (AUTOMATE)** |
| **Research vs Prod Separation** | Unity HPC for heavy empirical research; lightweight service for live paper execution. | Unity workflow established (`MAC -> UNITY -> SLURM -> RESULTS -> MAC`). | **COMPLETE FOR RESEARCH** |

---

## 2. Categorized Action Plan

### A. What Already Exists & Must Be Retained
1. **Engine V3 Quantitative Core**: Feature store V3, ranking forecaster V3, entry model V3, exit model V3.
2. **Provenance & Holdout Firewalls**: Cryptographic freeze manifests, SHA-256 verification, strict burned-holdout tracking.
3. **Unity HPC Research Engine**: Slurm submission, sync, and auditing pipeline (`MAC → UNITY → SLURM → RESULTS → MAC`).
4. **Workstation UI & Evidence Badges**: Fast-updating UI, risk dashboards, Copilot chat, and audit APIs.

### B. What Partially Exists & Should Be Refactored
1. **Capital Allocation**: Refactor `RealMarketAllocatorV3` to use formulaic risk budgeting:
   $$\text{Target Dollars} = \min\left(\frac{\text{Equity} \times \text{Risk Budget \%}}{\text{Stop Loss \%}}, \text{Max Position Capital}\right)$$
2. **Premarket Briefs & EOD Journals**: Formalize `MorningBriefService` and `PostCloseJournalService` into structured automated daemons.
3. **Account Drawdown State Machine**: Expand daily loss limit into formal 4-state risk engine (`NORMAL`, `REDUCED_RISK`, `CASH_PRESERVATION`, `HALTED`).

### C. What Is Missing & Must Be Built
1. **Dynamic Universe Scanner (`UniverseManager`, `LiquidityFilter`)**: Scanning 500–1,500 liquid US equities dynamically beyond the fixed 50 list.
2. **Deterministic Event Risk Policy (`EventRiskPolicy`)**: Automated disqualification of same-day earnings, halts, and binary events.
3. **Capacity & Liquidity Model (`CapacityModel`)**: Explicit ADV and minute-volume participation constraints for scaling beyond $1,000.
4. **Live Paper Trading Daemon**: Always-on real-time paper execution runtime connected to Alpaca Paper Trading API.

### D. What Must NOT Be Changed Yet (Strictly Frozen)
- `src/features/real_market_feature_store_v3.py`
- `src/models/real_market_ranking_forecaster_v3.py`
- `src/signals/real_market_entry_model_v3.py`
- `src/signals/real_market_exit_model_v3.py`
- `src/execution/real_market_allocator_v3.py`
- `src/replay/real_engine_v3_runner.py`
*(All frozen under `ENGINE_V3_FREEZE_MANIFEST.json` while Phase 11C historical replication is actively validating on Unity).*
