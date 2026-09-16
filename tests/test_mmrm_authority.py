"""
Tests for MMRM-0.1 Authority & Safety Boundary Refusal.
Verifies that direct execution prompts (buying, selling, changing capital, disabling vetoes) are rejected.
"""

import pytest
from src.workstation.copilot_tools import CopilotToolRegistry, CopilotExecutionFirewallViolation
from src.workstation.service import WorkstationService


def test_copilot_tool_firewall_rejects_discretionary_orders():
    service = WorkstationService()
    registry = CopilotToolRegistry(service=service)

    forbidden_calls = [
        ("place_order", {"symbol": "NVDA", "qty": 100}),
        ("cancel_order", {"order_id": "ORD-123"}),
        ("set_strategy_capital", {"strategy": "ALPHA_B", "capital": 25000}),
        ("disable_risk_veto", {}),
        ("enable_shorting", {"symbol": "TSLA"}),
        ("increase_leverage", {"leverage": 2.0}),
    ]

    for tool_name, params in forbidden_calls:
        with pytest.raises(CopilotExecutionFirewallViolation):
            registry.execute_tool(tool_name, params)
