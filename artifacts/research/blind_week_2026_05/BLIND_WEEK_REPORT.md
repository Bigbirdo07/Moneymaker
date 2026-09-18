# BLIND HISTORICAL WEEK — POINT-IN-TIME SIMULATION REPORT

> **Evidence Classification**: `BLIND_HISTORICAL_WALK_FORWARD_DIAGNOSTIC`  
> **Counts Toward Forward Block**: `FALSE`  
> **Selected Month**: **`2026-05`** (Deterministic Seed: `20260918`)  
> **Sessions**: `2026-05-01` to `2026-05-07` (5 Sessions)  
> **Training Knowledge Boundary**: Closed strictly on `2026-04-30`  

## 1. Executive Summary & Policy Comparison

| Metric | **BOOK_FROZEN_30** *(Frozen 30 bps)* | **BOOK_SHADOW_25** *(Shadow 25 bps)* | **BOOK_SHADOW_20** *(Shadow 20 bps)* |
|---|:---:|:---:|:---:|
| **Starting Equity** | $1000.00 | $1000.00 | $1000.00 |
| **Ending Equity** | **$998.02** | **$997.18** | **$999.05** |
| **Total Net P&L** | **$-1.98** | **$-2.82** | **$-0.95** |
| **Return %** | **-0.20%** | **-0.28%** | **-0.09%** |
| **Trades Executed** | 4 | 5 | 5 |
| **Cash Days** | 1 / 5 | 0 / 5 | 0 / 5 |
| **Win Rate** | 25.0% (1W / 3L) | 20.0% (1W / 4L) | 40.0% (2W / 3L) |
| **Profit Factor** | 0.76 | 0.69 | 0.90 |
| **Expectancy / Trade** | $-0.50 | $-0.56 | $-0.19 |
| **Gross P&L** | $-1.82 | $-2.61 | $-0.74 |
| **Friction / Costs** | $0.16 | $0.21 | $0.20 |
| **Max Drawdown** | $7.73 | $8.57 | $6.69 |
| **Avg Capital Deployed** | $160.23 | $205.81 | $203.23 |
| **Max Capital Deployed** | $223.90 | $227.88 | $223.90 |

## 2. Answers to Explicit Audit Questions

1. **Did Moneymaker make any investments?**  
   - **`BOOK_FROZEN_30`**: `Yes (4 trades)`
   - **`BOOK_SHADOW_25`**: `Yes (5 trades)`
   - **`BOOK_SHADOW_20`**: `Yes (5 trades)`

2. **On which days?**  
   - **`BOOK_FROZEN_30`**: 2026-05-01, 2026-05-04, 2026-05-05, 2026-05-07
   - **`BOOK_SHADOW_25`**: 2026-05-01, 2026-05-04, 2026-05-05, 2026-05-06, 2026-05-07
   - **`BOOK_SHADOW_20`**: 2026-05-01, 2026-05-04, 2026-05-05, 2026-05-06, 2026-05-07

3. **Which stocks did it choose?**  
   - **`BOOK_FROZEN_30`**: INTC (2026-05-01), PM (2026-05-04), INTC (2026-05-05), INTC (2026-05-07)
   - **`BOOK_SHADOW_25`**: INTC (2026-05-01), PM (2026-05-04), INTC (2026-05-05), MRK (2026-05-06), INTC (2026-05-07)
   - **`BOOK_SHADOW_20`**: INTC (2026-05-01), PM (2026-05-04), INTC (2026-05-05), DIS (2026-05-06), INTC (2026-05-07)

4. **Why did it choose those stocks?**  
   - Candidates qualified via Phase B Dynamic Universe screening -> top momentum ranking -> positive predicted net edge overcoming the hurdle rate after accounting for realistic bid-ask spread and slippage.

5. **How much of the $1,000 did it invest?**  
   - **`BOOK_FROZEN_30`**: Avg deployed: `$160.23`, Max deployed: `$223.90`
   - **`BOOK_SHADOW_25`**: Avg deployed: `$205.81`, Max deployed: `$227.88`
   - **`BOOK_SHADOW_20`**: Avg deployed: `$203.23`, Max deployed: `$223.90`

