# Moneymaker Workstation V1 — User Guide

## 1. Introduction
Moneymaker Workstation is a local-first trading and research desktop environment for monitoring multi-strategy quantitative execution, inspecting real-time market data, reviewing trade explanations, analyzing risk, and conversing with Moneymaker AI Copilot.

---

## 2. Launching the Workstation

### Step 1: Start the Backend API
From the project root:
```bash
.venv/bin/uvicorn src.workstation.api:app --host 127.0.0.1 --port 8000 --reload
```

### Step 2: Start the Frontend UI
In a separate terminal:
```bash
cd workstation
npm run dev
```
Open `http://localhost:3000` in your web browser.

---

## 3. Screen-by-Screen Walkthrough

### 1. Dashboard (`/`)
- **Top Metrics**: View total account equity ($16,576.00 USD), today's P&L (+$142.50 USD), cash reserve ($6,096.00 USD), and current drawdown (1.30%).
- **Strategy Cards**: Compare Alpha A (Intraday Momentum, $10,000 capital) and Alpha B (Multi-Day Reversal, $5,000 capital).
- **Equity Curve**: Toggle historical and intraday performance across 1D, 5D, 1M, 3M, and ALL horizons.
- **Activity Feed**: Real-time log of signals, order fills, and risk vetoes.

### 2. Markets (`/markets`)
- **Watchlist**: Track live quotes, spreads in basis points, and relative volume for universe tickers (NVDA, AMD, TSLA, AAPL, MSFT, META, GOOGL, AMZN).
- **Chart Viewer**: View multi-timeframe candles (1m, 5m, 15m, 1h, 1D) with VWAP overlays, active signals, and event flags.

### 3. Portfolio (`/portfolio`)
- **Positions**: Inspect all open positions with explicit strategy ownership tags (`ALPHA_A` or `ALPHA_B`), entry price, cost basis, unrealized P&L, cohort ID, and scheduled exit time.
- **Exposure Breakdown**: View capital deployed across strategies, sectors, high-beta clusters, and overnight holds.

### 4. Strategies (`/strategies`)
- **Opportunity Scanner**: View ranked candidate tables with raw model scores, expected gross return, estimated friction, and net expected edge.
- **Capacity Curve**: View empirical 3-point edge retention calibrations ($1k, $2.5k, $5k) and projected capacity thresholds.

### 5. Trades (`/trades`)
- **Trade Journal**: Search and filter all past trades by strategy and execution status.
- **"WHY?" Button**: Click the **WHY?** button on any trade to open the grounded LLM Trade Explanation modal.

### 6. Risk (`/risk`)
- **Risk Telemetry**: Inspect daily VaR 95/99%, Expected Shortfall, and portfolio beta.
- **Veto Log**: Review orders intercepted or resized by the `PortfolioRiskAggregator` and view net dollars saved.
- **Stress Testing**: Explore portfolio resilience under -2% overnight gaps, -5% market shocks, and 2x spread widening.

### 7. AI Copilot (`/copilot`)
- **Conversational Assistant**: Chat with Moneymaker AI Copilot about any aspect of the platform.
- **Suggested Prompts**: Click pre-populated chips like *"Why did we buy AMD?"*, *"Is either strategy degrading?"*, or *"What happens if the market drops 5%?"*.
- **Daily Briefs**: View structured Morning, Midday, and Closing executive reports.

### 8. System / Audit (`/system`)
- **Broker Sync**: Verify broker reconciliation state (`BROKER MATCHED`).
- **Kill Switches**: Check armed status of Global, Alpha A, and Alpha B emergency kill switches.
- **Provenance Auditor**: Run live audits to verify broker order IDs and detect synthetic data.
