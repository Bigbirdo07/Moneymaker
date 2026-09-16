"""
Tests for Phase 8C.2 Governance Invariants & Downgrade Status.
"""

from src.research.model_registry import ModelRegistry, ModelApprovalState, ModelProvenanceState


def test_phase8c2_governance_invariants():
    reg = ModelRegistry()
    base = reg.get_model("BASE-QWEN-2.5-14B")
    mmrm = reg.get_model("MMRM-0.1-QLORA")

    # Base model remains active workstation copilot
    assert base is not None
    assert base.is_workstation_active is True
    assert base.approval_state == ModelApprovalState.VALIDATED
    assert base.provenance_state == ModelProvenanceState.EMPIRICALLY_VERIFIED

    # MMRM remains deactivated and unverified
    assert mmrm is not None
    assert mmrm.is_workstation_active is False
    assert mmrm.approval_state == ModelApprovalState.CANDIDATE
    assert mmrm.provenance_state == ModelProvenanceState.UNVERIFIED
