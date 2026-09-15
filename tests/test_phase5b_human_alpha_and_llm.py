"""
Unit and Integration Tests for Phase 5B:
1. Human-Alpha Decomposition & Blinded Approval Gate
2. Operator Reason Codes & Latency Cost Tracking
3. Four-Book Multi-Execution Tracking (Books A, B, C, D)
4. RAG Knowledge Base Retrieval
5. Moneymaker Research Director (Read-Only Isolation, Provenance, & Refusal)
"""

from datetime import datetime, timezone
import pytest
import pandas as pd
import numpy as np

from src.data.market_provider import QuoteEvent
from src.governance.human_approval import (
    ApprovalAction,
    ApprovalDisplayMode,
    HumanApprovalGate,
    HumanApprovalRecord,
    OperatorReasonCode,
    ProposedOrderCard,
)
from src.governance.autonomous_counterfactual import (
    FourBookComparisonRecord,
    FourBookExecutionLedger,
)
from src.llm.rag_knowledge_base import RAGKnowledgeBase, KnowledgeDocument
from src.llm.research_director import (
    DataProvenanceType,
    ExecutionQualitySummary,
    LLMOutputType,
    ModelHealthSummary,
    MoneymakerResearchDirector,
    ProvenanceStatement,
    ResearchDirectorOutput,
    RiskSummary,
    SessionSummary,
)


def _make_quote(symbol: str, price: float = 125.0, spread_bps: float = 2.0, ts: pd.Timestamp = None) -> QuoteEvent:
    if ts is None:
        ts = pd.Timestamp("2026-09-15 14:00:00", tz=timezone.utc)
    half_spread = price * (spread_bps / 20000.0)
    return QuoteEvent(
        symbol=symbol,
        bid=price - half_spread,
        ask=price + half_spread,
        bid_size=100.0,
        ask_size=100.0,
        exchange_timestamp=ts - pd.Timedelta(milliseconds=15),
        provider_timestamp=ts - pd.Timedelta(milliseconds=5),
        received_timestamp=ts,
    )


def test_blinded_vs_full_information_card_rendering():
    """Verify blinded safety-only card hides predictive fields while full info shows them."""
    now = pd.Timestamp("2026-09-15 14:00:00", tz="UTC")
    card = ProposedOrderCard(
        proposal_id="PROP_BLIND_001",
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        current_bid=125.00,
        current_ask=125.02,
        spread_bps=1.6,
        expected_alpha_bps=4.8,
        estimated_friction_bps=2.6,
        expected_net_edge_bps=2.2,
        model_confidence=0.62,
        rank=1,
        current_portfolio_exposure_usd=0.0,
        daily_realized_pnl_usd=0.0,
        max_allowed_loss_usd=20.0,
        trade_reason="Stage-A Micro-Pilot Entry",
        risk_engine_status="APPROVED",
        display_mode=ApprovalDisplayMode.SAFETY_ONLY,
    )

    blind_text = card.render_display()
    assert "SAFETY-ONLY MODE" in blind_text
    assert "PREDICTIVE ALPHA / CONFIDENCE / RANK HIDDEN" in blind_text
    assert "Confidence:" not in blind_text
    assert "Expected Alpha:" not in blind_text

    # Full information mode
    card.display_mode = ApprovalDisplayMode.FULL_INFORMATION
    full_text = card.render_display()
    assert "Confidence: 62.0%" in full_text
    assert "Expected Alpha:     +4.8 bps" in full_text
    assert "Top-1 Opportunity" in full_text


def test_operator_reason_codes_and_latency_costs():
    """Verify structured reason codes and latency cost attribution."""
    gate = HumanApprovalGate(approval_timeout_seconds=30.0)
    now = pd.Timestamp("2026-09-15 14:00:00", tz="UTC")

    card = ProposedOrderCard(
        proposal_id="PROP_REASON_001",
        symbol="TSLA",
        side="BUY",
        shares=0.10,
        notional_usd=25.0,
        decision_timestamp=now,
        current_bid=250.00,
        current_ask=250.04,
        spread_bps=1.6,
        expected_alpha_bps=4.5,
        estimated_friction_bps=2.5,
        expected_net_edge_bps=2.0,
        model_confidence=0.60,
        rank=1,
        current_portfolio_exposure_usd=0.0,
        daily_realized_pnl_usd=0.0,
        max_allowed_loss_usd=20.0,
        trade_reason="Stage-A Entry",
        risk_engine_status="APPROVED",
    )
    gate.submit_proposal(card)

    # Operator rejects with structured code
    quote = _make_quote("TSLA", price=250.02, spread_bps=1.6, ts=now + pd.Timedelta(seconds=10))
    can_exec, reason = gate.process_operator_action(
        proposal_id="PROP_REASON_001",
        operator_id="OPERATOR_ALPHA",
        action=ApprovalAction.HUMAN_DISCRETIONARY_REJECT,
        current_time=now + pd.Timedelta(seconds=12),
        current_quote=quote,
        reason_code=OperatorReasonCode.EXTENDED_MOVE,
    )
    assert can_exec is False
    assert "HUMAN_DISCRETIONARY_REJECTED_EXTENDED_MOVE" in reason

    record = gate.approval_records[0]
    assert record.reason_code == OperatorReasonCode.EXTENDED_MOVE
    assert record.operator_latency_sec == 12.0


