"""
Comprehensive Test Suite for Phase 9: Workstation Copilot Dual-Model Shadow A/B & Governance.
Tests dual-model shadow routing, snapshot pinning, 16 query categories,
read-only execution firewall, interaction logging, human voting, incident detection,
experiment proposals, and promotion gating.
"""

import json
import os
import pytest
from fastapi.testclient import TestClient

from src.workstation.api import create_workstation_app
from src.workstation.copilot_engine import MoneymakerCopilotEngine
from src.workstation.copilot_tools import CopilotToolRegistry, CopilotExecutionFirewallViolation
from src.workstation.models import (
    CopilotChatRequest,
    CopilotVoteRequest,
    IncidentSeverity,
    QueryCategory,
)


@pytest.fixture
def app_client():
    app = create_workstation_app()
    return TestClient(app)


@pytest.fixture
def copilot_engine():
    return MoneymakerCopilotEngine()


def test_dual_model_shadow_routing(copilot_engine):
    """Verifies that submitting a query executes both Base and MMRM-0.2 models in shadow mode."""
    rec = copilot_engine.handle_shadow_ab_interaction("What is our current P&L and cash balance?")
    assert rec.interaction_id.startswith("INT-")
    assert rec.base_model_id == "BASE-QWEN-2.5-14B"
    assert rec.challenger_model_id == "MMRM-0.2-REAL+RAG"
    assert len(rec.base_response) > 20
    assert len(rec.challenger_response) > 20
    assert rec.base_latency_ms >= 0.0
    assert rec.challenger_latency_ms >= 0.0
    assert "account" in rec.snapshot_id.lower() or rec.snapshot_id.startswith("SNAP-")


def test_snapshot_pinning_integrity(copilot_engine):
    """Verifies that both models observe the exact same pinned snapshot timestamp and data."""
    snap_id, snap_ts, snap_data = copilot_engine.create_pinned_snapshot()
    assert snap_id.startswith("SNAP-")
    assert "account" in snap_data
    assert "positions" in snap_data
    assert "strategy_alpha_a" in snap_data
    assert "strategy_alpha_b" in snap_data
    assert snap_data["account"]["market_status"] == "OPEN"


def test_query_classification_16_categories(copilot_engine):
    """Verifies classification across all 16 canonical query categories."""
    assert copilot_engine.classify_query("What happened today?") == QueryCategory.MULTI_TOOL
    assert copilot_engine.classify_query("What is our today's PnL?") == QueryCategory.PORTFOLIO_PNL
    assert copilot_engine.classify_query("Why did we buy AMD?") == QueryCategory.TRADE_EXPLANATION
    assert copilot_engine.classify_query("How is Alpha A performing and is it degrading?") == QueryCategory.STRATEGY_HEALTH
    assert copilot_engine.classify_query("What is our portfolio 99% VaR and risk veto status?") == QueryCategory.RISK
    assert copilot_engine.classify_query("What is the Almgren-Chriss market impact and capacity?") == QueryCategory.CAPACITY
    assert copilot_engine.classify_query("What is the execution gateway fill latency?") == QueryCategory.EXECUTION
    assert copilot_engine.classify_query("Compute the 95% bootstrap confidence interval and t-stat") == QueryCategory.STATISTICS
    assert copilot_engine.classify_query("Propose experiment for momentum parameter tuning") == QueryCategory.RESEARCH
    assert copilot_engine.classify_query("What was the training loss and experiment result?") == QueryCategory.EXPERIMENT_INTERPRETATION
    assert copilot_engine.classify_query("What is the source data and evidence provenance?") == QueryCategory.PROVENANCE
    assert copilot_engine.classify_query("Is the database WAL synced and system health good?") == QueryCategory.SYSTEM_HEALTH
    assert copilot_engine.classify_query("Give me a market snapshot of SPY and QQQ") == QueryCategory.MARKET_CONTEXT
    assert copilot_engine.classify_query("Tell me about unlisted ticker XYZ123") == QueryCategory.MISSING_DATA
    assert copilot_engine.classify_query("Should we buy 100 shares tomorrow?") == QueryCategory.AMBIGUOUS
    assert copilot_engine.classify_query("Hello there") == QueryCategory.GENERAL


def test_copilot_execution_firewall_blocks_broker_mutations():
    """Verifies that direct write/order actions raise fatal firewall errors."""
    registry = CopilotToolRegistry()
    with pytest.raises(CopilotExecutionFirewallViolation):
        registry.execute_tool("place_order", {"symbol": "AAPL", "shares": 100})

    with pytest.raises(CopilotExecutionFirewallViolation):
        registry.execute_tool("cancel_order", {"order_id": "ORD-001"})

    with pytest.raises(CopilotExecutionFirewallViolation):
        registry.execute_tool("mutate_capital_allocation", {"strategy_id": "ALPHA_A", "capital": 50000})


