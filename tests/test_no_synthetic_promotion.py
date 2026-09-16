"""
Tests to Ensure Synthetic or Unverified Models Cannot Be Promoted.
"""

import pytest
from src.research.model_registry import ModelRegistry, ModelApprovalState, ModelProvenanceState


def test_unverified_model_cannot_be_promoted():
    reg = ModelRegistry()
    mmrm = reg.get_model("MMRM-0.1-QLORA")
    assert mmrm is not None
    assert mmrm.provenance_state == ModelProvenanceState.UNVERIFIED

    # Attempting candidate promotion with UNVERIFIED provenance must fail
    with pytest.raises(PermissionError, match="provenance audit failed"):
        reg.promote_to_candidate("MMRM-0.1-QLORA")

    # Attempting workstation promotion must also fail
    with pytest.raises(Exception):
        reg.promote_to_workstation_active("MMRM-0.1-QLORA", human_approved=True)
