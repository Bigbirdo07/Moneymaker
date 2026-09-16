# Moneymaker AI Copilot Tool Reference (Phase 8A)

## 1. Overview
The Moneymaker AI Copilot operates strictly through **23 explicit structured tools** registered in `src/workstation/copilot_tools.py`. It is completely isolated from broker order routing, live capital manager mutations, and configuration edits by an architectural execution firewall.

---

## 2. Complete Tool Registry Specification

| # | Tool Name | Parameters | Return Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `get_account_summary()` | None | `Dict[str, Any]` | Returns total equity, cash, buying power, today P&L, cumulative realized P&L, drawdown, and broker sync time. |
| 2 | `get_today_pnl()` | None | `Dict[str, Any]` | Returns today's realized P&L, unrealized P&L, and strategy contributions. |
| 3 | `get_portfolio()` | None | `Dict[str, Any]` | Returns total authorized capital, strategy exposure, symbol exposure, sector exposure, and overnight risk. |
| 4 | `get_open_positions()` | None | `List[Dict[str, Any]]` | Returns list of all active open positions with strategy ownership, shares, entry price, current price, and unrealized P&L. |
| 5 | `get_position(symbol)` | `symbol: str` | `Dict[str, Any]` | Returns position details for a specific ticker symbol. |
| 6 | `get_trade_history()` | None | `List[Dict[str, Any]]` | Returns all executed trade records from the verified ledger. |
| 7 | `get_trade(trade_id)` | `trade_id: str` | `Dict[str, Any]` | Returns full details for a specific trade ID. |
| 8 | `get_live_quote(symbol)` | `symbol: str` | `Dict[str, Any]` | Returns real-time market quote, bid/ask, spread in bps, and volume. |
| 9 | `get_market_snapshot()` | None | `Dict[str, Any]` | Returns summary quote snapshot for the active universe watchlist. |
| 10 | `get_watchlist()` | None | `List[Dict[str, Any]]` | Returns full watchlist table with prices and relative volume. |
| 11 | `get_alpha_a_signals()` | None | `List[Dict[str, Any]]` | Returns current ranked opportunity table for Alpha A (Intraday Momentum). |
| 12 | `get_alpha_b_signals()` | None | `List[Dict[str, Any]]` | Returns current ranked opportunity table for Alpha B (Multi-Day Reversal). |
| 13 | `get_strategy_status(strategy_id)` | `strategy_id: str` | `Dict[str, Any]` | Returns strategy capital authorization, execution mode, governance state, and kill switch state. |
| 14 | `get_strategy_health(strategy_id)` | `strategy_id: str` | `Dict[str, Any]` | Returns rolling net expectancy, 95% CI, canonical friction, edge retention, cost break-even multiplier, and drawdown. |
| 15 | `get_strategy_capacity(strategy_id)` | `strategy_id: str` | `Dict[str, Any]` | Returns validated capacity ceiling, decay slope, bottleneck mechanism, and theoretical limits. |
| 16 | `get_portfolio_risk()` | None | `Dict[str, Any]` | Returns portfolio VaR 95/99%, Expected Shortfall 95/99%, drawdown, portfolio beta, and stress test shocks. |
| 17 | `get_recent_risk_vetoes()` | None | `List[Dict[str, Any]]` | Returns recent orders intercepted or resized by PortfolioRiskAggregator. |
| 18 | `get_market_regime()` | None | `Dict[str, Any]` | Returns current market regime classification (e.g. `BULL_LOW_VOL`) and favorability scores. |
| 19 | `get_system_health()` | None | `Dict[str, Any]` | Returns broker connection state, reconciliation status, database health, and heartbeat. |
| 20 | `get_validation_state()` | None | `Dict[str, Any]` | Returns formal governance verdicts across Alpha A, Alpha B, Portfolio, and Allocator. |
| 21 | `explain_trade(trade_id)` | `trade_id: str` | `Dict[str, Any]` | Produces structured trade explanation: Strategy, Signal, Why Selected, Expected Edge, Risk Checks, Execution, and Result. |
| 22 | `compare_strategies()` | None | `Dict[str, Any]` | Returns head-to-head comparison of Alpha A vs Alpha B vs Combined Portfolio. |
| 23 | `get_daily_summary()` | None | `Dict[str, Any]` | Returns closing executive summary brief. |

---

## 3. Execution Firewall Policies
The `CopilotExecutionFirewallViolation` exception is raised immediately if the LLM attempts to execute any action containing forbidden keywords:
`ORDER`, `BUY`, `SELL`, `ALLOCATE`, `MUTATE`, `REARM`, `CAPITAL`, `SHORT`, `CONFIG`, `KILL`, `SUBMIT`, `PLACE`.
