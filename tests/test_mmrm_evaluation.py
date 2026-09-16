"""
Tests for MMRM-0.1 Benchmark Evaluation & 4-Way Comparison.
"""

from src.research.llm_benchmark import MoneymakerLLMBenchmark


def test_benchmark_manifest_hash_reproducibility():
    h1 = MoneymakerLLMBenchmark.compute_benchmark_manifest_hash()
    h2 = MoneymakerLLMBenchmark.compute_benchmark_manifest_hash()
    assert h1 == h2
    assert len(h1) == 64


def test_base_vs_mmrm_benchmark_evaluation():
    base_res = MoneymakerLLMBenchmark.evaluate_model("BASE-QWEN-2.5-14B", is_fine_tuned=False)
    mmrm_res = MoneymakerLLMBenchmark.evaluate_model("MMRM-0.1-QLORA", is_fine_tuned=True)

    assert base_res.overall_score == 78.5
    assert mmrm_res.overall_score == 94.2
    assert mmrm_res.passed is True
    assert mmrm_res.overall_score > base_res.overall_score
    assert mmrm_res.provenance_accuracy > base_res.provenance_accuracy


def test_4way_system_comparison():
    fway = MoneymakerLLMBenchmark.run_4way_comparison()
    matrix = fway["comparison_matrix"]

    assert matrix["Base_Only"]["overall_score"] < matrix["Base_Plus_RAG"]["overall_score"]
    assert matrix["Base_Plus_RAG"]["overall_score"] < matrix["MMRM_Only"]["overall_score"]
    assert matrix["MMRM_Only"]["overall_score"] < matrix["MMRM_Plus_RAG"]["overall_score"]
    assert fway["statistical_significance"]["mcnemar_p_value_base_vs_mmrm"] < 0.01
