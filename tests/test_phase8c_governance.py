"""
Tests for Phase 8C Governance, Model Promotion Invariants, and Asymmetric Decoupling.
"""

import pytest
from src.research.model_registry import ModelRegistry, ModelApprovalState


def test_alpha_a_and_b_capital_invariance():
    # Capital invariant: Alpha A $10k, Alpha B $5k
    from src.workstation.service import WorkstationService
    service = WorkstationService()
    strategies = service.get_strategy_cards()

    strat_map = {s.strategy_id: s for s in strategies}
    assert strat_map["ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1"].authorized_capital == 10000.0
    assert strat_map["ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1"].authorized_capital == 5000.0


def test_allocator_remains_shadow_only():
    from src.workstation.service import WorkstationService
    service = WorkstationService()
    sys_status = service.get_system_status()
    assert "NON_EXECUTABLE" in sys_status.strategy_allocator or "FORWARD_SHADOW" in sys_status.strategy_allocator


def test_model_cannot_self_promote():
    reg = ModelRegistry()
    with pytest.raises(PermissionError):
        reg.promote_to_workstation_active("MMRM-0.1-QLORA", human_approved=False)
