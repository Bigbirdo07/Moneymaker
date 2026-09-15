"""
Tests for Strategy Allocator Execution Firewall and Governance Isolation (Phase 7F).
"""

import pytest
from src.portfolio.strategy_allocator_research import (
    StrategyAllocationForwardShadowEngine,
    StrategyAllocatorResearchEngine,
    AllocatorExecutionViolation,
)


def test_firewall_blocks_broker_routing():
    shadow = StrategyAllocationForwardShadowEngine()
    with pytest.raises(AllocatorExecutionViolation, match="cannot route broker orders"):
        shadow.route_broker_order({"symbol": "NVDA", "quantity": 100})


def test_firewall_blocks_live_capital_budget_mutation():
    shadow = StrategyAllocationForwardShadowEngine()
    with pytest.raises(AllocatorExecutionViolation, match="cannot mutate live capital authorizations"):
        shadow.mutate_live_capital_budget(12000.0, 8000.0)


def test_firewall_blocks_execution_mode_activation():
    shadow = StrategyAllocationForwardShadowEngine()
    shadow._is_executable = True
    with pytest.raises(AllocatorExecutionViolation, match="attempted to activate execution mode"):
        shadow._assert_firewall_integrity()