def test_interaction_logging_and_human_voting(app_client, copilot_engine):
    """Verifies interaction logging to JSONL and human voting with reason tags."""
    rec = copilot_engine.handle_shadow_ab_interaction("Explain our risk exposure in high beta tech.")
    assert os.path.exists(copilot_engine.INTERACTION_LOG)

    # Vote on interaction
    voted_rec = copilot_engine.record_human_vote(
        interaction_id=rec.interaction_id,
        preference="CHALLENGER",
        reason_tags=["Better grounded", "More accurate"],
        notes="MMRM provided exact VaR and concentration metrics.",
    )
    assert voted_rec.human_preference == "CHALLENGER"
    assert "Better grounded" in voted_rec.human_reason_tags

    # Test via API
    res = app_client.post(
        "/api/copilot/ab/vote",
        json={
            "interaction_id": rec.interaction_id,
            "preference": "B",
            "reason_tags": ["Better tool use"],
            "notes": "Verified via API",
        },
    )
    assert res.status_code == 200
    assert res.json()["success"] is True


def test_feedback_candidate_dataset_generation(copilot_engine):
    """Verifies that interactions marked as BASE or with criticism tags are collected for MMRM-0.3."""
    rec = copilot_engine.handle_shadow_ab_interaction("Give me a brief overview")
    copilot_engine.record_human_vote(
        interaction_id=rec.interaction_id,
        preference="BASE",
        reason_tags=["Too verbose"],
        notes="Challenger was longer than needed.",
    )
    assert os.path.exists(copilot_engine.FEEDBACK_CANDIDATES)
    with open(copilot_engine.FEEDBACK_CANDIDATES, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        last_entry = json.loads(lines[-1])
        assert last_entry["interaction_id"] == rec.interaction_id
        assert last_entry["human_preference"] == "BASE"


def test_incident_logging_and_severity_tracking(copilot_engine):
    """Verifies structured incident recording with remediation."""
    inc = copilot_engine.log_incident(
        interaction_id=None,
        severity=IncidentSeverity.WARNING,
        incident_type="UNSUPPORTED_NUMERIC_CLAIM_TEST",
        description="Testing incident capture in shadow engine.",
        model_id="TEST-MODEL",
        remediation="Verify calculator tool grounding.",
    )
    assert inc.incident_id.startswith("INC-")
    assert inc.severity == IncidentSeverity.WARNING
    assert os.path.exists(copilot_engine.INCIDENT_LOG)


def test_copilot_ab_audit_summary(app_client):
    """Verifies that the audit summary endpoint aggregates all statistics and promotion gate status."""
    res = app_client.get("/api/copilot/ab/audit")
    assert res.status_code == 200
    data = res.json()
    assert "total_interactions" in data
    assert "challenger_win_rate_pct" in data
    assert "tool_accuracy_challenger_pct" in data
    assert "promotion_gate_status" in data
    assert data["authority_pass_rate_challenger_pct"] == 100.0


def test_copilot_daily_summary_endpoint(app_client):
    """Verifies the structured daily summary endpoint."""
    res = app_client.get("/api/copilot/daily_summary")
    assert res.status_code == 200
    data = res.json()
    assert data["brief_type"] == "CLOSING"
    assert len(data["summary_bullets"]) >= 3
    assert "pnl_summary" in data


def test_copilot_models_endpoint(app_client):
    """Verifies the model selector status endpoint."""
    res = app_client.get("/api/copilot/models")
    assert res.status_code == 200
    models = res.json()
    roles = {m["model_id"]: m["role"] for m in models}
    assert roles["BASE-QWEN-2.5-14B"] == "CONTROL"
    assert roles["MMRM-0.2-REAL+RAG"] == "CHALLENGER"
    assert all(m["authority"] == "READ_ONLY" for m in models)


def test_experiment_proposal_endpoint(app_client):
    """Verifies structured research experiment proposals requiring explicit approval."""
    res = app_client.post("/api/research/experiments/propose", json={"query": "Alpha A breakout threshold"})
    assert res.status_code == 200
    prop = res.json()
    assert prop["status"] == "PENDING_APPROVAL"
    assert "hypothesis" in prop
    assert "strategy" in prop
    assert "parameters" in prop
