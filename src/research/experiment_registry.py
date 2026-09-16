"""
Moneymaker Experiment Registry.
Maintains an immutable ledger of all quantitative research experiments,
tracking code commits, dataset hashes, config hashes, hardware specs,
and strict multi-stage validation states.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import os
from typing import Any, Dict, List, Optional


class ExperimentStatus(str, Enum):
    CREATED = "CREATED"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    CANDIDATE = "CANDIDATE"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ComputeTarget(str, Enum):
    LOCAL_CPU = "LOCAL_CPU"
    LOCAL_GPU = "LOCAL_GPU"
    UNITY_CPU = "UNITY_CPU"
    UNITY_GPU = "UNITY_GPU"
    UNITY_HIGHMEM = "UNITY_HIGHMEM"


@dataclass
class ExperimentRecord:
    experiment_id: str
    created_at: str
    strategy_id: str
    git_commit: str
    dataset_hash: str
    config_hash: str
    code_hash: str
    random_seed: int
    compute_target: ComputeTarget
    status: ExperimentStatus = ExperimentStatus.CREATED
    slurm_job_id: Optional[str] = None
    runtime_seconds: float = 0.0
    hardware_info: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    artifact_paths: List[str] = field(default_factory=list)
    manifest_path: Optional[str] = None
    rejection_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "strategy_id": self.strategy_id,
            "git_commit": self.git_commit,
            "dataset_hash": self.dataset_hash,
            "config_hash": self.config_hash,
            "code_hash": self.code_hash,
            "random_seed": self.random_seed,
            "compute_target": self.compute_target.value,
            "status": self.status.value,
            "slurm_job_id": self.slurm_job_id,
            "runtime_seconds": self.runtime_seconds,
            "hardware_info": self.hardware_info,
            "metrics": self.metrics,
            "artifact_paths": self.artifact_paths,
            "manifest_path": self.manifest_path,
            "rejection_reason": self.rejection_reason,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ExperimentRecord:
        return cls(
            experiment_id=data["experiment_id"],
            created_at=data["created_at"],
            strategy_id=data["strategy_id"],
            git_commit=data["git_commit"],
            dataset_hash=data["dataset_hash"],
            config_hash=data["config_hash"],
            code_hash=data["code_hash"],
            random_seed=data["random_seed"],
            compute_target=ComputeTarget(data["compute_target"]),
            status=ExperimentStatus(data["status"]),
            slurm_job_id=data.get("slurm_job_id"),
            runtime_seconds=data.get("runtime_seconds", 0.0),
            hardware_info=data.get("hardware_info", {}),
            metrics=data.get("metrics", {}),
            artifact_paths=data.get("artifact_paths", []),
            manifest_path=data.get("manifest_path"),
            rejection_reason=data.get("rejection_reason"),
        )


class ExperimentRegistry:
    """
    Central experiment registry for local and Unity HPC research runs.
    """

    def __init__(self, storage_path: str = "outputs/experiments/registry.json") -> None:
        self.storage_path = storage_path
        self._experiments: Dict[str, ExperimentRecord] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    data = json.load(f)
                    for item in data:
                        rec = ExperimentRecord.from_dict(item)
                        self._experiments[rec.experiment_id] = rec
            except Exception:
                pass

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w") as f:
            json.dump([e.to_dict() for e in self._experiments.values()], f, indent=2)

    def create_experiment(
        self,
        experiment_id: str,
        strategy_id: str,
        git_commit: str,
        dataset_hash: str,
        config_hash: str,
        code_hash: str,
        random_seed: int = 42,
        compute_target: ComputeTarget = ComputeTarget.UNITY_GPU,
    ) -> ExperimentRecord:
        rec = ExperimentRecord(
            experiment_id=experiment_id,
            created_at=datetime.now(timezone.utc).isoformat(),
            strategy_id=strategy_id,
            git_commit=git_commit,
            dataset_hash=dataset_hash,
            config_hash=config_hash,
            code_hash=code_hash,
            random_seed=random_seed,
            compute_target=compute_target,
            status=ExperimentStatus.CREATED,
        )
        self._experiments[experiment_id] = rec
        self.save()
        return rec

    def get_experiment(self, experiment_id: str) -> Optional[ExperimentRecord]:
        return self._experiments.get(experiment_id)

    def list_experiments(self) -> List[ExperimentRecord]:
        return list(self._experiments.values())

    def update_status(
        self,
        experiment_id: str,
        status: ExperimentStatus,
        metrics: Optional[Dict[str, Any]] = None,
        slurm_job_id: Optional[str] = None,
        runtime_seconds: Optional[float] = None,
        hardware_info: Optional[Dict[str, Any]] = None,
        rejection_reason: Optional[str] = None,
    ) -> ExperimentRecord:
        rec = self._experiments.get(experiment_id)
        if not rec:
            raise KeyError(f"Experiment {experiment_id} not found in registry.")

        rec.status = status
        if metrics is not None:
            rec.metrics.update(metrics)
        if slurm_job_id is not None:
            rec.slurm_job_id = slurm_job_id
        if runtime_seconds is not None:
            rec.runtime_seconds = runtime_seconds
        if hardware_info is not None:
            rec.hardware_info.update(hardware_info)
        if rejection_reason is not None:
            rec.rejection_reason = rejection_reason

        self.save()
        return rec
