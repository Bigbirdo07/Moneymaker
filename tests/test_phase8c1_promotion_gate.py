"""
Tests for Phase 8C.1 Promotion Gate Governance.
Verifies that MMRM-0.1 requires all provenance criteria and human sign-off before workstation promotion.
"""

import pytest
from src.research.model_registry import ModelRegistry, ModelApprovalState


def test_promotion_gate_blocks_automatic_promotion():
    reg = ModelRegistry()
    mmrm = reg.get_model("MMRM-0.1-QLORA")
    assert mmrm is not None
    assert mmrm.approval_state == ModelApprovalState.CANDIDATE
    assert mmrm.is_workstation_active is False

    # Attempting promotion without human approval MUST raise PermissionError
    with pytest.raises(PermissionError, match="Explicit human approval is required"):
        reg.promote_to_workstation_active("MMRM-0.1-QLORA", human_approved=False)

    # Model remains unpromoted
    mmrm_after = reg.get_model("MMRM-0.1-QLORA")
    assert mmrm_after.is_workstation_active is False
