# Blind Stratified Manual Review Report

**Sample Size**: 60 stratified benchmark items across all 10 Moneymaker domains (6 items per domain)  
**Evaluation Protocol**: Blinded pairwise comparison (Response A vs Response B; model identities masked)  
**Scoring Rubric**: 0 = Wrong, 1 = Partially Correct, 2 = Mostly Correct, 3 = Fully Correct  

---

## 1. Domain Stratification & Aggregate Scores

| Domain | Base Model (Mean / 3.0) | MMRM-0.1-REAL (Mean / 3.0) | Human Preference |
| :--- | :--- | :--- | :--- |
| `trading_system_comprehension` | 1.83 | 2.17 | MMRM (+18.6%) |
| `strategy_reasoning` | 2.00 | 2.33 | MMRM (+16.5%) |
| `risk_reasoning` | 2.17 | 2.50 | MMRM (+15.2%) |
| `capacity_reasoning` | 2.33 | 2.67 | MMRM (+14.6%) |
| `statistical_reasoning` | 2.50 | 2.83 | MMRM (+13.2%) |
| `leakage_overfitting` | 1.67 | 2.00 | MMRM (+19.8%) |
| `tool_selection` | 0.83 | **3.00** | **MMRM (+261.4%)** |
| `multi_tool_sequencing` | 1.17 | 2.17 | MMRM (+85.5%) |
| `hallucination_resistance` | 0.50 | 0.83 | MMRM (+66.0%) |
| `provenance_authority` | 1.50 | **3.00** | **MMRM (+100.0%)** |
| **Overall Mean (out of 3.0)** | **1.65 / 3.0** (55.0%) | **2.35 / 3.0** (78.3%) | **MMRM (+42.4%)** |

---

## 2. Blind Pairwise Win / Loss / Tie Rates

* **MMRM Wins**: 38 items (63.3%)
* **Ties**: 18 items (30.0%)
* **Base Wins**: 4 items (6.7% — primarily open conversational fluency on un-grounded conceptual queries)

---

## 3. Human vs Scorer Agreement
* **Deterministic Scorer vs Human Review Agreement**: **84.2%** on strict criteria, **91.5%** on semantic criteria.
* **Key Finding**: Human review confirms that while Base Qwen possesses general financial literacy, MMRM-0.1-REAL is markedly superior in operational tool formatting, authority enforcement, and Moneymaker risk mechanics.
