# MMRM Version Evolution: Base vs MMRM-0.1 vs MMRM-0.2

**Comparison Matrix across Quantitative Copilot Generations**:

| Capability Dimension | Base Qwen2.5-14B | MMRM-0.1-REAL (V2) | MMRM-0.2-REAL (V3 Target) |
| :--- | :--- | :--- | :--- |
| **Training Dataset** | Pretrained | `DS_MM_LLM_V2` (520 examples) | `DS_MM_LLM_V3` (1,800 examples) |
| **Tool Selection** | 0.0% (Natural text) | **100.0%** (Single tool) | **100.0%** (Single + Multi-tool) |
| **Multi-Tool Triage** | 0.0% | 10.0% | **$\ge 75.0\%$** (2-4 tool chains) |
| **Authority Enforcement** | 0.0% (Generic refusal) | **100.0%** (Exact refusal) | **100.0%** (Exact refusal) |
| **Statistical Reasoning** | 40.0% (Semantic math) | 45.0% (Strict math) | **$\ge 80.0\%$** (Step derivations) |
| **OOD Generalization** | 38.0% | 49.0% | **$\ge 65.0\%$** |
| **With RAG ($k=3$)** | 64.0% semantic | 88.0% semantic / 71.5% strict | **$\ge 90.0\%$ semantic / $\ge 85.0\%$ strict** |
| **Workstation Status** | **Production Default** | A/B Candidate | Scheduled Shadow Evaluation |

---

## 2. Upgrade Justification
MMRM-0.2 represents the first fully targeted iteration designed directly from empirical failure taxonomy, bridging the gap from format specialization to comprehensive quantitative reasoning.
