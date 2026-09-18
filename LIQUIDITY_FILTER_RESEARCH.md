# Liquidity Filter & Threshold Research (Phase B)

## 1. Research Framework & Objectives
The **Liquidity Filter** establishes parameterized criteria to eliminate illiquid, wide-spread, or micro-cap securities where execution slippage destroys quantitative momentum edges.

---

## 2. Liquidity Tier Hierarchy & Empirical Thresholds

| Liquidity Tier | 30-Day Median Dollar Vol | Typical Median Spread (bps) | Est. Eligible Universe Size | Tradability Status |
| :--- | :---: | :---: | :---: | :--- |
| **Tier 1: Mega-Liquid** | $\ge \$250\text{M}$ | $1.0\text{--}2.5\text{ bps}$ | $\approx 100\text{--}150$ symbols | **PRIMARY HIGH-CAPACITY** |
| **Tier 2: High-Liquid** | $\$100\text{M} \text{ to } \$250\text{M}$ | $2.5\text{--}4.0\text{ bps}$ | $\approx 250\text{--}350$ symbols | **PRIMARY TRADABLE** |
| **Tier 3: Mid-Liquid** | $\$50\text{M} \text{ to } \$100\text{M}$ | $4.0\text{--}6.0\text{ bps}$ | $\approx 400\text{--}600$ symbols | **TRADABLE WITH HURDLE** |
| **Tier 4: Moderate-Liquid** | $\$25\text{M} \text{ to } \$50\text{M}$ | $6.0\text{--}8.0\text{ bps}$ | $\approx 500\text{--}800$ symbols | **MARGINAL (RESEARCH ONLY)** |
| **Tier 5: Low-Liquid** | $\$10\text{M} \text{ to } \$25\text{M}$ | $8.0\text{--}15.0\text{ bps}$ | $\approx 600\text{--}900$ symbols | **DISQUALIFIED (SPREAD TOO WIDE)** |
| **Tier 6: Illiquid / Microcap** | $< \$10\text{M}$ | $> 15.0\text{ bps}$ | $10,000+$ symbols | **STRICTLY EXCLUDED** |

---

## 3. Price Filter Research

| Price Floor | Minimum Share Price | Spread Impact | Low-Price Reversal Noise | Recommended Adoption |
| :---: | :---: | :---: | :---: | :--- |
| **Sub-$5** | $<\$5.00$ | Severe ($>20\text{ bps}$ on 1-cent tick) | Extreme microcap noise | **STRICTLY EXCLUDED** |
| **$5.00** | $\ge \$5.00$ | Moderate ($5\text{--}10\text{ bps}$) | Elevated volatility | **RESEARCH CANDIDATE** |
| **$10.00 (Standard)** | $\ge \$10.00$ | Tight ($\le 5\text{ bps}$ on 1-cent tick) | Stable institutional flow | **BASELINE RECOMMENDED** |
| **$20.00** | $\ge \$20.00$ | Ultra-tight ($\le 2.5\text{ bps}$) | Low retail noise | **HIGH-CAPACITY TIER** |

---

## 4. Production Rule Recommendation
- **Price Minimum**: $\ge \$10.00$
- **30-Day Median Dollar Volume**: $\ge \$25,000,000$ (Guarantees sufficient depth for $\ge \$1,000\text{--}\$25,000$ orders)
- **30-Day ADV Shares**: $\ge 500,000\text{ shares/day}$
- **Max Estimated Spread**: $\le 8.0\text{ bps}$
