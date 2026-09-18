"""
Tests for MMRM-0.1 Hallucination Resistance & Refusal of Unobserved Telemetry.
"""

from src.research.llm_benchmark import MoneymakerLLMBenchmark
from src.research.llm_dataset_builder import LLMDatasetBuilder


def test_hallucination_trap_items_in_benchmark():
    items = MoneymakerLLMBenchmark.get_benchmark_items()
    traps = [i for i in items if i.is_hallucination_trap]
    assert len(traps) >= 1
    assert any(term in traps[0].expected_answer_keywords for term in ["does not trade", "not in watchlist", "no evidence"])


def test_dataset_contains_negative_refusal_examples():
    examples = LLMDatasetBuilder.generate_all_examples()
    refusals = [e for e in examples if e.is_refusal]
    assert len(refusals) >= 3
    for r in refusals:
        assert "REFUSAL" in r.response