def test_human_alpha_decomposition_and_incremental_value():
    """Test mathematical calculation of human incremental alpha across sets."""
    gate = HumanApprovalGate()
    now = pd.Timestamp("2026-09-15 14:00:00", tz="UTC")

    # Add synthetic records: 5 approved (mean +4.8 bps), 2 rejected (mean +1.0 bps)
    for i in range(5):
        r = HumanApprovalRecord(
            proposal_id=f"PROP_A_{i}",
            symbol="NVDA",
            operator_id="OP_1",
            action=ApprovalAction.APPROVE,
            display_mode=ApprovalDisplayMode.FULL_INFORMATION if i % 2 == 0 else ApprovalDisplayMode.SAFETY_ONLY,
            decision_timestamp=now,
            operator_action_timestamp=now + pd.Timedelta(seconds=10),
            operator_latency_sec=10.0,
            decision_midprice=120.0,
            approval_midprice=120.01,
            human_latency_cost_bps=0.8,
            future_15m_return_bps=4.8,
        )
        gate.approval_records.append(r)

    for j in range(2):
        r = HumanApprovalRecord(
            proposal_id=f"PROP_R_{j}",
            symbol="AMD",
            operator_id="OP_1",
            action=ApprovalAction.HUMAN_DISCRETIONARY_REJECT,
            display_mode=ApprovalDisplayMode.FULL_INFORMATION,
            decision_timestamp=now,
            operator_action_timestamp=now + pd.Timedelta(seconds=8),
            operator_latency_sec=8.0,
            decision_midprice=150.0,
            approval_midprice=150.0,
            human_latency_cost_bps=0.0,
            reason_code=OperatorReasonCode.BAD_MARKET_CONTEXT,
            future_15m_return_bps=1.0,
        )
        gate.approval_records.append(r)

    decomp = gate.compute_human_alpha_decomposition()
    assert decomp["total_proposals"] == 7
    assert decomp["approved_count"] == 5
    assert decomp["discretionary_rejected_count"] == 2
    assert abs(decomp["approved_mean_return_bps"] - 4.8) < 1e-4
    assert abs(decomp["rejected_mean_return_bps"] - 1.0) < 1e-4
    assert decomp["human_incremental_alpha_bps"] > 0.0  # Positive operator value-add


def test_four_book_execution_ledger_comparison():
    """Test comparative matrix calculation across Books A, B, C, D."""
    ledger = FourBookExecutionLedger(initial_cash=1000.0)
    now = pd.Timestamp("2026-09-15 14:00:00", tz="UTC")

    card = ProposedOrderCard(
        proposal_id="PROP_4BOOK_001",
        symbol="NVDA",
        side="BUY",
        shares=0.20,
        notional_usd=25.0,
        decision_timestamp=now,
        current_bid=125.00,
        current_ask=125.02,
        spread_bps=1.6,
        expected_alpha_bps=4.8,
        estimated_friction_bps=2.6,
        expected_net_edge_bps=2.2,
        model_confidence=0.62,
        rank=1,
        current_portfolio_exposure_usd=0.0,
        daily_realized_pnl_usd=0.0,
        max_allowed_loss_usd=20.0,
        trade_reason="Stage-A Entry",
        risk_engine_status="APPROVED",
    )

    # Record 10 sample trades with positive alpha
    for i in range(10):
        ledger.record_decision_cycle(
            card=card,
            operator_record=None,
            live_executed=True,
            live_fill_price=125.02,
            future_gross_return_bps=4.80,
        )

    matrix = ledger.compute_summary_matrix()
    assert "Book_A_Live_Governed" in matrix
    assert "Book_B_Realistic_Shadow" in matrix
    assert "Book_C_Broker_Paper" in matrix
    assert "Book_D_Autonomous_Counterfactual" in matrix

    # All books should maintain positive net expectancy
    assert matrix["Book_A_Live_Governed"]["net_expectancy_bps"] > 0.0
    assert matrix["Book_D_Autonomous_Counterfactual"]["net_expectancy_bps"] > 0.0
    assert matrix["Book_A_Live_Governed"]["trade_count"] == 10


