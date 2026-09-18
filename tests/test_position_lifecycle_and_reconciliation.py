"""Tests for PositionLifecycle and Reconciliation (Phases F22, F28)."""

import pytest
from src.portfolio.position_lifecycle import ManagedPosition, PositionLifecycleState
from src.broker.simulation_broker import SimulationBrokerAdapter
from src.broker.reconciliation import BrokerReconciliationService, ReconciliationStatus
from src.portfolio.strategy_capital_ledger import StrategyCapitalLedger


def test_managed_position_mfe_mae():
    pos = ManagedPosition(
        symbol="AMD",
        shares=10,
        entry_price=100.0,
        current_price=100.0,
        entry_timestamp="2026-09-18T10:00:00Z",
        stop_loss_price=98.5,
    )
    assert pos.unrealized_pnl == 0.0

    pos.update_price(105.0)
    assert pos.unrealized_pnl == 50.0
    assert pos.max_favorable_excursion_dollars == 50.0

    pos.update_price(97.0)
    assert pos.unrealized_pnl == -30.0
    assert pos.max_adverse_excursion_dollars == -30.0


def test_reconciliation_clean_and_mismatch():
    broker = SimulationBrokerAdapter()
    recon = BrokerReconciliationService(broker)
    ledger = StrategyCapitalLedger()

    # Clean empty state
    res = recon.reconcile({}, ledger)
    assert res.status == ReconciliationStatus.CLEAN
    assert res.is_safe_to_operate

    # Mismatch state: internal has position but broker does not
    pos = ManagedPosition(
        symbol="NVDA",
        shares=5,
        entry_price=130.0,
        current_price=130.0,
        entry_timestamp="2026-09-18T10:00:00Z",
        stop_loss_price=128.0,
    )
    res_mismatch = recon.reconcile({"NVDA": pos}, ledger)
    assert res_mismatch.status == ReconciliationStatus.FAILED
    assert not res_mismatch.is_safe_to_operate
    assert len(res_mismatch.unexplained_position_mismatches) > 0
