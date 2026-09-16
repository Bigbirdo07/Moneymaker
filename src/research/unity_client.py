"""
Moneymaker Unity HPC Remote Client & Job Orchestrator.
Provides secure SSH/Slurm submission, log streaming, and artifact synchronization.
Enforces strict research-only boundary: zero broker access and zero live config mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import os
import subprocess
from typing import Any, Dict, List, Optional

from src.research.experiment_registry import ComputeTarget, ExperimentRegistry, ExperimentStatus


class UnityGovernanceFirewallViolation(PermissionError):
    """Raised when an unauthorized live trading mutation is attempted via Unity client."""
    pass


@dataclass
class SlurmJobInfo:
    job_id: str
    job_name: str
    partition: str
    status: str
    nodes: int
    cpus: int
    runtime: str
    submit_time: str


class UnityHPCClient:
    """
    Client interface connecting Moneymaker local workstation to UMass Amherst Unity cluster.
    """

    def __init__(
        self,
        remote_host: str = "unity",
        remote_root: str = "/scratch3/workspace/alberto_paz_uri_edu-quahog_neoplasia_analysis/MM",
        registry: Optional[ExperimentRegistry] = None,
    ) -> None:
        self.remote_host = remote_host
        self.remote_root = remote_root
        self.registry = registry or ExperimentRegistry()
        self._mock_mode = os.environ.get("MONEYMAKER_MOCK_UNITY", "1") == "1"

    def submit_job(
        self,
        slurm_template: str,
        experiment_id: str,
        config_path: str,
        compute_target: ComputeTarget = ComputeTarget.UNITY_GPU,
        extra_sbatch_args: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Submits a Slurm job to the Unity cluster for offline research execution.
        """
        # Security firewall: verify this is strictly offline research
        forbidden_terms = ["BROKER", "LIVE_CAPITAL", "ORDER_ROUTER", "KILL_SWITCH", "REAL_MONEY"]
        if any(f in slurm_template.upper() or f in config_path.upper() for f in forbidden_terms):
            raise UnityGovernanceFirewallViolation(
                "FATAL: Unity HPC is restricted to offline research. Live broker operations are forbidden."
            )

        if self._mock_mode:
            # Deterministic mock response for offline/unit-testing environments
            mock_job_id = f"SLURM_{abs(hash(experiment_id)) % 1000000}"
            self.registry.update_status(
                experiment_id=experiment_id,
                status=ExperimentStatus.QUEUED,
                slurm_job_id=mock_job_id,
            )
            return {
                "success": True,
                "job_id": mock_job_id,
                "experiment_id": experiment_id,
                "remote_root": self.remote_root,
                "message": f"Job {mock_job_id} queued on Unity partition for experiment {experiment_id}.",
            }

        # Real SSH sbatch invocation
        cmd = [
            "ssh",
            self.remote_host,
            f"cd {self.remote_root} && sbatch {' '.join(extra_sbatch_args or [])} {slurm_template}",
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            output = res.stdout.strip()
            # Extract job id e.g. "Submitted batch job 1234567"
            job_id = output.split()[-1] if "Submitted batch job" in output else "UNKNOWN"
            self.registry.update_status(
                experiment_id=experiment_id,
                status=ExperimentStatus.QUEUED,
                slurm_job_id=job_id,
            )
            return {
                "success": True,
                "job_id": job_id,
                "experiment_id": experiment_id,
                "output": output,
            }
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": str(e), "stderr": e.stderr}

    def job_status(self, job_id: str) -> Dict[str, Any]:
        """Queries the status of a specific Slurm job."""
        if self._mock_mode:
            return {
                "job_id": job_id,
                "status": "COMPLETED",
                "partition": "uri-gpu",
                "runtime": "01:24:12",
                "nodes": 1,
                "cpus": 8,
            }

        cmd = ["ssh", self.remote_host, f"squeue -j {job_id} --json 2>/dev/null || echo 'NONE'"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return {"job_id": job_id, "raw_status": res.stdout.strip()}

    def list_jobs(self) -> List[Dict[str, Any]]:
        """Lists active Slurm jobs for the current user."""
        if self._mock_mode:
            return [
                {
                    "job_id": "781204",
                    "job_name": "mm_llm_finetune",
                    "partition": "uri-gpu",
                    "status": "RUNNING",
                    "runtime": "00:45:12",
                    "nodes": 1,
                    "cpus": 8,
                },
                {
                    "job_id": "781205",
                    "job_name": "mm_monte_carlo",
                    "partition": "uri-cpu",
                    "status": "COMPLETED",
                    "runtime": "01:12:00",
                    "nodes": 1,
                    "cpus": 32,
                },
            ]

        cmd = ["ssh", self.remote_host, "squeue -u $USER --format='%i|%j|%P|%T|%M|%D|%C' --noheader"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        jobs = []
        for line in res.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|")
            if len(parts) >= 7:
                jobs.append(
                    {
                        "job_id": parts[0],
                        "job_name": parts[1],
                        "partition": parts[2],
                        "status": parts[3],
                        "runtime": parts[4],
                        "nodes": int(parts[5]),
                        "cpus": int(parts[6]),
                    }
                )
        return jobs

    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancels an active job on Unity."""
        if self._mock_mode:
            return {"success": True, "job_id": job_id, "message": f"Job {job_id} cancelled."}

        cmd = ["ssh", self.remote_host, f"scancel {job_id}"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return {"success": res.returncode == 0, "job_id": job_id}

    def fetch_logs(self, job_id: str, lines: int = 50) -> str:
        """Retrieves stdout/stderr log snippets for a job."""
        if self._mock_mode:
            return f"[MOCK LOG FOR JOB {job_id}]\nEpoch 3/3 completed. Training loss: 0.0412. Validation Rank IC: +0.062."

        cmd = ["ssh", self.remote_host, f"tail -n {lines} {self.remote_root}/logs/*{job_id}*.out 2>/dev/null || echo 'No log available.'"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.stdout.strip()
