"""
Compute Guardrail Module.
Prevents heavy model training, walk-forward validation, and feature generation
from running on the local development workstation.
Directs execution to the UMass Amherst Unity cluster via Slurm.
"""

from __future__ import annotations

import os
import platform
import sys


class LocalHeavyComputeForbiddenError(RuntimeError):
    """Raised when heavy computation is initiated locally without explicit authorization."""
    pass


def assert_cluster_execution(task_name: str = "Heavy Research Workload") -> None:
    """
    Asserts that heavy research tasks are running on the Unity cluster (Linux/Slurm)
    and not on the local development Mac, unless explicitly overridden.
    """
    is_macos = platform.system() == "Darwin"
    allow_override = (
        os.environ.get("MONEYMAKER_ALLOW_LOCAL_HEAVY_COMPUTE", "").lower() in ("1", "true", "yes")
        or "--allow-local-compute" in sys.argv
    )
    is_slurm = "SLURM_JOB_ID" in os.environ

    if is_macos and not allow_override and not is_slurm:
        raise LocalHeavyComputeForbiddenError(
            f"\n"
            f"======================================================================\n"
            f"COMPUTE GUARDRAIL BLOCKED LOCAL EXECUTION: {task_name}\n"
            f"======================================================================\n"
            f"Heavy research execution must NOT run on the local Mac.\n"
            f"Please dispatch to the UMass Amherst Unity cluster using:\n"
            f"\n"
            f"  1. ./scripts/unity/sync_phase10_4_to_unity.sh\n"
            f"  2. ./scripts/unity/submit_phase10_4.sh\n"
            f"\n"
            f"To temporarily override for local unit testing only, set:\n"
            f"  MONEYMAKER_ALLOW_LOCAL_HEAVY_COMPUTE=1  or pass --allow-local-compute\n"
            f"======================================================================\n"
        )
