"""
Deterministic Event Risk Policy Engine.

Evaluates market events against configurable deterministic rules to output:
- PolicyAction: ALLOW | WARN | REDUCE_RISK | VETO
- OpenPositionAction: HOLD | REDUCE | EXIT | FREEZE_NO_ACTION_IF_HALTED
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

from src.events.event_types import (
    EventFamily,
    PolicyAction,
    OpenPositionAction,
    EventSeverity,
    EventRecord,
    EventRiskDecision,
)
from src.events.event_cache import PointInTimeEventCache
from src.events.event_service_health import EventServiceHealthManager, EventServiceHealthState
from src.events.event_provenance import EventAuditTracker


DEFAULT_POLICY_CONFIG = {
    "version": "1.0.0",
    "rules": {
        "trading_halt": {
            "entry_action": "VETO",
            "open_position_action": "FREEZE_NO_ACTION_IF_HALTED",
            "reason": "EXCHANGE_TRADING_HALT_ACTIVE",
        },
        "bankruptcy_distress": {
            "entry_action": "VETO",
            "open_position_action": "EXIT",
            "reason": "BANKRUPTCY_DISTRESS_RISK",
        },
        "same_day_earnings": {
            "entry_action": "VETO",
            "open_position_action": "HOLD",
            "reason": "SAME_DAY_EARNINGS_BINARY_RISK",
        },
        "clinical_fda_binary": {
            "entry_action": "VETO",
            "open_position_action": "EXIT",
            "reason": "FDA_CLINICAL_BINARY_EVENT",
        },
        "merger_acquisition": {
            "entry_action": "VETO",
            "open_position_action": "HOLD",
            "reason": "MERGER_ACQUISITION_DISCONTINUITY",
        },
        "share_offering_dilution": {
            "entry_action": "REDUCE_RISK",
            "open_position_action": "HOLD",
            "size_multiplier": 0.50,
            "reason": "SECONDARY_OFFERING_DILUTION_RISK",
        },
        "data_quote_anomaly": {
            "entry_action": "VETO",
            "open_position_action": "FREEZE_NO_ACTION_IF_HALTED",
            "reason": "MARKET_DATA_INTEGRITY_ANOMALY",
        },
        "market_wide_emergency": {
            "entry_action": "VETO",
            "open_position_action": "HOLD",
            "reason": "MARKET_WIDE_CIRCUIT_BREAKER",
        },
    }
}


class EventRiskPolicy:
    """
    Deterministic rule engine that prevents quantitative entries during unmodeled binary events.
    """
    def __init__(
        self,
        event_cache: Optional[PointInTimeEventCache] = None,
        health_manager: Optional[EventServiceHealthManager] = None,
        config: Optional[Dict[str, Any]] = None,
        config_path: Optional[str] = None,
    ):
        self.cache = event_cache or PointInTimeEventCache()
        self.health = health_manager or EventServiceHealthManager()
        self.audit_tracker = EventAuditTracker()

        if config_path and Path(config_path).exists():
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = config or DEFAULT_POLICY_CONFIG

    def evaluate(
        self,
        symbol: str,
        timestamp: str,
        has_open_position: bool = False,
        quant_rank: Optional[int] = None,
        predicted_edge_bps: Optional[float] = None,
    ) -> EventRiskDecision:
        """
        Evaluates deterministic event rules for a specific symbol at timestamp.
        """
        reason_codes: List[str] = []
        active_event_ids: List[str] = []
        current_action = PolicyAction.ALLOW
        current_open_action = OpenPositionAction.HOLD
        current_size_mult = 1.0
        earliest_expiry: Optional[str] = None

        # 1. Service Health Fail-Safe Check
        fail_safe_action = self.health.get_fail_safe_action()
        if fail_safe_action is not None:
            reason_codes.append(f"SERVICE_HEALTH_{self.health.overall_health_state.value}")
            if fail_safe_action == PolicyAction.VETO:
                current_action = PolicyAction.VETO
                current_size_mult = 0.0
            elif fail_safe_action == PolicyAction.REDUCE_RISK:
                current_action = PolicyAction.REDUCE_RISK
                current_size_mult = 0.50

        # 2. Market-Wide Emergency Events
        market_events = self.cache.get_market_wide_events(timestamp)
        for me in market_events:
            active_event_ids.append(me.event_id)
            if me.event_type == EventFamily.MARKET_WIDE_EMERGENCY:
                current_action = PolicyAction.VETO
                reason_codes.append("MARKET_WIDE_CIRCUIT_BREAKER_ACTIVE")
                current_size_mult = 0.0

        # 3. Symbol-Specific Active Events
        symbol_events = self.cache.get_active_events(symbol, timestamp)
        all_active = market_events + symbol_events

        for ev in symbol_events:
            active_event_ids.append(ev.event_id)
            if earliest_expiry is None or ev.expiry_timestamp < earliest_expiry:
                earliest_expiry = ev.expiry_timestamp

            # Rule: Trading Halt
            if ev.event_type == EventFamily.TRADING_HALT:
                current_action = PolicyAction.VETO
                current_open_action = OpenPositionAction.FREEZE_NO_ACTION_IF_HALTED
                reason_codes.append(f"TRADING_HALT_{ev.event_subtype}")
                current_size_mult = 0.0

            # Rule: Bankruptcy / Insolvency Distress
            elif ev.event_type == EventFamily.BANKRUPTCY_DISTRESS:
                current_action = PolicyAction.VETO
                current_open_action = OpenPositionAction.EXIT
                reason_codes.append(f"BANKRUPTCY_DISTRESS_{ev.event_subtype}")
                current_size_mult = 0.0

            # Rule: Same-Day Earnings
            elif ev.event_type == EventFamily.EARNINGS:
                current_action = PolicyAction.VETO
                reason_codes.append(f"EARNINGS_ANNOUNCEMENT_{ev.event_subtype}")
                current_size_mult = 0.0

            # Rule: FDA / Clinical Binary
            elif ev.event_type == EventFamily.CLINICAL_FDA_BINARY:
                current_action = PolicyAction.VETO
                current_open_action = OpenPositionAction.EXIT
                reason_codes.append(f"FDA_BINARY_{ev.event_subtype}")
                current_size_mult = 0.0

            # Rule: M&A / Takeover Deal Discontinuity
            elif ev.event_type == EventFamily.MERGER_ACQUISITION:
                current_action = PolicyAction.VETO
                reason_codes.append(f"MERGER_ACQUISITION_{ev.event_subtype}")
                current_size_mult = 0.0

            # Rule: Data Quote Anomaly
            elif ev.event_type == EventFamily.DATA_QUOTE_ANOMALY:
                current_action = PolicyAction.VETO
                current_open_action = OpenPositionAction.FREEZE_NO_ACTION_IF_HALTED
                reason_codes.append(f"DATA_QUOTE_ANOMALY_{ev.event_subtype}")
                current_size_mult = 0.0

            # Rule: Share Offering / Dilution
            elif ev.event_type == EventFamily.SHARE_OFFERING_DILUTION:
                if current_action != PolicyAction.VETO:
                    current_action = PolicyAction.REDUCE_RISK
                    current_size_mult = min(current_size_mult, 0.50)
                reason_codes.append(f"OFFERING_DILUTION_{ev.event_subtype}")

            # Rule: Legal / Regulatory Actions
            elif ev.event_type in (EventFamily.MAJOR_LEGAL_GOVERNMENT, EventFamily.REGULATORY_DECISION):
                if ev.severity in (EventSeverity.CRITICAL, EventSeverity.HIGH):
                    current_action = PolicyAction.VETO
                    current_size_mult = 0.0
                    reason_codes.append(f"MAJOR_LEGAL_{ev.severity.value}_{ev.event_subtype}")
                elif ev.severity == EventSeverity.MEDIUM:
                    if current_action != PolicyAction.VETO:
                        current_action = PolicyAction.REDUCE_RISK
                        current_size_mult = min(current_size_mult, 0.50)
                    reason_codes.append(f"LEGAL_MEDIUM_{ev.event_subtype}")
                else:
                    if current_action == PolicyAction.ALLOW:
                        current_action = PolicyAction.WARN
                    reason_codes.append(f"LEGAL_INFO_{ev.event_subtype}")

        decision = EventRiskDecision(
            symbol=symbol,
            timestamp=timestamp,
            action=current_action,
            open_position_action=current_open_action,
            reason_codes=reason_codes or ["NO_ACTIVE_EVENT_RESTRICTIONS"],
            active_event_ids=active_event_ids,
            size_multiplier=current_size_mult,
            expiry_timestamp=earliest_expiry,
            diagnostics={
                "has_open_position": has_open_position,
                "quant_rank": quant_rank,
                "predicted_edge_bps": predicted_edge_bps,
            },
        )

        # Audit and record
        self.audit_tracker.record_decision(
            decision=decision,
            active_events=all_active,
            quant_rank=quant_rank,
            predicted_edge_bps=predicted_edge_bps,
        )

        return decision
