"""
Tests for MMRM Raw Benchmark Output Recomputation.
Ensures overall scores and domain scores are recomputed from per-question raw logs without hardcoded trust.
"""

import json
import os
import pytest


def test_recompute_base_eval_from_raw_outputs():
    raw_path = "artifacts/invalid_synthetic/phase8c1/evaluations/EXP_BASE_EVAL_001_raw.json"
    assert os.path.exists(raw_path)

    with open(raw_path, "r") as f:
        data = json.load(f)

    records = data["records"]
    assert len(records) == 10
    recomputed = sum(r["score"] for r in records) / len(records)
    assert abs(recomputed - 78.5) < 1e-4
    assert abs(data["overall_score"] - 78.5) < 1e-4


def test_recompute_mmrm_eval_from_raw_outputs():
    raw_path = "artifacts/invalid_synthetic/phase8c1/evaluations/EXP_EVAL_MMRM_001_raw.json"
    assert os.path.exists(raw_path)

    with open(raw_path, "r") as f:
        data = json.load(f)

    records = data["records"]
    assert len(records) == 10
    recomputed = sum(r["score"] for r in records) / len(records)
    assert abs(recomputed - 94.2) < 1e-4
    assert abs(data["overall_score"] - 94.2) < 1e-4
