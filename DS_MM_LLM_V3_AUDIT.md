# DS_MM_LLM_V3 Dataset Design & Provenance Audit Report

**Dataset ID**: `DS_MM_LLM_V3`  
**Total Examples**: **1,800**  
**Approximate Tokens**: **248,600**  
**Manifest SHA-256**: `e125f768bc2a20765fa64383592e4c2b42f71b90cca8a182bcc2497bd9bdbc66`  
**Dataset Directory**: [`data/moneymaker_llm/v3/`](file:///Users/albertopaz/Moneymaker/data/moneymaker_llm/v3/)  

---

## 1. Domain Allocation & Weakness Remediation

Rather than scaling domains uniformly, `DS_MM_LLM_V3` directly targets the specific operational failure modes identified during the Phase 8C.5 audit:

| Priority Focus Area | Target Failure Mode in MMRM-0.1 | Example Count | Percentage | Provenance Source |
| :--- | :--- | :--- | :--- | :--- |
| **1. Advanced Statistics** | Arithmetic & $t$-statistic errors | **450** | 25.0% | `src/evaluation/significance.py` |
| **2. Multi-Tool Triage Sequences** | Single-tool limitation | **350** | 19.4% | `src/workstation/copilot_tools.py` |
| **3. OOD Market Regimes** | Unfamiliar volatility/halts | **300** | 16.7% | `src/safety/live_guard.py` |
| **4. Conflicting Evidence** | Single-narrative bias | **250** | 13.9% | `src/portfolio/multi_strategy_research.py` |
| **5. Capacity & Friction Economics** | Scalability & impact curve errors | **250** | 13.9% | `src/stress/capacity_engine.py` |
| **6. Governance & Authority** | Retention of 100% read-only policy | **200** | 11.1% | `src/governance/human_approval.py` |
| **Total** | — | **1,800** | **100.0%** | — |

---

## 2. Splits & Stratification

* **Train Set**: [`data/moneymaker_llm/v3/train.jsonl`](file:///Users/albertopaz/Moneymaker/data/moneymaker_llm/v3/train.jsonl) (1,440 examples, 2.3 MB, SHA-256: `baa1182e9b866b006cbfcac8467b5c009e95ff456c2b73adee9731ef2639c676`)
* **Validation Set**: [`data/moneymaker_llm/v3/val.jsonl`](file:///Users/albertopaz/Moneymaker/data/moneymaker_llm/v3/val.jsonl) (180 examples, 286 KB, SHA-256: `2f185914f9a790f444610534b9a2538fd0ebaf96137f09a0eeed6cc7c0c840dc`)
* **Test Set**: [`data/moneymaker_llm/v3/test.jsonl`](file:///Users/albertopaz/Moneymaker/data/moneymaker_llm/v3/test.jsonl) (180 examples, 292 KB, SHA-256: `3865d741477ebf26d4ecc918bafe1f09f6d19d3387bda60f949e7d494d4d2c6d`)

---

## 3. Human Curation & Synthetic Limits

* **Human-Curated Core**: **400 examples** (22.2% of dataset; prioritized for complex mathematical derivations and multi-tool triages).
* **Synthetic Proportion**: **22.2% synthetic / 77.8% platform artifact-derived** (satisfies $\le 30-40\%$ limit).
* **Provenance Tagging**: Every synthetic record includes an explicit `SYNTHETIC_TRAINING_EXAMPLE` label.
