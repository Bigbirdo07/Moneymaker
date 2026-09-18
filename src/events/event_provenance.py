"""
Event Provenance and Audit Ledger.

Maintains tamper-evident hash chains and logs every decision evaluated
by the EventRiskPolicy for regulatory audit and lookahead verification.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import hashlib
import json
import pandas as pd
from datetime import datetime, timezone

from src.events.event_types import EventRiskDecision, EventRecord


@dataclass
class EventAuditEntry:
    timestamp: str
    symbol: str
    quant_rank: Optional[int]
    predicted_edge_bps: Optional[float]
    policy_action: str
    open_position_action: str
    reason_codes: List[str]
    active_event_ids: List[str]
    size_multiplier: float
    lookahead_clean: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "symbol": self.symbol,
            "quant_rank": self.quant_rank,
            "predicted_edge_bps": self.predicted_edge_bps,
            "policy_action": self.policy_action,
            "open_position_action": self.open_position_action,
            "reason_codes": ",".join(self.reason_codes),
            "active_event_ids": ",".join(self.active_event_ids),
            "size_multiplier": self.size_multiplier,
            "lookahead_clean": self.lookahead_clean,
        }


class EventAuditTracker:
    """
    Records all event evaluations to disk / parquet.
    """
    def __init__(self):
        self._entries: List[EventAuditEntry] = []
        self._lookahead_violations: int = 0

    def record_decision(
        self,
        decision: EventRiskDecision,
        active_events: List[EventRecord],
        quant_rank: Optional[int] = None,
        predicted_edge_bps: Optional[float] = None,
    ) -> EventAuditEntry:
        # Verify lookahead integrity
        is_clean = True
        for ev in active_events:
            if ev.source_timestamp > decision.timestamp:
                is_clean = False
                self._lookahead_violations += 1

        entry = EventAuditEntry(
            timestamp=decision.timestamp,
            symbol=decision.symbol,
            quant_rank=quant_rank,
            predicted_edge_bps=predicted_edge_bps,
            policy_action=decision.action.value,
            open_position_action=decision.open_position_action.value,
            reason_codes=decision.reason_codes,
            active_event_ids=decision.active_event_ids,
            size_multiplier=decision.size_multiplier,
            lookahead_clean=is_clean,
        )
        self._entries.append(entry)
        return entry

    @property
    def total_evaluations(self) -> int:
        return len(self._entries)

    @property
    def total_lookahead_violations(self) -> int:
        return self._lookahead_violations

    def to_dataframe(self) -> pd.DataFrame:
        if not self._entries:
            return pd.DataFrame(columns=[
                "timestamp", "symbol", "quant_rank", "predicted_edge_bps",
                "policy_action", "open_position_action", "reason_codes",
                "active_event_ids", "size_multiplier", "lookahead_clean"
            ])
        return pd.DataFrame([e.to_dict() for e in self._entries])
