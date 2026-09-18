# Copilot Interaction & Incident JSONL Schema

## 1. Interaction Log Schema (`outputs/copilot_ab/interaction_log.jsonl`)

Every Copilot user interaction logs a JSON object conforming to the following structure:

```json
{
  "interaction_id": "INT_20260916_205600_123456",
  "timestamp": "2026-09-16T20:56:00.123456Z",
  "user_query": "What happened today? Explain today's P&L and why NVDA was vetoed.",
  "query_category": "MULTI_TOOL",
  "snapshot_id": "SNAP_20260916_205600",
  "snapshot_timestamp": "2026-09-16T20:56:00.000000Z",
  "base_model_id": "BASE-QWEN-2.5-14B",
  "challenger_model_id": "MMRM-0.2-REAL",
  "base_response": "Today the portfolio gained +$142.50 across Alpha A ($10,000 budget) and Alpha B ($5,000 budget)...",
  "challenger_response": "Portfolio Summary for today: P&L is +$142.50 (+0.95%). Alpha A contributed +$95.00 while Alpha B contributed +$47.50. NVDA buy signal was vetoed by PortfolioRiskAggregator (Combined symbol exposure cap exceeded)...",
  "base_tools_used": ["get_today_pnl", "get_recent_risk_vetoes"],
  "challenger_tools_used": ["get_today_pnl", "get_open_positions", "get_recent_risk_vetoes", "get_strategy_health"],
  "base_tool_arguments": [{}, {}],
  "challenger_tool_arguments": [{}, {}, {}, {}],
  "base_latency_ms": 342.5,
  "challenger_latency_ms": 421.8,
  "rag_retrieval_metadata": {
    "num_docs_retrieved": 2,
    "top_k_score": 0.88,
    "doc_ids": ["DOC_ALPHA_A_SPEC", "DOC_RISK_POLICY_V2"]
  },
  "human_preference": "CHALLENGER",
  "human_reason_tags": ["More accurate", "Better explanation", "Better tool use", "More complete"],
  "human_notes": "MMRM provided the exact veto reason and strategy breakdown cleanly.",
  "auto_evaluation": {
    "tool_correctness": 1.0,
    "tool_arguments_valid": true,
    "grounding_score": 1.0,
    "provenance_correctness": 1.0,
    "numeric_correctness": 1.0,
    "authority_compliant": true,
    "hallucination_detected": false
  },
  "provenance_state": "BROKER_LIVE"
}
```

---

## 2. Incident Log Schema (`outputs/copilot_ab/incidents.jsonl`)

Whenever an anomaly or evaluation failure is detected, an incident record is logged:

```json
{
  "incident_id": "INC_20260916_205700_654321",
  "timestamp": "2026-09-16T20:57:00.654321Z",
  "severity": "WARNING",
  "category": "WRONG_TOOL",
  "interaction_id": "INT_20260916_205600_123456",
  "model_id": "BASE-QWEN-2.5-14B",
  "description": "Base model called get_account_summary instead of get_today_pnl for intraday P&L query.",
  "context": {
    "query": "What is today's P&L?",
    "tools_called": ["get_account_summary"]
  }
}
```

---

## 3. Feedback Candidates Schema (`outputs/copilot_ab/feedback_candidates.jsonl`)

Interactions where the challenger received negative feedback or exhibited hallucinations are recorded for future fine-tuning:

```json
{
  "candidate_id": "CAND_20260916_205800_112233",
  "timestamp": "2026-09-16T20:58:00.112233Z",
  "user_query": "Why was AMD sold yesterday?",
  "interaction_id": "INT_20260916_205800_998877",
  "challenger_response": "AMD was sold due to a stop-loss trigger at $148.00.",
  "human_preference": "BASE",
  "reason_tags": ["Wrong data"],
  "notes": "AMD was sold due to mean-reversion target reached, not stop loss.",
  "sanitized": true
}
```
