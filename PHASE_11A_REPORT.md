# Phase 11A Master Report: Broader Real-Market Regime Validation (2025 Walk-Forward Study)

## 1. Executive Summary & Governance Overview
Phase 11A investigated the critical research question regarding the frozen **`REAL_MARKET_ENGINE_V2_CANDIDATE`**:
> *"Does the frozen strategy produce repeatable positive expectancy across multiple independent market regimes without depending on one symbol, one day, or a tiny number of outsized trades?"*

To resolve this, a 12-month rolling-origin walk-forward study was executed on the **UMass Amherst Unity HPC cluster** across 12 untouched monthly out-of-sample evaluation windows spanning **2025-01-02 through 2025-12-31** (250 trading sessions, 50 canonical equities, 319 executed trades).

In accordance with strict research governance:
- **Zero Retraining or Optimization on August 2026**: August 2026 remained strictly labeled `BURNED_HOLDOUT_DO_NOT_REUSE` and was excluded from all model training and tuning.
- **Strict Rolling Origin**: For each month $T$, models were trained strictly on observations $[t_0, t_{T-1}]$ with zero future leakage.
- **Candidate Freeze**: Strategy logic, parameters, thresholds, universe, and sizing rules were preserved with 100% SHA-256 hash parity.

---

## 2. Formal Governance Verdicts

| Governance Dimension | Formal Verdict | Operational Interpretation |
| :--- | :--- | :--- |
| **BROADER VALIDATION** | **`BROADER_VALIDATION_FAILED`** | Across 12 independent OOS months, net P&L was negative (-$28.12, net return -2.81%, PF 0.98), failing the multi-month positive expectancy threshold. |
| **CONCENTRATION** | **`CONCENTRATION_STRUCTURAL`** | Profitability in winning months was overwhelmingly driven by single-stock idiosyncratic outliers (e.g. TXN, AMD, NVDA, TSLA). Removing top 3 trades drives net P&L deeply negative (-$152.46). |
| **ENGINE STATUS** | **`ENGINE_V2_REDESIGN_REQUIRED`** | Engine V2 cannot be deployed as-is; alpha architecture requires fundamental redesign (Engine V3) focusing on true cross-sectional ranking and structural regime-robust features. |
| **PAPER TRADING GATE** | **`MORE_REAL_HISTORICAL_VALIDATION`** / `RETURN_TO_ALPHA_RESEARCH` | Strategy is not ready for live paper trading; must return to alpha modeling and regime diversification. |
| **REAL MONEY** | **`REAL_MONEY_NOT_AUTHORIZED`** | Real capital deployment remains strictly prohibited. |

---

## 3. Month-by-Month Empirical Performance Ledger (2025 OOS)

