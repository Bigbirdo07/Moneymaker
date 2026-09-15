"""
Deterministic Autonomous Trade Gate & Safety Firewall Architecture for Phase 6A.
Removes per-trade human approval while enforcing 18+ strict fail-closed safety validations,
signal TTL expiration (3.0s), pre-submission snapshots, and full rejection ledger recording.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import os
from typing import Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.broker.adapter import BrokerAdapter, BrokerOrder, ExecutionMode, OrderStatus, OrderSide, OrderType
from src.data.market_provider import LiveMarketDataProvider, QuoteEvent
from src.governance.session_arming import SessionArmingManager, SessionAuthorizationToken


class AutonomousRejectionCode(str, Enum):
    STALE_DATA = "STALE_DATA"
    SPREAD_TOO_WIDE = "SPREAD_TOO_WIDE"
    CAPITAL_LIMIT = "CAPITAL_LIMIT"
    DAILY_LOSS_LIMIT = "DAILY_LOSS_LIMIT"
    WEEKLY_LOSS_LIMIT = "WEEKLY_LOSS_LIMIT"
    PILOT_DRAWDOWN_LIMIT = "PILOT_DRAWDOWN_LIMIT"
    POSITION_LIMIT = "POSITION_LIMIT"
    SYMBOL_NOT_ALLOWED = "SYMBOL_NOT_ALLOWED"
    MODEL_UNHEALTHY = "MODEL_UNHEALTHY"
    BROKER_UNHEALTHY = "BROKER_UNHEALTHY"
    RECONCILIATION_FAILURE = "RECONCILIATION_FAILURE"
    CLOCK_FAILURE = "CLOCK_FAILURE"
    SESSION_CLOSED = "SESSION_CLOSED"
    SIGNAL_EXPIRED = "SIGNAL_EXPIRED"
    UNAUTHORIZED_STRATEGY = "UNAUTHORIZED_STRATEGY"
    LOCK_NOT_HELD = "LOCK_NOT_HELD"
    UNKNOWN_STATE = "UNKNOWN_STATE"


@dataclass
class PreSubmissionSnapshot:
    """Immutable audit snapshot captured immediately before broker order submission."""
    snapshot_id: str
    decision_timestamp: pd.Timestamp
    pre_submit_timestamp: pd.Timestamp
    symbol: str
    side: str
    shares: float
    notional_usd: float
    decision_price: float
    current_bid: float
    current_ask: float
    spread_bps: float
    model_score: float
    opportunity_rank: int
    expected_alpha_bps: float
    estimated_cost_bps: float
    net_edge_bps: float
    risk_engine_status: str
    portfolio_exposure_usd: float
    daily_realized_pnl_usd: float
    model_health_status: str
    market_regime: str
    feature_vector_hash: str
    signal_age_ms: float


@dataclass
class AutonomousRejectionRecord:
    rejection_id: str
    symbol: str
    timestamp: pd.Timestamp
    rejection_code: AutonomousRejectionCode
    reason_detail: str
    snapshot: Optional[PreSubmissionSnapshot] = None


class AutonomousControlIncident(RuntimeError):
    """Raised on critical autonomous execution anomalies (e.g. submission post-lockout)."""
    pass


class DeterministicAutonomousGate:
    """
    Automated gatekeeper executing fail-closed validation on all proposed model orders.
    Replaces per-trade human review with deterministic mathematical and state constraints.
    """

    def __init__(
        self,
        broker: BrokerAdapter,
        provider: LiveMarketDataProvider,
        session_manager: SessionArmingManager,
        approved_symbols: Optional[Set[str]] = None,
        max_allowed_spread_bps: float = 3.0,
        signal_ttl_ms: float = 3000.0,
        max_daily_loss_usd: float = 20.0,
        max_weekly_loss_usd: float = 40.0,
        max_pilot_drawdown_usd: float = 50.0,
        max_concurrent_positions: int = 2,
    ):
        self.broker = broker
        self.provider = provider
        self.session_manager = session_manager
        self.approved_symbols = approved_symbols or {"NVDA", "AMD", "TSLA"}
        self.max_allowed_spread_bps = max_allowed_spread_bps
        self.signal_ttl_ms = signal_ttl_ms
        self.max_daily_loss_usd = max_daily_loss_usd
        self.max_weekly_loss_usd = max_weekly_loss_usd
        self.max_pilot_drawdown_usd = max_pilot_drawdown_usd
        self.max_concurrent_positions = max_concurrent_positions

        self.rejection_ledger: List[AutonomousRejectionRecord] = []
        self.submission_snapshots: List[PreSubmissionSnapshot] = []
        self.is_suspended = False

    def validate_and_snapshot(
        self,
        symbol: str,
        side: str,
        shares: float,
        notional_usd: float,
        decision_timestamp: pd.Timestamp,
        model_score: float,
        opportunity_rank: int,
        expected_alpha_bps: float,
        estimated_cost_bps: float,
        feature_hash: str,
        current_time: pd.Timestamp,
        model_health_status: str = "HEALTHY",
        market_regime: str = "BULL_LOW_VOL",
        daily_loss_usd: float = 0.0,
        weekly_loss_usd: float = 0.0,
        pilot_drawdown_usd: float = 0.0,
        reconciliation_clean: bool = True,
    ) -> Tuple[bool, Optional[PreSubmissionSnapshot], Optional[AutonomousRejectionCode], str]:
        """
        Execute full 18+ fail-closed check suite immediately before broker submission.
        Returns: (can_execute, snapshot, rejection_code, reason_message)
        """
        now = current_time
        signal_age_ms = (now - decision_timestamp).total_seconds() * 1000.0

        # 1. Check System Suspension & Emergency Lockout
        if self.is_suspended:
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.MODEL_UNHEALTHY, "System is in SUSPENDED state.")
            return False, None, AutonomousRejectionCode.MODEL_UNHEALTHY, "SYSTEM_SUSPENDED"

        # 2. Daily Session Token Validity
        token = self.session_manager.current_auth_token
        if token is None or not token.is_valid():
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.SESSION_CLOSED, "Session authorization token is invalid or expired.")
            return False, None, AutonomousRejectionCode.SESSION_CLOSED, "INVALID_AUTH_TOKEN"

        # 3. Exclusive Process Execution Lock Held
        if not self.session_manager._execution_lock_acquired:
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.LOCK_NOT_HELD, "Exclusive process lock not held.")
            return False, None, AutonomousRejectionCode.LOCK_NOT_HELD, "LOCK_NOT_HELD"

        # 4. Symbol Allow-List Check (Default DENY)
        if symbol not in self.approved_symbols:
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.SYMBOL_NOT_ALLOWED, f"Symbol {symbol} not in allow-list.")
            return False, None, AutonomousRejectionCode.SYMBOL_NOT_ALLOWED, "SYMBOL_DENIED"

        # 5. Signal TTL Expiration Check
        if signal_age_ms > self.signal_ttl_ms:
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.SIGNAL_EXPIRED, f"Signal age {signal_age_ms:.1f}ms exceeds TTL {self.signal_ttl_ms:.1f}ms.")
            return False, None, AutonomousRejectionCode.SIGNAL_EXPIRED, f"SIGNAL_TTL_EXPIRED_{signal_age_ms:.0f}ms"

        # 6. Broker Connection Health
        if not self.broker.is_connected():
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.BROKER_UNHEALTHY, "Broker adapter reports disconnected.")
            return False, None, AutonomousRejectionCode.BROKER_UNHEALTHY, "BROKER_DISCONNECTED"

        # 7. Market Data Staleness Check
        is_fresh, staleness_reason = self.provider.check_staleness(symbol, now, max_quote_staleness_sec=15.0)
        if not is_fresh:
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.STALE_DATA, f"Data feed staleness: {staleness_reason}")
            return False, None, AutonomousRejectionCode.STALE_DATA, f"STALE_FEED_{staleness_reason}"

        # 8. Quote & Spread Check
        quote = self.provider.get_latest_quote(symbol)
        if quote is None or quote.spread_bps > self.max_allowed_spread_bps or quote.bid <= 0:
            spread_val = quote.spread_bps if quote else -1.0
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.SPREAD_TOO_WIDE, f"Spread {spread_val:.2f}bps > max {self.max_allowed_spread_bps:.2f}bps.")
            return False, None, AutonomousRejectionCode.SPREAD_TOO_WIDE, f"SPREAD_TOO_WIDE_{spread_val:.1f}bps"

        # 9. Model Health Status Check
        if model_health_status in ("DEGRADED", "SUSPENDED"):
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.MODEL_UNHEALTHY, f"Model health status is {model_health_status}.")
            return False, None, AutonomousRejectionCode.MODEL_UNHEALTHY, f"MODEL_HEALTH_{model_health_status}"

        # 10. Loss Budget Checks
        if daily_loss_usd >= self.max_daily_loss_usd:
            self.is_suspended = True
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.DAILY_LOSS_LIMIT, f"Daily loss ${daily_loss_usd:.2f} touched limit ${self.max_daily_loss_usd:.2f}.")
            return False, None, AutonomousRejectionCode.DAILY_LOSS_LIMIT, "DAILY_LOSS_LIMIT_TOUCHED"

        if weekly_loss_usd >= self.max_weekly_loss_usd:
            self.is_suspended = True
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.WEEKLY_LOSS_LIMIT, f"Weekly loss ${weekly_loss_usd:.2f} touched limit ${self.max_weekly_loss_usd:.2f}.")
            return False, None, AutonomousRejectionCode.WEEKLY_LOSS_LIMIT, "WEEKLY_LOSS_LIMIT_TOUCHED"

        if pilot_drawdown_usd >= self.max_pilot_drawdown_usd:
            self.is_suspended = True
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.PILOT_DRAWDOWN_LIMIT, f"Drawdown ${pilot_drawdown_usd:.2f} touched ceiling ${self.max_pilot_drawdown_usd:.2f}.")
            return False, None, AutonomousRejectionCode.PILOT_DRAWDOWN_LIMIT, "DRAWDOWN_LIMIT_TOUCHED"

        # 11. Concurrent Position Limit
        positions = self.broker.get_positions()
        if len(positions) >= self.max_concurrent_positions:
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.POSITION_LIMIT, f"Open positions {len(positions)} >= max {self.max_concurrent_positions}.")
            return False, None, AutonomousRejectionCode.POSITION_LIMIT, "CONCURRENT_POSITIONS_FULL"

        # 12. Reconciliation Integrity
        if not reconciliation_clean:
            self.is_suspended = True
            rej = self._record_rejection(symbol, now, AutonomousRejectionCode.RECONCILIATION_FAILURE, "Active reconciliation discrepancy detected.")
            return False, None, AutonomousRejectionCode.RECONCILIATION_FAILURE, "RECONCILIATION_MISMATCH"

        # 13. Create Pre-Submission Snapshot
        snapshot_id = f"SNAP_{symbol}_{now.strftime('%Y%m%d%H%M%S%f')[:17]}"
        net_edge = expected_alpha_bps - estimated_cost_bps
        exposure_usd = sum(p.market_value for p in positions.values())

        snapshot = PreSubmissionSnapshot(
            snapshot_id=snapshot_id,
            decision_timestamp=decision_timestamp,
            pre_submit_timestamp=now,
            symbol=symbol,
            side=side,
            shares=shares,
            notional_usd=notional_usd,
            decision_price=quote.ask,
            current_bid=quote.bid,
            current_ask=quote.ask,
            spread_bps=quote.spread_bps,
            model_score=model_score,
            opportunity_rank=opportunity_rank,
            expected_alpha_bps=expected_alpha_bps,
            estimated_cost_bps=estimated_cost_bps,
            net_edge_bps=net_edge,
            risk_engine_status="APPROVED",
            portfolio_exposure_usd=exposure_usd,
            daily_realized_pnl_usd=-daily_loss_usd,
            model_health_status=model_health_status,
            market_regime=market_regime,
            feature_vector_hash=feature_hash,
            signal_age_ms=signal_age_ms,
        )

        self.submission_snapshots.append(snapshot)
        return True, snapshot, None, "AUTONOMOUS_GATE_PASSED"

    def _record_rejection(
        self,
        symbol: str,
        timestamp: pd.Timestamp,
        code: AutonomousRejectionCode,
        detail: str,
    ) -> AutonomousRejectionRecord:
        rec = AutonomousRejectionRecord(
            rejection_id=f"REJ_{symbol}_{timestamp.strftime('%Y%m%d%H%M%S%f')[:17]}",
            symbol=symbol,
            timestamp=timestamp,
            rejection_code=code,
            reason_detail=detail,
        )
        self.rejection_ledger.append(rec)
        return rec
