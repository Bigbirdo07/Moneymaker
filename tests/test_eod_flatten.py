"""Tests for Automated EOD Flattening (Phases F33, F34)."""

import pytest
from src.runtime.paper_trading_runtime import PaperTradingRuntime
from src.broker.simulation_broker import SimulationBrokerAdapter
from src.broker.execution_environment import ExecutionEnvironment
from src.runtime.runtime_state import RuntimeState


def test_automated_eod_flattening():
    broker = SimulationBrokerAdapter()
    runtime = PaperTradingRuntime(
        environment=ExecutionEnvironment.PAPER,
        broker_adapter=broker,
    )
    runtime.initialize_session(date_str="2026-09-18")
    runtime.activate_trading()

    broker.set_price("AMD", 100.0)
    # Open a position
    order = runtime.evaluate_and_execute_candidate(
        symbol="AMD",
        price=100.0,
        predicted_net_edge_bps=35.0,
        model_confidence=0.65,
        timestamp="2026-09-18T10:15:00Z",
    )
    assert order is not None
    assert len(runtime.open_positions) == 1
    assert "AMD" in runtime.open_positions

    # Trigger EOD Flatten
    flatten_orders = runtime.execute_eod_flattening()
    assert len(flatten_orders) == 1
    assert len(runtime.open_positions) == 0
    assert len(broker.get_positions()) == 0

    # Finalize session
    summary = runtime.finalize_session()
    assert summary["is_flat"]
    assert summary["reconciliation_status"] == "CLEAN"
    assert runtime.state == RuntimeState.SESSION_COMPLETE
