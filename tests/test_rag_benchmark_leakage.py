"""
Tests for RAG Research Memory Leakage Prevention.
Verifies that benchmark question text and solution keys do not contaminate the institutional retrieval corpus.
"""

from src.research.llm_benchmark import MoneymakerLLMBenchmark
from src.research.research_memory import ResearchMemory


def test_rag_corpus_contains_zero_benchmark_leakage():
    memory = ResearchMemory()
    bm_items = MoneymakerLLMBenchmark.get_benchmark_items()

    for item in bm_items:
        for doc in memory._documents:
            # Check question leakage
            assert item.question.lower() not in doc.content.lower(), f"Leak detected for {item.item_id} in {doc.document_id}"
            # Check ID leakage
            assert item.item_id not in doc.content, f"Item ID {item.item_id} leaked in {doc.document_id}"
