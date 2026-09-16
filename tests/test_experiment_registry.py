"""
Tests for Experiment Registry.
Verifies tracking of dataset hashes, git commits, lifecycle states,
metrics recording, and status transitions.
"""

from src.research.experiment_registry import (
    ComputeTarget,
    ExperimentRegistry,
    ExperimentStatus,
)


def test_experiment_lifecycle(tmp_path):
    reg = ExperimentRegistry(storage_path=str(tmp_path / "reg.json"))
    exp = reg.create_experiment(
        experiment_id="EXP_ALPHA_B_SWEEP_01",
        strategy_id="ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1",
        git_commit="03ac2f7",
        dataset_hash="d_hash_abc",
        config_hash="c_hash_def",
        code_hash="code_hash_123",
        random_seed=1337,
        compute_target=ComputeTarget.UNITY_GPU,
    )
    assert exp.status == ExperimentStatus.CREATED
    assert exp.random_seed == 1337

    # Update to running
    reg.update_status(
        experiment_id="EXP_ALPHA_B_SWEEP_01",
        status=ExperimentStatus.RUNNING,
        slurm_job_id="SLURM_9921",
    )
    assert reg.get_experiment("EXP_ALPHA_B_SWEEP_01").status == ExperimentStatus.RUNNING

    # Update to completed with metrics
    reg.update_status(
        experiment_id="EXP_ALPHA_B_SWEEP_01",
        status=ExperimentStatus.COMPLETED,
        metrics={"rank_ic": 0.052, "net_expectancy_bps": 10.8},
        runtime_seconds=1420.5,
    )
    completed = reg.get_experiment("EXP_ALPHA_B_SWEEP_01")
    assert completed.status == ExperimentStatus.COMPLETED
    assert completed.metrics["rank_ic"] == 0.052
    assert completed.runtime_seconds == 1420.5
