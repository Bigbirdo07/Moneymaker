# Moneymaker: Staged Architectural Roadmap

A phased, dependency-aware blueprint to evolve the Moneymaker Quantitative Research Platform into the **Autonomous Intraday Quantitative Portfolio Manager**.

---

## 1. Phased Architecture Overview

```mermaid
flowchart TD
    subgraph Track 1: Empirical Core
        A[Phase A: Complete Phase 11C 2023 Holdout Replication] --> B[Phase B: Dynamic Universe & Liquidity Scanner]
        B --> C[Phase C: Deterministic Event Risk Policy]
        C --> D[Phase D: Risk-Budgeted Sizing & Capacity Model]
    end

    subgraph Track 2: Autonomous Production Runtime
        D --> E[Phase E: Premarket Intelligence & Regime Scanner]
        E --> F[Phase F: Live Autonomous Paper Trading Daemon]
        F --> G[Phase G: Post-Close Research Journal Service]
    end

    subgraph Track 3: Governance & Scaling
        G --> H[Phase H: Long-Duration Multi-Month Forward Paper Audit]
        H --> I[Phase I: Governed Micro-Capital Pilot Gate ($1,000)]
        I --> J[Phase J: Multi-Tier Capital Scaling ($5k -> $25k -> $100k+)]
    end
```

---

## 2. Detailed Phase Specifications

### Phase A: Complete Phase 11C Empirical Validation *(Current Phase)*
- **Objective**: Execute single-pass evaluation of frozen Engine V3 on 2023 untouched real Alpaca/IEX holdout on Unity HPC.
- **Deliverables**: All 15 required Phase 11C Parquet ledgers, diagnostic markdown reports, and formal replication verdicts.
- **Invariant**: Engine V3 architecture remains 100% frozen during execution.

### Phase B: Dynamic Universe Scanner & Liquidity Filter
- **Objective**: Expand from static 50 equities to dynamic multi-tier scanning across 3,000+ US listed equities.
- **Pipeline**:
  1. Price $\ge \$10.00$, Common Stock / ETF only (exclude penny stocks, OTC, warrants).
  2. 30-day median Dollar Volume $\ge \$25\text{M}$ (guaranteeing deep liquidity).
  3. Average bid-ask spread $\le 5\text{ bps}$.
  4. Candidate universe reduction: $3,000 \longrightarrow 500\text{--}1,500 \text{ eligible} \longrightarrow 100\text{--}300 \text{ scanned}$.
- **Module**: `src/data/universe_manager.py`, `src/data/liquidity_filter.py`.

### Phase C: Deterministic Event Risk Policy Engine
- **Objective**: Disqualify securities subject to unhedgeable binary gap risks before ranking.
- **Veto Rules**:
  - Same-day earnings announcement (premarket or postmarket).
  - Exchange trading halt (current or resumed within past 60 minutes).
  - Scheduled FDA binary trial readout / major antitrust litigation decision.
  - Merger vote / tender offer / corporate restructuring.
- **Module**: `src/safety/event_risk_policy.py`.

### Phase D: Risk-Budgeted Sizing & Scalable Capacity Model
- **Objective**: Replace static capital allocations with formulaic risk budgeting and capacity constraints.
- **Formula**:
  $$\text{Shares} = \left\lfloor \frac{\min(\text{Equity} \times \text{Risk Budget \%}, \text{Daily Risk Remaining})}{\text{Entry Price} \times \text{Stop Loss \%}} \right\rfloor$$
- **Capacity Controls**:
  - Max $1.0\%$ of 30-day ADV.
  - Max $2.0\%$ of expected 1-minute bar volume.
  - Non-linear market impact penalty function for portfolios scaling to $\$25\text{k}\text{--}\$100\text{k}+$.
- **Module**: `src/execution/risk_position_sizer.py`, `src/execution/capacity_model.py`.

### Phase E: Premarket Intelligence Pipeline (8:45–9:25 AM ET)
- **Objective**: Automated morning routine synthesizing macro regime, breadth, sector momentum, and top-5 watchlist.
- **Output**: Generates daily structured brief with session decision (`GO`, `CAUTION`, `NO_GO`).
- **Module**: `src/research/morning_brief_service.py`.

### Phase F: Autonomous Live Paper Trading Runtime
- **Objective**: Always-on low-latency paper execution service running during market hours (9:30 AM – 4:00 PM ET).
- **Features**:
  - Live websocket streaming from Alpaca Paper API.
  - Continuous intraday cross-sectional re-ranking.
  - Autonomous entry/exit execution without human confirmation modals.
  - Strict 3:55 PM ET mandatory flattening sweep (100% cash).
- **Module**: `src/execution/paper_trading_daemon.py`, `src/broker/alpaca_paper_adapter.py`.

### Phase G: Post-Close Daily Research Journal & Learning Engine (4:15 PM ET)
- **Objective**: Automated EOD research journal logging trade attribution, MFE/MAE, skipped setups, and regime stability.
- **Output**: Appends structured daily metrics to longitudinal research registry for scheduled offline retraining.
- **Module**: `src/research/post_close_journal_service.py`.

### Phase H: Long-Duration Forward Paper Validation
- **Objective**: Continuous multi-month live paper forward evaluation on unseen future market days.
- **Success Criteria**: Positive net expectancy, $\text{Profit Factor} \ge 1.25$, $\text{Max Drawdown} \le 5.0\%$, zero operational failures, verified daily flattening.

### Phase I: Governed Micro-Capital Proving Ground ($1,000 Live)
- **Objective**: Initial real-money pilot on $1,000 proving account with strict account-level circuit breakers.
- **Gate**: Requires formal audit and cryptographic authorization.
