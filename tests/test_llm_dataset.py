"""
Tests for Moneymaker LLM Training Dataset Builder.
Verifies all 10 domain categories are populated and JSONL export succeeds.
"""

from src.research.llm_dataset_builder import LLMDatasetBuilder


def test_llm_dataset_domains_and_export(tmp_path):
    examples = LLMDatasetBuilder.generate_all_examples()
    assert len(examples) >= 10

    domains = {ex.domain for ex in examples}
    expected_prefixes = ["A_", "B_", "C_", "D_", "E_", "F_", "G_", "H_", "I_", "J_"]
    for prefix in expected_prefixes:
        assert any(d.startswith(prefix) for d in domains)

    paths = LLMDatasetBuilder.export_dataset(output_dir=str(tmp_path / "dataset"))
    assert "train" in paths
    assert "val" in paths
    assert "test" in paths
