# Alpha B Forward Shadow Execution Specification

## 1. Specification Overview & Lifecycle Stage
- **Strategy ID**: `ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL`
- **Candidate Configuration**: [`configs/frozen_alpha_b_candidate_v1.yaml`](file:///Users/albertopaz/Moneymaker/configs/frozen_alpha_b_candidate_v1.yaml)
- **Lifecycle Status**: **`ALPHA_B_FORWARD_SHADOW_CANDIDATE`**
- **Execution Mode**: `ExecutionMode.SHADOW` (Zero broker interaction, zero capital at risk)

---

## 2. Daily Information Cutoff & Signal Timing Architecture
To strictly prevent same-close lookahead bias:
1. **16:00:00 EST**: Daily market cash close.
2. **16:05:00 EST**: Ingest finalized official daily close prices and volumes across universe `["NVDA", "AMD", "TSLA", "AAPL", "MSFT", "META", "GOOGL", "AMZN"]`.
3. **16:10:00 EST**: Compute 3-day relative reversal feature scores:
   $$\text{Score}_i = -1.0 \times \left(\frac{P_{i, t}}{P_{i, t-3}} - 1.0\right) - \text{RelStrength}_{i, 3d}$$
4. **16:15:00 EST**: Rank cross-sectional scores. Select Top-2 Long and Bottom-2 Short candidates.
5. **09:30:00 EST (Next Trading Day $T+1$)**: Log hypothetical simulated fills at official market open / 5-minute VWAP window.
6. **Holding Period**: Positions held for exactly 3 completed trading days ($T+1, T+2, T+3$), exiting at close/VWAP on day $T+3$.

---

## 3. Forward Shadow Target Metrics & Validation Gate
- **Required Minimum Shadow Period**: **40 to 60 trading days**.
- **Minimum Cross-Sectional Decisions**: $\ge 80$ rebalancing cohorts.
- **Promotion Thresholds to Future Broker Paper**:
  1. Forward Out-of-Sample Rank IC $\ge +0.025$ ($p < 0.05$)
  2. Net Realized Alpha after 5 bps friction $\ge +10.0$ bps / 3D cycle
  3. Realized Drawdown $\le 6.0\%$
  4. Realized Daily Correlation with concurrent Alpha A $\le +0.10$.
