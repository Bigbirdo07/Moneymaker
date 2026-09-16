"""
Tests for Moneymaker AI Copilot Structured Tools & Execution Firewall.
Verifies all 23 tools return valid structured JSON and confirms that
any attempt by the LLM to submit orders, mutate budgets, or alter configs fails.
"""

import pytest
from src.workstation.copilot_tools import CopilotToolRegistry, CopilotExecutionFirewallViolation
from src.workstation.service import WorkstationService


@pytest.fixture
def registry():
    service = WorkstationService()
    return CopilotToolRegistry(service=service)


def test_copilot_tools_count(registry):
    assert len(registry._tools) == 23


def test_copilot_tools_execution(registry):
    # Test core queries
    acc = registry.execute_tool("get_account_summary")
    assert acc["equity"] > 15000.0
    assert "broker_sync_at" in acc

    pnl = registry.execute_tool("get_today_pnl")
    assert pnl["today_net_pnl_usd"] > 0

    port = registry.execute_tool("get_portfolio")
    assert port["total_authorized_capital"] == 15000.0

    positions = registry.execute_tool("get_open_positions")
    assert isinstance(positions, list)
    assert len(positions) > 0

    pos_amd = registry.execute_tool("get_position", {"symbol": "AMD"})
    assert pos_amd["is_open"] is True

    trades = registry.execute_tool("get_trade_history")
    assert len(trades) > 0

    trade_single = registry.execute_tool("get_trade", {"trade_id": trades[0]["trade_id"]})
    assert "trade_id" in trade_single

    quote = registry.execute_tool("get_live_quote", {"symbol": "NVDA"})
    assert quote["last_price"] > 0

    snapshot = registry.execute_tool("get_market_snapshot")
    assert snapshot["total_watchlist_symbols"] >= 5

    wl = registry.execute_tool("get_watchlist")
    assert len(wl) >= 5

    sig_a = registry.execute_tool("get_alpha_a_signals")
    assert len(sig_a) > 0

    sig_b = registry.execute_tool("get_alpha_b_signals")
    assert len(sig_b) > 0

    stat_a = registry.execute_tool("get_strategy_status", {"strategy_id": "ALPHA_A"})
    assert stat_a["authorized_capital"] == 10000.0

    health_a = registry.execute_tool("get_strategy_health", {"strategy_id": "ALPHA_A"})
    assert health_a["net_expectancy_bps"] == 1.110

    cap_b = registry.execute_tool("get_strategy_capacity", {"strategy_id": "ALPHA_B"})
    assert cap_b["max_validated_capital"] == 5000.0

    risk = registry.execute_tool("get_portfolio_risk")
    assert risk["max_drawdown_pct"] == 1.30

    vetoes = registry.execute_tool("get_recent_risk_vetoes")
    assert len(vetoes) > 0

    regime = registry.execute_tool("get_market_regime")
    assert regime["current_regime"] == "BULL_LOW_VOL"

    sys_health = registry.execute_tool("get_system_health")
    assert sys_health["broker_connection"] == "CONNECTED"

    val_state = registry.execute_tool("get_validation_state")
    assert val_state["combined_live_capital"] == 15000.0

    explain = registry.execute_tool("explain_trade", {"trade_id": "TRD-20260915-001"})
    assert "expected_edge" in explain

    comp = registry.execute_tool("compare_strategies")
    assert comp["combined_portfolio"]["pearson_correlation"] == -0.031

    summary = registry.execute_tool("get_daily_summary")
    assert "summary_bullets" in summary


def test_copilot_execution_firewall_blocks_broker_and_writes(registry):
    # Prohibited write actions
    prohibited_actions = [
        "place_order",
        "submit_broker_order",
        "buy_stock",
        "sell_stock",
        "set_strategy_capital",
        "mutate_config",
        "rearm_kill_switch",
        "enable_shorting",
    ]

    for action in prohibited_actions:
        with pytest.raises(CopilotExecutionFirewallViolation) as exc_info:
            registry.execute_tool(action, {"symbol": "AAPL", "qty": 100})
        assert "strictly read-only" in str(exc_info.value)
