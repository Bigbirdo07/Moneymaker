# Moneymaker Institutional Research Memory & Retrieval Engine

## 1. Executive Summary

The **Moneymaker Research Memory Engine** (`src/research/research_memory.py`) creates an immutable, searchable corpus of all quantitative insights, capacity limits, risk findings, trade explanations, and post-mortem analyses generated throughout the platform's development.

This corpus serves as the foundational grounding knowledge for the **AI Copilot** and the domain-fine-tuned **Moneymaker Research Model** (`MMRM-0.1`).

---

## 2. Research Document Schema

Every document in the institutional corpus is indexed with strict metadata:
- `document_id`: Unique identifier (e.g. `DOC_CAPACITY_ALPHA_A_TIER3`).
- `document_type`: Category (`VALIDATION_REPORT`, `STRATEGY_REPORT`, `CAPACITY_FINDING`, `RISK_FINDING`, `TRADE_EXPLANATION_SCHEMA`, `EXPERIMENT_MANIFEST`, `INCIDENT_LOG`).
- `title`: Descriptive document title.
- `created_at`: UTC ISO timestamp.
- `strategy`: Target strategy (`ALPHA_A`, `ALPHA_B`, `PORTFOLIO`).
- `phase`: Platform phase (`PHASE_7A`, `PHASE_7B`, `PHASE_8A`, `PHASE_8B`, etc.).
- `evidence_type`: Provenance class (`LIVE_OBSERVATION`, `STATISTICAL_TEST`, `THEORETICAL_MODEL`).
- `source`: Originating file or test module path.
- `hash`: SHA-256 cryptographic digest of document text.
- `content`: Markdown text of the finding.

---

## 3. Grounded Retrieval Copilot Tools

The AI Copilot accesses research memory through 5 read-only tools:
1. `search_research_memory(query)`: Semantic and keyword retrieval across the corpus.
2. `get_model_history(strategy)`: Retrieves past iterations, benchmark scores, and validated parameter sets.
3. `get_previous_capacity_findings(strategy)`: Retrieves canonical friction bounds, participation limits, and empirical degradation curves.
4. `get_experiment_status(experiment_id)`: Inspects Slurm metrics and artifact manifests.
5. `explain_trade(trade_id)`: Synthesizes execution telemetry with strategy thesis.

---

## 4. Safety & Governance Firewall

- **Advisory Only**: All retrieved institutional memory is strictly explanatory and advisory.
- **Zero Live Execution Coupling**: No retrieved document or recommendation can trigger live broker order placement, capital adjustments, or live parameter alterations without manual human engineering.
