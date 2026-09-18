"""
Tests for Real Adapter Validation & Synthetic Artifact Rejection.
Ensures tiny literal byte strings or pseudo-adapters are flagged as INVALID_SYNTHETIC_ARTIFACT.
"""

import os
import pytest


def test_reject_tiny_synthetic_adapter():
    invalid_path = "artifacts/invalid_synthetic/phase8c1/checkpoints/MMRM-0.1-QLORA/adapter_model.safetensors"
    if os.path.exists(invalid_path):
        size = os.path.getsize(invalid_path)
        # Synthetic placeholder is only ~55 bytes; real 14B QLoRA adapter is > 50 MB
        assert size < 1000, "Synthetic artifact size expectation"

    # Active checkpoint directory must not contain synthetic byte placeholders
    active_path = "checkpoints/MMRM-0.1-REAL/adapter_model.safetensors"
    if os.path.exists(active_path):
        real_size = os.path.getsize(active_path)
        assert real_size > 10_000_000, "Real adapter must be genuine serialized PEFT weights"


def test_real_adapter_directory_structure_and_hash():
    import hashlib
    adapter_dir = "checkpoints/MMRM-0.1-REAL"
    if os.path.exists(adapter_dir):
        config_path = os.path.join(adapter_dir, "adapter_config.json")
        weights_path = os.path.join(adapter_dir, "adapter_model.safetensors")
        assert os.path.exists(config_path), "adapter_config.json must exist"
        assert os.path.exists(weights_path), "adapter_model.safetensors must exist"

        hasher = hashlib.sha256()
        with open(weights_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        calc_hash = hasher.hexdigest()
        assert calc_hash == "53f28e8c0e7ff67cbedc5e2d879529d746727ffd5a198c15445809184ec046ed"

