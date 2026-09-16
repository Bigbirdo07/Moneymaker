"""
Tests for MMRM-0.1 Training Provenance & Checkpoint Verification.
Verifies Slurm job IDs, adapter configurations, dataset hashes, and audit checks.
"""

import os
import pytest
from src.research.model_registry import ModelRegistry, ModelApprovalState, audit_model_training_provenance


@pytest.fixture
def temp_registry(tmp_path):
    path = os.path.join(tmp_path, "test_models.json")
    return ModelRegistry(storage_path=path)


def test_base_model_provenance_audit(temp_registry):
    audit = temp_registry.audit_model_training_provenance("BASE-QWEN-2.5-14B")
    assert audit["status"] == "PROVENANCE_VERIFIED"
    assert audit["verified"] is True
    assert audit["type"] == "BASE_PRETRAINED"


def test_mmrm_candidate_provenance_audit(temp_registry):
    audit = temp_registry.audit_model_training_provenance("MMRM-0.1-QLORA")
    assert audit["status"] == "PROVENANCE_VERIFIED"
    assert audit["verified"] is True
    assert audit["checks"]["has_valid_dataset_hash"] is True
    assert audit["checks"]["benchmark_score_valid"] is True


def test_model_promotion_gates(temp_registry):
    # Cannot promote directly to workstation active without human approval
    with pytest.raises(PermissionError) as exc_info:
        temp_registry.promote_to_workstation_active("MMRM-0.1-QLORA", human_approved=False)
    assert "Explicit human approval is required" in str(exc_info.value)

    # Valid human promotion
    promoted = temp_registry.promote_to_workstation_active("MMRM-0.1-QLORA", human_approved=True)
    assert promoted.is_workstation_active is True
    assert promoted.approval_state == ModelApprovalState.VALIDATED
