"""
Tests for Model Registry Reconciliation & Provenance Verification.
"""

from src.research.model_registry import ModelRegistry, ModelApprovalState


def test_model_registry_reconciliation_and_audit():
    reg = ModelRegistry()
    mmrm = reg.get_model("MMRM-0.1-QLORA")
    assert mmrm is not None
    assert mmrm.dataset_hash != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    assert len(mmrm.dataset_hash) == 64
    assert mmrm.approval_state == ModelApprovalState.CANDIDATE

    audit = reg.audit_model_training_provenance("MMRM-0.1-QLORA")
    assert audit["status"] == "PROVENANCE_UNVERIFIED"
    assert audit["verified"] is False
