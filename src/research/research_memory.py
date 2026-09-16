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


from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import os
import re
from typing import Any, Dict, List, Optional


class DocumentType(str, Enum):
    VALIDATION_REPORT = "VALIDATION_REPORT"
    INCIDENT_LOG = "INCIDENT_LOG"
    CAPACITY_FINDING = "CAPACITY_FINDING"
    RISK_FINDING = "RISK_FINDING"
    ALLOCATOR_RESEARCH = "ALLOCATOR_RESEARCH"
    MODEL_CARD = "MODEL_CARD"
    EXPERIMENT_MANIFEST = "EXPERIMENT_MANIFEST"


@dataclass
class CorpusDocument:
    document_id: str
    document_type: str | DocumentType
    title: str
    content: str
    strategy: Optional[str]
    phase: str
    created_at: str
    evidence_type: str
    file_path: str

    @property
    def hash(self) -> str:
        data = f"{self.document_id}:{self.title}:{self.content}:{self.phase}".encode("utf-8")
        return hashlib.sha256(data).hexdigest()


class ResearchMemory:
    """
    Manages indexing and querying of Moneymaker's institutional research knowledge.
    """

    def __init__(self, corpus_manifest_path: str = "research_corpus/manifest.jsonl") -> None:
        self.corpus_manifest_path = corpus_manifest_path
        self._documents: List[CorpusDocument] = []
        self._init_corpus()

    def _init_corpus(self) -> None:
        # Pre-populate index from core markdown reports and research findings
        default_docs = [
            CorpusDocument(
                document_id="DOC-PHASE-7F",
                document_type=DocumentType.VALIDATION_REPORT,
                title="Phase 7F Master Report",
                content="Alpha A held at $10k (CAPACITY_HOLD_WATCH). Alpha B Tier 2 validated at $5k with 97.47% edge retention. Portfolio Sharpe 7.67 with r=-0.031. Allocator shadow validated.",
                strategy="MULTI_STRATEGY",
                phase="7F",
                created_at="2026-09-15T19:34:00Z",
                evidence_type="EMPIRICAL_LIVE",
                file_path="PHASE_7F_REPORT.md",
            ),
            CorpusDocument(
                document_id="DOC-ALPHA-A-CAPACITY-HOLD",
                document_type=DocumentType.CAPACITY_FINDING,
                title="Alpha A Capacity Hold Assessment",
                content="Alpha A Intraday Relative Momentum validated at $10k capital. Placed in PRODUCTION_CAPACITY_HOLD due to observed gross alpha of +4.87 bps vs friction 3.76 bps. Net expectancy +1.11 bps. Edge decay observed at higher scale.",
                strategy="ALPHA_A",
                phase="7D",
                created_at="2026-09-15T18:00:00Z",
                evidence_type="EMPIRICAL_LIVE",
                file_path="ALPHA_A_PHASE7D_STABILITY_REPORT.md",
            ),
            CorpusDocument(
                document_id="DOC-ALPHA-B-CAPACITY-3PT",
                document_type=DocumentType.CAPACITY_FINDING,
                title="Alpha B Three-Point Capacity Curve",
                content="Empirical calibrations at $1k (+10.67 bps), $2.5k (+10.56 bps), $5k (+10.40 bps). Linear decay slope is -0.0675 bps / $1k. Bottleneck is Capital Utilization and Signal Scarcity rather than market impact.",
                strategy="ALPHA_B",
                phase="7F",
                created_at="2026-09-15T19:33:00Z",
                evidence_type="EMPIRICAL_LIVE",
                file_path="ALPHA_B_PRELIMINARY_CAPACITY_CURVE.md",
            ),
            CorpusDocument(
                document_id="DOC-PORTFOLIO-VETO-7F",
                document_type=DocumentType.RISK_FINDING,
                title="Portfolio Risk Aggregator Phase 7F Veto Audit",
                content="Evaluated 430 orders with 8 vetoes and 4 resizes. Net economic contribution of veto layer was +$74.20 USD in downside drag prevented.",
                strategy="PORTFOLIO_AGGREGATOR",
                phase="7F",
                created_at="2026-09-15T19:33:00Z",
                evidence_type="EMPIRICAL_LIVE",
                file_path="PORTFOLIO_PHASE7F_VETO_REPORT.md",
            ),
            CorpusDocument(
                document_id="DOC-ALLOCATOR-SHADOW-7F",
                document_type=DocumentType.ALLOCATOR_RESEARCH,
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

    def search(self, query: str, limit: int = 5) -> List[CorpusDocument]:
        """Returns matching CorpusDocument objects ranked by token relevance and title match."""
        tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) >= 1]
        scored: List[tuple[int, CorpusDocument]] = []

        for doc in self._documents:
            score = 0
            title_lower = doc.title.lower()
            content_lower = doc.content.lower()
            strat_lower = (doc.strategy or "").lower()

            for t in tokens:
                # Title matches have 3x weight
                score += title_lower.count(t) * 3
                # Exact strategy matches have 3x weight
                if strat_lower and t == strat_lower:
                    score += 3
                # Content matches have 1x weight
                score += content_lower.count(t)

            if score > 0:
                scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scored[:limit]] if scored else self._documents[:limit]

    def search_research_memory(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Keyword and token matching across research corpus returning structured chunks."""
        docs = self.search(query, limit=limit)
        return [
            {
                "document_id": doc.document_id,
                "title": doc.title,
                "document_type": str(doc.document_type),
                "phase": doc.phase,
                "strategy": doc.strategy,
                "chunk": doc.content,
                "snippet": doc.content,
                "file_path": doc.file_path,
                "evidence_type": doc.evidence_type,
                "hash": doc.hash,
                "created_at": doc.created_at,
            }
            for doc in docs
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
            if "CAPACITY" in str(doc.document_type) or "CAPACITY" in doc.title.upper()
        ]

