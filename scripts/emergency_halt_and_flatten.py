#!/usr/bin/env python3
"""
Emergency Manual Halt and Flatten Utility for Moneymaker (Phase F / Operational Safety).

Instantly halts trading, cancels all open orders across the paper broker,
flattens all open positions at market, logs a CRITICAL operational incident,
and verifies 100% flat cash state.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, List

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from src.broker.execution_environment import ExecutionEnvironment, validate_execution_environment
from src.broker.alpaca_paper_broker import AlpacaPaperBrokerAdapter
from src.broker.simulation_broker import SimulationBrokerAdapter
from src.broker.order_intent import OrderSide, OrderType, OrderIntent
from src.broker.reconciliation import BrokerReconciliationService
from src.portfolio.strategy_capital_ledger import StrategyCapitalLedger

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("scripts.emergency_halt_and_flatten")


def execute_emergency_halt_and_flatten(
    broker_type: str = "alpaca",
    reason: str = "MANUAL_OPERATIONAL_KILL_SWITCH",
    output_dir: Path = REPO_ROOT,
) -> Dict[str, Any]:
    """
    Executes unconditional halt and market flattening of all paper broker orders & positions.
    """
    logger.warning("======================================================================")
    logger.warning("EMERGENCY KILL SWITCH TRIGGERED: %s", reason)
    logger.warning("======================================================================")

    # 1. Initialize Broker Adapter
    if broker_type.lower() == "alpaca":
        broker = AlpacaPaperBrokerAdapter()
    else:
        broker = SimulationBrokerAdapter()

    # 2. Cancel All Open Orders
    open_orders = broker.get_open_orders()
    canceled_orders = []
    for order in open_orders:
        success = broker.cancel_order(order.broker_order_id)
        canceled_orders.append({
            "broker_order_id": order.broker_order_id,
            "symbol": order.symbol,
            "side": str(order.side),
            "quantity": order.quantity,
            "canceled": success,
        })
        logger.warning("Canceled open order: %s (%s %d %s)", order.broker_order_id, order.symbol, order.quantity, str(order.side))

    # 3. Close All Open Positions
    open_positions = broker.get_positions()
    flattened_positions = []
    for sym, shares in open_positions.items():
        if abs(shares) > 1e-5:
            close_order = broker.close_position(sym)
            flattened_positions.append({
                "symbol": sym,
                "shares_closed": shares,
                "close_order_id": close_order.broker_order_id if close_order else "NONE",
            })
            logger.warning("Flattened open position: %s (%d shares closed)", sym, int(shares))

    # 4. Verify Final Account State
    account = broker.get_account()
    remaining_positions = broker.get_positions()
    is_flat = len(remaining_positions) == 0

    # 5. Record Critical Operational Incident
    timestamp = datetime.now(timezone.utc).isoformat()
    incident_record = {
        "incident_id": f"INC_EMERGENCY_HALT_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "timestamp": timestamp,
        "type": "MANUAL_EMERGENCY_HALT_AND_FLATTEN",
        "severity": "CRITICAL",
        "reason": reason,
        "canceled_orders_count": len(canceled_orders),
        "flattened_positions_count": len(flattened_positions),
        "is_flat": is_flat,
        "ending_equity": account.equity,
        "ending_cash": account.cash,
    }

    # Write audit log
    audit_path = output_dir / "artifacts" / "emergency_halt_audit.json"
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    existing_audits = []
    if audit_path.exists():
        try:
            with open(audit_path, "r") as f:
                existing_audits = json.load(f)
        except Exception:
            existing_audits = []
    existing_audits.append(incident_record)
    with open(audit_path, "w") as f:
        json.dump(existing_audits, f, indent=2)

    logger.warning("======================================================================")
    logger.warning("EMERGENCY FLATTEN COMPLETE: Status = %s", "100% FLAT" if is_flat else "FAILED_TO_FLATTEN")
    logger.warning("Orders Canceled    : %d", len(canceled_orders))
    logger.warning("Positions Closed   : %d", len(flattened_positions))
    logger.warning("Account Cash       : $%.2f", account.cash)
    logger.warning("Account Equity     : $%.2f", account.equity)
    logger.warning("======================================================================")

    return incident_record


def main():
    parser = argparse.ArgumentParser(description="Moneymaker Emergency Halt & Flatten")
    parser.add_argument("--broker", type=str, default="alpaca", choices=["alpaca", "sim"], help="Broker adapter to halt")
    parser.add_argument("--reason", type=str, default="MANUAL_OPERATIONAL_KILL_SWITCH", help="Reason for emergency halt")
    args = parser.parse_args()

    execute_emergency_halt_and_flatten(broker_type=args.broker, reason=args.reason)


if __name__ == "__main__":
    main()
