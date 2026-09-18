# MMRM-0.2 Empirical Evaluation Plan & Target Capabilities

**Benchmark Manifest**: `MONEYMAKER_LLM_BENCHMARK_V3` (320 Frozen Items)  
**Manifest SHA-256**: `638e39a8aeae48252c06598d058054d7fe0787f817ad238f871daf577440eadc`  

---

## 1. Targeted Improvements from MMRM-0.1 $\to$ MMRM-0.2

| Evaluated Dimension | Base (Observed) | MMRM-0.1 (Observed) | MMRM-0.2 (Target) | Design Strategy in DS_MM_LLM_V3 |
| :--- | :--- | :--- | :--- | :--- |
| **Statistical Reasoning** | 0.0% / 100% sem | 45.0% / 100% sem | **$\ge 80.0\%$ strict** | 450 verified mathematical step-by-step derivations |
| **Multi-Tool Sequencing** | 0.0% | 10.0% | **$\ge 75.0\%$ strict** | 350 multi-step diagnostic pipelines with stop criteria |
| **Tool Selection** | 0.0% | 100.0% | **100.0% strict** | Retain direct tool routing examples |
| **Governance & Authority** | 0.0% / 50% sem | 100.0% / 50% sem | **100.0% strict** | 200 adversarial prompt rejection assertions |
| **OOD Regimes** | 38.0% (OOD-V1) | 49.0% (OOD-V1) | **$\ge 65.0\%$ (OOD-V1)** | 300 stress/tail event diagnostic examples |
| **Ambiguity & Uncertainty**| 0.0% | 0.0% | **$\ge 80.0\%$ strict** | 250 `KNOWN`/`LIKELY`/`UNKNOWN` taxonomy items |

---

## 2. Evaluation Matrix Plan
Upon cluster completion of Job `64519876`:
1. Submit real benchmark inference across all 320 items of Benchmark V3.
2. Score in both `STRICT_PLATFORM` and `SEMANTIC_CAPABILITY` modes.
3. Compute paired McNemar test and bootstrap confidence intervals against MMRM-0.1 and Base Qwen.
