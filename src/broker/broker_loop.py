"""
Broker Paper Decision Loop Orchestrator for Phase 3B.
Executes the frozen champion strategy against a paper broker environment with dual execution tracking,
strict idempotency, automatic reconciliation, and hard kill switch controls.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
import numpy as np
import pandas as pd

from src.broker.adapter import (
    BrokerAdapter,
    BrokerOrder,
    ExecutionMode,
    OrderStatus,
    OrderSide,
    OrderType,
    OrderTimestamps,
    verify_execution_mode,
)
from src.broker.reconciliation import (
    AccountReconciler,
    DualExecutionComparison,
    DualExecutionLedger,
    KillSwitchCommand,
)
from src.data.market_provider import LiveMarketDataProvider, QuoteEvent, BarEvent
from src.features.incremental_features import IncrementalFeatureEngine
from src.evaluation.latency import LatencyRecord, LatencyTracker
from src.evaluation.model_health import ModelHealthMonitor, ModelHealthState
from src.portfolio.risk_engine import DeterministicRiskEngine, RiskDecisionType
from src.portfolio.shadow_portfolio import ShadowPaperPortfolio, ExitReason


class BrokerPaperDecisionLoop:
    """Orchestrates real-time broker paper execution, dual books, and safety monitoring."""

    def __init__(
        self,
        provider: LiveMarketDataProvider,
        broker: BrokerAdapter,
        symbols: List[str],
        mode: ExecutionMode = ExecutionMode.BROKER_PAPER,
        cooldown_bars: int = 4,
        top_k: int = 3,
        confidence_threshold: float = 0.58,
        meta_threshold: float = 0.52,
    ):
        # 1. Fatal Safety Verification
        verify_execution_mode(mode)
        self.mode = mode

        # 2. Verify Broker Paper Environment
        if not broker.verify_paper_environment():
            raise RuntimeError("CRITICAL: Broker adapter is NOT in verified PAPER mode. Aborting initialization.")

        self.provider = provider
        self.broker = broker
        self.symbols = symbols

        # Internal Shadow Book & Reconciler
        self.internal_portfolio = ShadowPaperPortfolio(initial_cash=1000.0)
        self.reconciler = AccountReconciler(broker=broker, internal_portfolio=self.internal_portfolio)
        self.dual_ledger = DualExecutionLedger()
        self.risk_engine = DeterministicRiskEngine()
        self.latency_tracker = LatencyTracker()
        self.health_monitor = ModelHealthMonitor()

        self.cooldown_bars = cooldown_bars
        self.top_k = top_k
        self.confidence_threshold = confidence_threshold
        self.meta_threshold = meta_threshold

        self._last_trade_bar_index: Dict[str, int] = {}
        self._current_bar_index: int = 0
        self._submitted_client_order_ids: Set[str] = set()
        self._disabled_symbols: Set[str] = set()
        self.is_paused = False
        self.is_system_locked_out = False

    def execute_kill_switch(self, command: KillSwitchCommand, symbol: Optional[str] = None) -> str:
        """Execute hard kill switch safety directives."""
        if command == KillSwitchCommand.PAUSE_NEW_ORDERS:
            self.is_paused = True
            return "PAUSED_NEW_ORDERS"
        elif command == KillSwitchCommand.RESUME_NEW_ORDERS:
            self.is_paused = False
            return "RESUMED_NEW_ORDERS"
        elif command == KillSwitchCommand.CANCEL_ALL_OPEN_ORDERS:
            open_orders = self.broker.get_open_orders()
            for o in open_orders:
                self.broker.cancel_order(o.client_order_id)
            return f"CANCELLED_{len(open_orders)}_OPEN_ORDERS"
        elif command == KillSwitchCommand.CLOSE_ALL_POSITIONS:
            closed = self.broker.close_all_positions()
            for c in closed:
                if c.symbol in self.internal_portfolio.positions:
                    self.internal_portfolio.close_position(
                        c.symbol, c.avg_fill_price, pd.Timestamp.now(tz=timezone.utc), ExitReason.EOD_LIQUIDATION
                    )
            return f"CLOSED_{len(closed)}_POSITIONS"
        elif command == KillSwitchCommand.DISABLE_SYMBOL and symbol:
            self._disabled_symbols.add(symbol)
            return f"DISABLED_SYMBOL_{symbol}"
        elif command == KillSwitchCommand.ENABLE_SYMBOL and symbol:
            self._disabled_symbols.discard(symbol)
            return f"ENABLED_SYMBOL_{symbol}"
        elif command == KillSwitchCommand.FULL_SYSTEM_LOCKOUT:
            self.is_system_locked_out = True
            self.is_paused = True
            self.broker.close_all_positions()
            return "FULL_SYSTEM_LOCKOUT_EXECUTED"
        return "UNKNOWN_COMMAND"

    def step(self, current_time: pd.Timestamp) -> Dict[str, any]:
        """
        Execute a single decision cycle under broker paper execution rules.
        """
        self._current_bar_index += 1
        t_received = pd.Timestamp.now(tz=timezone.utc)

        # 1. Fail-closed safety checks
        if self.is_system_locked_out or self.is_paused:
            return {"status": "PAUSED_OR_LOCKED_OUT", "orders_submitted": 0}

        if not self.broker.is_connected() or not self.provider.is_connected():
            return {"status": "FAIL_CLOSED_DISCONNECTED", "orders_submitted": 0}

        # Validate market data freshness
        feed_valid = True
        for sym in self.symbols:
            valid, reason = self.provider.check_staleness(sym, current_time)
            if not valid:
                feed_valid = False
                break

        if not feed_valid:
            return {"status": "FEED_STALE_NO_TRADES", "orders_submitted": 0}

        # 2. Check Reconciliation Status
        is_clean, recon_errors = self.reconciler.reconcile()
        if not is_clean:
            return {"status": "RECONCILIATION_ERROR_FROZEN", "errors": len(recon_errors)}

        # 3. Process Position Exits First
        self._process_exits(current_time)

        # 4. Generate Incremental Features & Scores
        spy_bars = self.provider.get_bar_history("SPY", timeframe="5m", count=20)
        candidates = []
        t_feat_start = pd.Timestamp.now(tz=timezone.utc)

        for sym in self.symbols:
            if sym in self._disabled_symbols:
                continue

            quote = self.provider.get_latest_quote(sym)
            bar_history = self.provider.get_bar_history(sym, timeframe="5m", count=20)
            if quote is None or len(bar_history) < 14:
                continue

            feats = IncrementalFeatureEngine.compute_features(
                symbol_bars=bar_history,
                current_quote=quote,
                market_benchmark_bars=spy_bars,
            )

            # Frozen Champion Momentum Model
            raw_logit = (feats["ret_15m"] * 120.0) + (feats["rvol_14"] * 0.15) - (feats["spread_bps"] * 0.05)
            model_conf = 1.0 / (1.0 + np.exp(-raw_logit))
            expected_alpha_bps = (model_conf - 0.50) * 40.0

            # Meta-Labeling Filter
            meta_logit = (model_conf * 2.0) - (feats["spread_bps"] * 0.20) + (feats["rvol_14"] * 0.10)
            meta_prob = 1.0 / (1.0 + np.exp(-meta_logit))
            meta_decision = "TAKE_TRADE" if meta_prob >= self.meta_threshold else "REJECT_TRADE"

            # Opportunity Score
            friction_bps = quote.spread_bps + 1.0
            vol_penalty = 0.05 * feats["volatility_bps"]
            opportunity_score = expected_alpha_bps - friction_bps - vol_penalty

            candidates.append({
                "symbol": sym,
                "quote": quote,
                "bars": bar_history,
                "features": feats,
                "model_conf": model_conf,
                "expected_alpha_bps": expected_alpha_bps,
                "meta_decision": meta_decision,
                "opportunity_score": opportunity_score,
                "price": quote.ask,
            })

        t_model_end = pd.Timestamp.now(tz=timezone.utc)

        if not candidates:
            return {"status": "NO_CANDIDATES", "orders_submitted": 0}

        # 5. Cross-Sectional Ranking
        candidates.sort(key=lambda c: c["opportunity_score"], reverse=True)
        t_ranking = pd.Timestamp.now(tz=timezone.utc)

        # 6. Candidate Selection & Submission
        orders_submitted = 0
        for rank_idx, cand in enumerate(candidates, start=1):
            sym = cand["symbol"]
            client_order_id = f"ORD_{sym}_{current_time.strftime('%Y%m%d%H%M')}"
            decision_id = f"DEC_{sym}_{current_time.strftime('%Y%m%d%H%M')}"

            # Idempotency Protection
            if client_order_id in self._submitted_client_order_ids:
                continue

            last_traded = self._last_trade_bar_index.get(sym, -999)
            cooldown_active = (self._current_bar_index - last_traded) < self.cooldown_bars

            is_top_k = (rank_idx <= self.top_k)
            passes_conf = (cand["model_conf"] >= self.confidence_threshold)
            passes_meta = (cand["meta_decision"] == "TAKE_TRADE")

            if not is_top_k or not passes_conf or not passes_meta or cooldown_active:
                continue

            # Evaluate Risk Engine
            broker_acc = self.broker.get_account()
            broker_pos = self.broker.get_positions()
            open_pos_dict = {
                p_sym: {"shares": p.qty, "notional": p.market_value, "sector": "Technology"}
                for p_sym, p in broker_pos.items()
            }

            risk_eval = self.risk_engine.evaluate_order(
                symbol=sym,
                price=cand["price"],
                shares=100.0 / cand["price"],
                sector="Technology",
                current_equity=broker_acc.portfolio_value,
                available_cash=broker_acc.cash,
                current_daily_pnl=self.internal_portfolio.daily_pnl,
                current_drawdown_pct=self.internal_portfolio.current_drawdown_pct,
                open_positions=open_pos_dict,
            )

            if risk_eval.decision == RiskDecisionType.REJECT:
                continue

            # Create and Submit Broker Order
            t_submit = pd.Timestamp.now(tz=timezone.utc)
            broker_order = BrokerOrder(
                client_order_id=client_order_id,
                symbol=sym,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                qty=risk_eval.approved_shares,
                signal_id=f"SIG_{sym}_{current_time.strftime('%Y%m%d%H%M')}",
                decision_id=decision_id,
                timestamps=OrderTimestamps(
                    decision_created=t_received,
                    risk_approved=t_submit,
                ),
            )
            broker_order.transition_to(OrderStatus.RISK_APPROVED)

            # Submit to Broker Gateway
            try:
                submitted = self.broker.submit_order(broker_order)
                self._submitted_client_order_ids.add(client_order_id)
                self._last_trade_bar_index[sym] = self._current_bar_index
                orders_submitted += 1

                # Execute Simulated Paper Fill
                fill_price = cand["quote"].ask * 1.00005  # Slight paper spread
                fee = fill_price * risk_eval.approved_shares * 0.00005
                self.broker.execute_fill(
                    client_order_id=client_order_id,
                    fill_qty=risk_eval.approved_shares,
                    fill_price=fill_price,
                    fee=fee,
                )

                # Update Internal Shadow Book
                self.internal_portfolio.open_position(
                    symbol=sym,
                    shares=risk_eval.approved_shares,
                    entry_price=fill_price,
                    entry_timestamp=current_time,
                    sector="Technology",
                )

                # Record Dual Book Comparison
                mid = cand["quote"].mid_price
                paper_shortfall = ((fill_price - mid) / mid) * 10000.0
                shadow_fill = fill_price * 1.00005  # Realistic conservative slippage
                shadow_shortfall = ((shadow_fill - mid) / mid) * 10000.0

                self.dual_ledger.record_dual_execution(
                    DualExecutionComparison(
                        decision_id=decision_id,
                        symbol=sym,
                        side="BUY",
                        decision_midprice=mid,
                        quote_bid=cand["quote"].bid,
                        quote_ask=cand["quote"].ask,
                        spread_bps=cand["quote"].spread_bps,
                        broker_fill_price=fill_price,
                        broker_fill_ts=pd.Timestamp.now(tz=timezone.utc),
                        broker_slippage_bps=0.5,
                        broker_shortfall_bps=paper_shortfall,
                        shadow_fill_price=shadow_fill,
                        shadow_fill_ts=pd.Timestamp.now(tz=timezone.utc),
                        shadow_slippage_bps=1.0,
                        shadow_shortfall_bps=shadow_shortfall,
                    )
                )

                # Record Latency
                self.latency_tracker.record(
                    LatencyRecord(
                        decision_id=decision_id,
                        symbol=sym,
                        exchange_timestamp=cand["quote"].exchange_timestamp,
                        provider_timestamp=cand["quote"].provider_timestamp,
                        received_timestamp=t_received,
                        feature_ready_timestamp=t_feat_start,
                        model_start_timestamp=t_feat_start,
                        model_end_timestamp=t_model_end,
                        ranking_timestamp=t_ranking,
                        decision_timestamp=t_submit,
                        hypothetical_fill_timestamp=pd.Timestamp.now(tz=timezone.utc),
                    )
                )

            except Exception as e:
                # Catch broker error and record
                broker_order.transition_to(OrderStatus.ERROR, reason=str(e))

        # Reconcile after submissions
        self.reconciler.reconcile()

        return {
            "status": "COMPLETED",
            "orders_submitted": orders_submitted,
            "broker_equity": self.broker.get_account().portfolio_value,
            "internal_equity": self.internal_portfolio.total_equity,
        }

    def _process_exits(self, current_time: pd.Timestamp) -> None:
        """Process time exits (15m / 3 bars) and risk stops."""
        for sym, pos in list(self.internal_portfolio.positions.items()):
            quote = self.provider.get_latest_quote(sym)
            if quote is None:
                continue

            current_px = quote.bid
            self.internal_portfolio.update_mark_to_market(sym, current_px)

            should_exit = False
            reason = ExitReason.TIME_EXIT

            if current_px <= pos.stop_loss_price:
                should_exit = True
                reason = ExitReason.STOP_LOSS
            elif current_px >= pos.take_profit_price:
                should_exit = True
                reason = ExitReason.TAKE_PROFIT
            elif pos.bars_held >= pos.target_exit_bars:
                should_exit = True
                reason = ExitReason.TIME_EXIT

            if should_exit:
                self.broker.close_position(sym)
                self.internal_portfolio.close_position(sym, current_px, current_time, reason)
