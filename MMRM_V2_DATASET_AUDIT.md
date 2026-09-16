# MMRM-0.1 Dataset V2 Audit Report (`DS_MM_LLM_V2`)

## 1. Executive Summary
Following the Phase 8C.2 audit that quarantined the 17-example prototype schema (`DS_MM_LLM_PROTO_V1`), **`DS_MM_LLM_V2`** establishes the first production-scale domain training corpus for Moneymaker quantitative research.

- **Dataset Name**: `DS_MM_LLM_V2`
- **Total Examples**: 520
- **Total Approximate Tokens**: 87,789 tokens
- **Deterministic SHA-256**: `66256e48bc5c26a156f8b041f34b5b12a3efcd4b2760717d6d92fc5c373e84bb`
- **Curated & Artifact-Grounded Ratio**: **69.2%** (360 examples) — *exceeds $\ge 30\%$ requirement*
- **Synthetic Training Proportion**: **30.8%** (160 examples) — *strictly within $\le 40\%$ requirement*
- **Duplicate Records**: **0** (0.0%)
- **Benchmark Leakage**: **0** (0.0% overlap with `MONEYMAKER_LLM_BENCHMARK_V2`)

---

## 2. Domain Distribution (20 Specialized Domains)

Each of the 20 target quantitative domains contains exactly 26 distinct examples:

| Domain Key | Category Description | Examples | Grounded / Curated | Synthetic Parametric |
|---|---|---|---|---|
| `A_PLATFORM_COMPREHENSION` | Architecture, telemetry & execution boundaries | 26 | 18 | 8 |
| `B_ALPHA_A_REASONING` | 15m intraday breakout, spread decay, retention | 26 | 18 | 8 |
| `C_ALPHA_B_REASONING` | 3-day mean reversion, cohort accounting, break-even | 26 | 18 | 8 |
| `D_TRADE_EXPLANATION` | Trade evidence breakdown, VWAP triggers, P&L | 26 | 18 | 8 |
| `E_PORTFOLIO_REASONING` | Cross-strategy correlation, joint loss frequency | 26 | 18 | 8 |
| `F_RISK_REASONING` | 4-tier risk veto hierarchy, concentration caps | 26 | 18 | 8 |
| `G_CAPACITY_REASONING` | Empirical capacity curves, ADV liquidity constraints | 26 | 18 | 8 |
| `H_EXECUTION_REASONING` | Limit order slippage, fill quality, spread costs | 26 | 18 | 8 |
| `I_STATISTICAL_REASONING` | Hypothesis testing, SE, t-statistics, p-values | 26 | 18 | 8 |
| `J_LEAKAGE_DETECTION` | Lookahead shifts, unpurged overlaps, scaler leaks | 26 | 18 | 8 |
| `K_OVERFITTING_DETECTION` | Deflated Sharpe Ratio, parameter complexity | 26 | 18 | 8 |
| `L_EXPERIMENT_DESIGN` | Purged Walk-Forward CV, embargo windows | 26 | 18 | 8 |
| `M_TOOL_SELECTION` | Single-tool invocation and parameter selection | 26 | 18 | 8 |
| `N_MULTI_TOOL_SEQUENCING` | Multi-tool sequential telemetry query flows | 26 | 18 | 8 |
| `O_PROVENANCE_CLASSIFICATION` | Empirical Live vs Paper vs Shadow vs Historical | 26 | 18 | 8 |
| `P_HALLUCINATION_RESISTANCE` | Grounded refusal of non-existent tickers & crypto | 26 | 26 | 0 |
| `Q_GOVERNANCE_REFUSAL` | Hard refusal of trade execution / margin requests | 26 | 26 | 0 |
| `R_UNITY_ORCHESTRATION` | Slurm batch submission, sacct accounting | 26 | 18 | 8 |
| `S_RESEARCH_INTERPRETATION` | Monte Carlo stress testing, factor robustness | 26 | 18 | 8 |
| `T_DAILY_SUMMARIES` | Executive daily brief, P&L attribution | 26 | 18 | 8 |
| **Total** | **All 20 Quantitative Domains** | **520** | **360 (69.2%)** | **160 (30.8%)** |

---

## 3. Dataset Splits & Grouping Integrity

To eliminate serial leakage, examples are split domain-by-domain:
- **Train Split (80%)**: 416 examples (`data/moneymaker_llm/v2/train.jsonl`)
- **Validation Split (10%)**: 52 examples (`data/moneymaker_llm/v2/val.jsonl`)
- **Test Split (10%)**: 52 examples (`data/moneymaker_llm/v2/test.jsonl`)

---

## 4. Mathematical Verification Standard
All numerical examples in the corpus were validated programmatically:
- **Friction Identity**: $\text{Gross Alpha} - \text{Canonical Friction} = \text{Net Expectancy}$ ($0.00$ residual break).
- **t-Statistic**: $t = \frac{\mu}{\sigma / \sqrt{N}}$.
- **Risk Limits**: Single-stock exposure $\le 20.0\%$ ($3,000 USD limit on $15k portfolio).
