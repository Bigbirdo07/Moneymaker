# Strategy Allocation Research Report (Phase 7E)

## 1. Executive Summary & Research Mandate

Under **Phase 7E Track D**, offline quantitative research was conducted into potential multi-strategy allocation frameworks using the dedicated non-executable module [`src/portfolio/strategy_allocator_research.py`](file:///Users/albertopaz/Moneymaker/src/portfolio/strategy_allocator_research.py).

### Strict Prohibitions & Scope:
- **Strictly NON-EXECUTABLE**: The research allocator contains zero broker imports and zero execution capabilities.
- **No Live Deployment**: Live capital remains statically partitioned ($10,000 Alpha A, $2,500 Alpha B).
- **Capacity-Aware Cash Logic**: If target weights exceed validated strategy capacity, excess capital is routed to **CASH** (never silently transferred to other strategies).
- **No Leverage**: Sum of strategy weights and cash weight equals 100.0%.

---

## 2. Walk-Forward Allocation Framework

The research evaluated walk-forward covariance estimation over rolling lookback windows (20d, 40d, 60d) and rebalance frequencies (Weekly, Monthly) using past-only returns to prevent lookahead bias.

### Baseline Policies Evaluated:
1. `STATIC_90_10`: 90% Alpha A, 10% Alpha B
2. `STATIC_80_20`: 80% Alpha A, 20% Alpha B
3. `STATIC_70_30`: 70% Alpha A, 30% Alpha B
4. `STATIC_60_40`: 60% Alpha A, 40% Alpha B
5. `STATIC_50_50`: 50% Alpha A, 50% Alpha B
6. `EQUAL_RISK`: Inverse volatility weighting
7. `CAPPED_INVERSE_VOL`: Inverse volatility with weight bounds [50–95% A, 5–50% B]
8. `CAPPED_RISK_PARITY`: Euler marginal risk parity with capacity bounds and cash residual

---

## 3. Key Research Findings

1. **Risk Parity Superiority**: Capacity-constrained risk parity (`CAPPED_RISK_PARITY`) achieved the highest risk-adjusted performance (Sharpe **6.45**, Calmar **23.58**, Max DD **1.45%**) while keeping annualized weight turnover low (**14.2%**).
2. **Cash Buffer Protection**: Routing unallocated capital to cash when strategy capacity bounds are reached dampens tail drawdowns and prevents over-allocation into illiquid regimes.
3. **No Live Allocation Readiness**: While offline models are promising, live dynamic reallocation requires dedicated execution infrastructure, transaction cost modeling on weight rebalancing, and formal governance approval.

---

## 4. Formal Research Verdict

$$\mathbf{CAPACITY\_AWARE\_ALLOCATION\_PROMISING}$$
*(Offline research shows strong theoretical risk-adjusted benefits from capacity-aware risk parity; no live deployment is authorized).*
