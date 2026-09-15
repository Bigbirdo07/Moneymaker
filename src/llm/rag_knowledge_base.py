"""
RAG Knowledge Base & Document Retrieval Layer for Moneymaker Research Director.
Indexes architecture documentation, phase reports, risk policies, model cards,
and incident logs to provide factual grounding without LLM hallucinations.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import os
import re
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class KnowledgeDocument:
    doc_id: str
    title: str
    category: str  # "ARCHITECTURE", "POLICY", "PHASE_REPORT", "INCIDENT_LOG", "MODEL_CARD"
    filepath: str
    content: str
    chunks: List[str] = field(default_factory=list)
    indexed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RetrievalResult:
    doc_id: str
    title: str
    category: str
    filepath: str
    chunk: str
    relevance_score: float


class RAGKnowledgeBase:
    """Manages document chunking, indexing, and keyword/lexical retrieval for Research Director."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents: Dict[str, KnowledgeDocument] = {}

    def index_document(self, doc_id: str, title: str, category: str, filepath: str, content: str) -> KnowledgeDocument:
        """Chunk and index a markdown document."""
        chunks = self._chunk_text(content)
        doc = KnowledgeDocument(
            doc_id=doc_id,
            title=title,
            category=category,
            filepath=filepath,
            content=content,
            chunks=chunks,
        )
        self.documents[doc_id] = doc
        return doc

    def index_repository_file(self, filepath: str, category: str = "PHASE_REPORT") -> Optional[KnowledgeDocument]:
        """Index a file directly from the repository filesystem if it exists."""
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            doc_id = os.path.basename(filepath).replace(".", "_")
            title = os.path.basename(filepath)
            return self.index_document(doc_id, title, category, filepath, content)
        except Exception:
            return None

    def query(self, query_text: str, top_k: int = 3, category_filter: Optional[str] = None) -> List[RetrievalResult]:
        """
        Retrieve relevant document chunks scoring on term matching and TF density.
        """
        terms = set(re.findall(r"\w+", query_text.lower()))
        if not terms:
            return []

        results: List[RetrievalResult] = []

        for doc in self.documents.values():
            if category_filter and doc.category != category_filter:
                continue

            for chunk in doc.chunks:
                chunk_terms = re.findall(r"\w+", chunk.lower())
                if not chunk_terms:
                    continue
                
                # Term overlap score
                matched_count = sum(1 for t in terms if t in chunk_terms)
                if matched_count == 0:
                    continue
                
                score = matched_count / len(terms)
                results.append(
                    RetrievalResult(
                        doc_id=doc.doc_id,
                        title=doc.title,
                        category=doc.category,
                        filepath=doc.filepath,
                        chunk=chunk,
                        relevance_score=score,
                    )
                )

        results.sort(key=lambda r: r.relevance_score, reverse=True)
        return results[:top_k]

    def _chunk_text(self, text: str) -> List[str]:
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text] if text.strip() else []

        chunks = []
        step = max(1, self.chunk_size - self.chunk_overlap)
        for i in range(0, len(words), step):
            chunk_words = words[i:i + self.chunk_size]
            chunks.append(" ".join(chunk_words))
        return chunks
