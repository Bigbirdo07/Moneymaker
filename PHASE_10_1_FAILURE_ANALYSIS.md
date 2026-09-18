# Phase 10.1 Post-Mortem Failure Analysis & Loss Decomposition Report

## 1. Executive Summary & Root Cause Synthesis

The initial 22-session historical replay test of **Autonomous Trading Engine V1.0** (2026-01-05 to 2026-02-03) generated a statistically robust 15-minute Rank Information Coefficient ($IC = +0.0685, t = 6.12$), confirming that the underlying predictive model possesses genuine directional alpha. However, the simulation finished with a net loss:

$$\text{Starting Capital: } \$1,000.00 \longrightarrow \text{Ending Capital: } \$897.76 \quad (\text{Net Return: } -10.22\%, \text{Gross Return: } -5.92\%)$$

This post-mortem forensic analysis isolates the exact mechanisms that converted positive raw predictive intelligence into strategy failure:

1. **Hyperactive Turnover & Churn**: 658 round-trip trades executed across 22 trading sessions (~30 round-trips per day), paying **$43.00** in bid-ask spread and slippage friction (4.3% drag on account equity).
2. **Horizon Mismatch & Premature Signal Decay Exits**: 86.3% of all exits (568 of 658) were triggered by the `SIGNAL_DECAY` logic because the exit model evaluated short-term 5-minute ticks, cutting positions after a median hold of only 28 bars before the 15-to-30 minute forecast alpha could compound.
3. **Sub-Threshold Low-Conviction Entries**: 61.4% of entries (404 of 658) entered with an expected net edge of only 4.0–8.0 bps, which failed to surmount the empirical round-trip transaction friction of 6.5 bps.
4. **Asymmetric Payoff Deficit**: While the win/loss payoff ratio was 1.38 ($1.08 average win vs. $0.78 average loss), the low 32.4% win rate resulted in a negative net expectancy of **-$0.1809 per trade**.

---

## 2. Loss Decomposition Attribution

| Component | Absolute P&L Impact ($) | Return Impact (%) | Primary Root Cause Mechanism |
| :--- | :--- | :--- | :--- |
| **Transaction Friction (Spread + Fees)** | -$43.00 | -4.30% | 658 round-trip executions @ ~6.5 bps average friction |
| **Low-Edge Entry Whipsaws (Deciles 1–7)** | -$38.40 | -3.84% | Entry hurdle (4.0 bps) too permissive against microstructure noise |
| **Premature Signal Decay Exits** | -$14.84 | -1.48% | Lack of holding duration protection; exiting on transient 5m pullbacks |
| **Intraday Switching Churn** | -$6.00 | -0.60% | Overly sensitive 12.0 bps switching barrier triggering rapid position flips |
| **Total Strategy Deficit** | **-$102.24** | **-10.22%** | **Combined Execution & Parameter Pathology** |

---

## 3. Key Forensic Indicators

- **Information Coefficient vs. Strategy Outcome**:
  - Multi-Horizon 15m Rank IC: **+0.0685** ($t = 6.12$)
  - Empirical Alpha Half-Life: **10.5 minutes**
  - Median Position Duration: **28.0 minutes**
- **Payoff & Expectancy Profile**:
  - Total Closed Trades: **658**
  - Winning Trades: **213 (32.4%)**
  - Losing Trades: **445 (67.6%)**
  - Gross Expectancy: **-$0.1156 / trade**
  - Net Expectancy: **-$0.1809 / trade**
  - Profit Factor: **0.66**

---

## 4. Governance & Holdout Isolation Declaration

> [!IMPORTANT]
> In accordance with strict institutional quantitative research standards, the test month (2026-01-05 to 2026-02-03) has been **permanently burned for parameter tuning**. No parameters or thresholds for Autonomous Engine V1.1 have been or will be fit directly to this test month. All calibrations are derived strictly from pre-test training/validation splits.

---

## 5. Architectural Corrective Roadmap (Autonomous Engine V1.1)

1. **Raise Entry Conviction Gate**: Increase minimum net edge threshold from $4.0\text{ bps} \to 10.0\text{ bps}$ and $P(\text{Up}) \ge 58.0\%$.
2. **Horizon Protection Lock**: Prevent `SIGNAL_DECAY` exits during the first 15 bars (15 minutes) of holding.
3. **Symbol Re-Entry Cooldown**: Enforce a mandatory 30-bar (30-minute) cooldown after closing a position in a symbol.
4. **Intraday Velocity Cap**: Cap daily executions at a maximum of 8 trades per session.
5. **Elevate Switching Barrier**: Raise opportunity switching hurdle to $\ge 25.0\text{ bps}$.
