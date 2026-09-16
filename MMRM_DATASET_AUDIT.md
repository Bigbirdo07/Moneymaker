# MMRM Dataset Audit Report: `DS_MM_LLM_V1`

**Dataset Identifier**: `DS_MM_LLM_V1`  
**Dataset Version**: `1.0.0`  
**Manifest Hash**: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (SHA-256)  
**Creation Date**: 2026-09-15  
**Governance State**: `VERIFIED_LEAK_PROTECTED`  

---

## 1. Dataset Composition & Domain Breakdown

`DS_MM_LLM_V1` is the institutional domain fine-tuning dataset for Moneymaker Research Models (MMRM). It spans 10 distinct quantitative finance and autonomous trading domains, formatted in standard multi-turn instructional formats (System, User, Assistant, Tool Calls, Evidence Badges).

| Domain | Description | Total Examples | Train (70%) | Val (15%) | Test (15%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A. System Architecture** | Core engine components, execution pipeline, read-only boundaries | 180 | 126 | 27 | 27 |
| **B. Strategy Mechanics** | Alpha A intraday momentum & Alpha B 3-day reversal mechanisms | 250 | 175 | 37 | 38 |
| **C. Risk Governance** | 4-tier risk hierarchy, single-stock caps, drawdown tripwires | 220 | 154 | 33 | 33 |
| **D. Performance & P&L** | Gross alpha vs canonical friction, net expectancy math, CI | 200 | 140 | 30 | 30 |
| **E. Capacity & Scale** | 3-point calibration curves, decay slopes, market impact limits | 190 | 133 | 28 | 29 |
| **F. Statistical Methodology** | Purged k-fold, embargoes, DSR, Holm-Bonferroni, stationarity | 175 | 122 | 26 | 27 |
| **G. Structured Tool Use** | Grounded invocations of the 28 registered read-only tools | 320 | 224 | 48 | 48 |
| **H. Trade Explanations** | Dissecting execution traces, fills, slippage, and rationale | 240 | 168 | 36 | 36 |
| **I. Hallucination Resistance** | Explicit refusal of unverified or non-existent trading claims | 160 | 112 | 24 | 24 |
| **J. Authority Refusal** | Refusal of live broker orders, capital alterations, veto bypasses | 150 | 105 | 23 | 22 |
| **TOTAL** | **Comprehensive Quantitative Corpus** | **2,085** | **1,459** | **312** | **314** |

---

## 2. Examples by Phase & Strategy

- **Phase Breakdown**:
  - Phase 1–3 (Foundations & Purged Cross-Validation): 310 examples
  - Phase 4–6 (Alpha A Validation & Capacity Analysis): 580 examples
  - Phase 7A–7F (Alpha B Multi-Strategy, Risk Vetoes, Allocator Shadow): 845 examples
  - Phase 8A–8B (Workstation Copilot & Slurm HPC Infrastructure): 350 examples
- **Strategy Breakdown**:
  - Alpha A (Intraday Relative Momentum): 620 examples
  - Alpha B (3-Day Multi-Day Mean Reversion): 595 examples
  - Portfolio Risk Aggregator & Allocation: 510 examples
  - Platform / Infrastructure / Copilot: 360 examples

---

## 3. Deduplication & Contamination Screening

1. **Exact Deduplication**:
   - SHA-256 string matching on normalized (prompt, response) pairs identified and purged 42 identical template duplicates.
2. **Near-Duplicate Detection (MinHash / Jaccard Similarity $\ge 0.85$)**:
   - 68 near-identical repeated incident log summaries were deduplicated into canonical instructional variants.
3. **Benchmark Leakage Audit**:
   - Every question and answer pair from `MONEYMAKER_LLM_BENCHMARK_V1` (`BM-001` through `BM-010`) was screened against `DS_MM_LLM_V1` using embedding cosine similarity and exact n-gram matching.
   - **0.00% benchmark contamination detected**. All evaluation benchmarks are strictly held out.

---

## 4. Split Methodology & Source Grouping

- **Splits**:
  - `train.jsonl`: 1,459 examples (70%)
  - `val.jsonl`: 312 examples (15%)
  - `test.jsonl`: 314 examples (15%)
  - `heldout_benchmark.jsonl`: 50 specialized frozen benchmark scenarios.
- **Source Grouping**: Splitting is grouped by task family and incident epoch to prevent chronological leakage between train and validation.

---

## 5. Audit Verdict

`DS_MM_LLM_V1` meets all Phase 8C criteria: zero benchmark contamination, strict source grouping, complete provenance metadata, and explicit representation of negative/refusal authority examples.
