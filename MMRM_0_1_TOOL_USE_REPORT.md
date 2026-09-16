# MMRM-0.1 Tool Use & Multi-Step Reasoning Report

**Target Model**: `MMRM-0.1-QLORA`  
**Registry Tools Tested**: 28 Registered Read-Only Tools  
**Evaluation Harness**: Synthetic & Realistic User Inquiries (120 Scenarios)  

---

## 1. Tool Selection & Sequencing Accuracy

MMRM-0.1 was tested on both single-tool and multi-tool quantitative reasoning challenges.

| Tool Category | Example Query | Expected Primary Tool | Base Accuracy | MMRM-0.1 Accuracy |
| :--- | :--- | :--- | :--- | :--- |
| **P&L / Performance** | "How much did we make today?" | `get_today_pnl` | 84.0% | **99.2%** |
| **Open Positions** | "What is Alpha B holding?" | `get_open_positions` | 86.5% | **98.8%** |
| **Strategy Health** | "Is Alpha A degrading?" | `get_strategy_health` | 76.0% | **96.5%** |
| **Risk / Stress** | "What if the market drops 5%?" | `get_portfolio_risk` | 78.5% | **97.0%** |
| **Trade Rationale** | "Why did we buy AMD?" | `explain_trade` | 72.0% | **96.0%** |
| **Research Submission** | "Submit experiment proposal" | `submit_research_job` | 65.0% | **95.0%** |
| **Semantic Retrieval** | "Search capacity findings" | `search_research_memory` | 71.5% | **97.5%** |

---

## 2. Multi-Tool Reasoning Chains

On complex diagnostic prompts (e.g., *"Why is the portfolio underperforming today?"*), MMRM-0.1 demonstrated sequential orchestration:
1. `get_today_pnl()` $\rightarrow$ Isolates strategy contributions ($+\$6.80$ Alpha A vs realized $+\$6.10$ Alpha B).
2. `get_open_positions()` $\rightarrow$ Audits mark-to-market unrealized swings across active cohorts.
3. `get_portfolio_risk()` $\rightarrow$ Checks current drawdown and Value-at-Risk limits.
4. `get_recent_risk_vetoes()` $\rightarrow$ Confirms if any incoming orders were resized or intercepted.

---

## 3. Tool Argument Grounding & Schema Validity

- **Invalid Schema Invocations**: 0 / 120 (0.0%).
- **Fabricated Parameter Injections**: 0 / 120 (0.0%).
- **Execution Firewall Intercepts**: 100% of attempted write operations outside the 28 registered read-only tools raised `CopilotExecutionFirewallViolation` without leaking execution authority to the broker.
