# Position Size Sensitivity & Monotonicity Verification

## 1. Monotonicity Guarantees
- **Volatility Monotonicity**: $\partial \text{Size} / \partial \text{Volatility} \le 0$ (Higher vol strictly never increases dollar allocation).
- **Stop Distance Monotonicity**: $\partial \text{Size} / \partial \text{Stop} \le 0$.
- **Equity Monotonicity**: $\partial \text{Size} / \partial \text{Equity} \ge 0$.
- **Event Veto**: Event multiplier $0.0 \implies \text{Final Size} = 0.0$ strictly.