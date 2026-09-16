"""
Tests for HPC Governance & Asymmetric Isolation.
Verifies that Unity HPC cannot mutate broker credentials, modify live capital,
or automatically promote unvalidated research models.
"""

import pytest
from src.research.experiment_registry import ExperimentRegistry
from src.research.model_registry import ModelApprovalState, ModelRegistry
from src.research.unity_client import UnityGovernanceFirewallViolation, UnityHPCClient


def test_hpc_client_cannot_execute_broker_or_live_capital(tmp_path):
    reg = ExperimentRegistry(storage_path=str(tmp_path / "reg.json"))
    client = UnityHPCClient(registry=reg)

    with pytest.raises(UnityGovernanceFirewallViolation):
        client.submit_job(
            slurm_template="jobs/place_real_money_orders.slurm",
            experiment_id="EXP_UNAUTHORIZED",
            config_path="configs/live_broker.yaml",
        )


def test_model_registry_cannot_auto_promote(tmp_path):
    registry = ModelRegistry(storage_path=str(tmp_path / "models.json"))
    model = registry.get_model("MMRM-0.1-QLORA")
    assert model is not None
    # Model must be CANDIDATE, not automatically active in workstation
    assert model.approval_state == ModelApprovalState.CANDIDATE
    assert model.is_workstation_active is False
