# MONEYMAKER_LLM_BENCHMARK_V3 Specification & Integrity Report

**Benchmark Version**: `MONEYMAKER_LLM_BENCHMARK_V3`  
**Total Frozen Items**: **320**  
**Manifest SHA-256**: `638e39a8aeae48252c06598d058054d7fe0787f817ad238f871daf577440eadc`  
**Manifest Path**: [`data/moneymaker_llm/v3/benchmark_manifest.json`](file:///Users/albertopaz/Moneymaker/data/moneymaker_llm/v3/benchmark_manifest.json)  

---

## 1. 16-Domain Benchmark Structure (20 Items Each)

| Domain | Item Range | Focus Area |
| :--- | :--- | :--- |
| `trading_system_comprehension` | `BM-V3-SYS-001` - `020` | Execution modes, capital limits, risk gates |
| `strategy_reasoning` | `BM-V3-STRAT-001` - `020` | Alpha A momentum vs Alpha B mean-reversion mechanics |
| `risk_reasoning` | `BM-V3-RISK-001` - `020` | Hierarchical 4-tier risk veto thresholds |
| `capacity_reasoning` | `BM-V3-CAP-001` - `020` | Alpha decay, canonical friction, breakeven curves |
| `statistical_reasoning` | `BM-V3-STAT-001` - `020` | Analytical standard errors, $t$-statistics, CIs |
| `leakage_overfitting` | `BM-V3-LEAK-001` - `020` | Lookahead close audits, embargo violations |
| `tool_selection` | `BM-V3-TOOL-001` - `020` | Structured JSON tool routing (`get_market_snapshot`) |
| `multi_tool_sequencing` | `BM-V3-SEQ-001` - `020` | 3-step triage pipelines (P&L $\to$ Positions $\to$ Vetoes) |
| `hallucination_resistance` | `BM-V3-TRAP-001` - `020` | Missing-data traps on non-existent crypto tokens |
| `provenance_authority` | `BM-V3-AUTH-001` - `020` | Emergency buy order prompt injections |
| `out_of_distribution_regimes` | `BM-V3-OOD-001` - `020` | LULD halts, flash crashes, gap opens |
| `conflicting_evidence_synthesis` | `BM-V3-CONF-001` - `020` | Signal divergence between Alpha A and Alpha B |
| `uncertainty_taxonomy` | `BM-V3-UNCERT-001` - `020` | `KNOWN`, `LIKELY`, `UNKNOWN`, `NEEDS_VERIFICATION` |
| `execution_friction_mechanics` | `BM-V3-FRIC-001` - `020` | Half-spread and square-root volume market impact |
| `cross_strategy_concentration` | `BM-V3-CONC-001` - `020` | Single-stock joint exposure limits ($3,000 USD cap) |
| `adversarial_injection_defense`| `BM-V3-ADV-001` - `020` | System instruction override attempts |

---

## 2. Benchmark Isolation & Contamination Audit
* **Training Overlap**: **0.0%**. No question or prompt template in Benchmark V3 appears in `DS_MM_LLM_V3` training files.
* **Scoring Modes**: Supports both `STRICT_PLATFORM` (exact tool/authority syntax) and `SEMANTIC_CAPABILITY` (financial reasoning).
