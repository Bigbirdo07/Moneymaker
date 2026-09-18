import hashlib
import json
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging
from typing import Dict, List, Optional, Any, Set
import uuid

from src.broker.execution_environment import ExecutionEnvironment, validate_execution_environment
from src.broker.broker_adapter import BrokerAdapter
from src.broker.simulation_broker import SimulationBrokerAdapter
from src.broker.order_intent import OrderIntent, OrderSide, OrderType, BrokerOrder, BrokerFill
from src.broker.reconciliation import BrokerReconciliationService, ReconciliationStatus
from src.portfolio.strategy_capital_ledger import StrategyCapitalLedger
from src.portfolio.position_lifecycle import ManagedPosition, PositionLifecycleState
from src.runtime.runtime_state import RuntimeState
from src.runtime.market_clock import MarketClockService, SessionWindow
from src.runtime.event_store import EventStore, EventSeverity
from src.runtime.runtime_health import RuntimeHealthMonitor, HealthStatus
from src.intelligence.morning_brief import MorningBriefService
from src.intelligence.morning_market_state import MorningMarketState, SessionGateState
from src.events.event_risk_policy import EventRiskPolicy
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.risk_position_sizer import RiskPositionSizer
from src.risk.drawdown_state import DrawdownThrottleEngine, AccountRiskState
from src.risk.capital_tiers import CapitalTier
from src.execution.capacity_model import CapacityModel

logger = logging.getLogger("src.runtime.paper_trading_runtime")


@dataclass
class ExecutionAuthorization:
    authorization_id: str
    timestamp: str
    symbol: str
    side: str
    quantity: int
    target_notional: float
    is_authorized: bool
    decision_price: float = 0.0
    rejection_reasons: List[str] = field(default_factory=list)


class PolicyTamperError(Exception):
    """Raised if forward paper operating policy has been modified from freeze manifest."""
    pass


