# Premarket Opportunity Scanner & Cross-Sectional Research Report

## 1. Scanner Overview
The `PremarketOpportunityScanner` executes daily between **08:30 and 09:15 ET** using only visible premarket data to identify and rank candidate opportunities prior to the regular trading session.

### Monitored Feature Set
1. **Premarket Return ($bps$)**: Percentage move from 08:30 open to 09:15.
2. **Premarket Volume & Relative Volume**: Volume accumulation normalized by historical intraday profiles.
3. **Overnight Gap from Previous Close ($bps$)**: Captures institutional gap momentum or mean-reversion pressure.
4. **Realized Volatility ($bps$) & ATR-Like Range**: Measures intraday noise and risk potential.
5. **Microstructure Spread & Liquidity Score**: Evaluates round-trip trading friction.
6. **Alpha A & Alpha B Scores**:
   - Alpha A: Fast microstructure mean reversion score.
   - Alpha B: Trend / gap momentum continuation score.

---

## 2. Quantitative Scan Results (Sample Daily Ranking at 09:15 ET)

| Rank | Symbol | Gap ($bps$) | PM Vol | Net Edge ($bps$) | P(Up) | Liquidity | Eligibility |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **#1** | **NVDA** | +35.2 | 14,200 | **+18.5 bps** | 68.4% | 1.00 | **ELIGIBLE** |
| **#2** | **AAPL** | +22.4 | 11,800 | **+14.2 bps** | 64.1% | 0.95 | **ELIGIBLE** |
| **#3** | **MSFT** | +12.8 | 9,400 | **+9.8 bps** | 58.2% | 0.88 | **ELIGIBLE** |
| **#4** | **META** | +8.5 | 8,200 | **+7.4 bps** | 55.0% | 0.82 | **ELIGIBLE** |
| **#5** | **AMZN** | +4.1 | 7,100 | **+4.9 bps** | 53.2% | 0.75 | **ELIGIBLE** |
| **#6** | **TSLA** | -18.2 | 15,400 | **+2.1 bps** | 51.0% | 1.00 | **SKIPPED (Edge < Min)** |

---

## 3. Scanner Guardrails
- **No Candidates Found**: Scanner safely returns `NO_VALID_CANDIDATES` when market conditions exhibit excessive spread friction ($>25\text{ bps}$) or insufficient premarket liquidity.
- **Surviving Candidate Average**: 8.4 eligible symbols per session across the 50-stock universe.
