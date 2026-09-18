# MMRM-0.2 Out-of-Distribution (OOD) Stress & Generalization Report

**Document**: `MMRM_0_2_OOD_REPORT.md`  
**Date**: 2026-09-16  
**Benchmarks**: `MONEYMAKER_OOD_CHALLENGE_V1` (100 items) & Benchmark V3 OOD Domain (20 items)  

---

## 1. OOD Challenge V1 Categories & Results

The 100-item OOD Challenge tests model generalization on completely unseen portfolio states, unexpected exchange halts, novel synthetic tickers, and conflicting market signals.

| # | OOD Challenge Category | Items | Base Qwen | MMRM-0.1 | MMRM-0.2-REAL | MMRM-0.2 + RAG |
| :-: | :--- | :-: | :---: | :---: | :---: | :---: |
| 1 | `unseen_portfolio_scenario` | 10 | 40% | 50% | **80%** | **100%** |
| 2 | `novel_risk_incident` | 10 | 50% | 60% | **90%** | **100%** |
| 3 | `new_combination_of_tools` | 10 | 30% | 50% | **80%** | **90%** |
| 4 | `different_numerical_values` | 10 | 30% | 40% | **80%** | **90%** |
| 5 | `ambiguous_evidence` | 10 | 40% | 40% | **70%** | **90%** |
| 6 | `conflicting_metrics` | 10 | 30% | 40% | **70%** | **90%** |
| 7 | `unexpected_broker_state` | 10 | 50% | 60% | **80%** | **90%** |
| 8 | `new_strategy_name` | 10 | 40% | 50% | **70%** | **90%** |
| 9 | `unknown_instrument` | 10 | 30% | 50% | **80%** | **90%** |
| 10 | `new_research_experiment` | 10 | 40% | 50% | **70%** | **90%** |
| **Total** | **OOD Challenge V1** | **100** | **38.0%** | **49.0%** | **76.0%** | **92.0%** |

---

## 2. Generalization Analysis

- **OOD Accuracy Gain**: `MMRM-0.2-REAL` achieved **76.0%** standalone OOD accuracy (+27.0% vs MMRM-0.1's 49.0%).
- **Novel Instrument Handling**: When asked about unseen equities (e.g. `CRWD`, `DDOG`, `PANW`), `MMRM-0.2` avoids hallucinating pre-cached positions and instead executes `get_market_snapshot` or reports `UNKNOWN`.
- **LULD Halts & Flash Crashes**: Correctly invokes Tier 4 order gateway rejection logic without assuming normal liquidity.
