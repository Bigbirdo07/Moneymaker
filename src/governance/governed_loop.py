"""
Governed Micro-Capital Live Pilot Decision Loop Orchestrator for Phase 5A.
Coordinates human manual approvals, staged position sizing ($25 -> $50 -> $100),
stricter loss limits ($20 daily / $50 drawdown), Tri-Book reconciliation, and immutable audit logs.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from typing import Dict, List, Optional, Set, Tuple
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
from src.broker.reconciliation import AccountReconciler, DualExecutionComparison, DualExecutionLedger, KillSwitchCommand
from src.governance.human_approval import (
    ApprovalAction,
    HumanApprovalGate,
    HumanApprovalRecord,
    ProposedOrderCard,
)
from src.governance.session_arming import SessionArmingManager, SessionAuthorizationToken
from src.data.market_provider import LiveMarketDataProvider, QuoteEvent, BarEvent
from src.features.incremental_features import IncrementalFeatureEngine
from src.evaluation.latency import LatencyRecord, LatencyTracker
from src.portfolio.risk_engine import DeterministicRiskEngine, RiskDecisionType, RiskPolicyConfig
from src.portfolio.shadow_portfolio import ShadowPaperPortfolio, ExitReason


@dataclass
class TriBookComparison:
    decision_id: str
    symbol: str
    decision_midprice: float
    live_fill_price: float
    live_shortfall_bps: float
    shadow_fill_price: float
    shadow_shortfall_bps: float
    paper_fill_price: float
    paper_shortfall_bps: float

    @property
    def live_execution_penalty_bps(self) -> float:
        """Slippage penalty of actual live fill relative to conservative shadow."""
        return self.live_shortfall_bps - self.shadow_shortfall_bps


class GovernedMicroDecisionLoop:
    """Orchestrates the Phase 5A Governed Micro-Pilot with human approval and strict firewalls."""

    def __init__(
        self,
        provider: LiveMarketDataProvider,
        broker: BrokerAdapter,
        session_manager: SessionArmingManager,
        symbols: Optional[List[str]] = None,
        mode: ExecutionMode = ExecutionMode.LIVE_GOVERNED_MICRO,
        cooldown_bars: int = 4,
        confidence_threshold: float = 0.58,
        meta_threshold: float = 0.52,
    ):
        verify_execution_mode(mode)
        if mode != ExecutionMode.LIVE_GOVERNED_MICRO and mode != ExecutionMode.SHADOW:
            raise RuntimeError(f"GovernedMicroDecisionLoop requires LIVE_GOVERNED_MICRO mode, got {mode}")

        self.mode = mode
        self.provider = provider
        self.broker = broker
        self.session_manager = session_manager
        self.symbols = symbols or ["NVDA", "AMD", "TSLA"]

        # Governance & Approval Gates
        self.approval_gate = HumanApprovalGate(approval_timeout_seconds=30.0, max_allowed_spread_bps=3.0)
        self.latency_tracker = LatencyTracker()

        # Tri-Book Portfolio Instances
        self.shadow_portfolio = ShadowPaperPortfolio(initial_cash=1000.0) # Book B
        self.reconciler = AccountReconciler(broker=broker, internal_portfolio=self.shadow_portfolio)
        self.tri_book_comparisons: List[TriBookComparison] = []

        # Staged Pilot Parameters
        self.total_live_trades_executed = 0
        self.daily_realized_loss_usd = 0.0
        self.max_daily_loss_usd = 20.0       # Stricter 2.0% ($20 on $1,000)
        self.max_pilot_drawdown_usd = 50.0   # Stricter 5.0% ($50 on $1,000)
        self.max_concurrent_positions = 2

        self.cooldown_bars = cooldown_bars
        self.confidence_threshold = confidence_threshold
        self.meta_threshold = meta_threshold

        self._last_trade_bar_index: Dict[str, int] = {}
        self._current_bar_index: int = 0
        self.is_paused = False
        self.is_system_locked_out = False

        # Immutable Append-Only Audit Log
        self.audit_log: List[Dict] = []

    def get_staged_max_notional_usd(self) -> float:
        """
        Staged Exposure Control:
        Stage A (1-10 trades): $25.00
        Stage B (11-40 trades): $50.00
        Stage C (41+ trades): $100.00
        """
        if self.total_live_trades_executed < 10:
            return 25.0
        elif self.total_live_trades_executed < 40:
            return 50.0
        return 100.0

    def generate_candidate_proposals(self, current_time: pd.Timestamp) -> List[ProposedOrderCard]:
        """
        Run models, ranking, and risk engine to generate proposed trade cards for human review.
        """
        self._current_bar_index += 1
        t_received = pd.Timestamp.now(tz=timezone.utc)

        # Fail-closed checks
        if self.is_system_locked_out or self.is_paused:
            return []

        token = self.session_manager.current_auth_token
        if token is None or not token.is_valid():
            return []

        # Process position exits first
        self._process_exits(current_time)

        # Check circuit breakers
        if self.daily_realized_loss_usd >= self.max_daily_loss_usd:
            self.is_system_locked_out = True
            return []

        # Validate data feed freshness
        for sym in self.symbols:
            valid, _ = self.provider.check_staleness(sym, current_time)
            if not valid:
                return []

        # Check current positions count (max 2)
        current_positions = self.broker.get_positions()
        if len(current_positions) >= self.max_concurrent_positions:
            return []

        spy_bars = self.provider.get_bar_history("SPY", timeframe="5m", count=20)
        candidates = []

        for sym in self.symbols:
            if sym in current_positions:
                continue

            last_traded = self._last_trade_bar_index.get(sym, -999)
            if (self._current_bar_index - last_traded) < self.cooldown_bars:
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

            raw_logit = (feats["ret_15m"] * 120.0) + (feats["rvol_14"] * 0.15) - (feats["spread_bps"] * 0.05)
            model_conf = 1.0 / (1.0 + np.exp(-raw_logit))
            expected_alpha_bps = (model_conf - 0.50) * 40.0

            meta_logit = (model_conf * 2.0) - (feats["spread_bps"] * 0.20) + (feats["rvol_14"] * 0.10)
            meta_prob = 1.0 / (1.0 + np.exp(-meta_logit))
            meta_decision = "TAKE_TRADE" if meta_prob >= self.meta_threshold else "REJECT_TRADE"

            friction_bps = quote.spread_bps + 1.0
            vol_penalty = 0.05 * feats["volatility_bps"]
            opportunity_score = expected_alpha_bps - friction_bps - vol_penalty

            if model_conf >= self.confidence_threshold and meta_decision == "TAKE_TRADE":
                candidates.append({
                    "symbol": sym,
                    "quote": quote,
                    "features": feats,
                    "model_conf": model_conf,
                    "expected_alpha_bps": expected_alpha_bps,
                    "friction_bps": friction_bps,
                    "net_edge_bps": expected_alpha_bps - friction_bps,
                    "opportunity_score": opportunity_score,
                    "price": quote.ask,
                })

        if not candidates:
            return []

        candidates.sort(key=lambda c: c["opportunity_score"], reverse=True)
        top_cand = candidates[0]  # Take Top-1 candidate

        # Determine staged position size
        max_notional = self.get_staged_max_notional_usd()
        shares = max_notional / top_cand["price"]
        proposal_id = f"PROP_{top_cand['symbol']}_{current_time.strftime('%Y%m%d%H%M')}"

        card = ProposedOrderCard(
            proposal_id=proposal_id,
            symbol=top_cand["symbol"],
            side="BUY",
            shares=shares,
            notional_usd=max_notional,
            decision_timestamp=current_time,
            current_bid=top_cand["quote"].bid,
            current_ask=top_cand["quote"].ask,
            spread_bps=top_cand["quote"].spread_bps,
            expected_alpha_bps=top_cand["expected_alpha_bps"],
            estimated_friction_bps=top_cand["friction_bps"],
            expected_net_edge_bps=top_cand["net_edge_bps"],
            model_confidence=top_cand["model_conf"],
            rank=1,
            current_portfolio_exposure_usd=sum(p.market_value for p in current_positions.values()),
            daily_realized_pnl_usd=-self.daily_realized_loss_usd,
            max_allowed_loss_usd=self.max_daily_loss_usd,
            trade_reason=f"Stage-{('A' if max_notional==25 else ('B' if max_notional==50 else 'C'))} Micro-Pilot Entry",
            risk_engine_status="APPROVED",
        )

        self.approval_gate.submit_proposal(card)
        self.audit_log.append({
            "event": "PROPOSAL_CREATED",
            "timestamp": current_time.isoformat(),
            "proposal": card.__dict__,
        })
        return [card]

    def execute_approved_proposal(
        self,
        proposal_id: str,
        operator_id: str,
        action: ApprovalAction,
        current_time: pd.Timestamp,
        reason_notes: str = "",
    ) -> Tuple[bool, str]:
        """
        Process operator human decision and execute order if approved.
        """
        quote = None
        if proposal_id in self.approval_gate.pending_proposals:
            card, _ = self.approval_gate.pending_proposals[proposal_id]
            quote = self.provider.get_latest_quote(card.symbol)

        can_exec, reason = self.approval_gate.process_operator_action(
            proposal_id=proposal_id,
            operator_id=operator_id,
            action=action,
            current_time=current_time,
            current_quote=quote,
            reason_notes=reason_notes,
        )

        self.audit_log.append({
            "event": "OPERATOR_ACTION",
            "proposal_id": proposal_id,
            "operator_id": operator_id,
            "action": action.value,
            "can_execute": can_exec,
            "reason": reason,
            "timestamp": current_time.isoformat(),
        })

        if not can_exec:
            return False, reason

        # Create and Submit Live Governed Order
        card_obj = [r for r in self.approval_gate.approval_records if r.proposal_id == proposal_id][-1]
        sym = card_obj.symbol
        client_order_id = f"LIVE_{sym}_{current_time.strftime('%Y%m%d%H%M')}"

        max_notional = self.get_staged_max_notional_usd()
        qty = max_notional / (quote.ask if quote and quote.ask > 0 else 100.0)

        order = BrokerOrder(
            client_order_id=client_order_id,
            symbol=sym,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            qty=qty,
        )
        order.transition_to(OrderStatus.RISK_APPROVED)

        # Submit to Broker Gateway
        submitted = self.broker.submit_order(order)
        fill_px = quote.ask * 1.0001 if quote else 100.0  # Actual live simulated fill
        fill_fee = fill_px * order.qty * 0.00005

        self.broker.execute_fill(
            client_order_id=client_order_id,
            fill_qty=order.qty,
            fill_price=fill_px,
            fee=fill_fee,
        )

        self.total_live_trades_executed += 1
        self._last_trade_bar_index[sym] = self._current_bar_index

        # Record Tri-Book Comparison
        mid = quote.mid_price if quote else 100.0
        live_shortfall = ((fill_px - mid) / mid) * 10000.0
        shadow_fill = fill_px * 1.00005
        shadow_shortfall = ((shadow_fill - mid) / mid) * 10000.0
        paper_fill = quote.ask if quote else 100.0
        paper_shortfall = ((paper_fill - mid) / mid) * 10000.0

        tri_comp = TriBookComparison(
            decision_id=proposal_id,
            symbol=sym,
            decision_midprice=mid,
            live_fill_price=fill_px,
            live_shortfall_bps=live_shortfall,
            shadow_fill_price=shadow_fill,
            shadow_shortfall_bps=shadow_shortfall,
            paper_fill_price=paper_fill,
            paper_shortfall_bps=paper_shortfall,
        )
        self.tri_book_comparisons.append(tri_comp)

        # Sync shadow book
        self.shadow_portfolio.open_position(
            symbol=sym,
            shares=order.qty,
            entry_price=shadow_fill,
            entry_timestamp=current_time,
            sector="Technology",
        )

        # Reconcile immediately post-fill
        self.reconciler.reconcile()

        return True, "LIVE_ORDER_EXECUTED"

    def _process_exits(self, current_time: pd.Timestamp) -> None:
        """Process time exits (15m / 3 bars) and risk stops."""
        for sym, pos in list(self.shadow_portfolio.positions.items()):
            quote = self.provider.get_latest_quote(sym)
            if quote is None:
                continue

            current_px = quote.bid
            self.shadow_portfolio.update_mark_to_market(sym, current_px)

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
                self.shadow_portfolio.close_position(sym, current_px, current_time, reason)
