# Alpha A Tier 3 Longitudinal Stability Report (Phase 7A Track A)

**Strategy**: `ALPHA_A_INTRADAY_RELATIVE_MOMENTUM_V1`  
**Capital Tier**: **Tier 3 ($10,000 USD)**  
**Sample Window**: 210 live fills across 35 autonomous market sessions  
**Evidence Type**: `LIVE_AUTONOMOUS`

---

## 1. Longitudinal Empirical Performance

| Metric | Tier 0 ($1k) | Tier 1 ($2.5k) | Tier 2 ($5k) | Tier 3 ($10k) | Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Gross Alpha** | +4.920 | +4.900 | +4.890 | **+4.870** | bps / trade |
| **Canonical Friction** | 3.350 | 3.400 | 3.580 | **3.760** | bps / trade |
| **Net Expectancy** | +1.570 | +1.500 | +1.310 | **+1.110** | bps / trade |
| **95% Confidence Interval** | [+1.02, +2.12] | [+0.95, +2.05] | [+0.76, +1.86] | **[+0.58, +1.64]** | bps / trade |
| **Absolute Retention** | 100.0% | 95.5% | 83.4% | **70.7%** | % of Tier 0 |
| **Incremental Retention** | N/A | 95.5% | 87.3% | **84.7%** | % of Prev Tier |
| **Cost Break-Even Mult** | 1.47x | 1.44x | 1.37x | **1.30x** | Ratio |
| **Spearman Rank IC** | +0.049 | +0.048 | +0.047 | **+0.046** | Rank Corr |
| **Profit Factor** | 1.26 | 1.24 | 1.21 | **1.18** | Ratio |
| **Max Drawdown** | $13.50 (1.35%) | $34.50 (1.38%) | $72.00 (1.44%) | **$148.00 (1.48%)**| USD (%) |
| **Passive Fill Rate** | 63.6% | 62.4% | 61.5% | **60.2%** | % |
| **Partial Fill Rate** | 0.0% | 1.2% | 3.1% | **4.8%** | % |
| **P95 Participation** | 0.012% | 0.029% | 0.058% | **0.118%** | % Volume |

---

## 2. Canonical Friction Accounting & Spread Reconciliation

$$\begin{aligned}
\text{Total Round-Trip Friction (Tier 3)} &= \text{Entry Spread (1.64 bps)} + \text{Exit Spread (1.64 bps)} \\
&\quad + \text{Entry Slippage (0.05 bps)} + \text{Exit Slippage (0.05 bps)} \\
&\quad + \text{Market Impact (0.32 bps)} + \text{Latency (0.06 bps)} + \text{Fees (0.00 bps)} \\
&= \mathbf{3.760\text{ bps}}
\end{aligned}$$

$$\text{Gross Alpha (+4.870 bps)} - \text{Total Friction (3.760 bps)} = \mathbf{+1.110\text{ bps}}\quad (\text{Exact Identity Verified})$$

---

## 3. Symbol-Level Friction & Partial Fill Breakdown

| Symbol | Fills | Gross Alpha (bps) | Canonical Friction (bps) | Net Expectancy (bps) | Partial Fill Rate (%) | P95 Participation (%) | Capacity State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NVDA** | 78 | +5.12 | 3.65 | +1.47 | 3.8% | 0.095% | `HEALTHY` |
| **AMD** | 64 | +4.85 | 3.78 | +1.07 | 4.7% | 0.124% | `WATCH` |
| **TSLA** | 68 | +4.60 | 3.88 | +0.72 | 6.0% | 0.142% | `WATCH` |

> [!NOTE]
> All three core production archetype symbols remain net positive after full canonical friction. TSLA exhibits slightly higher friction (3.88 bps) due to wider quoted spreads during morning volatility, but retains positive edge (+0.72 bps).

---

## 4. Stability Audit Summary

Alpha A demonstrates stable intraday operation at $10,000 USD. While retention has moderated to 70.7%, execution parameters and loss firewalls remain well within pre-registered limits.
