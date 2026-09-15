"""
Human-in-the-Loop Manual Order Approval Gate for Phase 5A/5B Governed Micro-Pilot.
Enforces mandatory operator review, comprehensive and blinded trade card display, 30-second expiration timeouts,
pre-submission stale data validation, latency cost attribution, operator fatigue metrics, and human-alpha decomposition.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
from typing import Dict, List, Optional, Tuple, Set
import numpy as np
import pandas as pd

from src.data.market_provider import QuoteEvent


class ApprovalAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "HUMAN_DISCRETIONARY_REJECT"
    HUMAN_DISCRETIONARY_REJECT = "HUMAN_DISCRETIONARY_REJECT"
    SYSTEM_SAFETY_REJECT = "SYSTEM_SAFETY_REJECT"
    EXPIRED_TIMEOUT = "EXPIRED_TIMEOUT"
    STALE_DATA_CANCELLED = "STALE_DATA_CANCELLED"


class OperatorReasonCode(str, Enum):
    EXTENDED_MOVE = "EXTENDED_MOVE"
    BAD_MARKET_CONTEXT = "BAD_MARKET_CONTEXT"
    LOW_LIQUIDITY = "LOW_LIQUIDITY"
    EVENT_RISK = "EVENT_RISK"
    UNUSUAL_PRICE_ACTION = "UNUSUAL_PRICE_ACTION"
    NO_CONFIDENCE = "NO_CONFIDENCE"
    OTHER = "OTHER"
    NONE = "NONE"


class ApprovalDisplayMode(str, Enum):
    FULL_INFORMATION = "FULL_INFORMATION"
    SAFETY_ONLY = "SAFETY_ONLY"


@dataclass
class ProposedOrderCard:
    """Comprehensive trade proposal card displayed for human operator review."""
    proposal_id: str
    symbol: str
    side: str  # "BUY"
    shares: float
    notional_usd: float
    decision_timestamp: pd.Timestamp
    current_bid: float
    current_ask: float
    spread_bps: float
    expected_alpha_bps: float
    estimated_friction_bps: float
    expected_net_edge_bps: float
    model_confidence: float
    rank: int
    current_portfolio_exposure_usd: float
    daily_realized_pnl_usd: float
    max_allowed_loss_usd: float
    trade_reason: str
    risk_engine_status: str  # "APPROVED", "RESIZED"
    display_mode: ApprovalDisplayMode = ApprovalDisplayMode.FULL_INFORMATION

    def render_display(self) -> str:
        """Render formatted operator terminal display based on display mode."""
        if self.display_mode == ApprovalDisplayMode.SAFETY_ONLY:
            return (
                f"\n=======================================================\n"
                f"   LIVE GOVERNED ORDER PROPOSAL (SAFETY-ONLY MODE)     \n"
                f"=======================================================\n"
                f"Proposal ID:        {self.proposal_id}\n"
                f"Symbol:             {self.symbol} | Side: {self.side}\n"
                f"Quantity:           {self.shares:.4f} shares (${self.notional_usd:.2f} notional)\n"
                f"Decision Time:      {self.decision_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
                f"Market Bid / Ask:   ${self.current_bid:.2f} / ${self.current_ask:.2f} (Spread: {self.spread_bps:.1f} bps)\n"
                f"Portfolio Exposure: ${self.current_portfolio_exposure_usd:.2f} | Daily PnL: ${self.daily_realized_pnl_usd:+.2f}\n"
                f"Max Loss Budget:    ${self.max_allowed_loss_usd:.2f}\n"
                f"Risk Engine Status: {self.risk_engine_status} ({self.trade_reason})\n"
                f"[PREDICTIVE ALPHA / CONFIDENCE / RANK HIDDEN FOR BLINDED EVALUATION]\n"
                f"=======================================================\n"
            )

        return (
            f"\n=======================================================\n"
            f"          LIVE GOVERNED MICRO ORDER PROPOSAL           \n"
            f"=======================================================\n"
            f"Proposal ID:        {self.proposal_id}\n"
            f"Symbol:             {self.symbol} | Side: {self.side}\n"
            f"Quantity:           {self.shares:.4f} shares (${self.notional_usd:.2f} notional)\n"
            f"Decision Time:      {self.decision_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"Market Bid / Ask:   ${self.current_bid:.2f} / ${self.current_ask:.2f} (Spread: {self.spread_bps:.1f} bps)\n"
            f"Expected Alpha:     +{self.expected_alpha_bps:.1f} bps | Est. Friction: {self.estimated_friction_bps:.1f} bps\n"
            f"Expected Net Edge:  +{self.expected_net_edge_bps:.1f} bps | Confidence: {self.model_confidence*100:.1f}%\n"
            f"Universe Rank:      Top-{self.rank} Opportunity\n"
            f"Portfolio Exposure: ${self.current_portfolio_exposure_usd:.2f} | Daily PnL: ${self.daily_realized_pnl_usd:+.2f}\n"
            f"Max Loss Budget:    ${self.max_allowed_loss_usd:.2f}\n"
            f"Risk Engine Status: {self.risk_engine_status} ({self.trade_reason})\n"
            f"=======================================================\n"
        )


@dataclass
class HumanApprovalRecord:
    proposal_id: str
    symbol: str
    operator_id: str
    action: ApprovalAction
    display_mode: ApprovalDisplayMode
    decision_timestamp: pd.Timestamp
    operator_action_timestamp: pd.Timestamp
    operator_latency_sec: float
    decision_midprice: float
    approval_midprice: float
    human_latency_cost_bps: float
    reason_code: OperatorReasonCode = OperatorReasonCode.NONE
    reason_notes: str = ""
    future_15m_return_bps: Optional[float] = None
    review_sequence_index: int = 1
    hour_of_day_utc: int = 14


class HumanApprovalGate:
    """Manages order proposal queue, operator approvals, expiration, latency costs, and bias audits."""

    def __init__(
        self,
        approval_timeout_seconds: float = 30.0,
        max_allowed_spread_bps: float = 3.0,
        blinded_experiment_ratio: float = 0.50,
    ):
        self.approval_timeout_sec = approval_timeout_seconds
        self.max_allowed_spread_bps = max_allowed_spread_bps
        self.blinded_experiment_ratio = blinded_experiment_ratio
        self.pending_proposals: Dict[str, Tuple[ProposedOrderCard, pd.Timestamp]] = {}
        self.approval_records: List[HumanApprovalRecord] = []
        self._daily_review_count: int = 0

    def assign_display_mode(self, proposal_id: str) -> ApprovalDisplayMode:
        """Deterministic pseudo-random assignment of display condition."""
        h = int(hashlib.sha256(proposal_id.encode()).hexdigest(), 16)
        if (h % 100) < int(self.blinded_experiment_ratio * 100):
            return ApprovalDisplayMode.SAFETY_ONLY
        return ApprovalDisplayMode.FULL_INFORMATION

    def submit_proposal(self, card: ProposedOrderCard) -> None:
        now = pd.Timestamp.now(tz=timezone.utc)
        card.display_mode = self.assign_display_mode(card.proposal_id)
        self.pending_proposals[card.proposal_id] = (card, now)

    def process_operator_action(
        self,
        proposal_id: str,
        operator_id: str,
        action: ApprovalAction,
        current_time: pd.Timestamp,
        current_quote: Optional[QuoteEvent] = None,
        reason_code: OperatorReasonCode = OperatorReasonCode.NONE,
        reason_notes: str = "",
    ) -> Tuple[bool, str]:
        """
        Process human review action with expiration, pre-submit staleness verification,
        and latency cost calculation.
        """
        if proposal_id not in self.pending_proposals:
            return False, "PROPOSAL_NOT_FOUND"

        self._daily_review_count += 1
        card, submit_time = self.pending_proposals.pop(proposal_id)
        latency_sec = (current_time - card.decision_timestamp).total_seconds()
        decision_mid = (card.current_bid + card.current_ask) / 2.0
        current_mid = current_quote.mid_price if current_quote else decision_mid

        # Latency cost: adverse price movement against the trade during human deliberation
        # For BUY: (current_mid - decision_mid) / decision_mid * 10,000 bps
        latency_cost_bps = ((current_mid - decision_mid) / decision_mid) * 10000.0 if decision_mid > 0 else 0.0

        # 1. Expiration Timeout Check
        if latency_sec > self.approval_timeout_sec:
            record = HumanApprovalRecord(
                proposal_id=proposal_id,
                symbol=card.symbol,
                operator_id=operator_id,
                action=ApprovalAction.EXPIRED_TIMEOUT,
                display_mode=card.display_mode,
                decision_timestamp=card.decision_timestamp,
                operator_action_timestamp=current_time,
                operator_latency_sec=latency_sec,
                decision_midprice=decision_mid,
                approval_midprice=current_mid,
                human_latency_cost_bps=latency_cost_bps,
                reason_code=OperatorReasonCode.NONE,
                reason_notes=f"Approval expired: latency {latency_sec:.1f}s > {self.approval_timeout_sec}s",
                review_sequence_index=self._daily_review_count,
                hour_of_day_utc=current_time.hour,
            )
            self.approval_records.append(record)
            return False, f"EXPIRED_TIMEOUT_{latency_sec:.1f}s"

        # 2. Operator Discretionary Rejection
        if action in (ApprovalAction.HUMAN_DISCRETIONARY_REJECT,):
            record = HumanApprovalRecord(
                proposal_id=proposal_id,
                symbol=card.symbol,
                operator_id=operator_id,
                action=ApprovalAction.HUMAN_DISCRETIONARY_REJECT,
                display_mode=card.display_mode,
                decision_timestamp=card.decision_timestamp,
                operator_action_timestamp=current_time,
                operator_latency_sec=latency_sec,
                decision_midprice=decision_mid,
                approval_midprice=current_mid,
                human_latency_cost_bps=latency_cost_bps,
                reason_code=reason_code,
                reason_notes=reason_notes or reason_code.value,
                review_sequence_index=self._daily_review_count,
                hour_of_day_utc=current_time.hour,
            )
            self.approval_records.append(record)
            rej_reason = f"HUMAN_DISCRETIONARY_REJECTED_{reason_code.value}" if reason_code != OperatorReasonCode.NONE else "OPERATOR_REJECTED"
            return False, rej_reason

        # 3. Pre-Submission Stale Signal Re-Verification
        if current_quote is not None:
            quote_age_sec = (current_time - current_quote.received_timestamp).total_seconds()
            if quote_age_sec > 15.0 or current_quote.spread_bps > self.max_allowed_spread_bps:
                record = HumanApprovalRecord(
                    proposal_id=proposal_id,
                    symbol=card.symbol,
                    operator_id=operator_id,
                    action=ApprovalAction.STALE_DATA_CANCELLED,
                    display_mode=card.display_mode,
                    decision_timestamp=card.decision_timestamp,
                    operator_action_timestamp=current_time,
                    operator_latency_sec=latency_sec,
                    decision_midprice=decision_mid,
                    approval_midprice=current_mid,
                    human_latency_cost_bps=latency_cost_bps,
                    reason_code=OperatorReasonCode.UNUSUAL_PRICE_ACTION,
                    reason_notes=f"Stale quote ({quote_age_sec:.1f}s) or spread expansion ({current_quote.spread_bps:.1f}bps)",
                    review_sequence_index=self._daily_review_count,
                    hour_of_day_utc=current_time.hour,
                )
                self.approval_records.append(record)
                return False, "STALE_DATA_PRE_SUBMIT_CANCELLED"

        # 4. Successful Approval
        record = HumanApprovalRecord(
            proposal_id=proposal_id,
            symbol=card.symbol,
            operator_id=operator_id,
            action=ApprovalAction.APPROVE,
            display_mode=card.display_mode,
            decision_timestamp=card.decision_timestamp,
            operator_action_timestamp=current_time,
            operator_latency_sec=latency_sec,
            decision_midprice=decision_mid,
            approval_midprice=current_mid,
            human_latency_cost_bps=latency_cost_bps,
            reason_code=OperatorReasonCode.NONE,
            reason_notes=reason_notes,
            review_sequence_index=self._daily_review_count,
            hour_of_day_utc=current_time.hour,
        )
        self.approval_records.append(record)
        return True, "APPROVED_FOR_EXECUTION"

    def compute_human_alpha_decomposition(self) -> Dict[str, any]:
        """
        Decompose observed edge between model-eligible, approved, rejected, blinded, and full info subsets.
        """
        if not self.approval_records:
            return {"total_proposals": 0}

        approved = [r for r in self.approval_records if r.action == ApprovalAction.APPROVE]
        rejected_disc = [r for r in self.approval_records if r.action == ApprovalAction.HUMAN_DISCRETIONARY_REJECT]
        expired = [r for r in self.approval_records if r.action == ApprovalAction.EXPIRED_TIMEOUT]
        safety_rej = [r for r in self.approval_records if r.action in (ApprovalAction.STALE_DATA_CANCELLED, ApprovalAction.SYSTEM_SAFETY_REJECT)]

        full_info_app = [r for r in approved if r.display_mode == ApprovalDisplayMode.FULL_INFORMATION]
        safety_only_app = [r for r in approved if r.display_mode == ApprovalDisplayMode.SAFETY_ONLY]

        app_rets = [r.future_15m_return_bps for r in approved if r.future_15m_return_bps is not None]
        rej_rets = [r.future_15m_return_bps for r in rejected_disc if r.future_15m_return_bps is not None]
        all_rets = [r.future_15m_return_bps for r in self.approval_records if r.future_15m_return_bps is not None]

        full_rets = [r.future_15m_return_bps for r in full_info_app if r.future_15m_return_bps is not None]
        blind_rets = [r.future_15m_return_bps for r in safety_only_app if r.future_15m_return_bps is not None]

        latencies = [r.operator_latency_sec for r in self.approval_records]
        lat_costs = [r.human_latency_cost_bps for r in approved]

        mean_app = float(np.mean(app_rets)) if app_rets else 0.0
        mean_all = float(np.mean(all_rets)) if all_rets else 0.0
        human_inc_alpha = mean_app - mean_all

        return {
            "total_proposals": len(self.approval_records),
            "approved_count": len(approved),
            "discretionary_rejected_count": len(rejected_disc),
            "safety_rejected_count": len(safety_rej),
            "expired_timeout_count": len(expired),
            "full_info_approved_count": len(full_info_app),
            "safety_only_approved_count": len(safety_only_app),
            "approval_rate_pct": (len(approved) / len(self.approval_records)) * 100.0,
            "mean_operator_latency_sec": float(np.mean(latencies)) if latencies else 0.0,
            "latency_p50_sec": float(np.percentile(latencies, 50)) if latencies else 0.0,
            "latency_p75_sec": float(np.percentile(latencies, 75)) if latencies else 0.0,
            "latency_p90_sec": float(np.percentile(latencies, 90)) if latencies else 0.0,
            "latency_p95_sec": float(np.percentile(latencies, 95)) if latencies else 0.0,
            "latency_p99_sec": float(np.percentile(latencies, 99)) if latencies else 0.0,
            "mean_human_latency_cost_bps": float(np.mean(lat_costs)) if lat_costs else 0.0,
            "model_eligible_mean_return_bps": mean_all,
            "approved_mean_return_bps": mean_app,
            "rejected_mean_return_bps": float(np.mean(rej_rets)) if rej_rets else 0.0,
            "full_info_mean_return_bps": float(np.mean(full_rets)) if full_rets else 0.0,
            "safety_only_mean_return_bps": float(np.mean(blind_rets)) if blind_rets else 0.0,
            "human_incremental_alpha_bps": human_inc_alpha,
        }

    def compute_selection_bias_audit(self) -> Dict[str, any]:
        """Backward compatibility alias for selection bias audit."""
        decomp = self.compute_human_alpha_decomposition()
        decomp["rejected_count"] = decomp["discretionary_rejected_count"]
        decomp["expired_count"] = decomp["expired_timeout_count"]
        decomp["approved_mean_alpha_bps"] = decomp["approved_mean_return_bps"]
        decomp["rejected_mean_alpha_bps"] = decomp["rejected_mean_return_bps"]
        return decomp
