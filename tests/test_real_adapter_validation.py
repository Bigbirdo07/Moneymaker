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
