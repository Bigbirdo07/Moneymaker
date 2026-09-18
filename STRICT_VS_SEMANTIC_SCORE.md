# Strict Platform Score vs Semantic Capability Score Report

**Purpose**: Disentangle exact Moneymaker syntax/format compliance from core quantitative and financial reasoning capability.

---

## 1. 4-System Calibrated Results Matrix

| System | Strict Platform Score | Semantic Capability Score | Strict vs Semantic Delta |
| :--- | :--- | :--- | :--- |
| **1. Base Only (Qwen2.5-14B)** | **0.00%** (0 / 200) | **40.00%** (80 / 200) | **+40.00%** |
| **2. Base + RAG** | **42.50%** (85 / 200) | **64.00%** (128 / 200) | **+21.50%** |
| **3. MMRM-0.1-REAL** | **26.00%** (52 / 200) | **50.50%** (101 / 200) | **+24.50%** |
| **4. MMRM-0.1-REAL + RAG** | **71.50%** (143 / 200) | **88.00%** (176 / 200) | **+16.50%** |

---

## 2. Multi-Dimensional Score Radar

| Evaluated Dimension | Base (Strict) | Base (Semantic) | MMRM (Strict) | MMRM (Semantic) |
| :--- | :--- | :--- | :--- | :--- |
| **General Quantitative Reasoning** | 0.0% | 40.0% | 0.0% | **53.0%** |
| **Domain Platform Knowledge** | 0.0% | 12.5% | 0.0% | **12.5%** |
| **Tool Execution & Routing** | 0.0% | 0.0% | **22.0%** | **22.0%** |
| **Numerical Calculations** | 0.0% | **100.0%** | 45.0% | **100.0%** |
| **Provenance Tagging** | 0.0% | **100.0%** | **100.0%** | **100.0%** |
| **Governance & Authority** | 0.0% | 50.0% | **50.0%** | **50.0%** |
| **Hallucination Resistance** | 0.0% | 0.0% | 0.0% | 0.0% |
| **Format Compliance** | 0.0% | **100.0%** | **100.0%** | **100.0%** |

---

## 3. Conclusions & Recommendations
* **Strict Scoring is essential for Copilot Tool Actions**: A model must emit exact valid JSON/tool syntax to trigger workstation API endpoints. On this metric, MMRM achieves a decisive breakthrough over Base.
* **Semantic Scoring reflects user satisfaction for explanations**: When explaining capacity decay or trade statistics, semantic evaluations demonstrate that MMRM-0.1-REAL outperforms Base by +10.5% to +13.0%.
* **Production Recommendation**: Use **MMRM-0.1-REAL + RAG** for Workstation Copilot A/B testing (88.0% semantic accuracy, 71.5% strict execution accuracy).
