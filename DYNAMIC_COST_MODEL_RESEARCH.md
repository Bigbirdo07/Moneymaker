# Dynamic Transaction Cost Model V2 Research (Phase B)

## 1. Mathematical Formulation

Total round-trip expected friction for candidate $i$ on bar $t$:

$$\text{Expected Total Friction}_{i, t} = 2 \times \left( \text{HalfSpread}_{i, t} + \text{HalfSlippage}_{i, t} + \text{Commission}_{i, t} + \text{MarketImpact}_{i, t} \right)$$

Where:
- $\text{HalfSpread}_{i, t} = \max\left(\frac{\$0.005}{P_i}, \frac{4.0}{\sqrt{\text{DolVol}_{i}/\$1\text{M}}} \times \left(1 + \frac{\text{Vol}_{i}}{100}\right) \times \text{TOD}(t)\right)$
- $\text{HalfSlippage}_{i, t} = 2.0 \times \left(1 + \frac{\text{Vol}_{i}}{100}\right) \times \text{TOD}(t)$
- $\text{Commission}_{i, t} = \frac{\text{Shares} \times \$0.005}{\text{Trade Dollars}} \times 10,000\text{ bps}$
- $\text{MarketImpact}_{i, t} = 5.0 \times \sqrt{\frac{\text{Trade Dollars}}{\text{Minute Volume}_{i, t}}}$

---

## 2. Dynamic Net Edge Decision Rule
A candidate qualifies for entry if and only if:

$$\text{Predicted Net Edge}_{i, t} = \widehat{\text{GrossReturn}}_{i, t} - \text{Expected Total Friction}_{i, t} \ge \text{Hurdle} \quad (\ge 25.0\text{ bps})$$

This formulation naturally penalizes wider-spread mid-caps unless their forecasted momentum expansion is exceptionally strong.
