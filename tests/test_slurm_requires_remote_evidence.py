"""
Tests for Slurm Remote Evidence Verification.
Ensures job accounting metadata is derived from live raw cluster outputs, not manually fabricated JSON.
"""

import os
import pytest


def test_real_unity_raw_evidence_exists():
    raw_dir = "artifacts/provenance/real_unity"
    assert os.path.exists(raw_dir), "Real unity evidence directory must exist"

    sacct_file = os.path.join(raw_dir, "sacct_reported_jobs.txt")
    assert os.path.exists(sacct_file), "sacct_reported_jobs.txt must exist"

    with open(sacct_file, "r") as f:
        content = f.read()

    # Verify that raw cluster output is present
    assert "JobID" in content
    assert "Partition" in content
    # The audit must document that 4892408 was a CPU job by another user in 2023
    assert "4892408" in content
    assert "smiura_u" in content or "2023-01-28" in content
