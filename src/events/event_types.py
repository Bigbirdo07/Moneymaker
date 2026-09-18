"""
Canonical Event Risk Taxonomy and Core Types.

Defines the 12 canonical event families, policy actions, severity levels,
open-position actions, and point-in-time event records.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime


class EventFamily(str, Enum):
    EARNINGS = "EARNINGS"
    TRADING_HALT = "TRADING_HALT"
    REGULATORY_DECISION = "REGULATORY_DECISION"
    CLINICAL_FDA_BINARY = "CLINICAL_FDA_BINARY"
    MERGER_ACQUISITION = "MERGER_ACQUISITION"
    BANKRUPTCY_DISTRESS = "BANKRUPTCY_DISTRESS"
    MATERIAL_CORPORATE_ACTION = "MATERIAL_CORPORATE_ACTION"
    SHARE_OFFERING_DILUTION = "SHARE_OFFERING_DILUTION"
    MAJOR_LEGAL_GOVERNMENT = "MAJOR_LEGAL_GOVERNMENT"
    INDEX_EXCHANGE_LISTING = "INDEX_EXCHANGE_LISTING"
    DATA_QUOTE_ANOMALY = "DATA_QUOTE_ANOMALY"
    MARKET_WIDE_EMERGENCY = "MARKET_WIDE_EMERGENCY"


class PolicyAction(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REDUCE_RISK = "REDUCE_RISK"
    VETO = "VETO"


class OpenPositionAction(str, Enum):
    HOLD = "HOLD"
    REDUCE = "REDUCE"
    EXIT = "EXIT"
    FREEZE_NO_ACTION_IF_HALTED = "FREEZE_NO_ACTION_IF_HALTED"


class EventSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class EventRecord:
    """
    Represents an immutable, point-in-time financial market event record.
    """
    event_id: str
    symbol: str
    event_type: EventFamily
    event_subtype: str
    source: str
    source_timestamp: str       # Exact ISO-8601 when published by source
    effective_timestamp: str    # When event takes market effect
    expiry_timestamp: str       # When event restriction ceases
    severity: EventSeverity
    confidence: float           # 0.0 to 1.0
    known_before_open: bool = False
    raw_reference_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_active_at(self, query_timestamp: str) -> bool:
        """
        Evaluates point-in-time visibility and active duration.
        Must satisfy: source_timestamp <= query_timestamp < expiry_timestamp.
        """
        return (self.source_timestamp <= query_timestamp) and (query_timestamp < self.expiry_timestamp)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "symbol": self.symbol,
            "event_type": self.event_type.value,
            "event_subtype": self.event_subtype,
            "source": self.source,
            "source_timestamp": self.source_timestamp,
            "effective_timestamp": self.effective_timestamp,
            "expiry_timestamp": self.expiry_timestamp,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "known_before_open": self.known_before_open,
            "raw_reference_hash": self.raw_reference_hash,
        }


@dataclass(frozen=True)
class EventRiskDecision:
    """
    Outcome of deterministic event policy evaluation.
    """
    symbol: str
    timestamp: str
    action: PolicyAction
    open_position_action: OpenPositionAction
    reason_codes: List[str]
    active_event_ids: List[str]
    size_multiplier: float = 1.0
    expiry_timestamp: Optional[str] = None
    diagnostics: Dict[str, Any] = field(default_factory=dict)

    @property
    def is_vetoed(self) -> bool:
        return self.action == PolicyAction.VETO

    @property
    def is_permitted(self) -> bool:
        return self.action in (PolicyAction.ALLOW, PolicyAction.WARN, PolicyAction.REDUCE_RISK)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "action": self.action.value,
            "open_position_action": self.open_position_action.value,
            "reason_codes": self.reason_codes,
            "active_event_ids": self.active_event_ids,
            "size_multiplier": self.size_multiplier,
            "expiry_timestamp": self.expiry_timestamp,
            "is_vetoed": self.is_vetoed,
        }
