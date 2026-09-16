"""
Tests for Training Dataset Provenance & Scale Review.
Audits example count and ensures prototype scale (17 examples) is explicitly declared.
"""

import os
from src.research.llm_dataset_builder import LLMDatasetBuilder


def test_dataset_scale_is_prototype():
    examples = LLMDatasetBuilder.generate_all_examples()
    total_count = len(examples)

    # Dataset contains exactly 17 prototype examples
    assert total_count == 17
    # Flag that this is a prototype, not a scaled production training set
    assert total_count < 100, "Dataset is a proof-of-concept prototype"


def test_dataset_jsonl_records_match_generator():
    paths = LLMDatasetBuilder.export_dataset("data/moneymaker_llm")
    total_records = 0
    for split, p in paths.items():
        with open(p, "r") as f:
            lines = [l for l in f if l.strip()]
            total_records += len(lines)

    assert total_records == 17
