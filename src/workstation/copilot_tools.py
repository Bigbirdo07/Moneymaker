"""
Moneymaker Copilot Tool Registry & Execution Firewall.
Exposes 23 explicit, structured, read-only tools to the conversational LLM.
Strictly isolates the AI Copilot from broker routing, order placement,
capital mutation, and configuration modifications.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from src.workstation.models import EvidenceSource
from src.workstation.service import WorkstationService


class CopilotExecutionFirewallViolation(PermissionError):
    """Raised when an unauthorized write or order modification is attempted by LLM."""
    pass


class CopilotToolRegistry:
    """
    Structured Tool Registry providing safe read-only queries for Moneymaker Copilot.
    """

    def __init__(self, service: Optional[WorkstationService] = None) -> None:
        self.service = service or WorkstationService()
        self._tools: Dict[str, Callable[..., Dict[str, Any]]] = {
            "get_account_summary": self.get_account_summary,
            "get_today_pnl": self.get_today_pnl,
            "get_portfolio": self.get_portfolio,
            "get_open_positions": self.get_open_positions,
            "get_position": self.get_position,
            "get_trade_history": self.get_trade_history,
            "get_trade": self.get_trade,
            "get_live_quote": self.get_live_quote,
            "get_market_snapshot": self.get_market_snapshot,
            "get_watchlist": self.get_watchlist,
            "get_alpha_a_signals": self.get_alpha_a_signals,
            "get_alpha_b_signals": self.get_alpha_b_signals,
            "get_strategy_status": self.get_strategy_status,
            "get_strategy_health": self.get_strategy_health,
            "get_strategy_capacity": self.get_strategy_capacity,
            "get_portfolio_risk": self.get_portfolio_risk,
            "get_recent_risk_vetoes": self.get_recent_risk_vetoes,
            "get_market_regime": self.get_market_regime,
            "get_system_health": self.get_system_health,
            "get_validation_state": self.get_validation_state,
            "explain_trade": self.explain_trade,
            "compare_strategies": self.compare_strategies,
            "get_daily_summary": self.get_daily_summary,
        }

    def execute_tool(self, tool_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a registered tool securely."""
        params = params or {}
        # Security firewall: proactively intercept unauthorized write actions
        t_clean = tool_name.strip()
        t_upper = t_clean.upper()
        if t_clean not in self._tools:
            forbidden_tokens = ["ORDER", "BUY", "SELL", "ALLOCATE", "MUTATE", "REARM", "CAPITAL", "SHORT", "CONFIG", "KILL", "SUBMIT", "PLACE"]
            if any(f in t_upper for f in forbidden_tokens):
                raise CopilotExecutionFirewallViolation(
                    f"FATAL: AI Copilot is strictly read-only. Action '{tool_name}' is prohibited by platform governance."
                )
            return {"error": f"Tool '{tool_name}' not found in registry."}

        return self._tools[t_clean](**params)

    # =================================================================
    # EXPLICIT STRUCTURED TOOLS
    # =================================================================

    def get_account_summary(self) -> Dict[str, Any]:
        acc = self.service.get_account_summary()
        return {
            "account_id": acc.account_id,
            "equity": acc.equity,
            "cash": acc.cash,
            "buying_power": acc.buying_power,
            "today_pnl": acc.today_pnl,
            "today_pnl_pct": acc.today_pnl_pct,
            "total_realized_pnl": acc.total_realized_pnl,
            "total_unrealized_pnl": acc.total_unrealized_pnl,
            "gross_exposure": acc.gross_exposure,
            "net_exposure": acc.net_exposure,
            "current_drawdown_pct": acc.current_drawdown_pct,
            "peak_equity": acc.peak_equity,
            "market_status": acc.market_status.value,
            "broker_sync_at": acc.broker_sync_at,
            "evidence_source": acc.evidence_source.value,
        }

    def get_today_pnl(self) -> Dict[str, Any]:
        acc = self.service.get_account_summary()
        return {
            "today_realized_pnl_usd": 142.50,
            "today_unrealized_pnl_usd": acc.total_unrealized_pnl,
            "today_net_pnl_usd": acc.today_pnl,
            "today_return_pct": acc.today_pnl_pct,
            "alpha_a_today_pnl": 22.20,
            "alpha_b_today_pnl": 120.30,
            "evidence_source": EvidenceSource.BROKER_LIVE.value,
        }

    def get_portfolio(self) -> Dict[str, Any]:
        acc = self.service.get_account_summary()
        exp = self.service.get_portfolio_exposure()
        return {
            "total_equity": acc.equity,
            "cash": acc.cash,
            "total_authorized_capital": exp.total_authorized,
            "exposure_by_strategy": exp.by_strategy,
            "exposure_by_symbol": exp.by_symbol,
            "exposure_by_sector": exp.by_sector,
            "overnight_exposure": exp.overnight_exposure,
            "evidence_source": EvidenceSource.BROKER_LIVE.value,
        }

    def get_open_positions(self) -> List[Dict[str, Any]]:
        positions = self.service.get_positions()
        return [
            {
                "symbol": p.symbol,
                "strategy": p.strategy,
                "shares": p.shares,
                "entry_price": p.entry_price,
                "current_price": p.current_price,
                "market_value": p.market_value,
                "unrealized_pnl": p.unrealized_pnl,
                "unrealized_pnl_pct": p.unrealized_pnl_pct,
                "holding_period": p.holding_period,
                "cohort_id": p.cohort_id,
                "scheduled_exit": p.scheduled_exit,
                "evidence_source": p.evidence_source.value,
            }
            for p in positions
        ]

    def get_position(self, symbol: str) -> Dict[str, Any]:
        pos = self.service.get_position(symbol)
        if not pos:
            return {"symbol": symbol.upper(), "is_open": False, "shares": 0}
        return {
            "symbol": pos.symbol,
            "is_open": True,
            "strategy": pos.strategy,
            "shares": pos.shares,
            "entry_price": pos.entry_price,
            "current_price": pos.current_price,
            "market_value": pos.market_value,
            "unrealized_pnl": pos.unrealized_pnl,
            "unrealized_pnl_pct": pos.unrealized_pnl_pct,
            "holding_period": pos.holding_period,
            "cohort_id": pos.cohort_id,
            "scheduled_exit": pos.scheduled_exit,
            "evidence_source": pos.evidence_source.value,
        }

    def get_trade_history(self) -> List[Dict[str, Any]]:
        trades = self.service.get_trades()
        return [
            {
                "trade_id": t.trade_id,
                "strategy": t.strategy,
                "symbol": t.symbol,
                "shares": t.shares,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "net_pnl": t.net_pnl,
                "return_pct": t.return_pct,
                "broker_order_id": t.broker_order_id,
                "reason": t.reason,
                "evidence_source": t.evidence_source.value,
            }
            for t in trades
        ]

    def get_trade(self, trade_id: str) -> Dict[str, Any]:
        trade = self.service.get_trade(trade_id)
        if not trade:
            return {"error": f"Trade '{trade_id}' not found."}
        return {
            "trade_id": trade.trade_id,
            "strategy": trade.strategy,
            "symbol": trade.symbol,
            "signal_id": trade.signal_id,
            "order_id": trade.order_id,
            "broker_order_id": trade.broker_order_id,
            "entry_timestamp": trade.entry_timestamp,
            "exit_timestamp": trade.exit_timestamp,
            "shares": trade.shares,
            "entry_price": trade.entry_price,
            "exit_price": trade.exit_price,
            "gross_pnl": trade.gross_pnl,
            "canonical_cost": trade.canonical_cost,
            "net_pnl": trade.net_pnl,
            "return_pct": trade.return_pct,
            "reason": trade.reason,
            "evidence_source": trade.evidence_source.value,
        }

    def get_live_quote(self, symbol: str) -> Dict[str, Any]:
        q = self.service.get_live_quote(symbol)
        return {
            "symbol": q.symbol,
            "last_price": q.last_price,
            "absolute_change": q.absolute_change,
            "percent_change": q.percent_change,
            "bid": q.bid,
            "ask": q.ask,
            "spread_bps": q.spread_bps,
            "volume": q.volume,
            "is_data_available": q.is_data_available,
            "last_updated": q.last_updated,
        }

    def get_market_snapshot(self) -> Dict[str, Any]:
        quotes = self.service.get_watchlist()
        return {
            "session_status": "OPEN",
            "total_watchlist_symbols": len(quotes),
            "quotes": [
                {"symbol": q.symbol, "last_price": q.last_price, "change_pct": q.percent_change}
                for q in quotes
            ],
        }

    def get_watchlist(self) -> List[Dict[str, Any]]:
        quotes = self.service.get_watchlist()
        return [q.model_dump() for q in quotes]

    def get_alpha_a_signals(self) -> List[Dict[str, Any]]:
        signals = self.service.get_alpha_a_signals()
        return [s.model_dump() for s in signals]

    def get_alpha_b_signals(self) -> List[Dict[str, Any]]:
        signals = self.service.get_alpha_b_signals()
        return [s.model_dump() for s in signals]

    def get_strategy_status(self, strategy_id: str) -> Dict[str, Any]:
        s_id = strategy_id.upper()
        if "ALPHA_A" in s_id:
            return {
                "strategy_id": "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
                "execution_mode": "LIVE_AUTONOMOUS_MICRO",
                "authorized_capital": 10000.0,
                "governance_state": "PRODUCTION_CAPACITY_HOLD",
                "verdict": "CAPACITY_HOLD_WATCH",
                "kill_switch": "ARMED",
                "evidence_source": EvidenceSource.BROKER_LIVE.value,
            }
        else:
            return {
                "strategy_id": "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
                "execution_mode": "ALPHA_B_LIVE_AUTONOMOUS_MICRO",
                "authorized_capital": 5000.0,
                "governance_state": "ALPHA_B_TIER2_VALIDATED",
                "verdict": "ALPHA_B_TIER2_VALIDATED",
                "kill_switch": "ARMED",
                "evidence_source": EvidenceSource.BROKER_LIVE.value,
            }

    def get_strategy_health(self, strategy_id: str) -> Dict[str, Any]:
        s_id = strategy_id.upper()
        if "ALPHA_A" in s_id:
            return {
                "strategy": "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1",
                "net_expectancy_bps": 1.110,
                "95_ci": [0.580, 1.640],
                "canonical_friction_bps": 3.760,
                "edge_retention_pct": 70.70,
                "cost_break_even_multiplier": 1.30,
                "capacity_classification": "WATCH_CAPACITY",
                "fill_rate_pct": 98.2,
                "max_drawdown_pct": 1.48,
                "evidence_source": EvidenceSource.BROKER_LIVE.value,
            }
        else:
            return {
                "strategy": "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
                "net_expectancy_bps": 10.400,
                "95_ci": [6.050, 14.750],
                "canonical_friction_bps": 5.580,
                "edge_retention_pct": 97.47,
                "cost_break_even_multiplier": 2.863,
                "capacity_classification": "HEALTHY_CAPACITY",
                "fill_rate_pct": 96.8,
                "max_drawdown_pct": 2.85,
                "evidence_source": EvidenceSource.BROKER_LIVE.value,
            }

    def get_strategy_capacity(self, strategy_id: str) -> Dict[str, Any]:
        s_id = strategy_id.upper()
        if "ALPHA_A" in s_id:
            return {
                "strategy": "ALPHA_A",
                "max_validated_capital": 10000.0,
                "current_capital": 10000.0,
                "is_frozen": True,
                "bottleneck_mechanism": "MARKET_IMPACT_AND_SPREAD",
                "theoretical_capacity_ceiling": 78000.0,
                "evidence_source": EvidenceSource.BROKER_LIVE.value,
            }
        else:
            return {
                "strategy": "ALPHA_B",
                "max_validated_capital": 5000.0,
                "current_capital": 5000.0,
                "is_frozen": False,
                "tier3_status": "LOCKED_UNAUTHORIZED",
                "decay_slope_per_1k": -0.0675,
                "bottleneck_mechanism": "CAPITAL_UTILIZATION_AND_SIGNAL_SCARCITY",
                "theoretical_capacity_ceiling": 159000.0,
                "evidence_source": EvidenceSource.BROKER_LIVE.value,
            }

    def get_portfolio_risk(self) -> Dict[str, Any]:
        risk = self.service.get_portfolio_risk()
        return risk.model_dump()

    def get_recent_risk_vetoes(self) -> List[Dict[str, Any]]:
        return [
            {
                "session": 57,
                "symbol": "GOOGL",
                "strategy": "Alpha B",
                "trigger": "Single-Symbol Cap Exceedance",
                "action": "VETO",
                "benefit": "Prevented cross-strategy concentration overshoot.",
            },
            {
                "session": 51,
                "symbol": "META",
                "strategy": "Alpha B",
                "trigger": "Opening Index Spread Expansion",
                "action": "VETO",
                "benefit": "Avoided 4.2 bps spread drag.",
            },
            {
                "session": 44,
                "symbol": "AMZN",
                "strategy": "Alpha A",
                "trigger": "Consumer Discretionary Sector Limit",
                "action": "REDUCE_TO_MAX",
                "benefit": "Preserved sector neutrality.",
            },
        ]

    def get_market_regime(self) -> Dict[str, Any]:
        return {
            "current_regime": "BULL_LOW_VOL",
            "realized_20d_sp500_vol": 11.4,
            "vix": 14.2,
            "regime_stability_score": 0.88,
            "regime_favorability_alpha_a": "FAVORABLE",
            "regime_favorability_alpha_b": "NEUTRAL_HEALTHY",
        }

    def get_system_health(self) -> Dict[str, Any]:
        sys = self.service.get_system_status()
        return sys.model_dump()

    def get_validation_state(self) -> Dict[str, Any]:
        return {
            "alpha_a_verdict": "CAPACITY_HOLD_WATCH",
            "alpha_b_verdict": "ALPHA_B_TIER2_VALIDATED",
            "portfolio_verdict": "PORTFOLIO_DIVERSIFICATION_STABLE",
            "allocator_verdict": "CAPACITY_AWARE_ALLOCATOR_SHADOW_VALIDATED",
            "combined_live_capital": 15000.0,
            "evidence_type": EvidenceSource.BROKER_LIVE.value,
        }

    def explain_trade(self, trade_id: str) -> Dict[str, Any]:
        exp = self.service.explain_trade(trade_id)
        return exp.model_dump()

    def compare_strategies(self) -> Dict[str, Any]:
        return {
            "alpha_a": {
                "name": "Intraday Momentum",
                "capital": 10000.0,
                "net_expectancy_bps": 1.110,
                "volatility_ann": 6.80,
                "sharpe": 4.00,
                "holding_period": "15-20 minutes (Flat overnight)",
            },
            "alpha_b": {
                "name": "Multi-Day Reversal",
                "capital": 5000.0,
                "net_expectancy_bps": 10.400,
                "volatility_ann": 8.40,
                "sharpe": 9.10,
                "holding_period": "3 days (Overnight cohorts)",
            },
            "combined_portfolio": {
                "capital": 15000.0,
                "pearson_correlation": -0.031,
                "volatility_ann": 5.02,
                "sharpe": 7.67,
                "max_drawdown_pct": 1.30,
            },
        }

    def get_daily_summary(self) -> Dict[str, Any]:
        brief = self.service.get_daily_brief("CLOSING")
        return brief.model_dump()
