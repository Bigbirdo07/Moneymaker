"""
Tests for Institutional Research Memory (RAG) Corpus & Retrieval.
"""

from src.research.research_memory import ResearchMemory, DocumentType


def test_research_memory_indexing_and_search():
    memory = ResearchMemory()
    results = memory.search("capacity hold Alpha A")

    assert len(results) >= 1
    doc = results[0]
    assert doc.strategy == "ALPHA_A"
    assert doc.document_type == DocumentType.CAPACITY_FINDING
    assert doc.hash is not None
    assert len(doc.hash) == 64


def test_research_memory_evidence_tagging():
    memory = ResearchMemory()
    results = memory.search("Alpha B Tier 2")

    assert len(results) >= 1
    for r in results:
        assert r.evidence_type in ["EMPIRICAL_LIVE", "FORWARD_SHADOW", "STATISTICAL_TEST"]
