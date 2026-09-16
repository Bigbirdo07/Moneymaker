"""
Tests for Moneymaker Workstation REST API.
Verifies all read endpoints, schemas, trade explanations, and copilot chat routes.
"""

import pytest
from fastapi.testclient import TestClient
from src.workstation.api import create_workstation_app


@pytest.fixture
def client():
    app = create_workstation_app()
    return TestClient(app)


def test_api_get_account(client):
    response = client.get("/api/account")
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == "MM-LIVE-001"
    assert data["equity"] > 15000.0
    assert data["cash"] > 0.0
    assert data["evidence_source"] == "BROKER_LIVE"


def test_api_get_portfolio_exposure(client):
    response = client.get("/api/portfolio/exposure")
    assert response.status_code == 200
    data = response.json()
    assert "Alpha A ($10k)" in data["by_strategy"]
    assert "Alpha B ($5k)" in data["by_strategy"]
    assert data["total_authorized"] == 15000.0


def test_api_get_positions(client):
    response = client.get("/api/positions")
    assert response.status_code == 200
    positions = response.json()
    assert len(positions) >= 3
    strategies = {p["strategy"] for p in positions}
    assert any("ALPHA_A" in s for s in strategies)
    assert any("ALPHA_B" in s for s in strategies)


def test_api_get_trades_and_detail(client):
    response = client.get("/api/trades")
    assert response.status_code == 200
    trades = response.json()
    assert len(trades) >= 3
    t0 = trades[0]
    trade_id = t0["trade_id"]

    res_single = client.get(f"/api/trades/{trade_id}")
    assert res_single.status_code == 200
    assert res_single.json()["trade_id"] == trade_id

    res_explain = client.get(f"/api/trades/{trade_id}/explain")
    assert res_explain.status_code == 200
    exp_data = res_explain.json()
    assert exp_data["trade_id"] == trade_id
    assert len(exp_data["risk_checks"]) > 0
    assert "expected_edge" in exp_data


def test_api_get_strategies_and_signals(client):
    res_strats = client.get("/api/strategies")
    assert res_strats.status_code == 200
    strats = res_strats.json()
    assert len(strats) == 2

    res_sig_a = client.get("/api/strategies/ALPHA_A/signals")
    assert res_sig_a.status_code == 200
    assert len(res_sig_a.json()) >= 2

    res_sig_b = client.get("/api/strategies/ALPHA_B/signals")
    assert res_sig_b.status_code == 200
    assert len(res_sig_b.json()) >= 2


def test_api_get_risk_and_vetoes(client):
    res_risk = client.get("/api/risk")
    assert res_risk.status_code == 200
    risk = res_risk.json()
    assert risk["current_drawdown_pct"] == 1.30
    assert risk["var_95_pct"] == 0.46

    res_vetoes = client.get("/api/risk/vetoes")
    assert res_vetoes.status_code == 200
    assert len(res_vetoes.json()) >= 2


def test_api_get_watchlist_and_detail(client):
    res_wl = client.get("/api/market/watchlist")
    assert res_wl.status_code == 200
    wl = res_wl.json()
    assert len(wl) >= 5

    res_detail = client.get("/api/market/AMD/detail")
    assert res_detail.status_code == 200
    detail = res_detail.json()
    assert detail["symbol"] == "AMD"
    assert len(detail["bars_5m"]) > 0


def test_api_briefs_and_system(client):
    for b_type in ["morning", "midday", "closing"]:
        res_b = client.get(f"/api/briefs/{b_type}")
        assert res_b.status_code == 200
        assert res_b.json()["brief_type"] == b_type.upper()

    res_sys = client.get("/api/system")
    assert res_sys.status_code == 200
    assert res_sys.json()["broker_connection"] == "CONNECTED"


def test_api_copilot_chat(client):
    res_chat = client.post("/api/copilot/chat", json={"message": "What happened today?"})
    assert res_chat.status_code == 200
    data = res_chat.json()
    assert "reply" in data
    assert len(data["tool_calls"]) > 0
    assert data["evidence_badge"] == "BROKER_LIVE"
