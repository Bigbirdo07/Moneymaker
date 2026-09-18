# Replay Execution Simulator & Microstructure Friction Report

## 1. Execution Model Formulation
The `ReplayExecutionSimulator` models non-instantaneous fills on bar $T+1$ without same-bar lookahead:

$$\text{Fill Price}_{\text{BUY}} = \text{Open}_{T+1} + \frac{\text{Spread}_{T+1}}{2} + \text{Slippage}(\text{Volume}, \text{Order Size})$$
$$\text{Fill Price}_{\text{SELL}} = \text{Open}_{T+1} - \frac{\text{Spread}_{T+1}}{2} - \text{Slippage}(\text{Volume}, \text{Order Size})$$

### Microstructure Friction Parameters
- **Base Slippage**: 1.5 bps
- **Market Impact Model**: Square-root participation model: $25.0 \times \left(\frac{\text{Shares}}{\text{Bar Volume}}\right)^{0.50}\text{ bps}$
- **Per-Share Broker Commission**: $0.0005 per share
- **SEC / FINRA Transaction Fees**: $0.0000278 per dollar of gross sell principal
- **Simulated Latency**: 0.50 seconds

---

## 2. Friction Accounting Over 22 Replay Sessions

| Friction Component | Total Dollars Paid | % of Total Friction | Effective bps Paid |
| :--- | :--- | :--- | :--- |
| **Bid/Ask Spread Friction** | $26.42 | 61.4% | ~2.5 bps / trade |
| **Market Impact Slippage** | $14.86 | 34.6% | ~1.4 bps / trade |
| **Broker Commissions & Fees** | $1.72 | 4.0% | ~0.2 bps / trade |
| **Total Cumulative Friction** | **$43.00** | **100.0%** | **~4.1 bps / trade** |

---

## 3. Realism Stress Testing
- **2x Spread Stress**: Total return degrades by -4.2% ($43.00 \to $69.42 friction).
- **2x Slippage Stress**: Total return degrades by -2.1% ($43.00 \to $57.86 friction).
- **Execution Timing Verification**: 100% of fills executed on bar $T+1$ timestamp $\ge \text{Decision Time } T$.
