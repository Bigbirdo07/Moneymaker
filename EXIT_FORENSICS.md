# Exit Decision Model Forensics Report

## 1. Executive Summary

This report performs a comprehensive post-mortem on all 21,823 open position exit evaluations and 658 closed trades executed by `ExitDecisionModel`.

The analysis examines reason categories, holding durations, Maximum Favorable Excursions (MFE), Maximum Adverse Excursions (MAE), and post-exit price action.

---

## 2. Exit Reason Category Breakdown

Across the 658 closed trades, exits were triggered by the following mechanisms:

| Exit Reason Category | Count | Percentage | Win Rate (%) | Avg Realized Return (bps) | Primary Forensic Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`SIGNAL_DECAY`** | 568 | 86.32% | 31.5% | -8.45 bps | **Premature exit on 5m noise before alpha matured** |
| **`STOP_LOSS`** | 38 | 5.77% | 0.0% | -152.40 bps | Hard risk cutoff functioning as designed |
| **`SESSION_CLOSE`** | 22 | 3.34% | 45.5% | -2.10 bps | Forced end-of-day market-on-close liquidation |
| **`BETTER_OPPORTUNITY`** | 16 | 2.43% | 37.5% | -6.80 bps | Position switching due to 12 bps margin |
| **`TAKE_PROFIT`** | 8 | 1.22% | 100.0% | +254.10 bps | Successful full profit realization |
| **`DRAWDOWN_FROM_PEAK`** | 4 | 0.61% | 100.0% | +48.20 bps | Trailing stop lock-in |
| **`TIME_STOP`** | 2 | 0.30% | 50.0% | +3.40 bps | 120-minute holding duration expiration |

```
Exit Reason Distribution:
SIGNAL_DECAY         ████████████████████████████████████ (568 trades, 86.3%)
STOP_LOSS            ██ (38 trades, 5.8%)
SESSION_CLOSE        █ (22 trades, 3.3%)
BETTER_OPPORTUNITY   █ (16 trades, 2.4%)
TAKE_PROFIT          ░ (8 trades, 1.2%)
DRAWDOWN_FROM_PEAK   ░ (4 trades, 0.6%)
TIME_STOP            ░ (2 trades, 0.3%)
```

---

## 3. The Signal Decay Pathology

The overwhelming majority (86.3%) of exits were triggered by `SIGNAL_DECAY`.

### Forensic Trace of a Typical Premature Exit:
1. **T=0**: Position entered on high 15m composite forecast (+16.5 bps edge).
2. **T+4m**: Asset experiences a minor normal tick pullback of -4 bps.
3. **T+5m**: 5-minute forecast tick recalculates and drops to -2.5 bps.
4. **T+6m**: `ExitDecisionModel` triggers immediate `SELL` on `SIGNAL_DECAY`.
5. **T+15m to T+30m**: Asset rallies strongly, hitting original target (+22.0 bps), but position was already closed at a loss after paying bid-ask spread twice.

### MFE / MAE Evidence:
- For trades closed on `SIGNAL_DECAY`:
  - **Median MFE**: +14.2 bps
  - **Median MAE**: -16.8 bps
  - **Post-Exit 15m Drift**: In 68.4% of `SIGNAL_DECAY` exits, the stock was higher 15 minutes after exit than at the exit fill price.

---

## 4. Remediation in `ExitDecisionModelV1_1`

To eliminate premature decay whipsaws while maintaining risk controls:
1. **Horizon Protection**: Prohibit `SIGNAL_DECAY` exits during the first **15 bars (15 minutes)** of holding (`min_holding_bars_for_signal_decay = 15`).
2. **Higher Switching Hurdle**: Increase `opportunity_switch_margin_bps` from $12.0\text{ bps} \to 25.0\text{ bps}$ to eliminate frivolous position flips.
3. **Preserve Catastrophic Stops**: Retain hard stop-loss at -1.5% and take-profit at +2.5% with unconditional immediate execution.
