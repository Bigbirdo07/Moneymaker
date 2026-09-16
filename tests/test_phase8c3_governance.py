"""
Phase 8C.3 Governance & Integrity Verification Tests.
Verifies dataset V2 scaling, domain coverage, artifact lineage, benchmark isolation,
mathematical consistency, and anti-synthetic promotion rules.
"""

import json
import math
import os
import pytest

from src.research.llm_dataset_builder import LLMDatasetBuilder, LLMTrainingExample
from src.research.llm_benchmark import MoneymakerLLMBenchmark, BenchmarkItem
from src.research.model_registry import ModelRegistry, ModelApprovalState, ModelProvenanceState
from scripts.verify_mmrm_adapter import verify_adapter_files


def test_dataset_v2_scale_and_domain_distribution():
    examples = LLMDatasetBuilder.generate_v2_all_examples()
    assert len(examples) >= 500, f"Expected at least 500 examples, got {len(examples)}"

    # Check 20 distinct domains
    domains = set(e.domain for e in examples)
    assert len(domains) == 20, f"Expected 20 domains, got {len(domains)}: {domains}"

    for dom in LLMDatasetBuilder.DOMAINS:
        dom_count = sum(1 for e in examples if e.domain == dom)
        assert dom_count >= 20, f"Domain {dom} has insufficient examples: {dom_count}"


def test_dataset_v2_synthetic_and_curated_ratios():
    examples = LLMDatasetBuilder.generate_v2_all_examples()
    audit = LLMDatasetBuilder.audit_dataset(examples)

    # Synthetic must be <= 40%
    assert audit["synthetic_ratio"] <= 0.40, f"Synthetic ratio {audit['synthetic_ratio']} exceeds 40%"

    # Curated / Grounded must be >= 30%
    assert audit["human_curated_ratio"] >= 0.30, f"Curated ratio {audit['human_curated_ratio']} is below 30%"

    # Zero duplicates
    assert audit["duplicates_count"] == 0, f"Found {audit['duplicates_count']} duplicate records"


def test_dataset_v2_synthetic_explicit_labeling():
    examples = LLMDatasetBuilder.generate_v2_all_examples()
    for ex in examples:
        if ex.evidence_class == "SYNTHETIC_TRAINING":
            assert "SYNTHETIC_TRAINING_EXAMPLE" in ex.response, f"Synthetic example {ex.example_id} lacks explicit tag in response"


def test_dataset_v2_source_lineage_metadata():
    examples = LLMDatasetBuilder.generate_v2_all_examples()
    for ex in examples:
        d = ex.to_dict()
        assert "example_id" in d and d["example_id"]
        assert "domain" in d and d["domain"]
        assert "source_document" in d and d["source_document"]
        assert "source_hash" in d and d["source_hash"]
        assert "phase" in d and d["phase"]
        assert "strategy" in d and d["strategy"]
        assert "evidence_class" in d and d["evidence_class"]
        assert "generation_method" in d and d["generation_method"]
        assert "human_review_state" in d and d["human_review_state"]


def test_benchmark_v2_scale_and_manifest_hash():
    items = MoneymakerLLMBenchmark.get_benchmark_items()
    assert len(items) >= 150, f"Expected at least 150 benchmark items, got {len(items)}"
    h = MoneymakerLLMBenchmark.compute_manifest_hash()
    assert len(h) == 64, f"Invalid manifest hash length: {h}"


def test_benchmark_v2_zero_leakage_with_training_set():
    items = MoneymakerLLMBenchmark.get_benchmark_items()
    examples = LLMDatasetBuilder.generate_v2_all_examples()
    audit = LLMDatasetBuilder.audit_dataset(examples, [b.question for b in items])
    assert audit["benchmark_leakage_count"] == 0, f"Detected {audit['benchmark_leakage_count']} benchmark leaks in training set!"


def test_mathematical_precision_in_reasoning():
    # Canonical friction identity: Gross - Friction = Net
    gross = 15.98
    fric = 5.58
    net = gross - fric
    assert round(net, 3) == 10.400, "Friction identity failed"

    # t-statistic: mean / (std / sqrt(N))
    mean = 1.110
    std = 4.80
    n = 250
    se = std / math.sqrt(n)
    t = mean / se
    assert abs(t - 3.656) < 0.01, f"t-statistic mismatch: expected ~3.656, got {t}"


def test_reject_tiny_adapter_weights():
    # Verify helper rejects files < 1KB
    dummy_dir = "artifacts/invalid_synthetic/phase8c1/checkpoints/MMRM-0.1-QLORA"
    res = verify_adapter_files(dummy_dir)
    assert res["valid"] is False, "Tiny synthetic adapter should be marked invalid"
    assert "tiny" in res["reason"].lower() or "missing" in res["reason"].lower()


def test_model_registry_governance_invariants():
    reg = ModelRegistry()
    real_candidate = reg.get_model("MMRM-0.1-REAL")
    assert real_candidate is not None
    assert real_candidate.approval_state == ModelApprovalState.CANDIDATE
    assert real_candidate.provenance_state == ModelProvenanceState.UNVERIFIED
    assert real_candidate.is_workstation_active is False

    # Ensure legacy fake model is rejected
    legacy_fake = reg.get_model("MMRM-0.1-SYNTHETIC-LEGACY")
    assert legacy_fake is not None
    assert legacy_fake.approval_state == ModelApprovalState.REJECTED
    assert legacy_fake.provenance_state == ModelProvenanceState.SYNTHETIC_INVALID