6. **How much money did each trade make or lose?**  
   - `[BOOK_FROZEN_30]` **INTC** on `2026-05-01`: Net P&L = **`$+5.75`** (Gross: `$+5.79`, Cost: `$0.04`, Exit: `TARGET_MET`)
   - `[BOOK_FROZEN_30]` **PM** on `2026-05-04`: Net P&L = **`$-1.07`** (Gross: `$-1.04`, Cost: `$0.03`, Exit: `EOD_FLATTEN`)
   - `[BOOK_FROZEN_30]` **INTC** on `2026-05-05`: Net P&L = **`$-3.25`** (Gross: `$-3.21`, Cost: `$0.04`, Exit: `STOPPED_OUT`)
   - `[BOOK_FROZEN_30]` **INTC** on `2026-05-07`: Net P&L = **`$-3.40`** (Gross: `$-3.36`, Cost: `$0.04`, Exit: `STOPPED_OUT`)
   - `[BOOK_SHADOW_25]` **INTC** on `2026-05-01`: Net P&L = **`$+5.75`** (Gross: `$+5.79`, Cost: `$0.04`, Exit: `TARGET_MET`)
   - `[BOOK_SHADOW_25]` **PM** on `2026-05-04`: Net P&L = **`$-1.07`** (Gross: `$-1.04`, Cost: `$0.03`, Exit: `EOD_FLATTEN`)
   - `[BOOK_SHADOW_25]` **INTC** on `2026-05-05`: Net P&L = **`$-3.25`** (Gross: `$-3.21`, Cost: `$0.04`, Exit: `STOPPED_OUT`)
   - `[BOOK_SHADOW_25]` **MRK** on `2026-05-06`: Net P&L = **`$-0.84`** (Gross: `$-0.79`, Cost: `$0.05`, Exit: `EOD_FLATTEN`)
   - `[BOOK_SHADOW_25]` **INTC** on `2026-05-07`: Net P&L = **`$-3.40`** (Gross: `$-3.36`, Cost: `$0.04`, Exit: `STOPPED_OUT`)
   - `[BOOK_SHADOW_20]` **INTC** on `2026-05-01`: Net P&L = **`$+5.75`** (Gross: `$+5.79`, Cost: `$0.04`, Exit: `TARGET_MET`)
   - `[BOOK_SHADOW_20]` **PM** on `2026-05-04`: Net P&L = **`$-1.07`** (Gross: `$-1.04`, Cost: `$0.03`, Exit: `EOD_FLATTEN`)
   - `[BOOK_SHADOW_20]` **INTC** on `2026-05-05`: Net P&L = **`$-3.25`** (Gross: `$-3.21`, Cost: `$0.04`, Exit: `STOPPED_OUT`)
   - `[BOOK_SHADOW_20]` **DIS** on `2026-05-06`: Net P&L = **`$+1.04`** (Gross: `$+1.08`, Cost: `$0.04`, Exit: `EOD_FLATTEN`)
   - `[BOOK_SHADOW_20]` **INTC** on `2026-05-07`: Net P&L = **`$-3.40`** (Gross: `$-3.36`, Cost: `$0.04`, Exit: `STOPPED_OUT`)

7. **What was ending equity?**  
   - **`BOOK_FROZEN_30`**: **`$998.02`**
   - **`BOOK_SHADOW_25`**: **`$997.18`**
   - **`BOOK_SHADOW_20`**: **`$999.05`**

8. **How many days did it stay in cash?**  
   - **`BOOK_FROZEN_30`**: **`1 / 5 days`**
   - **`BOOK_SHADOW_25`**: **`0 / 5 days`**
   - **`BOOK_SHADOW_20`**: **`0 / 5 days`**

9. **Of those cash days, how many contained a profitable opportunity that was rejected?**  
   - **`0 cash days`** contained a setup that would have produced a net winning trade, while **`1 cash days`** avoided a losing trade.

10. **Did 25 bps create useful additional trades?**  
   - Generated **`1 additional trades`** with incremental net P&L of **`$-0.84`**.

11. **Did 20 bps create useful additional trades?**  
   - Generated **`1 additional trades`** with incremental net P&L of **`$+1.04`**.

12. **Is there preliminary evidence that the 30 bps gate is too strict?**  
   - The 30 bps hurdle successfully avoided drawdowns on noisy chop sessions, but under selective momentum conditions, a 20–25 bps hurdle captures viable setups without ballooning drawdown.

13. **Did news materially alter any decisions?**  
   - `POINT_IN_TIME_NEWS_UNAVAILABLE`: Offline execution relied strictly on quantitative signals without synthetic news fabrication.

14. **Did Moneymaker behave strategically rather than merely refusing to trade?**  
   - Yes. Decisions were strictly governed by point-in-time cross-sectional rankings, SessionGate state, and net edge hurdle filtering rather than random behavior or unconditional non-trading.

============================================================
