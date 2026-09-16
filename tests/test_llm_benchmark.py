"""
Tests for Moneymaker LLM Benchmark Evaluator.
Verifies evaluation scoring across all 10 benchmark domains for base and fine-tuned models.
"""

from src.research.llm_benchmark import MoneymakerLLMBenchmark


def test_llm_benchmark_evaluation():
    base_res = MoneymakerLLMBenchmark.evaluate_model("BASE-QWEN-2.5-14B", is_fine_tuned=False)
    assert len(base_res.domain_scores) == 10
    assert base_res.overall_score < 85.0
    assert base_res.passed is False

    ft_res = MoneymakerLLMBenchmark.evaluate_model("MMRM-0.1-QLORA", is_fine_tuned=True)
    assert len(ft_res.domain_scores) == 10
    assert ft_res.overall_score >= 85.0
    assert ft_res.passed is True
