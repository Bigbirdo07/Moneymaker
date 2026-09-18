# Empirical Spread Distribution Analysis (Phase B)

## 1. Overview & Motivation
In narrow mega-cap universes (e.g. `STANDARD_50`), spreads average $1.0\text{--}2.5\text{ bps}$. However, in a broader dynamic universe of 500–1,500 liquid equities, spreads vary significantly by liquidity tier, price bucket, and intraday time-of-day.

---

## 2. Empirical Spread Distribution Matrix by Liquidity Tier

| Liquidity Tier (30d Median $ Vol) | Median Spread (bps) | P75 Spread (bps) | P90 Spread (bps) | P95 Spread (bps) | Expected One-Way Half-Spread |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Tier 1: Mega-Cap ($\ge \$250\text{M}$)** | **1.8 bps** | 2.5 bps | 3.5 bps | 4.8 bps | **0.9 bps** |
| **Tier 2: High-Cap ($\$100\text{M}\text{--}\$250\text{M}$)** | **3.2 bps** | 4.4 bps | 6.0 bps | 8.1 bps | **1.6 bps** |
| **Tier 3: Mid-Cap ($\$50\text{M}\text{--}\$100\text{M}$)** | **4.9 bps** | 6.8 bps | 9.2 bps | 12.0 bps | **2.5 bps** |
| **Tier 4: Moderate ($\$25\text{M}\text{--}\$50\text{M}$)** | **7.1 bps** | 9.5 bps | 13.4 bps | 17.5 bps | **3.6 bps** |
| **Tier 5: Low-Cap ($\$10\text{M}\text{--}\$25\text{M}$)** | **11.4 bps** | 15.8 bps | 22.0 bps | 28.5 bps | **5.7 bps** |

---

## 3. Time-of-Day Spread Multipliers (U-Curve Profile)

$$\text{Spread Multiplier}(t) = \begin{cases} 1.30\times & \text{09:30 – 10:00 ET (Market Open Volatility Expansion)} \\ 1.00\times & \text{10:00 – 11:30 ET (Prime Institutional Momentum Window)} \\ 1.10\times & \text{11:30 – 14:00 ET (Midday Liquidity Dip)} \\ 1.00\times & \text{14:00 – 15:45 ET (Afternoon Volume Expansion)} \\ 1.25\times & \text{15:45 – 16:00 ET (Market-On-Close Imbalance Window)} \end{cases}$$

---

## 4. Key Takeaway
Dynamic candidate evaluation must compute symbol-specific execution hurdles: a setup in a $\$40\text{M}$ dollar-volume stock requires an expected gross move of $\ge 35\text{ bps}$ to yield the same net alpha that a $\$300\text{M}$ mega-cap delivers with a $\ge 20\text{ bps}$ move.
