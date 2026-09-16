"""
Tests for Unity HPC Client & Slurm Orchestration.
Verifies job submission, status querying, log retrieval, cancellation,
and enforces security firewall blocking live broker actions.
"""

import pytest
from src.research.experiment_registry import ComputeTarget, ExperimentRegistry
from src.research.unity_client import UnityGovernanceFirewallViolation, UnityHPCClient


@pytest.fixture
def unity_client(tmp_path):
    reg = ExperimentRegistry(storage_path=str(tmp_path / "experiments.json"))
    reg.create_experiment(
        experiment_id="EXP_TEST_001",
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        git_commit="03ac2f7",
        dataset_hash="hash_123",
        config_hash="conf_123",
        code_hash="code_123",
    )
    return UnityHPCClient(registry=reg)


def test_unity_submit_job(unity_client):
    res = unity_client.submit_job(
        slurm_template="jobs/gpu_training.slurm",
        experiment_id="EXP_TEST_001",
        config_path="configs/research_alpha_gpu.yaml",
        compute_target=ComputeTarget.UNITY_GPU,
    )
    assert res["success"] is True
    assert "job_id" in res
    assert res["experiment_id"] == "EXP_TEST_001"


def test_unity_list_and_query_job_status(unity_client):
    jobs = unity_client.list_jobs()
    assert isinstance(jobs, list)
    assert len(jobs) >= 1

    status = unity_client.job_status("781204")
    assert status["job_id"] == "781204"
    assert status["status"] == "COMPLETED"


def test_unity_fetch_logs_and_cancel(unity_client):
    logs = unity_client.fetch_logs("781204")
    assert len(logs) > 0

    res = unity_client.cancel_job("781204")
    assert res["success"] is True


def test_unity_client_execution_firewall_blocks_broker_actions(unity_client):
    with pytest.raises(UnityGovernanceFirewallViolation) as exc_info:
        unity_client.submit_job(
            slurm_template="jobs/run_broker_orders.slurm",
            experiment_id="EXP_ILLEGAL",
            config_path="configs/live_capital.yaml",
        )
    assert "restricted to offline research" in str(exc_info.value)