| Month | Starting Cap ($) | Ending Cap ($) | Net Ret (%) | Net P&L ($) | Gross P&L ($) | Friction ($) | Trades | Win Rate (%) | PF | Max DD (%) | Trades/Day | Best Symbol | Best Sym Share % |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2025-01** | $1,000.00 | $1,042.78 | **+4.28%** | +$42.78 | +$52.51 | $9.73 | 27 | 59.3% | 1.41 | 5.52% | 1.35 | `INTC` | 105.1% |
| **2025-02** | $1,042.78 | $1,064.25 | **+2.06%** | +$21.47 | +$29.43 | $7.96 | 21 | 47.6% | 1.23 | 4.19% | 1.11 | `NVDA` | 109.5% |
| **2025-03** | $1,064.25 | $1,044.79 | **-1.83%** | -$19.46 | -$9.75 | $9.71 | 28 | 46.4% | 0.84 | 3.24% | 1.40 | `INTC` | 92.7% |
| **2025-04** | $1,044.79 | $1,050.33 | **+0.53%** | +$5.54 | +$15.09 | $9.55 | 32 | 50.0% | 1.04 | 4.33% | 1.52 | `TXN` | 922.9% |
| **2025-05** | $1,050.33 | $1,064.24 | **+1.32%** | +$13.91 | +$23.59 | $9.68 | 31 | 51.6% | 1.12 | 5.34% | 1.48 | `AMD` | 329.4% |
| **2025-06** | $1,064.24 | $1,055.14 | **-0.86%** | -$9.10 | -$3.67 | $5.43 | 16 | 43.8% | 0.84 | 2.31% | 0.80 | `ORCL` | 103.7% |
| **2025-07** | $1,055.14 | $1,138.82 | **+7.93%** | +$83.68 | +$91.41 | $7.73 | 21 | 61.9% | 2.89 | 1.83% | 0.95 | `TMO` | 60.5% |
| **2025-08** | $1,138.82 | $1,133.20 | **-0.49%** | -$5.62 | +$1.84 | $7.47 | 20 | 50.0% | 0.95 | 3.58% | 0.95 | `TSLA` | 317.4% |
| **2025-09** | $1,133.20 | $1,155.92 | **+2.00%** | +$22.72 | +$32.86 | $10.14 | 27 | 48.1% | 1.22 | 3.78% | 1.29 | `TSLA` | 104.9% |
| **2025-10** | $1,155.92 | $1,157.41 | **+0.13%** | +$1.49 | +$15.37 | $13.89 | 46 | 52.2% | 1.01 | 4.67% | 2.00 | `AMD` | 2691.7% |
| **2025-11** | $1,157.41 | $1,047.88 | **-9.46%** | -$109.52 | -$99.35 | $10.17 | 32 | 31.2% | 0.45 | 9.71% | 1.68 | `NFLX` | 9.4% |
| **2025-12** | $1,047.88 | $971.87 | **-7.25%** | -$76.01 | -$71.47 | $4.54 | 18 | 50.0% | 0.21 | 7.85% | 0.82 | `GOOGL` | 7.4% |
| **TOTAL** | **$1,000.00** | **$971.87** | **-2.81%** | **-$28.12** | **+$77.86** | **$106.00** | **319** | **49.2%** | **0.98** | **9.71%** | **1.27** | `TXN` | **495.2%** |

---

## 4. Key Quantitative Insights & Scientific Discoveries

### A. The "Profitable Month" Illusion vs. Structural Expectancy
- In single-month snapshots, Engine V2 produced seemingly attractive returns (+5.76% in June–July 2026, +5.12% in August 2026, +7.93% in July 2025, +4.28% in January 2025). Indeed, **7 out of 12 months in 2025 were profitable (58.3% monthly win rate)**.
- However, across a full 12-month multi-regime walk-forward cycle, the cumulative net P&L was **-$28.12** with an aggregate profit factor of **0.98**.
- The root cause is asymmetry in tail risk: winning months generated small to moderate profits (+$1.49 to +$83.68), but adverse regime transitions (e.g. Nov 2025 -$109.52, Dec 2025 -$76.01) generated severe multi-position drawdowns that erased all accumulated gains.

### B. Structural Concentration Proven
- In every profitable month, a single ticker represented between **60% and 900%+** of that month's net P&L.
- Across the entire 12-month study, the diagnostic counterfactuals reveal:
  - Full Strategy Net P&L: `-$28.12`
  - Excluding Best Trade: `-$71.65`
  - Excluding Top 3 Trades: `-$152.46`
  - Excluding Best Symbol (`TXN`): `-$90.37`
- This proves conclusively that **concentration is structural, not accidental or isolated to 2026**. Engine V2 does not have a broad, diversified edge across the 50-stock universe; it is a lottery ticket on idiosyncratic momentum bursts that gets slowly eroded by transaction friction and whipsaw selloffs.

### C. Cost Drag & Breakeven Multiplier
- The strategy generated **+$77.86** in gross price edge, but paid **$106.00** in realistic transaction costs (spread + slippage + commission).
- Aggregate breakeven friction multiplier is **0.73x** baseline costs (meaning transaction costs must be cut by >27% just to achieve zero P&L over the full cycle).

---

## 5. Architectural Recommendation: Transition to Engine V3
The empirical findings from Phase 10.4, 10.5, and 11A provide decisive clarity:
1. `REAL_MARKET_ENGINE_V2_CANDIDATE` is retired from live forward candidate status.
2. Development must transition to **REAL_MARKET_ENGINE_V3_CANDIDATE** with core architectural innovations:
   - **Cross-Sectional Rank Long/Short or Neutralization**: Remove market direction and single-stock beta drift dependency.
   - **Regime-Adaptive Volatility Sizing**: Dynamically scale down portfolio capital during high-volatility regime shifts.
   - **Tighter Friction-Aware Gating**: Only trade when expected gross edge exceeds 3x round-trip friction.