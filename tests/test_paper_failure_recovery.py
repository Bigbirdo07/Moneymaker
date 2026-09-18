"""Tests for Paper Runtime Failure Modes & Emergency Kill Switch (Phases F27, F73)."""

import pytest
from src.runtime.paper_trading_runtime import PaperTradingRuntime
from src.broker.simulation_broker import SimulationBrokerAdapter
from src.runtime.runtime_state import RuntimeState


def test_emergency_kill_switch():
    broker = SimulationBrokerAdapter()
    runtime = PaperTradingRuntime(broker_adapter=broker)
    runtime.initialize_session(date_str="2026-09-18")
    runtime.activate_trading()

    # Trigger manual kill switch
    runtime.halt_trading(reason="OPERATOR_OVERRIDE")
    assert runtime.state == RuntimeState.HALTED
    assert runtime.is_halted

    # Verify no new orders permitted while halted
    order = runtime.evaluate_and_execute_candidate(
        symbol="NVDA",
        price=130.0,
        predicted_net_edge_bps=40.0,
        model_confidence=0.70,
        timestamp="2026-09-18T10:30:00Z",
    )
    assert order is None
    assert len(runtime.open_positions) == 0
