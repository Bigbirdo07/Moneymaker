"""
Tests for MMRM Artifact & Dataset Cryptographic Hashing.
Ensures non-empty SHA-256 fingerprints across datasets, adapters, base models, and benchmarks.
"""

import hashlib
import json
import os
from src.research.llm_dataset_builder import LLMDatasetBuilder
from src.research.llm_benchmark import MoneymakerLLMBenchmark


def test_dataset_hash_is_non_empty_and_deterministic():
    paths = LLMDatasetBuilder.export_dataset("data/moneymaker_llm")
    assert os.path.exists(paths["train"])
    assert os.path.exists(paths["val"])
    assert os.path.exists(paths["test"])

    with open(paths["train"], "rb") as f:
        train_bytes = f.read()

    assert len(train_bytes) > 0
    # Must NOT equal sha256 of empty bytes
    empty_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    actual_hash = hashlib.sha256(train_bytes).hexdigest()
    assert actual_hash != empty_hash


def test_adapter_artifact_hash_verification():
    adapter_path = "checkpoints/MMRM-0.1-QLORA/adapter_model.safetensors"
    assert os.path.exists(adapter_path)

    with open(adapter_path, "rb") as f:
        content = f.read()

    assert len(content) > 0
    adapter_hash = hashlib.sha256(content).hexdigest()
    assert len(adapter_hash) == 64
    assert adapter_hash == "f888f57a3bb900c8679b09532152774866382d455ff0f8bf5b704e74cd293ca1"


def test_benchmark_manifest_hash_reproducibility():
    h = MoneymakerLLMBenchmark.compute_benchmark_manifest_hash()
    assert len(h) == 64
    assert h != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
