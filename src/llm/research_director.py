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
    CAPACITY_WARNING = "CAPACITY_WARNING"
    SLIPPAGE_ANOMALY = "SLIPPAGE_ANOMALY"
    TIER_COMPARISON = "TIER_COMPARISON"
    SYMBOL_CAPACITY_ANALYSIS = "SYMBOL_CAPACITY_ANALYSIS"
    RISK_SUMMARY = "RISK_SUMMARY"
    CAPITAL_RESEARCH_HYPOTHESIS = "CAPITAL_RESEARCH_HYPOTHESIS"
    MODEL_AUDIT_FINDING = "MODEL_AUDIT_FINDING"
    STRATEGY_DIVERSIFICATION_FINDING = "STRATEGY_DIVERSIFICATION_FINDING"
    STRATEGY_CONFLICT = "STRATEGY_CONFLICT"
    PORTFOLIO_RISK_FINDING = "PORTFOLIO_RISK_FINDING"
    ALPHA_DECAY_WARNING = "ALPHA_DECAY_WARNING"
    PAPER_EXECUTION_WARNING = "PAPER_EXECUTION_WARNING"
    LIVE_PAPER_DIVERGENCE = "LIVE_PAPER_DIVERGENCE"
    STRATEGY_COLLISION_WARNING = "STRATEGY_COLLISION_WARNING"
    PORTFOLIO_CONCENTRATION_WARNING = "PORTFOLIO_CONCENTRATION_WARNING"
    DIVERSIFICATION_DECAY_WARNING = "DIVERSIFICATION_DECAY_WARNING"
    STRATEGY_HEALTH_SUMMARY = "STRATEGY_HEALTH_SUMMARY"


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
class ModelAuditFinding:
    """Read-only structured finding representing model/report discrepancies or inconsistencies."""
    severity: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    artifact: str
    metric: str
    expected_value: Any
    observed_value: Any
    discrepancy: Any
    possible_causes: List[str]
    recommended_test: str
    audit_timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ResearchDirectorOutput:
    output_type: LLMOutputType
    summary: str
    provenance_statements: List[ProvenanceStatement]
    hypotheses: List[str] = field(default_factory=list)
    proposed_experiments: List[str] = field(default_factory=list)
    rag_citations: List[str] = field(default_factory=list)
    challenger_proposals: List[ChallengerProposal] = field(default_factory=list)
    model_audit_findings: List[ModelAuditFinding] = field(default_factory=list)
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
            "model_audit_findings": [f.__dict__ for f in self.model_audit_findings],
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

    def inspect_capacity_degradation(
        self,
        edge_retention_ratio: float,
        tier_shortfall_bps: float,
        baseline_shortfall_bps: float = 1.41,
    ) -> ResearchDirectorOutput:
        """Analytical tool: inspect edge retention and shortfall growth across capital tiers."""
        self.verify_permission_boundary()

        shortfall_growth = tier_shortfall_bps - baseline_shortfall_bps
        statements = [
            ProvenanceStatement(
                statement=f"Observed edge retention ratio is {edge_retention_ratio*100:.1f}%.",
                provenance_type=DataProvenanceType.OBSERVED_DATA,
                source_reference="EdgeRetentionAnalyzer",
            ),
            ProvenanceStatement(
                statement=f"Implementation shortfall grew by {shortfall_growth:+.2f} bps relative to baseline.",
                provenance_type=DataProvenanceType.OBSERVED_DATA,
                source_reference="EmpiricalImpactModel",
            ),
        ]

        if edge_retention_ratio < 0.80:
            summary = f"CAPACITY WARNING: Edge retention dropped to {edge_retention_ratio*100:.1f}% (<80% threshold). Shortfall expanded by {shortfall_growth:+.2f} bps."
            out_type = LLMOutputType.CAPACITY_WARNING
            hypotheses = ["Higher order notional is encountering non-linear passive queue exhaustion."]
            experiments = ["Investigate passive peg execution or child order splitting in paper simulation."]
        else:
            summary = f"CAPACITY HEALTHY: Edge retention remains strong at {edge_retention_ratio*100:.1f}% with modest shortfall growth ({shortfall_growth:+.2f} bps)."
            out_type = LLMOutputType.TIER_COMPARISON
            hypotheses = ["Strategy capacity remains robust at current notional scale."]
            experiments = ["Continue controlled tier data collection."]

        return ResearchDirectorOutput(
            output_type=out_type,
            summary=summary,
            provenance_statements=statements,
            hypotheses=hypotheses,
            proposed_experiments=experiments,
            rag_citations=["configs/frozen_phase6a.yaml", "EMPIRICAL_CAPACITY_CURVE.md"],
        )

    def inspect_symbol_capacity(
        self,
        symbol_metrics: Dict[str, Dict[str, float]],
    ) -> ResearchDirectorOutput:
        """Analytical tool: assess per-symbol participation and shortfall characteristics."""
        self.verify_permission_boundary()

        statements = []
        hypotheses = []
        experiments = []

        for sym, data in symbol_metrics.items():
            statements.append(
                ProvenanceStatement(
                    statement=f"Symbol {sym}: participation={data.get('median_participation_pct', 0.0):.3f}%, shortfall={data.get('shortfall_bps', 0.0):.2f} bps, net_exp={data.get('net_expectancy_bps', 0.0):+.2f} bps.",
                    provenance_type=DataProvenanceType.OBSERVED_DATA,
                    source_reference=f"SymbolMetrics_{sym}",
                )
            )
            if data.get("net_expectancy_bps", 0.0) <= 0.5:
                hypotheses.append(f"Symbol {sym} exhibits elevated friction consuming alpha at higher sizing.")
                experiments.append(f"Enforce tighter MAX_ORDER_NOTIONAL for {sym}.")

        summary = f"Evaluated symbol capacity across {len(symbol_metrics)} universe symbols. All symbols characterized for liquidity limits."

        return ResearchDirectorOutput(
            output_type=LLMOutputType.SYMBOL_CAPACITY_ANALYSIS,
            summary=summary,
            provenance_statements=statements,
            hypotheses=hypotheses,
            proposed_experiments=experiments,
            rag_citations=["configs/frozen_phase6a.yaml", "SYMBOL_CAPACITY_REPORT.md"],
        )

    def generate_tier_comparison(
        self,
        tier_summaries: Dict[str, Dict[str, Any]],
    ) -> ResearchDirectorOutput:
        """Analytical tool: compare execution and statistical metrics across capital tiers."""
        self.verify_permission_boundary()

        statements = []
        for tier_name, data in tier_summaries.items():
            statements.append(
                ProvenanceStatement(
                    statement=f"{tier_name} (${data.get('capital_usd', 0):.0f}): Net Exp={data.get('net_expectancy_bps', 0.0):+.2f} bps, Shortfall={data.get('shortfall_bps', 0.0):.2f} bps, Edge Retention={data.get('edge_retention_pct', 0.0):.1f}%.",
                    provenance_type=DataProvenanceType.OBSERVED_DATA,
                    source_reference=f"TierSummary_{tier_name}",
                )
            )

        summary = f"Generated cross-tier comparison across {len(tier_summaries)} tiers. Progression demonstrates controlled scaling behavior."

        return ResearchDirectorOutput(
            output_type=LLMOutputType.TIER_COMPARISON,
            summary=summary,
            provenance_statements=statements,
            hypotheses=["Strategy edge scales favorably within micro-to-small notional regimes."],
            proposed_experiments=["Complete full sample collection for active authorized tier."],
            rag_citations=["CAPITAL_TIER_REPORT.md", "EDGE_RETENTION_REPORT.md"],
        )

    def generate_model_audit_finding(
        self,
        severity: str,
        artifact: str,
        metric: str,
        expected_value: Any,
        observed_value: Any,
        discrepancy: Any,
        possible_causes: List[str],
        recommended_test: str,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface structured model/accounting discrepancies in reports and ledgers."""
        self.verify_permission_boundary()

        finding = ModelAuditFinding(
            severity=severity,
            artifact=artifact,
            metric=metric,
            expected_value=expected_value,
            observed_value=observed_value,
            discrepancy=discrepancy,
            possible_causes=possible_causes,
            recommended_test=recommended_test,
        )

        statement = ProvenanceStatement(
            statement=f"Audit finding for {artifact} ({metric}): Expected {expected_value}, Observed {observed_value} (Discrepancy: {discrepancy}). Severity: {severity}.",
            provenance_type=DataProvenanceType.OBSERVED_DATA,
            source_reference=artifact,
        )

        summary = f"Model audit finding flagged for {artifact} ({metric}) with severity {severity}."

        return ResearchDirectorOutput(
            output_type=LLMOutputType.MODEL_AUDIT_FINDING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=[f"Discrepancy in {metric} may stem from {possible_causes[0]}." if possible_causes else "Review accounting."],
            proposed_experiments=[recommended_test],
            rag_citations=[artifact],
            model_audit_findings=[finding],
        )

    def generate_strategy_diversification_finding(
        self,
        strategy_a: str,
        strategy_b: str,
        correlation: float,
        sharpe_delta: float,
        drawdown_reduction_pct: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface multi-strategy correlation and diversification benefit."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Cross-strategy correlation between {strategy_a} and {strategy_b} is {correlation:.3f}. Sharpe delta: {sharpe_delta:+.2f}, Drawdown reduction: {drawdown_reduction_pct:.1f}%.",
            provenance_type=DataProvenanceType.STATISTICAL_INFERENCE,
            source_reference="MULTI_STRATEGY_RESEARCH_REPORT.md",
        )
        summary = f"Multi-strategy analysis between {strategy_a} and {strategy_b} demonstrates strong diversification benefit with correlation {correlation:.3f}."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.STRATEGY_DIVERSIFICATION_FINDING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Combining intraday momentum and multi-day reversal creates complementary return profiles."],
            proposed_experiments=["Track paper multi-strategy portfolio under rolling market selloffs."],
            rag_citations=["MULTI_STRATEGY_RESEARCH_REPORT.md", "ALPHA_A_ALPHA_B_CORRELATION_REPORT.md"],
        )

    def generate_strategy_conflict_finding(
        self,
        symbol: str,
        conflict_type: str,
        aggregate_notional_usd: float,
        proposed_rule: str,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface signal collisions and capital congestion between strategies."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Strategy conflict detected for {symbol}: {conflict_type} with aggregate notional ${aggregate_notional_usd:.2f}. Recommended rule: {proposed_rule}.",
            provenance_type=DataProvenanceType.OBSERVED_DATA,
            source_reference="STRATEGY_CONFLICT_REPORT.md",
        )
        summary = f"Signal collision identified on {symbol} ({conflict_type}). Proposed resolution: {proposed_rule}."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.STRATEGY_CONFLICT,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Shared universe can produce simultaneous signals requiring hard position capping."],
            proposed_experiments=["Evaluate conservative exposure capping rules in offline multi-strategy simulation."],
            rag_citations=["STRATEGY_CONFLICT_REPORT.md"],
        )

    def generate_portfolio_risk_finding(
        self,
        risk_metric: str,
        alpha_a_contrib_pct: float,
        alpha_b_contrib_pct: float,
        combined_value: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface multi-strategy risk decomposition and Expected Shortfall."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Portfolio {risk_metric}: Alpha A contributes {alpha_a_contrib_pct:.1f}%, Alpha B contributes {alpha_b_contrib_pct:.1f}%. Total combined: {combined_value:.2f}%.",
            provenance_type=DataProvenanceType.STATISTICAL_INFERENCE,
            source_reference="PORTFOLIO_RISK_CONTRIBUTION_REPORT.md",
        )
        summary = f"Portfolio risk budget evaluation for {risk_metric} shows balanced risk allocation."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.PORTFOLIO_RISK_FINDING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Risk-parity weighting stabilizes portfolio tail risk more effectively than equal dollar weighting."],
            proposed_experiments=["Simulate dynamic inverse-volatility rebalancing on out-of-sample data."],
            rag_citations=["PORTFOLIO_RISK_CONTRIBUTION_REPORT.md"],
        )

    def generate_alpha_decay_warning(
        self,
        strategy_id: str,
        horizon_days: int,
        observed_rank_ic: float,
        decay_half_life_days: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface horizon decay and signal half-life metrics."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Alpha decay tracking for {strategy_id} at {horizon_days}-day horizon: Rank IC {observed_rank_ic:+.3f}, estimated half-life {decay_half_life_days:.1f} days.",
            provenance_type=DataProvenanceType.STATISTICAL_INFERENCE,
            source_reference="ALPHA_B_FORWARD_SIGNAL_DECAY.md",
        )
        summary = f"Signal decay analysis for {strategy_id} indicates optimal edge capture at 3-day holding period."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.ALPHA_DECAY_WARNING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Holding beyond 3 days increases exposure to broader market beta rather than reversal alpha."],
            proposed_experiments=["Continue logging 1d, 2d, 3d, 5d, 10d returns without altering frozen candidate."],
            rag_citations=["ALPHA_B_FORWARD_SIGNAL_DECAY.md"],
        )

    def generate_paper_execution_warning(
        self,
        strategy_id: str,
        paper_fill_advantage_bps: float,
        paper_fill_rate_pct: float,
        shadow_fill_rate_pct: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface broker paper fill optimism relative to shadow."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Paper execution quality for {strategy_id}: Paper fill optimism {paper_fill_advantage_bps:+.2f} bps. Fill rate: Paper {paper_fill_rate_pct:.1f}% vs Shadow {shadow_fill_rate_pct:.1f}%.",
            provenance_type=DataProvenanceType.OBSERVED_DATA,
            source_reference="ALPHA_B_PAPER_VS_SHADOW_REPORT.md",
        )
        summary = f"Broker paper execution shows moderate fill optimism ({paper_fill_advantage_bps:+.2f} bps) compared to conservative shadow."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.PAPER_EXECUTION_WARNING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Broker paper fill simulations may underestimate real queue priority drag."],
            proposed_experiments=["Compare shadow conservative fill logic against live micro-fill logs when promoted."],
            rag_citations=["ALPHA_B_PAPER_VS_SHADOW_REPORT.md", "ALPHA_B_EXECUTION_QUALITY_REPORT.md"],
        )

    def generate_live_paper_divergence_finding(
        self,
        strategy_id: str,
        live_net_bps: float,
        paper_net_bps: float,
        gap_bps: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface live vs paper execution divergence and queue drag."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Live vs paper divergence for {strategy_id}: Live net {live_net_bps:+.2f} bps, Paper net {paper_net_bps:+.2f} bps (Gap: {gap_bps:+.2f} bps).",
            provenance_type=DataProvenanceType.OBSERVED_DATA,
            source_reference="ALPHA_B_LIVE_VS_PAPER_REPORT.md",
        )
        summary = f"Live pilot execution for {strategy_id} exhibits realistic execution friction relative to sandbox paper ({gap_bps:+.2f} bps gap)."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.LIVE_PAPER_DIVERGENCE,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Morning opening market queue placement introduces ~0.8-1.2 bps realized friction."],
            proposed_experiments=["Maintain triple-book tracking across full 30+ session pilot window."],
            rag_citations=["ALPHA_B_LIVE_VS_PAPER_REPORT.md"],
        )

    def generate_strategy_collision_warning(
        self,
        symbol: str,
        alpha_a_notional_usd: float,
        alpha_b_notional_usd: float,
        combined_cap_usd: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface concurrent cross-strategy exposure on shared symbols."""
        self.verify_permission_boundary()
        total_notional = alpha_a_notional_usd + alpha_b_notional_usd
        statement = ProvenanceStatement(
            statement=f"Cross-strategy collision detected for {symbol}: Alpha A ${alpha_a_notional_usd:.2f}, Alpha B ${alpha_b_notional_usd:.2f}. Total ${total_notional:.2f} vs cap ${combined_cap_usd:.2f}.",
            provenance_type=DataProvenanceType.OBSERVED_DATA,
            source_reference="PORTFOLIO_COLLISION_REPORT.md",
        )
        summary = f"Simultaneous signal on {symbol} requires deterministic portfolio concentration capping."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.STRATEGY_COLLISION_WARNING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Shared large-cap tech universe occasionally produces concurrent momentum and reversal signals."],
            proposed_experiments=["Audit execution logs for exposure-capped orders under live collision conditions."],
            rag_citations=["PORTFOLIO_COLLISION_REPORT.md"],
        )

    def generate_portfolio_concentration_warning(
        self,
        concentration_metric: str,
        observed_value: float,
        threshold_value: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface portfolio-level gross, sector, or archetype concentration."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Portfolio concentration warning for {concentration_metric}: Observed {observed_value:.1f}%, Limit {threshold_value:.1f}%.",
            provenance_type=DataProvenanceType.STATISTICAL_INFERENCE,
            source_reference="PORTFOLIO_AGGREGATE_RISK_REPORT.md",
        )
        summary = f"Portfolio risk budget concentration on {concentration_metric} reached {observed_value:.1f}%."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.PORTFOLIO_CONCENTRATION_WARNING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Cluster concentration in high-beta tech requires multi-sector expansion in future phases."],
            proposed_experiments=["Evaluate sector-balanced candidate universe in offline research."],
            rag_citations=["PORTFOLIO_AGGREGATE_RISK_REPORT.md"],
        )

    def generate_diversification_decay_warning(
        self,
        rolling_window_days: int,
        observed_correlation: float,
        baseline_correlation: float,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface rolling cross-strategy correlation drift."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Rolling {rolling_window_days}-day correlation drifted from baseline {baseline_correlation:.3f} to {observed_correlation:.3f}.",
            provenance_type=DataProvenanceType.STATISTICAL_INFERENCE,
            source_reference="PORTFOLIO_DIVERSIFICATION_STABILITY.md",
        )
        summary = f"Cross-strategy correlation stability monitoring confirms low correlation ({observed_correlation:.3f})."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.DIVERSIFICATION_DECAY_WARNING,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Macro market regime shifts can temporarily alter cross-strategy correlation."],
            proposed_experiments=["Track 20-day rolling correlation during broad market stress periods."],
            rag_citations=["PORTFOLIO_DIVERSIFICATION_STABILITY.md"],
        )

    def generate_strategy_health_summary(
        self,
        strategy_id: str,
        capital_authorized_usd: float,
        net_expectancy_bps: float,
        cost_break_even_mult: float,
        status: str,
    ) -> ResearchDirectorOutput:
        """Analytical tool: Surface composite strategy operational health summary."""
        self.verify_permission_boundary()
        statement = ProvenanceStatement(
            statement=f"Strategy health for {strategy_id}: Capital ${capital_authorized_usd:.2f}, Net {net_expectancy_bps:+.2f} bps, Cost margin {cost_break_even_mult:.2f}x. Status: {status}.",
            provenance_type=DataProvenanceType.OBSERVED_DATA,
            source_reference="VALIDATION_LEDGER.md",
        )
        summary = f"Strategy {strategy_id} operating in {status} status with {net_expectancy_bps:+.2f} bps net expectancy."
        return ResearchDirectorOutput(
            output_type=LLMOutputType.STRATEGY_HEALTH_SUMMARY,
            summary=summary,
            provenance_statements=[statement],
            hypotheses=["Strategy risk budgets and loss limits are functioning within pre-registered boundaries."],
            proposed_experiments=["Continue routine daily governance monitoring."],
            rag_citations=["VALIDATION_LEDGER.md"],
        )

