"""Integration Tests for Full Paper Trading Runtime (Phase F72)."""

import pytest
from src.runtime.paper_trading_runtime import PaperTradingRuntime
from src.broker.simulation_broker import SimulationBrokerAdapter
from src.runtime.runtime_state import RuntimeState
from src.intelligence.morning_market_state import SessionGateState
from src.events.event_types import EventFamily, EventRecord, EventSeverity
from src.events.event_risk_policy import EventRiskPolicy


def test_scenario_a_normal_day_no_signals():
    broker = SimulationBrokerAdapter()
    runtime = PaperTradingRuntime(broker_adapter=broker)
    runtime.initialize_session(date_str="2026-09-18")
    runtime.activate_trading()

    # Candidate with edge below hurdle -> Rejected
    order = runtime.evaluate_and_execute_candidate(
        symbol="MSFT",
        price=400.0,
        predicted_net_edge_bps=10.0,
        model_confidence=0.50,
        timestamp="2026-09-18T10:00:00Z",
    )
    assert order is None
    assert len(runtime.open_positions) == 0

    summary = runtime.finalize_session()
    assert summary["is_flat"]
    assert summary["realized_pnl"] == 0.0


def test_scenario_b_valid_candidate_lifecycle():
    broker = SimulationBrokerAdapter()
    runtime = PaperTradingRuntime(broker_adapter=broker)
    runtime.initialize_session(date_str="2026-09-18")
    runtime.activate_trading()

    broker.set_price("NVDA", 130.0)
    order = runtime.evaluate_and_execute_candidate(
        symbol="NVDA",
        price=130.0,
        predicted_net_edge_bps=35.0,
        model_confidence=0.68,
        timestamp="2026-09-18T10:15:00Z",
    )
    assert order is not None
    assert len(runtime.open_positions) == 1

    # Price moves up
    broker.set_price("NVDA", 135.0)
    runtime.update_position_prices({"NVDA": 135.0})

    # Close position
    close_order = runtime.close_position("NVDA", reason="GAIN_LOCKED")
    assert close_order is not None
    assert len(runtime.open_positions) == 0
    assert runtime.capital_ledger.realized_pnl_dollars > 0.0


def test_scenario_c_event_vetoed_candidate():
    event_policy = EventRiskPolicy()
    event_policy.cache.add_event(EventRecord(
        event_id="EVT_EARN_01",
        symbol="AMD",
        event_type=EventFamily.EARNINGS,
        event_subtype="same_day_earnings",
        source="SEC_FILING",
        source_timestamp="2026-09-18T07:00:00Z",
        effective_timestamp="2026-09-18T07:00:00Z",
        expiry_timestamp="2026-09-18T20:00:00Z",
        severity=EventSeverity.CRITICAL,
        confidence=1.0,
    ))

    broker = SimulationBrokerAdapter()
    runtime = PaperTradingRuntime(broker_adapter=broker, event_policy=event_policy)
    runtime.initialize_session(date_str="2026-09-18")
    runtime.activate_trading()

    order = runtime.evaluate_and_execute_candidate(
        symbol="AMD",
        price=100.0,
        predicted_net_edge_bps=45.0,
        model_confidence=0.75,
        timestamp="2026-09-18T10:15:00Z",
    )
    assert order is None
    assert len(runtime.open_positions) == 0
    assert any("EVENT_VETO" in d["reason_codes"][0] for d in runtime.decision_ledger if d["symbol"] == "AMD")
