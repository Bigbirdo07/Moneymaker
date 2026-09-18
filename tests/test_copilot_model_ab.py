"""
Tests for Workstation Copilot A/B Comparison & Feedback Ingestion.
"""

from fastapi.testclient import TestClient
from src.workstation.api import create_workstation_app


def test_copilot_ab_compare_endpoint():
    app = create_workstation_app()
    client = TestClient(app)

    res = client.post("/api/copilot/ab_compare", json={"prompt": "Why did we buy AMD?"})
    assert res.status_code == 200
    data = res.json()

    assert "base_response" in data
    assert "mmrm_response" in data
    assert "rag_context" in data
    assert data["base_response"]["model_id"] == "BASE-QWEN-2.5-14B"
    assert data["mmrm_response"]["model_id"] in ["MMRM-0.1-QLORA", "MMRM-0.1-REAL", "MMRM-0.2-REAL+RAG", "MMRM-0.2-REAL"]


def test_copilot_ab_feedback_endpoint():
    app = create_workstation_app()
    client = TestClient(app)

    res = client.post(
        "/api/copilot/ab_feedback",
        json={"prompt": "Why did we buy AMD?", "winner": "MMRM_BETTER", "notes": "Clearer grounding"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["entry"]["winner"] == "MMRM_BETTER"
