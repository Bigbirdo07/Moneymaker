# Engine V2 Empirical Failure Forensics & Loss Analysis Report

## 1. Executive Summary
This report provides root-cause forensics on all **319 trades executed by Engine V2** during the 12-month 2025 out-of-sample walk-forward validation on real Alpaca/IEX data.

## 2. Failure Mode Taxonomy & Attribution

| Failure Mode Classification | Trade Count | Total Net P&L ($) | Avg P&L / Trade ($) | Description & Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **`INTRADAY_STOP_OUT`** | 100 | **$-676.22** | $-6.76 | Adverse intraday drift hitting -1.50% hard stop loss. |
| **`OVERNIGHT_GAP_SHOCK`** | 34 | **$-614.39** | $-18.07 | Severe gap-downs (e.g. NKE -10.85%, AMD -7.57%, ORCL -6.25%) blowing through stop losses. |
| **`SIGNAL_DECAY_FAILURE`** | 16 | **$-53.88** | $-3.37 | Predicted edge decayed to negative within 10-30 bars. |
| **`LOW_EDGE_CHURN`** | 5 | **$-7.84** | $-1.57 | Small price drift (-0.5% to +0.5%) overwhelmed by round-trip transaction costs. |
| **`REGIME_CASCADE_FAILURE`** | 2 | **$-7.43** | $-3.72 | Broad market selloffs where long positions experienced multi-bar decay. |
| **`FRICTION_CHURN_LOSS`** | 5 | **$-0.93** | $-0.19 | Gross price move was positive, but transaction friction turned trade into a net loss. |
| **`WINNING_MODERATE`** | 85 | **$+306.16** | $+3.60 | Modest positive returns (+0.5% to +2.5%). |
| **`WINNING_HIGH_QUALITY`** | 72 | **$+1,026.40** | $+14.26 | Large multi-percent right-tail winners (> +2.5% net). |

## 3. The Three Primary Architectural Flaws of Engine V2

### A. Friction Subsidization on Low-Quality Churn
- Out of 319 trades, **162 were losing or flat trades**.
- Total friction paid was **$106.00**, completely exceeding total gross price alpha (**+$77.86**).
- **Flaw**: Engine V2 evaluated opportunities in isolation with a low net edge hurdle (12 bps), causing excessive churn on marginal candidates.

### B. Blindness to Macro Market & Volatility Regimes
- In November 2025, Engine V2 took 32 long trades during a tech-sector correction, losing **-$109.52** in a single month.
- In December 2025, NKE gapped down -10.85% on earnings, causing a **-$50.75** single-trade loss.
- **Flaw**: Engine V2 lacked a Stage-1 Market Regime Gate to disable long entries during SPY downtrends or elevated volatility shocks.

### C. Absolute Momentum vs. Cross-Sectional Ranking
- Engine V2 traded individual stocks whose past 15m/60m momentum was positive, even when the entire market was falling.
- **Flaw**: It lacked contemporaneous cross-sectional ranking across the 50-stock universe.

## 4. Design Imperatives for Engine V3
1. **Stage 1 Market Regime Gate**: 100% Cash preservation when SPY is in a downtrend or volatility expansion is elevated.
2. **Stage 2 Cross-Sectional Ranker**: Rank all 50 stocks contemporaneously; only trade the top 1st percentile relative strength leaders.
3. **Stage 3 Cost-Aware Hurdle**: Minimum 25.0 bps expected edge ($\ge 2.5x$ friction).
4. **Turnover Cap**: Maximum 1 high-conviction trade per day (reducing annual volume to ~100–150 trades).