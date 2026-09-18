# Point-in-Time Universe Specification (Phase B)

## 1. System Pipeline & Reduction Funnel

$$\begin{aligned}
\text{All Listed U.S. Securities } (\approx 33,500) &\xrightarrow{\text{SecurityEligibilityPolicy}} \text{Eligible Common Equities } (\approx 6,500) \\
&\xrightarrow{\text{Price } \ge \$10.00} \text{Non-Penny Common Stocks } (\approx 3,800) \\
&\xrightarrow{\text{30d Median DolVol } \ge \$25\text{M}} \text{Tradable Liquid Universe } (\approx 800\text{--}1,200) \\
&\xrightarrow{\text{FastScanner Ranking}} \text{Top Candidates } (\approx 50\text{--}100) \\
&\xrightarrow{\text{Expected Net Edge } \ge 25\text{ bps}} \text{Executed Trades } (0\text{--}2\text{/day})
\end{aligned}$$

---

## 2. Point-in-Time Integrity Invariants
1. **No Forward Leakage**: Universe membership on date $T$ is computed strictly using volume, price, and listing data available as of $T-1$ market close.
2. **Audit Trails**: Every daily universe decision is saved to `daily_universe_manifest.parquet` and every symbol rejection is archived to `universe_exclusions.parquet`.
