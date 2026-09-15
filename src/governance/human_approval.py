"""
Human-in-the-Loop Manual Order Approval Gate for Phase 5A Governed Micro-Pilot.
Enforces mandatory operator review, comprehensive trade card display, 30-second expiration timeouts,
pre-submission stale data validation, and selection bias tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple
import pandas as pd

from src.data.market_provider import QuoteEvent


class ApprovalAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    EXPIRED_TIMEOUT = "EXPIRED_TIMEOUT"
    STALE_DATA_CANCELLED = "STALE_DATA_CANCELLED"


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

    def render_display(self) -> str:
        """Render formatted operator terminal display."""
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
    decision_timestamp: pd.Timestamp
    operator_action_timestamp: pd.Timestamp
    operator_latency_sec: float
    reason_notes: str = ""
    future_15m_return_bps: Optional[float] = None


class HumanApprovalGate:
    """Manages order proposal queue, operator approvals, expiration, and bias audits."""

    def __init__(self, approval_timeout_seconds: float = 30.0, max_allowed_spread_bps: float = 3.0):
        self.approval_timeout_sec = approval_timeout_seconds
        self.max_allowed_spread_bps = max_allowed_spread_bps
        self.pending_proposals: Dict[str, Tuple[ProposedOrderCard, pd.Timestamp]] = {}
        self.approval_records: List[HumanApprovalRecord] = []

    def submit_proposal(self, card: ProposedOrderCard) -> None:
        now = pd.Timestamp.now(tz=timezone.utc)
        self.pending_proposals[card.proposal_id] = (card, now)

    def process_operator_action(
        self,
        proposal_id: str,
        operator_id: str,
        action: ApprovalAction,
        current_time: pd.Timestamp,
        current_quote: Optional[QuoteEvent] = None,
        reason_notes: str = "",
    ) -> Tuple[bool, str]:
        """
        Process human review action with expiration and pre-submit staleness verification.
        Returns: (can_execute, final_status_reason)
        """
        if proposal_id not in self.pending_proposals:
            return False, "PROPOSAL_NOT_FOUND"

        card, submit_time = self.pending_proposals.pop(proposal_id)
        latency_sec = (current_time - card.decision_timestamp).total_seconds()

        # 1. Expiration Timeout Check
        if latency_sec > self.approval_timeout_sec:
            record = HumanApprovalRecord(
                proposal_id=proposal_id,
                symbol=card.symbol,
                operator_id=operator_id,
                action=ApprovalAction.EXPIRED_TIMEOUT,
                decision_timestamp=card.decision_timestamp,
                operator_action_timestamp=current_time,
                operator_latency_sec=latency_sec,
                reason_notes=f"Approval expired: latency {latency_sec:.1f}s > {self.approval_timeout_sec}s",
            )
            self.approval_records.append(record)
            return False, f"EXPIRED_TIMEOUT_{latency_sec:.1f}s"

        # 2. Operator Explicit Rejection
        if action == ApprovalAction.REJECT:
            record = HumanApprovalRecord(
                proposal_id=proposal_id,
                symbol=card.symbol,
                operator_id=operator_id,
                action=ApprovalAction.REJECT,
                decision_timestamp=card.decision_timestamp,
                operator_action_timestamp=current_time,
                operator_latency_sec=latency_sec,
                reason_notes=reason_notes or "OPERATOR_REJECTED",
            )
            self.approval_records.append(record)
            return False, "OPERATOR_REJECTED"

        # 3. Pre-Submission Stale Signal Re-Verification
        if current_quote is not None:
            quote_age_sec = (current_time - current_quote.received_timestamp).total_seconds()
            if quote_age_sec > 15.0 or current_quote.spread_bps > self.max_allowed_spread_bps:
                record = HumanApprovalRecord(
                    proposal_id=proposal_id,
                    symbol=card.symbol,
                    operator_id=operator_id,
                    action=ApprovalAction.STALE_DATA_CANCELLED,
                    decision_timestamp=card.decision_timestamp,
                    operator_action_timestamp=current_time,
                    operator_latency_sec=latency_sec,
                    reason_notes=f"Stale quote ({quote_age_sec:.1f}s) or spread expansion ({current_quote.spread_bps:.1f}bps)",
                )
                self.approval_records.append(record)
                return False, "STALE_DATA_PRE_SUBMIT_CANCELLED"

        # 4. Successful Approval
        record = HumanApprovalRecord(
            proposal_id=proposal_id,
            symbol=card.symbol,
            operator_id=operator_id,
            action=ApprovalAction.APPROVE,
            decision_timestamp=card.decision_timestamp,
            operator_action_timestamp=current_time,
            operator_latency_sec=latency_sec,
            reason_notes=reason_notes,
        )
        self.approval_records.append(record)
        return True, "APPROVED_FOR_EXECUTION"

    def compute_selection_bias_audit(self) -> Dict[str, any]:
        """Audit whether human intervention adds or destroys value."""
        if not self.approval_records:
            return {"total_proposals": 0, "approved_count": 0, "rejected_count": 0, "expired_count": 0}

        approved = [r for r in self.approval_records if r.action == ApprovalAction.APPROVE]
        rejected = [r for r in self.approval_records if r.action == ApprovalAction.REJECT]
        expired = [r for r in self.approval_records if r.action == ApprovalAction.EXPIRED_TIMEOUT]

        app_rets = [r.future_15m_return_bps for r in approved if r.future_15m_return_bps is not None]
        rej_rets = [r.future_15m_return_bps for r in rejected if r.future_15m_return_bps is not None]

        import numpy as np
        return {
            "total_proposals": len(self.approval_records),
            "approved_count": len(approved),
            "rejected_count": len(rejected),
            "expired_count": len(expired),
            "approval_rate_pct": (len(approved) / len(self.approval_records)) * 100.0,
            "mean_operator_latency_sec": float(np.mean([r.operator_latency_sec for r in self.approval_records])),
            "approved_mean_alpha_bps": float(np.mean(app_rets)) if app_rets else 0.0,
            "rejected_mean_alpha_bps": float(np.mean(rej_rets)) if rej_rets else 0.0,
        }
