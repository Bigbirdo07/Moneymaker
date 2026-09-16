"""
Tests for Research Memory & Semantic Indexing.
Verifies keyword searching, capacity findings retrieval, and strategy history queries.
"""

from src.research.research_memory import ResearchMemory


def test_research_memory_search():
    rm = ResearchMemory()
    results = rm.search_research_memory("Alpha B capacity curve")
    assert len(results) > 0
    top = results[0]
    assert "Alpha B" in top["title"] or "Capacity" in top["title"]


def test_research_memory_strategy_and_capacity_queries():
    rm = ResearchMemory()
    history = rm.get_model_history("ALPHA_B")
    assert len(history) > 0

    cap_findings = rm.get_previous_capacity_findings()
    assert len(cap_findings) > 0