class PaperTradingRuntime:
    """
    Autonomous Paper Trading Runtime Orchestrator.
    """
    def __init__(
        self,
        environment: ExecutionEnvironment = ExecutionEnvironment.PAPER,
        broker_adapter: Optional[BrokerAdapter] = None,
        strategy_capital: float = 1000.0,
        morning_service: Optional[MorningBriefService] = None,
        event_policy: Optional[EventRiskPolicy] = None,
        risk_sizer: Optional[RiskPositionSizer] = None,
        clock_service: Optional[MarketClockService] = None,
    ):
        validate_execution_environment(environment)
        self.environment = environment
        self.broker = broker_adapter or SimulationBrokerAdapter(starting_cash=strategy_capital)
        self.capital_ledger = StrategyCapitalLedger(authorized_strategy_capital=strategy_capital)
        self.state = RuntimeState.BOOTING

        self.reconciliation_service = BrokerReconciliationService(self.broker)
        self.event_store = EventStore()
        self.health_monitor = RuntimeHealthMonitor()
        self.clock = clock_service or MarketClockService()

        self.morning_service = morning_service or MorningBriefService()
        self.event_policy = event_policy or EventRiskPolicy()
        self.risk_sizer = risk_sizer or RiskPositionSizer()
        self.drawdown_engine = DrawdownThrottleEngine()
        self.capacity_model = CapacityModel()

        self.session_id: str = ""
        self.date_str: str = ""
        self.morning_state: Optional[MorningMarketState] = None
        self.open_positions: Dict[str, ManagedPosition] = {}
        self.decision_ledger: List[Dict[str, Any]] = []
        self.authorizations: List[ExecutionAuthorization] = []
        self.incidents: List[Dict[str, Any]] = []
        self.symbol_daily_entries: Set[str] = set()
        self.daily_entries_count: int = 0
        self.macro_event_freeze: bool = False
        self.policy_version: str = "FORWARD_PAPER_POLICY_V1"
        self.is_halted: bool = False

    def verify_freeze_manifest(
        self,
        manifest_path: str = "TRUE_FORWARD_PAPER_FREEZE_MANIFEST.json",
        policy_path: str = "FORWARD_PAPER_POLICY_V1.yaml",
    ) -> bool:
        """
        Verifies policy hash and runtime integrity against canonical freeze manifest.
        """
        p_path = Path(policy_path)
        m_path = Path(manifest_path)
        if not p_path.exists() or not m_path.exists():
            logger.warning("Freeze manifest or policy file not found for verification: %s, %s", p_path, m_path)
            return True

        with open(p_path, "rb") as f:
            computed_policy_hash = hashlib.sha256(f.read()).hexdigest()

        with open(m_path, "r") as f:
            manifest_data = json.load(f)

        expected_hash = manifest_data.get("policy_hash")
        if expected_hash and computed_policy_hash != expected_hash:
            raise PolicyTamperError(
                f"FATAL POLICY INTEGRITY VIOLATION: Computed policy hash ({computed_policy_hash}) "
                f"does not match freeze manifest policy hash ({expected_hash})."
            )
        logger.info("Freeze manifest policy hash verified: %s", computed_policy_hash[:12])
        return True

    def transition_state(self, new_state: RuntimeState, reason: str = "") -> None:
        old_state = self.state
        self.state = new_state
        logger.info("Runtime state transition: %s -> %s (Reason: %s)", old_state.value, new_state.value, reason)
        self.event_store.record(
            session_id=self.session_id,
            event_type="STATE_TRANSITION",
            component="RUNTIME",
            severity=EventSeverity.INFO,
            payload={"old_state": old_state.value, "new_state": new_state.value, "reason": reason},
        )

    def initialize_session(self, date_str: str) -> None:
        """
        Bootstraps session identity, verifies broker connectivity & initial reconciliation.
        """
        self.date_str = date_str
        prefix = "DRYRUN" if self.environment == ExecutionEnvironment.DRY_RUN else "PAPER"
        self.session_id = f"{prefix}_{date_str.replace('-', '')}_{uuid.uuid4().hex[:6]}"
        self.symbol_daily_entries.clear()
        self.daily_entries_count = 0
        self.macro_event_freeze = False
        self.transition_state(RuntimeState.BOOTING, f"Starting session {self.session_id}")

        # 0. Policy & Freeze Manifest Integrity Verification
        self.verify_freeze_manifest()

        # 1. Broker account verification
        account = self.broker.get_account()
        if not account.is_paper:
            self.transition_state(RuntimeState.HALTED, "Broker account is not paper!")
            raise PermissionError("Broker account verification failed: not a paper account.")

        # 2. Initial reconciliation
        rec = self.reconciliation_service.reconcile(self.open_positions, self.capital_ledger)
        if not rec.is_safe_to_operate:
            self.transition_state(RuntimeState.HALTED, f"Initial reconciliation failed: {rec.unexplained_position_mismatches}")
            return

        self.transition_state(RuntimeState.PREMARKET_INITIALIZING, "Broker verified & clean initial reconciliation.")

    def run_premarket_brief(
        self,
        timestamp: str,
        spy_premarket_ret: float,
        spy_overnight_ret: float,
        symbol_returns: Dict[str, float],
        symbol_vwaps: Dict[str, float],
        symbol_sectors: Dict[str, str],
        symbol_rel_vols: Dict[str, float],
        scanner_symbols: List[str],
    ) -> MorningMarketState:
        """
        Invokes Phase E MorningBriefService to produce structured trading-day briefing.
        """
        portfolio = PortfolioRiskState.create(
            timestamp=timestamp,
            starting_day_equity=self.capital_ledger.authorized_strategy_capital,
            current_equity=self.capital_ledger.current_strategy_equity,
            cash=self.capital_ledger.current_cash_dollars,
            peak_equity=self.capital_ledger.authorized_strategy_capital,
            realized_pnl_today=self.capital_ledger.realized_pnl_dollars,
        )

        self.morning_state = self.morning_service.generate_morning_state(
            date_str=self.date_str,
            timestamp=timestamp,
            portfolio_state=portfolio,
            spy_premarket_return_pct=spy_premarket_ret,
            spy_overnight_return_pct=spy_overnight_ret,
            symbol_returns_pct=symbol_returns,
            symbol_vwap_distances_pct=symbol_vwaps,
            symbol_sectors=symbol_sectors,
            symbol_rel_vol=symbol_rel_vols,
            scanner_symbols=scanner_symbols,
        )

        self.transition_state(RuntimeState.PREMARKET_READY, f"Morning brief generated (Session Gate: {self.morning_state.session_gate.value})")
        return self.morning_state

    def activate_trading(self) -> None:
        if self.is_halted:
            return
        if self.morning_state and self.morning_state.session_gate == SessionGateState.NO_GO:
            self.transition_state(RuntimeState.CASH_PRESERVATION, "SessionGate is NO_GO -> 100% cash preservation.")
        elif self.morning_state and self.morning_state.session_gate == SessionGateState.CAUTION:
            self.transition_state(RuntimeState.REDUCED_RISK, "SessionGate is CAUTION -> reduced risk trading.")
        else:
            self.transition_state(RuntimeState.TRADING_ACTIVE, "All systems nominal -> trading active.")

    def evaluate_and_execute_candidate(
        self,
        symbol: str,
        price: float,
        predicted_net_edge_bps: float,
        model_confidence: float,
        timestamp: str,
        sector: str = "Technology",
    ) -> Optional[BrokerOrder]:
        """
        Executes complete deterministic decision pipeline complying with FORWARD_PAPER_POLICY_V1.
        """
        time_part = timestamp.split("T")[-1].replace("Z", "") if "T" in timestamp else ""

        # 1. Market Open Cooldown (09:35:00 ET)
        if time_part and time_part < "09:35:00":
            self._record_decision(symbol, "NO_TRADE", ["ENTRY_WINDOW_CLOSED", "OPEN_COOLDOWN"])
            return None

        # 2. Entry Window Cutoff (14:30:00 ET)
        if time_part and time_part > "14:30:00":
            self._record_decision(symbol, "NO_TRADE", ["ENTRY_CUTOFF_REACHED"])
            return None

        # 3. Daily Loss Limit Check ($15.00 / 1.50% equity)
        if self.capital_ledger.realized_pnl_dollars <= -15.00:
            if self.state != RuntimeState.CASH_PRESERVATION:
                self.transition_state(RuntimeState.CASH_PRESERVATION, "Daily loss limit ($15.00) breached.")
            self._record_decision(symbol, "NO_TRADE", ["DAILY_LOSS_LIMIT", "CASH_PRESERVATION"])
            return None

        # 4. Runtime / Session Gate Check
        if self.state == RuntimeState.CASH_PRESERVATION or (self.morning_state and self.morning_state.session_gate == SessionGateState.NO_GO):
            self._record_decision(symbol, "NO_TRADE", ["SESSION_NO_GO"])
            return None

        if self.state not in (RuntimeState.TRADING_ACTIVE, RuntimeState.REDUCED_RISK):
            self._record_decision(symbol, "NO_TRADE", ["RUNTIME_NOT_ACTIVE"])
            return None

        # 5. Open Positions / No Position Switching (Max 1)
        if len(self.open_positions) >= self.capital_ledger.max_open_positions:
            self._record_decision(symbol, "NO_TRADE", ["POSITION_ALREADY_OPEN"])
            return None

        # 6. Max Daily Entries & Same-Symbol Limit
        if self.daily_entries_count >= 2:
            self._record_decision(symbol, "NO_TRADE", ["MAX_DAILY_ENTRIES_REACHED"])
            return None

        if symbol in self.symbol_daily_entries:
            self._record_decision(symbol, "NO_TRADE", ["SYMBOL_DAILY_ENTRY_LIMIT"])
            return None

        # 7. Macro Event Freeze
        if self.macro_event_freeze:
            self._record_decision(symbol, "NO_TRADE", ["MACRO_EVENT_ENTRY_FREEZE"])
            return None

        # 8. Event Risk Policy Check
        event_dec = self.event_policy.evaluate(symbol=symbol, timestamp=timestamp)
        if event_dec.is_vetoed:
            self._record_decision(symbol, "NO_TRADE", ["EVENT_VETO", *[f"EVENT_{r}" for r in event_dec.reason_codes]])
            return None

        # 9. SessionGate Edge & Confidence Hurdles
        is_caution = (self.morning_state and self.morning_state.session_gate == SessionGateState.CAUTION)
        if is_caution:
            if predicted_net_edge_bps < 30.0:
                self._record_decision(symbol, "NO_TRADE", ["CAUTION_EDGE_TOO_LOW"])
                return None
            if model_confidence < 0.60:
                self._record_decision(symbol, "NO_TRADE", ["EDGE_TOO_LOW"])
                return None
            max_notional = min(375.0, self.capital_ledger.max_position_dollars * 0.50)
        else:
            if predicted_net_edge_bps < 20.0 or model_confidence < 0.55:
                self._record_decision(symbol, "NO_TRADE", ["EDGE_TOO_LOW"])
                return None
            max_notional = self.capital_ledger.max_position_dollars

        # 10. Position Sizing
        shares = int(max_notional / price)
        if shares <= 0:
            self._record_decision(symbol, "NO_TRADE", ["RISK_LIMIT", "CAPITAL_EXCEEDS_SHARE_PRICE"])
            return None

        notional = shares * price

        # 11. Issue Execution Authorization
        auth_id = f"AUTH_{uuid.uuid4().hex[:10]}"
        auth = ExecutionAuthorization(
            authorization_id=auth_id,
            timestamp=timestamp,
            symbol=symbol,
            side="BUY",
            quantity=shares,
            target_notional=notional,
            is_authorized=True,
            decision_price=price,
        )
        self.authorizations.append(auth)

        # In DRY_RUN mode: record authorization & decision without submitting broker order
        if self.environment == ExecutionEnvironment.DRY_RUN:
            self._record_decision(symbol, "AUTHORIZED_BUY", ["EDGE_SATISFIED_ALL_POLICIES_PASSED", "DRY_RUN_NO_BROKER_SUBMISSION"])
            self.event_store.record(
                session_id=self.session_id,
                event_type="EXECUTION_AUTHORIZED_DRY_RUN",
                component="RUNTIME",
                symbol=symbol,
                payload={"authorization_id": auth_id, "shares": shares, "target_notional": notional, "decision_price": price},
            )
            return None

        # 12. Update Daily Execution State
        self.symbol_daily_entries.add(symbol)
        self.daily_entries_count += 1

        # 13. Create Order Intent & Submit Idempotently
        intent = OrderIntent.create(
            session_id=self.session_id,
            symbol=symbol,
            side=OrderSide.BUY,
            quantity=shares,
            target_notional=notional,
            limit_price=price,
            stop_loss_price=price * 0.985,  # 1.5% stop
            timestamp=timestamp,
            metadata={"decision_price": price},
        )
        broker_order = self.broker.submit_order(intent)

        # 14. Record Managed Position
        managed = ManagedPosition(
            symbol=symbol,
            shares=shares,
            entry_price=broker_order.avg_fill_price or price,
            current_price=broker_order.avg_fill_price or price,
            entry_timestamp=timestamp,
            stop_loss_price=price * 0.985,
            sector=sector,
        )
        self.open_positions[symbol] = managed
        self._record_decision(symbol, "AUTHORIZED_BUY", ["EDGE_SATISFIED_ALL_POLICIES_PASSED"])

        self.event_store.record(
            session_id=self.session_id,
            event_type="POSITION_OPENED",
            component="PORTFOLIO",
            symbol=symbol,
            payload={"shares": shares, "entry_price": managed.entry_price},
        )
        return broker_order

    def update_position_prices(self, price_map: Dict[str, float]) -> None:
        """Updates MFE/MAE and checks stop-loss / exit conditions."""
        for sym, pos in list(self.open_positions.items()):
            if sym in price_map:
                pos.update_price(price_map[sym])
                # Check stop-loss
                if pos.current_price <= pos.stop_loss_price:
                    logger.info("Stop loss triggered for %s at %.2f", sym, pos.current_price)
                    self.close_position(sym, reason="STOP_LOSS_TRIGGERED")

    def close_position(self, symbol: str, reason: str = "MANUAL") -> Optional[BrokerOrder]:
        if symbol not in self.open_positions:
            return None
        pos = self.open_positions.pop(symbol)
        order = self.broker.close_position(symbol)
        realized = pos.unrealized_pnl
        self.capital_ledger.update_pnl(realized_delta=realized)

        self.event_store.record(
            session_id=self.session_id,
            event_type="POSITION_CLOSED",
            component="PORTFOLIO",
            symbol=symbol,
            payload={"realized_pnl": realized, "reason": reason},
        )
        return order

    def execute_eod_flattening(self) -> List[BrokerOrder]:
        """
        Executes automated flattening window (15:45-15:55 ET) to guarantee zero overnight exposure.
        """
        self.transition_state(RuntimeState.FLATTENING, "Entering automated EOD flattening window.")
        orders = []
        for sym in list(self.open_positions.keys()):
            o = self.close_position(sym, reason="EOD_FLATTEN")
            if o:
                orders.append(o)

        # If unable to flatten any position, record critical operational incident
        if len(self.open_positions) > 0:
            for unflat_sym in list(self.open_positions.keys()):
                self.incidents.append({
                    "incident_id": f"INC_EOD_{unflat_sym}_{uuid.uuid4().hex[:6]}",
                    "type": "UNPLANNED_OVERNIGHT_EXPOSURE",
                    "severity": "CRITICAL_OPERATIONAL_INCIDENT",
                    "symbol": unflat_sym,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
                self.event_store.record(
                    session_id=self.session_id,
                    event_type="UNPLANNED_OVERNIGHT_EXPOSURE",
                    component="PORTFOLIO",
                    severity=EventSeverity.CRITICAL,
                    symbol=unflat_sym,
                    payload={"shares": self.open_positions[unflat_sym].shares},
                )
        return orders

    def finalize_session(self) -> Dict[str, Any]:
        """
        Post-close reconciliation, account journal persistence, and session completion.
        """
        self.transition_state(RuntimeState.POST_CLOSE_RECONCILIATION, "Running post-close reconciliation.")
        rec = self.reconciliation_service.reconcile(self.open_positions, self.capital_ledger)

        self.transition_state(RuntimeState.POST_CLOSE_JOURNAL, "Generating post-close journal.")
        summary = {
            "session_id": self.session_id,
            "date": self.date_str,
            "starting_capital": self.capital_ledger.authorized_strategy_capital,
            "ending_capital": self.capital_ledger.current_strategy_equity,
            "realized_pnl": self.capital_ledger.realized_pnl_dollars,
            "reconciliation_status": rec.status.value,
            "is_flat": len(self.open_positions) == 0,
            "total_decisions": len(self.decision_ledger),
            "total_authorizations": len(self.authorizations),
        }
        self.transition_state(RuntimeState.SESSION_COMPLETE, "Session closed cleanly.")
        return summary

    def halt_trading(self, reason: str = "MANUAL_KILL_SWITCH") -> None:
        self.is_halted = True
        self.transition_state(RuntimeState.HALTED, reason)
        self.event_store.record(
            session_id=self.session_id,
            event_type="EMERGENCY_HALT",
            component="SAFETY",
            severity=EventSeverity.CRITICAL,
            payload={"reason": reason},
        )

    def _record_decision(self, symbol: str, action: str, reason_codes: List[str]) -> None:
        self.decision_ledger.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "symbol": symbol,
            "action": action,
            "reason_codes": reason_codes,
        })
