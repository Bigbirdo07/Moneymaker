"""
Tests for Compute Guardrail.
Verifies that local heavy execution is blocked on macOS without explicit override.
"""

import os
import sys
import pytest
from src.core.compute_guard import assert_cluster_execution, LocalHeavyComputeForbiddenError


def test_guardrail_blocks_local_execution(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.delenv("SLURM_JOB_ID", raising=False)
    monkeypatch.delenv("MONEYMAKER_ALLOW_LOCAL_HEAVY_COMPUTE", raising=False)
    if "--allow-local-compute" in sys.argv:
        sys.argv.remove("--allow-local-compute")

    with pytest.raises(LocalHeavyComputeForbiddenError) as exc_info:
        assert_cluster_execution("Test Workload")
    assert "COMPUTE GUARDRAIL BLOCKED LOCAL EXECUTION" in str(exc_info.value)


def test_guardrail_allows_slurm_environment(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Linux")
    monkeypatch.setenv("SLURM_JOB_ID", "64519999")
    # Should not raise
    assert_cluster_execution("Slurm Job Workload")


def test_guardrail_allows_explicit_local_override(monkeypatch):
    monkeypatch.setattr("platform.system", lambda: "Darwin")
    monkeypatch.setenv("MONEYMAKER_ALLOW_LOCAL_HEAVY_COMPUTE", "1")
    # Should not raise
    assert_cluster_execution("Overridden Local Workload")
