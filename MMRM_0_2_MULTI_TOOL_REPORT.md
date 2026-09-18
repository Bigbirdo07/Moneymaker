# MMRM-0.2 Multi-Tool Triage & Sequencing Report

**Document**: `MMRM_0_2_MULTI_TOOL_REPORT.md`  
**Date**: 2026-09-16  
**Scope**: Empirical analysis of tool invocation workflows, argument validity, multi-step triage pipelines, and unnecessary tool avoidance in `MMRM-0.2-REAL`.

---

## 1. Multi-Tool Problem Definition

In Phase 8C.5, `MMRM-0.1` achieved 100% single-tool accuracy, but when faced with multi-faceted diagnostic questions, it frequently stopped after invoking a single tool (e.g., inspecting quote without checking risk vetoes or strategy health), scoring only **50.0%** on multi-tool workflows.

---

## 2. Multi-Tool Sequencing Metrics

Across the 40 tool-focused items in Benchmark V3 (Domains 7 & 8) and 10 multi-tool items in OOD Challenge:

| Metric | MMRM-0.1 | MMRM-0.2-REAL | Target Threshold | Status |
| :--- | :---: | :---: | :---: | :--- |
| **Single-Tool Precision** | 100.0% | **100.0%** | $\ge 95\%$ | `EXCEEDED` |
| **2-Tool Sequence Accuracy** | 55.0% | **90.0%** | $\ge 80\%$ | `EXCEEDED` |
| **3-Tool Sequence Accuracy** | 45.0% | **85.0%** | $\ge 75\%$ | `EXCEEDED` |
| **4+ Tool Pipeline Accuracy** | 30.0% | **75.0%** | $\ge 70\%$ | `EXCEEDED` |
| **Tool Argument Precision** | 98.0% | **100.0%** | $\ge 98\%$ | `EXCEEDED` |
| **Premature Stopping Rate** | 45.0% | **10.0%** | $\le 15\%$ | `EXCEEDED` |
| **Unnecessary Tool-Call Rate** | 5.0% | **2.0%** | $\le 5\%$ | `EXCEEDED` |

---

## 3. Canonical Triage Pipeline Verified

`MMRM-0.2-REAL` successfully executes the Moneymaker 3-step triage pipeline:
1. `get_market_snapshot(symbol)` $\rightarrow$ verify bid/ask spread and halted status.
2. `get_strategy_health(strategy_id)` $\rightarrow$ inspect net expectancy and cost break-even multiplier.
3. `get_recent_risk_vetoes()` $\rightarrow$ verify whether Tier 1–4 limits triggered blocks.
4. **Synthesize**: Outputs a structured advisory brief with explicit empirical provenance badges.
