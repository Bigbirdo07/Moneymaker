"""
Unit tests for Launch Readiness and Invalidation Checks (Phase F Operational Safety).
"""

import hashlib
import json
from pathlib import Path
import pytest

from src.broker.execution_environment import ExecutionEnvironment, validate_execution_environment, RealMoneyAuthorizationError
from src.broker.alpaca_paper_broker import AlpacaPaperBrokerAdapter
from src.broker.simulation_broker import SimulationBrokerAdapter
from src.broker.order_intent import OrderSide, BrokerFill, OrderIntent
from src.runtime.market_clock import MarketClockService
from src.runtime.runtime_health import RuntimeHealthMonitor, StayAwakeGuard, HealthStatus
from src.runtime.paper_trading_runtime import PaperTradingRuntime, PolicyTamperError
from scripts.verify_launch_readiness import (
    verify_dynamic_universe,
    verify_implementation_shortfall,
    verify_alpaca_paper_guard,
    verify_policy_and_manifest_hash,
    verify_market_clock_and_timezone,
    verify_stay_awake_and_continuity,
    verify_emergency_halt_and_flatten,
)


def test_launch_readiness_check1_dynamic_universe():
    is_valid, details = verify_dynamic_universe()
    assert is_valid is True
    assert details["status"] == "PASS"
    assert details["top_100_count"] == 100
    assert details["top_250_count"] == 250
    assert details["fallback_to_50_names_detected"] is False


def test_launch_readiness_check2_implementation_shortfall():
    is_valid, details = verify_implementation_shortfall()
    assert is_valid is True
    assert details["status"] == "PASS"
    assert details["buy_shortfall_bps"] == 2.0
    assert details["sell_shortfall_bps"] == 3.0
    assert details["is_default_zero_detected"] is False


def test_launch_readiness_check3_alpaca_paper_guard():
    is_valid, details = verify_alpaca_paper_guard()
    assert is_valid is True
    assert details["status"] == "PASS"
    assert "paper" in details["adapter_base_url"]
    assert details["live_endpoint_rejection_verified"] is True
    assert details["live_environment_rejection_verified"] is True


def test_launch_readiness_check4_policy_and_manifest_hash():
    is_valid, details = verify_policy_and_manifest_hash()
    assert is_valid is True
    assert details["status"] == "PASS"
    assert details["hash_match"] is True


def test_launch_readiness_check5_market_clock_and_timezone():
    is_valid, details = verify_market_clock_and_timezone()
    assert is_valid is True
    assert details["status"] == "PASS"
    assert details["trading_start_cooldown"] == "09:35:00"
    assert details["flatten_window_start"] == "15:45:00"


def test_launch_readiness_check6_stay_awake_and_continuity():
    is_valid, details = verify_stay_awake_and_continuity()
    assert is_valid is True
    assert details["status"] == "PASS"
    assert details["stay_awake_guard_supported"] is True


def test_launch_readiness_check7_emergency_halt_and_flatten():
    is_valid, details = verify_emergency_halt_and_flatten()
    assert is_valid is True
    assert details["status"] == "PASS"
    assert details["is_100_percent_flat"] is True
