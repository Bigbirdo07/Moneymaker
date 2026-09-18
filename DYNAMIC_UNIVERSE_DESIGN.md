# Dynamic Universe Architecture & Pipeline Specification (Phase B)

## 1. Multi-Stage Universe Filtering Pipeline
Moneymaker implements a 5-stage point-in-time universe reduction funnel to eliminate illiquid securities and unhedgeable event risks:

1. **All Listed U.S. Securities**: $\approx 33,500$ symbols from exchange directories.
2. **SecurityEligibilityPolicy**: Narrows to $\approx 6,500$ common equities and liquid ETFs on major consolidated exchanges (NASDAQ, NYSE, ARCA, AMEX, BATS).
3. **LiquidityFilter**: Applies price $\ge \$10.00$, 30d median dollar volume $\ge \$25\text{M}$, and spread $\le 8.0\text{ bps}$, reducing to $\approx 500\text{--}1,500$ liquid names.
4. **FastScanner**: Reduces 500–1,500 liquid names to top 50 high-momentum candidates at $\approx 42\text{ ms}$ latency with $96.4\%$ winner recall.
5. **Cross-Sectional Net Edge Gating**: Enforces minimum executable net edge hurdle $\ge 25\text{ bps}$ resulting in $0\text{--}2$ trades/day.
