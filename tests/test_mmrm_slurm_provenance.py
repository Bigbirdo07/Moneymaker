"""
Tests for Unity HPC Slurm Job Provenance.
Verifies recorded job telemetry for baseline eval, QLoRA fine-tuning, MMRM eval, and RAG embedding.
"""

import json
import os


def test_slurm_job_records_exist_and_match_hardware():
    job_dir = "artifacts/provenance/unity_jobs"
    expected_jobs = ["4892011", "4892408", "4892815", "4893102"]

    for jid in expected_jobs:
        p = os.path.join(job_dir, f"job_{jid}.json")
        assert os.path.exists(p), f"Job record {p} missing"
        with open(p, "r") as f:
            data = json.load(f)

        assert data["job_id"] == jid
        assert data["user"] == "alberto_paz_uri_edu"
        assert data["state"] == "COMPLETED"
        assert data["gpu_model"] == "NVIDIA A100-SXM4-80GB"
        assert data["elapsed_seconds"] > 0
        assert "raw_sacct" in data
        assert "raw_scontrol" in data
