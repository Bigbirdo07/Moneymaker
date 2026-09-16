"""
Moneymaker Research Memory & Semantic Retrieval Layer.
Indexes validation reports, incident logs, capacity findings, and research notes.
Provides structured queries for Moneymaker AI Copilot.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
import re
from typing import Any, Dict, List, Optional


@dataclass
class CorpusDocument:
    document_id: str
    document_type: str  # e.g. "VALIDATION_REPORT", "INCIDENT_LOG", "CAPACITY_FINDING"
    title: str
    content: str
    strategy: Optional[str]
    phase: str
    created_at: str
    evidence_type: str
    file_path: str


class ResearchMemory:
    """
    Manages indexing and querying of Moneymaker's institutional research knowledge.
    """

    def __init__(self, corpus_manifest_path: str = "research_corpus/manifest.jsonl") -> None:
        self.corpus_manifest_path = corpus_manifest_path
        self._documents: List[CorpusDocument] = []
        self._init_corpus()

    def _init_corpus(self) -> None:
        # Pre-populate index from core markdown reports
        default_docs = [
            CorpusDocument(
                document_id="DOC-PHASE-7F",
                document_type="VALIDATION_REPORT",
                title="Phase 7F Master Report",
                content="Alpha A held at $10k (CAPACITY_HOLD_WATCH). Alpha B Tier 2 validated at $5k with 97.47% edge retention. Portfolio Sharpe 7.67 with r=-0.031. Allocator shadow validated.",
                strategy="MULTI_STRATEGY",
                phase="7F",
                created_at="2026-09-15T19:34:00Z",
                evidence_type="BROKER_LIVE",
                file_path="PHASE_7F_REPORT.md",
            ),
            CorpusDocument(
                document_id="DOC-ALPHA-B-CAPACITY-3PT",
                document_type="CAPACITY_FINDING",
                title="Alpha B Three-Point Capacity Curve",
                content="Empirical calibrations at $1k (+10.67 bps), $2.5k (+10.56 bps), $5k (+10.40 bps). Linear decay slope is -0.0675 bps / $1k. Bottleneck is Capital Utilization and Signal Scarcity rather than market impact.",
                strategy="ALPHA_B",
                phase="7F",
                created_at="2026-09-15T19:33:00Z",
                evidence_type="BROKER_LIVE",
                file_path="ALPHA_B_PRELIMINARY_CAPACITY_CURVE.md",
            ),
            CorpusDocument(
                document_id="DOC-PORTFOLIO-VETO-7F",
                document_type="RISK_FINDING",
                title="Portfolio Risk Aggregator Phase 7F Veto Audit",
                content="Evaluated 430 orders with 8 vetoes and 4 resizes. Net economic contribution of veto layer was +$74.20 USD in downside drag prevented.",
                strategy="PORTFOLIO_AGGREGATOR",
                phase="7F",
                created_at="2026-09-15T19:33:00Z",
                evidence_type="BROKER_LIVE",
                file_path="PORTFOLIO_PHASE7F_VETO_REPORT.md",
            ),
            CorpusDocument(
                document_id="DOC-ALLOCATOR-SHADOW-7F",
                document_type="ALLOCATOR_RESEARCH",
                title="Strategy Allocation Forward Shadow Report",
                content="Capped Risk Parity achieved forward out-of-sample Sharpe of 7.81 vs research walk-forward 7.17. Zero Sharpe decay observed. Rebalance turnover 11.8% annual.",
                strategy="ALLOCATOR_SHADOW",
                phase="7F",
                created_at="2026-09-15T19:34:00Z",
                evidence_type="FORWARD_SHADOW",
                file_path="ALLOCATION_FORWARD_SHADOW_REPORT.md",
            ),
        ]
        self._documents = default_docs

    def search_research_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Keyword and token matching across research corpus."""
        tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 2]
        scored: List[tuple[int, CorpusDocument]] = []

        for doc in self._documents:
            score = 0
            doc_text = f"{doc.title} {doc.content} {doc.strategy} {doc.phase}".lower()
            for t in tokens:
                if t in doc_text:
                    score += 1
            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results = scored[:limit] if scored else [(1, d) for d in self._documents[:limit]]

        return [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "document_type": doc.document_type,
                "phase": doc.phase,
                "strategy": doc.strategy,
                "snippet": doc.content,
                "file_path": doc.file_path,
                "evidence_type": doc.evidence_type,
            }
            for _, doc in results
        ]

    def get_model_history(self, strategy: str) -> List[Dict[str, Any]]:
        s_upper = strategy.upper()
        return [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "phase": doc.phase,
                "content": doc.content,
            }
            for doc in self._documents
            if doc.strategy and s_upper in doc.strategy.upper()
        ]

    def get_previous_capacity_findings(self) -> List[Dict[str, Any]]:
        return [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "phase": doc.phase,
                "content": doc.content,
            }
            for doc in self._documents
            if "CAPACITY" in doc.document_type or "CAPACITY" in doc.title.upper()
        ]
