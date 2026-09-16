"""
Tests for Model Registry & Approval Governance.
Verifies model registration, benchmark score tracking, and promotion state transitions.
"""

from src.research.model_registry import ModelApprovalState, ModelRegistry


def test_model_registry_defaults_and_registration(tmp_path):
    registry = ModelRegistry(storage_path=str(tmp_path / "models.json"))
    models = registry.list_models()
    assert len(models) >= 2

    # Check baseline model
    base = registry.get_model("BASE-QWEN-2.5-14B")
    assert base is not None
    assert base.approval_state == ModelApprovalState.VALIDATED
    assert base.is_workstation_active is True

    # Check candidate fine-tuned model
    qlora = registry.get_model("MMRM-0.1-QLORA")
    assert qlora is not None
    assert qlora.benchmark_score > 90.0
    assert qlora.approval_state == ModelApprovalState.CANDIDATE
