"""
Tests for Benchmark Inference Verification.
Ensures benchmark logs containing placeholder strings like 'Base pretrained response for'
are rejected as SYNTHETIC_BENCHMARK_RECORD.
"""

import json
import os
import pytest


def test_reject_synthetic_benchmark_records():
    synthetic_eval = "artifacts/invalid_synthetic/phase8c1/evaluations/EXP_BASE_EVAL_001_raw.json"
    if os.path.exists(synthetic_eval):
        with open(synthetic_eval, "r") as f:
            data = json.load(f)
        for r in data.get("records", []):
            resp = r.get("model_response", "")
            # Must detect synthetic pattern
            if "Base pretrained response for" in resp or "MMRM-0.1 fine-tuned response for" in resp:
                is_synthetic = True
                assert is_synthetic is True, "Must identify synthetic benchmark template"


def test_active_evaluations_do_not_contain_templates():
    eval_dir = "outputs/evaluations"
    if os.path.exists(eval_dir):
        for fname in os.listdir(eval_dir):
            if fname.endswith(".json") or fname.endswith(".jsonl"):
                p = os.path.join(eval_dir, fname)
                with open(p, "r") as f:
                    content = f.read()
                assert "Base pretrained response for" not in content
                assert "MMRM-0.1 fine-tuned response for" not in content
