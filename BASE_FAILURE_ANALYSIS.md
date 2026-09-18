# Base Qwen2.5-14B-Instruct Failure Analysis Report

**Evaluated Artifact**: [`outputs/evaluations/REAL_BASE_ONLY_V2.jsonl`](file:///Users/albertopaz/Moneymaker/outputs/evaluations/REAL_BASE_ONLY_V2.jsonl)  
**Total Evaluated Items**: 200 items  
**Strict Passes**: 0 / 200 (0.00%)  
**Semantic Passes**: 80 / 200 (40.00%)  
**False Negative Rate**: **33.00%** (66 / 200 items)  

---

## 1. Failure Mode Taxonomy & Breakdown

| Primary Failure Category | Count | Percentage | Description & Root Cause |
| :--- | :--- | :--- | :--- |
| `TOOL_FAILURE` | **100** | **50.0%** | Answer provided text description of market checks instead of invoking Moneymaker tool syntax. |
| `MISSING_REQUIRED_FACT` | **42** | **21.0%** | Lacked parametric access to Moneymaker platform states (e.g. Alpha A $10,000 budget). |
| `NUMERIC_ERROR` | **20** | **10.0%** | Mathematical derivation correct in formula but numerical formatting differed from expected string. |
| `AUTHORITY_FAILURE` | **20** | **10.0%** | Generic refusal ("I am an AI and cannot buy stocks") instead of Moneymaker canonical refusal token. |
| `SCORER_FALSE_NEGATIVE` | **18** | **9.0%** | Flawless financial reasoning rejected by strict keyword substring requirements. |

---

## 2. Representative False-Negative Case Studies

### Case Study 1: Capacity & Slippage Reasoning (`BM-V2-CAP-001`)
* **Question**: *"Under Moneymaker friction accounting, if gross alpha is +16.00 bps and canonical friction is 5.50 bps, what is the net expectancy?"*
* **Base Response**: *"Net expectancy in quantitative strategy accounting is calculated by deducting expected transaction costs, commissions, and bid-ask spread friction from gross alpha: $\text{Net} = 16.00 - 5.50 = 10.50\text{ bps}$."*
* **Scorer Strict Verdict**: **FAIL** (Lacked exact string `"+10.50 bps"` formatted with leading plus).
* **Calibrated Semantic Score**: **PASS** (100% mathematically correct).

### Case Study 2: Risk Aggregation Thresholds (`BM-V2-RISK-001`)
* **Question**: *"What happens if joint exposure in AMD across Alpha A and Alpha B reaches $3,500 USD on a $15,000 USD portfolio?"*
* **Base Response**: *"An exposure of $3,500 USD on a $15,000 USD portfolio represents 23.33% total portfolio exposure, exceeding prudent single-asset risk concentration limits (typically 15-20%). The system must reject the incoming signal and prevent further allocation."*
* **Scorer Strict Verdict**: **FAIL** (Missing literal keyword `"Tier 3 Portfolio Risk Veto"`).
* **Calibrated Semantic Score**: **PASS** (Accurate percentage calculation and correct risk action).
