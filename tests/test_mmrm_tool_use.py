"""
Tests for MMRM-0.1 Structured Tool Use & Sequence Correctness.
"""

from src.workstation.copilot_engine import MoneymakerCopilotEngine
from src.workstation.copilot_tools import CopilotToolRegistry
from src.workstation.models import CopilotChatRequest
from src.workstation.service import WorkstationService


def test_copilot_tool_selection_for_pnl():
    service = WorkstationService()
    registry = CopilotToolRegistry(service=service)
    engine = MoneymakerCopilotEngine(tool_registry=registry)

    req = CopilotChatRequest(message="How much did we make today?")
    res = engine.handle_message(req)

    assert len(res.tool_calls) >= 2
    tool_names = [t.tool_name for t in res.tool_calls]
    assert "get_today_pnl" in tool_names
    assert "get_account_summary" in tool_names
    assert "+$" in res.reply


def test_copilot_tool_selection_for_positions():
    service = WorkstationService()
    registry = CopilotToolRegistry(service=service)
    engine = MoneymakerCopilotEngine(tool_registry=registry)

    req = CopilotChatRequest(message="What open positions do we have?")
    res = engine.handle_message(req)

    assert len(res.tool_calls) >= 1
    tool_names = [t.tool_name for t in res.tool_calls]
    assert "get_open_positions" in tool_names
