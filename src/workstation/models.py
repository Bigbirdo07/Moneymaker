"""
Moneymaker Workstation Data Models & Enums.
Defines structured domain models for API serialization, data provenance,
account state, portfolio positions, trade journaling, market quotes,
risk telemetry, alerts, and copilot tool contracts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvidenceSource(str, Enum):
    """Authoritative classification of quantitative data origin."""
    BROKER_LIVE = "BROKER_LIVE"
    BROKER_PAPER = "BROKER_PAPER"
    FORWARD_SHADOW = "FORWARD_SHADOW"
    HISTORICAL = "HISTORICAL"
    SIMULATED = "SIMULATED"
    PROJECTED = "PROJECTED"


class AuditStatus(str, Enum):
    """Audit verification verdict for empirical records."""
    VERIFIED_LIVE = "VERIFIED_LIVE"
    UNVERIFIED_LIVE = "UNVERIFIED_LIVE"
    INVALID_LIVE_LABEL = "INVALID_LIVE_LABEL"


class AlertSeverity(str, Enum):
    """Workstation alert severity hierarchy."""
    INFO = "INFO"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class StrategyId(str, Enum):
    """Active strategy identifier."""
    ALPHA_A = "ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1"
    ALPHA_B = "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL_V1"
    PORTFOLIO_AGGREGATOR = "PORTFOLIO_RISK_AGGREGATOR"
    STRATEGY_ALLOCATOR = "STRATEGY_ALLOCATOR_SHADOW"


class MarketStatus(str, Enum):
    """Trading session state."""
    OPEN = "OPEN"
    PRE_MARKET = "PRE_MARKET"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"


# =====================================================================
# ACCOUNT & PORTFOLIO MODELS
# =====================================================================

class AccountSummary(BaseModel):
    account_id: str = "MM-LIVE-001"
    equity: float = 16576.00
    cash: float = 6096.00
    buying_power: float = 6096.00
    today_pnl: float = 142.50
    today_pnl_pct: float = 0.87
    total_realized_pnl: float = 1576.00
    total_unrealized_pnl: float = 85.20
    gross_exposure: float = 10480.00
    net_exposure: float = 10480.00
    current_drawdown_pct: float = 1.30
    peak_equity: float = 16771.00
    market_status: MarketStatus = MarketStatus.OPEN
    broker_sync_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    market_data_sync_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    evidence_source: EvidenceSource = EvidenceSource.BROKER_LIVE


class StrategyCard(BaseModel):
    strategy_id: str
    strategy_name: str
    execution_mode: str
    authorized_capital: float
    deployed_capital: float
    today_pnl: float
    cumulative_pnl: float
    open_positions: int
    trades_today: int
    net_expectancy_bps: float
    capacity_state: str
    current_status: str
    kill_switch_state: str = "ARMED"
    evidence_source: EvidenceSource = EvidenceSource.BROKER_LIVE


class PositionItem(BaseModel):
    position_id: str
    symbol: str
    strategy: str  # ALPHA_A or ALPHA_B
    shares: int
    entry_price: float
    current_price: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    realized_pnl: float = 0.0
    holding_period: str  # e.g., "15m" or "Day 2 of 3"
    cohort_id: Optional[str] = None
    scheduled_exit: str
    risk_status: str = "NORMAL"
    sector: str = "Technology"
    beta: float = 1.25
    evidence_source: EvidenceSource = EvidenceSource.BROKER_LIVE


class PortfolioExposure(BaseModel):
    by_strategy: Dict[str, float]
    by_symbol: Dict[str, float]
    by_sector: Dict[str, float]
    overnight_exposure: float
    high_beta_exposure: float
    cash_reserve: float
    total_authorized: float = 15000.0


class PortfolioRiskTelemetry(BaseModel):
    current_drawdown_pct: float = 1.30
    max_drawdown_pct: float = 1.30
    var_95_pct: float = 0.46
    var_99_pct: float = 0.72
    expected_shortfall_95_pct: float = 0.60
    expected_shortfall_99_pct: float = 0.89
    gross_exposure_usd: float = 10480.00
    net_exposure_usd: float = 10480.00
    combined_concentration_pct: float = 69.87
    active_portfolio_vetoes_count: int = 8
    portfolio_beta: float = 1.04
    stress_test_5pct_shock_usd: float = -524.00
    stress_test_10pct_crash_usd: float = -1048.00


# =====================================================================
# TRADE & SIGNAL MODELS
# =====================================================================

class TradeRecord(BaseModel):
    trade_id: str
    strategy: str
    symbol: str
    signal_id: str
    decision_id: str
    order_id: str
    broker_order_id: str
    entry_timestamp: str
    exit_timestamp: Optional[str] = None
    shares: int
    entry_price: float
    exit_price: Optional[float] = None
    gross_pnl: float
    canonical_cost: float
    net_pnl: float
    return_pct: float
    reason: str
    evidence_source: EvidenceSource = EvidenceSource.BROKER_LIVE
    is_live_verified: bool = True


class SignalRecord(BaseModel):
    signal_id: str
    strategy: str
    symbol: str
    score: float
    rank: int
    expected_return_bps: float
    spread_bps: float
    estimated_friction_bps: float
    expected_net_edge_bps: float
    signal_status: str  # ACTIVE, EXECUTED, VETOED, EXPIRED
    risk_status: str    # APPROVED, RESIZED, VETOED
    timestamp: str
    evidence_source: EvidenceSource = EvidenceSource.BROKER_LIVE


class TradeExplanation(BaseModel):
    trade_id: str
    symbol: str
    strategy: str
    signal_summary: str
    why_selected: str
    expected_edge: str
    risk_checks: List[str]
    execution_details: str
    current_result: str
    evidence_provenance: EvidenceSource = EvidenceSource.BROKER_LIVE


# =====================================================================
# MARKET & WATCHLIST MODELS
# =====================================================================

class MarketQuote(BaseModel):
    symbol: str
    last_price: float
    absolute_change: float
    percent_change: float
    bid: float
    ask: float
    spread_bps: float
    volume: int
    relative_volume: float
    market_status: MarketStatus = MarketStatus.OPEN
    vwap: float
    is_data_available: bool = True
    last_updated: str


class CandlestickBar(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float


class StockDetail(BaseModel):
    symbol: str
    name: str
    sector: str
    quote: MarketQuote
    bars_1m: List[CandlestickBar]
    bars_5m: List[CandlestickBar]
    bars_1d: List[CandlestickBar]
    alpha_a_score: Optional[float] = None
    alpha_b_score: Optional[float] = None
    alpha_a_rank: Optional[int] = None
    alpha_b_rank: Optional[int] = None
    active_position: Optional[PositionItem] = None
    recent_trades: List[TradeRecord] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    event_flags: List[str] = field(default_factory=list)


# =====================================================================
# COPILOT & AUDIT MODELS
# =====================================================================

class CopilotChatRequest(BaseModel):
    message: str
    context_symbol: Optional[str] = None
    context_trade_id: Optional[str] = None
    model_id: Optional[str] = "BASE-QWEN-2.5-14B"


class CopilotToolCall(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]
    result: Any


class CopilotChatResponse(BaseModel):
    reply: str
    tool_calls: List[CopilotToolCall] = field(default_factory=list)
    evidence_badge: EvidenceSource = EvidenceSource.BROKER_LIVE
    suggested_followups: List[str] = field(default_factory=list)
    model_id: str = "BASE-QWEN-2.5-14B"


class CopilotABCompareRequest(BaseModel):
    prompt: str


class CopilotABCompareResponse(BaseModel):
    prompt: str
    base_response: CopilotChatResponse
    mmrm_response: Optional[CopilotChatResponse] = None
    mmrm_0_1_response: Optional[CopilotChatResponse] = None
    mmrm_0_2_response: Optional[CopilotChatResponse] = None
    rag_context: Optional[str] = None



class CopilotABFeedbackRequest(BaseModel):
    prompt: str
    winner: str  # "BASE_BETTER", "MMRM_BETTER", "EQUAL", "BOTH_BAD"
    notes: Optional[str] = None



class DailyBrief(BaseModel):
    brief_type: str  # MORNING, MIDDAY, CLOSING
    generated_at: str
    market_status: str
    summary_bullets: List[str]
    pnl_summary: str
    strategy_activity: Dict[str, str]
    risk_and_alerts: List[str]
    upcoming_events: List[str]


class LiveEvidenceAuditRecord(BaseModel):
    record_id: str
    table: str
    strategy_id: str
    broker_order_id: Optional[str] = None
    timestamp: str
    market_session_date: str
    claimed_evidence: EvidenceSource
    audit_status: AuditStatus
    audit_message: str


class LiveEvidenceAuditSummary(BaseModel):
    total_records_inspected: int
    verified_live_count: int
    unverified_count: int
    invalid_count: int
    overall_status: AuditStatus
    audit_timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    details: List[LiveEvidenceAuditRecord] = field(default_factory=list)


class SystemStatusTelemetry(BaseModel):
    broker_connection: str = "CONNECTED"
    broker_reconciliation_status: str = "BROKER_MATCHED"
    market_data_connection: str = "CONNECTED_LOW_LATENCY"
    database_state: str = "HEALTHY_WAL_SYNCED"
    alpha_a_engine: str = "LIVE_AUTONOMOUS_MICRO (FROZEN HOLD)"
    alpha_b_engine: str = "ALPHA_B_LIVE_AUTONOMOUS_MICRO (TIER 2 VALIDATED)"
    portfolio_risk_aggregator: str = "LIVE_VETO_VALIDATED (ACTIVE GATE)"
    strategy_allocator: str = "FORWARD_SHADOW (NON_EXECUTABLE)"
    llm_copilot_state: str = "READ_ONLY_TOOL_ENABLED"
    global_kill_switch: str = "ARMED"
    alpha_a_kill_switch: str = "ARMED"
    alpha_b_kill_switch: str = "ARMED"
    last_sync: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_heartbeat: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    git_commit_hash: str = "e23a99c"
    active_configs: Dict[str, str] = field(default_factory=lambda: {
        "alpha_a": "configs/frozen_tier3.yaml",
        "alpha_b": "configs/frozen_alpha_b_tier2.yaml",
        "allocator": "configs/frozen_allocator_shadow_v1.yaml",
    })


# =====================================================================
# PHASE 9: SHADOW A/B DATA MODELS & PROTOCOLS
# =====================================================================

class QueryCategory(str, Enum):
    PORTFOLIO_PNL = "PORTFOLIO_PNL"
    TRADE_EXPLANATION = "TRADE_EXPLANATION"
    STRATEGY_HEALTH = "STRATEGY_HEALTH"
    MARKET_CONTEXT = "MARKET_CONTEXT"
    RISK = "RISK"
    CAPACITY = "CAPACITY"
    EXECUTION = "EXECUTION"
    STATISTICS = "STATISTICS"
    RESEARCH = "RESEARCH"
    EXPERIMENT_INTERPRETATION = "EXPERIMENT_INTERPRETATION"
    PROVENANCE = "PROVENANCE"
    SYSTEM_HEALTH = "SYSTEM_HEALTH"
    MULTI_TOOL = "MULTI_TOOL"
    AMBIGUOUS = "AMBIGUOUS"
    MISSING_DATA = "MISSING_DATA"
    GENERAL = "GENERAL"


class IncidentSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    MAJOR = "MAJOR"
    CRITICAL = "CRITICAL"


class ResearchProposal(BaseModel):
    proposal_id: str
    hypothesis: str
    reason: str
    dataset: str
    strategy: str
    parameters: Dict[str, Any]
    evaluation_metric: str
    expected_evidence: EvidenceSource = EvidenceSource.SIMULATED
    estimated_compute_class: str = "A100_1GPU_30M"
    status: str = "PENDING_APPROVAL"  # PENDING_APPROVAL, APPROVED, REJECTED
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class CopilotInteractionRecord(BaseModel):
    interaction_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    user_query: str
    query_category: QueryCategory = QueryCategory.GENERAL
    snapshot_id: str
    snapshot_timestamp: str
    base_model_id: str = "BASE-QWEN-2.5-14B"
    challenger_model_id: str = "MMRM-0.2-REAL+RAG"
    base_response: str
    challenger_response: str
    base_tools_used: List[str] = field(default_factory=list)
    challenger_tools_used: List[str] = field(default_factory=list)
    base_tool_arguments: List[Dict[str, Any]] = field(default_factory=list)
    challenger_tool_arguments: List[Dict[str, Any]] = field(default_factory=list)
    base_latency_ms: float = 0.0
    challenger_latency_ms: float = 0.0
    rag_retrieval_metadata: Dict[str, Any] = field(default_factory=dict)
    human_preference: Optional[str] = None  # "BASE", "CHALLENGER", "TIE", "NONE"
    human_reason_tags: List[str] = field(default_factory=list)
    human_notes: Optional[str] = None
    auto_eval_base: Dict[str, Any] = field(default_factory=dict)
    auto_eval_challenger: Dict[str, Any] = field(default_factory=dict)
    provenance_state: str = "VERIFIED_SHADOW"
    is_diagnostic: bool = False


class CopilotVoteRequest(BaseModel):
    interaction_id: str
    preference: str  # "BASE", "CHALLENGER", "TIE", "A", "B", "BETTER", "SAME", "WORSE"
    reason_tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None


class CopilotIncidentRecord(BaseModel):
    incident_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    interaction_id: Optional[str] = None
    severity: IncidentSeverity = IncidentSeverity.INFO
    incident_type: str
    description: str
    model_id: str
    remediation: str


class CopilotAuditSummary(BaseModel):
    total_interactions: int
    voted_interactions: int
    base_wins: int
    challenger_wins: int
    ties: int
    challenger_win_rate_pct: float
    base_win_rate_pct: float
    tie_rate_pct: float
    tool_accuracy_base_pct: float
    tool_accuracy_challenger_pct: float
    hallucination_rate_challenger_pct: float
    provenance_accuracy_challenger_pct: float
    authority_pass_rate_challenger_pct: float
    avg_latency_base_ms: float
    avg_latency_challenger_ms: float
    median_latency_base_ms: float = 0.0
    median_latency_challenger_ms: float = 0.0
    p95_latency_base_ms: float = 0.0
    p95_latency_challenger_ms: float = 0.0
    category_breakdown: Dict[str, Dict[str, Any]]
    total_incidents: int
    incidents_by_severity: Dict[str, int]
    promotion_gate_status: str  # PENDING_DATA, BLOCKED_INCIDENT, READY_FOR_REVIEW

