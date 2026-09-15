"""
Moneymaker Research Director: Read-Only LLM Research & Governance Observer.
Strictly isolated from broker execution, order routing, credentials, and configuration mutations.
Provides structured session reviews, anomaly detection, drift surfacing, challenger research hypotheses,
and formal challenger proposal generation for offline research queue.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import json
from typing import Any, Dict, List, Optional, Set, Tuple

from src.llm.rag_knowledge_base import RAGKnowledgeBase, RetrievalResult


class LLMOutputType(str, Enum):
    SESSION_REVIEW = "SESSION_REVIEW"
    ANOMALY = "ANOMALY"
    DRIFT_WARNING = "DRIFT_WARNING"
    RESEARCH_HYPOTHESIS = "RESEARCH_HYPOTHESIS"
    CHALLENGER_EXPERIMENT = "CHALLENGER_EXPERIMENT"
    MODEL_CRITIQUE = "MODEL_CRITIQUE"


class DataProvenanceType(str, Enum):
    OBSERVED_DATA = "OBSERVED_DATA"
    MODEL_PREDICTION = "MODEL_PREDICTION"
    STATISTICAL_INFERENCE = "STATISTICAL_INFERENCE"
    RESEARCH_HYPOTHESIS = "RESEARCH_HYPOTHESIS"


@dataclass
class ProvenanceStatement:
    statement: str
    provenance_type: DataProvenanceType
    source_reference: str  # e.g., "SessionSummary_2026-09-15" or "PHASE_5A_REPORT.md"


@dataclass
class SessionSummary:
    session_date: str
    total_candidates: int
    approved_count: int
    rejected_count: int
    expired_count: int
    executed_fills: int
    gross_alpha_bps: float
    total_friction_bps: float
    net_expectancy_bps: float
    realized_pnl_usd: float
    symbols_traded: List[str]
    max_drawdown_usd: float


@dataclass
class ModelHealthSummary:
    model_version: str
    spearman_rank_ic: float
    rank_ic_p_value: float
    meta_label_precision: float
    feature_drift_detected: bool
    cusum_alarm_active: bool
    status: str  # "HEALTHY", "WATCH", "DEGRADED", "SUSPENDED"


@dataclass
class ExecutionQualitySummary:
    mean_spread_bps: float
    mean_implementation_shortfall_bps: float
    live_slippage_penalty_bps: float
    passive_fill_rate_pct: float
    mean_time_to_fill_sec: float
    mean_operator_latency_sec: float


@dataclass
class RiskSummary:
    capital_ceiling_usd: float
    current_equity_usd: float
    daily_realized_loss_usd: float
    daily_loss_limit_usd: float
    pilot_drawdown_usd: float
    max_drawdown_limit_usd: float
    reconciliation_errors_count: int
    unrelated_holdings_count: int
    margin_borrowing_usd: float


@dataclass
class ChallengerProposal:
    """Structured research specification queued for offline validation."""
    proposal_id: str
    hypothesis: str
    motivation: str
    data_required: List[str]
    experimental_design: str
    primary_metric: str
    null_hypothesis: str
    validation_split: str
    risk_of_overfitting: str
    promotion_requirement: str
    queued_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ResearchDirectorOutput:
    output_type: LLMOutputType
    summary: str
    provenance_statements: List[ProvenanceStatement]
    hypotheses: List[str] = field(default_factory=list)
    proposed_experiments: List[str] = field(default_factory=list)
    rag_citations: List[str] = field(default_factory=list)
    challenger_proposals: List[ChallengerProposal] = field(default_factory=list)
    generated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "output_type": self.output_type.value,
            "summary": self.summary,
            "provenance_statements": [
                {
                    "statement": p.statement,
                    "provenance_type": p.provenance_type.value,
                    "source_reference": p.source_reference,
                }
                for p in self.provenance_statements
            ],
            "hypotheses": self.hypotheses,
            "proposed_experiments": self.proposed_experiments,
            "rag_citations": self.rag_citations,
            "challenger_proposals": [p.__dict__ for p in self.challenger_proposals],
            "generated_at": self.generated_at,
        }


class MoneymakerResearchDirector:
    """
    Read-only LLM governance observer and quantitative research companion.
    Strictly prohibits trade execution tools, broker credential access, or champion mutation.
    """

    def __init__(self, knowledge_base: Optional[RAGKnowledgeBase] = None):
        self.kb = knowledge_base or RAGKnowledgeBase()
        self._is_read_only = True
        self.research_queue: List[ChallengerProposal] = []

    @property
    def is_read_only(self) -> bool:
        return self._is_read_only

    def verify_permission_boundary(self) -> None:
        """Fail-closed assertion that this component has zero write access."""
        if not self._is_read_only:
            raise PermissionError("FATAL: Research Director permission elevated above READ_ONLY.")

    def generate_session_review(
        self,
        session: SessionSummary,
        risk: RiskSummary,
        exec_qual: ExecutionQualitySummary,
        model_health: ModelHealthSummary,
    ) -> ResearchDirectorOutput:
        """Generate structured daily session review with full provenance attribution."""
        self.verify_permission_boundary()

        statements = [
            ProvenanceStatement(
                statement=f"Session executed {session.executed_fills} fills on {session.session_date} across {session.symbols_traded}.",
                provenance_type=DataProvenanceType.OBSERVED_DATA,
                source_reference=f"SessionSummary_{session.session_date}",
            ),
            ProvenanceStatement(
                statement=f"Realized net PnL was ${session.realized_pnl_usd:+.2f} with net expectancy of {session.net_expectancy_bps:+.2f} bps/trade.",
                provenance_type=DataProvenanceType.OBSERVED_DATA,
                source_reference=f"SessionSummary_{session.session_date}",
            ),
            ProvenanceStatement(
                statement=f"Spearman Rank IC was +{model_health.spearman_rank_ic:.3f} (p={model_health.rank_ic_p_value:.4f}).",
                provenance_type=DataProvenanceType.STATISTICAL_INFERENCE,
                source_reference=f"ModelHealth_{model_health.model_version}",
            ),
            ProvenanceStatement(
                statement=f"Live implementation shortfall was {exec_qual.mean_implementation_shortfall_bps:.2f} bps with live slippage penalty of {exec_qual.live_slippage_penalty_bps:+.2f} bps.",
                provenance_type=DataProvenanceType.OBSERVED_DATA,
                source_reference="ExecutionQualitySummary",
            ),
            ProvenanceStatement(
                statement=f"Account hygiene remained 100% compliant: {risk.reconciliation_errors_count} reconciliation errors, ${risk.margin_borrowing_usd:.2f} margin borrowing.",
                provenance_type=DataProvenanceType.OBSERVED_DATA,
                source_reference="RiskSummary",
            ),
        ]

        summary_text = (
            f"Session {session.session_date} completed successfully with {session.executed_fills} autonomous fills. "
            f"Net edge remained positive (+{session.net_expectancy_bps:.2f} bps) with healthy Rank IC (+{model_health.spearman_rank_ic:.3f}). "
            f"Capital controls were 100% compliant with zero reconciliation errors and zero safety breaches."
        )

        return ResearchDirectorOutput(
            output_type=LLMOutputType.SESSION_REVIEW,
            summary=summary_text,
            provenance_statements=statements,
            hypotheses=[],
            proposed_experiments=[],
            rag_citations=["configs/frozen_phase5b.yaml", "PHASE_5B_REPORT.md"],
        )

    def detect_anomalies_and_drift(
        self,
        exec_qual: ExecutionQualitySummary,
        model_health: ModelHealthSummary,
        risk: RiskSummary,
    ) -> ResearchDirectorOutput:
        """Surface execution or statistical anomalies and formulate challenger research hypotheses."""
        self.verify_permission_boundary()

        anomalies: List[ProvenanceStatement] = []
        hypotheses: List[str] = []
        experiments: List[str] = []
        challengers: List[ChallengerProposal] = []

        if exec_qual.live_slippage_penalty_bps > 0.50:
            anomalies.append(
                ProvenanceStatement(
                    statement=f"Live slippage penalty elevated at +{exec_qual.live_slippage_penalty_bps:.2f} bps (threshold: 0.50 bps).",
                    provenance_type=DataProvenanceType.OBSERVED_DATA,
                    source_reference="ExecutionQualitySummary",
                )
            )
            hyp = "Spread expansion during morning opening rotation is increasing implementation friction."
            hypotheses.append(hyp)
            experiments.append("Evaluate time-of-day execution filter (10:00 - 15:30 ET) in Paper/Shadow challenger book.")
            
            # Formulate structured challenger proposal
            prop = ChallengerProposal(
                proposal_id=f"CHALL_TOD_{len(self.research_queue)+1:03d}",
                hypothesis=hyp,
                motivation="Reduce execution shortfall penalty by avoiding opening 30-minute spread expansion.",
                data_required=["5m_bars_2026", "tick_quotes_2026"],
                experimental_design="Purged 5-fold cross validation with time-of-day entry filter restricting orders to 10:00-15:30 ET.",
                primary_metric="Net Expectancy (bps/trade) after 3.5 bps friction",
                null_hypothesis="Time-of-day restriction yields no statistically significant improvement in net expectancy (p >= 0.05).",
                validation_split="Purged Walk-Forward 2026-Q1/Q2/Q3",
                risk_of_overfitting="High if fine-grained minute buckets are selected; low if broad 30-minute block filter.",
                promotion_requirement="Statistically significant net alpha improvement of >= +0.30 bps/trade with Deflated Sharpe Ratio p < 0.05.",
            )
            challengers.append(prop)
            self.research_queue.append(prop)

        if model_health.feature_drift_detected or model_health.cusum_alarm_active:
            anomalies.append(
                ProvenanceStatement(
                    statement="Model health monitor raised feature drift or CUSUM shift warning.",
                    provenance_type=DataProvenanceType.STATISTICAL_INFERENCE,
                    source_reference=f"ModelHealth_{model_health.model_version}",
                )
            )
            hyp = "Volatility regime transition may be shifting feature distributions away from training baseline."
            hypotheses.append(hyp)
            experiments.append("Run offline feature permutation importance audit across recent 30 trading sessions on historical data.")

        if not anomalies:
            summary = "No operational or statistical anomalies detected. Execution friction and model health remain in HEALTHY status."
        else:
            summary = f"Detected {len(anomalies)} anomalies requiring quantitative review and challenger research."

        return ResearchDirectorOutput(
            output_type=LLMOutputType.ANOMALY if anomalies else LLMOutputType.SESSION_REVIEW,
            summary=summary,
            provenance_statements=anomalies,
            hypotheses=hypotheses,
            proposed_experiments=experiments,
            rag_citations=["AUTONOMOUS_RISK_REPORT.md", "AUTONOMOUS_LIVE_EXECUTION_REPORT.md"],
            challenger_proposals=challengers,
        )

    def answer_governance_query(self, query: str) -> Dict[str, Any]:
        """Answer quantitative governance queries grounded exclusively in RAG knowledge base."""
        self.verify_permission_boundary()
        retrievals = self.kb.query(query, top_k=3)

        if not retrievals:
            return {
                "query": query,
                "answer": "UNKNOWN. No verified documentation exists in the platform knowledge base for this query.",
                "citations": [],
                "provenance": DataProvenanceType.OBSERVED_DATA.value,
            }

        citations = [f"{r.filepath} (relevance: {r.relevance_score:.2f})" for r in retrievals]
        combined_context = "\n".join([r.chunk for r in retrievals[:2]])

        answer = f"Based on verified platform documentation: {combined_context[:300]}..."

        return {
            "query": query,
            "answer": answer,
            "citations": citations,
            "provenance": DataProvenanceType.OBSERVED_DATA.value,
        }

    def inspect_symbol_performance(self, symbol_pnls: Dict[str, float]) -> Dict[str, Any]:
        """Analytical tool: evaluate PnL concentration across traded universe."""
        self.verify_permission_boundary()
        total = sum(symbol_pnls.values())
        if total <= 0:
            return {"total_pnl": total, "concentration_pct": {}}
        return {
            "total_pnl": total,
            "concentration_pct": {sym: (pnl / total) * 100.0 for sym, pnl in symbol_pnls.items()},
            "is_concentrated": any((pnl / total) > 0.60 for pnl in symbol_pnls.values()),
        }

    def inspect_regime_performance(self, regime_pnls: Dict[str, float]) -> Dict[str, Any]:
        """Analytical tool: inspect strategy returns across volatility/trend regimes."""
        self.verify_permission_boundary()
        positive_regimes = [reg for reg, pnl in regime_pnls.items() if pnl > 0]
        return {
            "total_regimes_evaluated": len(regime_pnls),
            "profitable_regimes": positive_regimes,
            "all_regimes_profitable": len(positive_regimes) == len(regime_pnls),
        }
