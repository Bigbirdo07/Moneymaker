"""Tests for Order Intent Idempotency (Phases F19, F20)."""

import pytest
from src.broker.order_intent import OrderIntent, OrderSide, OrderType
from src.broker.simulation_broker import SimulationBrokerAdapter


def test_order_intent_idempotent_creation():
    intent1 = OrderIntent.create(
        session_id="SESSION_01",
        symbol="NVDA",
        side=OrderSide.BUY,
        quantity=5,
        target_notional=650.0,
        timestamp="2026-09-18T10:00:00Z",
    )
    intent2 = OrderIntent.create(
        session_id="SESSION_01",
        symbol="NVDA",
        side=OrderSide.BUY,
        quantity=5,
        target_notional=650.0,
        timestamp="2026-09-18T10:00:00Z",
    )
    assert intent1.order_intent_id == intent2.order_intent_id
    assert intent1.client_order_id == intent2.client_order_id


def test_broker_idempotent_submission():
    broker = SimulationBrokerAdapter()
    broker.set_price("NVDA", 130.0)
    intent = OrderIntent.create(
        session_id="SESSION_01",
        symbol="NVDA",
        side=OrderSide.BUY,
        quantity=5,
        target_notional=650.0,
        timestamp="2026-09-18T10:00:00Z",
    )

    order1 = broker.submit_order(intent)
    order2 = broker.submit_order(intent)

    # Second submission returns existing order without creating duplicate
    assert order1.broker_order_id == order2.broker_order_id
    assert len(broker.orders) == 1
    assert broker.positions["NVDA"] == 5.0