def test_rag_knowledge_base_indexing_and_retrieval():
    """Test document chunking, indexing, and keyword/term retrieval."""
    kb = RAGKnowledgeBase(chunk_size=50, chunk_overlap=10)
    doc_content = (
        "Phase 5A governed micro-capital pilot established strict $1,000 capital ceiling. "
        "ExecutionMode.LIVE remains fatal blocked. Human approval gate has 30 second timeout. "
        "The champion model uses XGBoost with Platt Scaling calibration and 15 minute horizon."
    )
    kb.index_document("PHASE_5A_TEST", "Phase 5A Summary", "POLICY", "/path/test.md", doc_content)

    results = kb.query("capital ceiling timeout", top_k=2)
    assert len(results) > 0
    assert "1,000" in results[0].chunk
    assert results[0].doc_id == "PHASE_5A_TEST"


def test_moneymaker_research_director_read_only_and_refusal():
    """Verify Research Director is strictly read-only, refuses hallucinations, and categorizes provenance."""
    kb = RAGKnowledgeBase()
    kb.index_document(
        "GOV_POLICY",
        "Governance Policy",
        "POLICY",
        "configs/frozen_phase5a.yaml",
        "MAX_LIVE_CAPITAL_USD is 1000. Margin, shorting, and options are strictly prohibited.",
    )

    director = MoneymakerResearchDirector(knowledge_base=kb)
    assert director.is_read_only is True

    # 1. Answer governance query grounded in knowledge base
    ans = director.answer_governance_query("capital ceiling margin shorting")
    assert "1000" in ans["answer"]
    assert len(ans["citations"]) > 0

    # 2. Refusal / UNKNOWN for missing facts
    ans_unknown = director.answer_governance_query("quantum gravitational arbitrage non-existent strategy")
    assert "UNKNOWN" in ans_unknown["answer"]

    # 3. Session Review generation
    sess = SessionSummary(
        session_date="2026-09-15",
        total_candidates=5,
        approved_count=4,
        rejected_count=1,
        expired_count=0,
        executed_fills=4,
        gross_alpha_bps=4.80,
        total_friction_bps=3.35,
        net_expectancy_bps=1.45,
        realized_pnl_usd=1.20,
        symbols_traded=["NVDA", "AMD"],
        max_drawdown_usd=0.50,
    )
    risk = RiskSummary(
        capital_ceiling_usd=1000.0,
        current_equity_usd=1001.20,
        daily_realized_loss_usd=0.0,
        daily_loss_limit_usd=20.0,
        pilot_drawdown_usd=0.50,
        max_drawdown_limit_usd=50.0,
        reconciliation_errors_count=0,
        unrelated_holdings_count=0,
        margin_borrowing_usd=0.0,
    )
    exec_qual = ExecutionQualitySummary(
        mean_spread_bps=1.65,
        mean_implementation_shortfall_bps=1.52,
        live_slippage_penalty_bps=0.12,
        passive_fill_rate_pct=63.5,
        mean_time_to_fill_sec=2.1,
        mean_operator_latency_sec=11.2,
    )
    model_health = ModelHealthSummary(
        model_version="CHAMPION_PHASE_5A",
        spearman_rank_ic=0.048,
        rank_ic_p_value=0.006,
        meta_label_precision=0.57,
        feature_drift_detected=False,
        cusum_alarm_active=False,
        status="HEALTHY",
    )

    review = director.generate_session_review(sess, risk, exec_qual, model_health)
    assert review.output_type == LLMOutputType.SESSION_REVIEW
    assert len(review.provenance_statements) == 5
    assert review.provenance_statements[0].provenance_type == DataProvenanceType.OBSERVED_DATA

    # 4. Anomaly detection & challenger hypothesis generation
    exec_qual_degraded = ExecutionQualitySummary(
        mean_spread_bps=3.50,
        mean_implementation_shortfall_bps=2.80,
        live_slippage_penalty_bps=0.85, # Elevated
        passive_fill_rate_pct=50.0,
        mean_time_to_fill_sec=5.0,
        mean_operator_latency_sec=15.0,
    )
    anomaly_output = director.detect_anomalies_and_drift(exec_qual_degraded, model_health, risk)
    assert anomaly_output.output_type == LLMOutputType.ANOMALY
    assert len(anomaly_output.hypotheses) > 0
    assert len(anomaly_output.proposed_experiments) > 0
