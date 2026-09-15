"""Automated research report generator and tear-sheet renderer."""

from __future__ import annotations

from typing import Any, Dict, List, Optional
import pandas as pd

from src.evaluation.metrics import PerformanceSummary


class ResearchReportGenerator:
    """Generates standardized, rigorous markdown research tear-sheets for quantitative strategies."""

    @staticmethod
    def generate_strategy_report(
        summary: PerformanceSummary,
        hypothesis: str,
        universe: str,
        start_date: str,
        end_date: str,
        benchmark_summary: Optional[PerformanceSummary] = None,
        verdict: str = "INCONCLUSIVE",
        known_limitations: Optional[List[str]] = None,
    ) -> str:
        """Renders a comprehensive markdown experiment report."""
        limits = known_limitations or [
            "Evaluated on historical 5-minute simulated bars.",
            "Zero market impact beyond linear slippage model.",
            "No overnight gap risk accounted for (pure intraday).",
        ]
        limits_md = "\n".join([f"- {lim}" for lim in limits])

        bench_str = ""
        if benchmark_summary:
            bench_str = f"""
### Benchmark Comparison ({benchmark_summary.strategy_name})
| Metric | Strategy | Benchmark |
| :--- | :--- | :--- |
| **Total Return** | {summary.total_return_pct:.2f}% | {benchmark_summary.total_return_pct:.2f}% |
| **Sharpe Ratio** | {summary.sharpe_ratio:.2f} | {benchmark_summary.sharpe_ratio:.2f} |
| **Max Drawdown** | {summary.max_drawdown_pct:.2f}% | {benchmark_summary.max_drawdown_pct:.2f}% |
| **Beta to Benchmark** | {summary.beta_to_benchmark:.2f} | 1.00 |
| **Correlation** | {summary.benchmark_correlation:.2f} | 1.00 |
"""

        report = f"""# Quantitative Research Report: {summary.strategy_name}

## 1. Executive Summary
- **Verdict**: **`{verdict}`**
- **Universe**: `{universe}`
- **Evaluation Period**: `{start_date}` to `{end_date}`
- **Initial Capital**: `${summary.initial_capital:,.2f}` | **Final Capital**: `${summary.final_capital:,.2f}`

## 2. Research Hypothesis
> {hypothesis}

## 3. Performance & Risk Tear-Sheet
| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Total Return** | {summary.total_return_pct:.2f}% | **Max Drawdown** | {summary.max_drawdown_pct:.2f}% |
| **Sharpe Ratio** | {summary.sharpe_ratio:.2f} | **Calmar Ratio** | {summary.calmar_ratio:.2f} |
| **Sortino Ratio** | {summary.sortino_ratio:.2f} | **Annualized Volatility** | {summary.annualized_volatility_pct:.2f}% |
| **CAGR** | {summary.cagr_pct:.2f}% | **Alpha (Annualized)** | {summary.alpha_annualized:.2f}% |

## 4. Trade Analysis & Expectancy
| Metric | Value | Metric | Value |
| :--- | :--- | :--- | :--- |
| **Total Trades** | {summary.total_trades} | **Win Rate** | {summary.win_rate_pct:.1f}% |
| **Winning Trades** | {summary.winning_trades} | **Loss Rate** | {summary.loss_rate_pct:.1f}% |
| **Profit Factor** | {summary.profit_factor:.2f} | **Avg Trade PnL** | ${summary.avg_trade_pnl:.2f} |
| **Avg Win** | ${summary.avg_win_dollar:.2f} | **Avg Loss** | ${summary.avg_loss_dollar:.2f} |
| **Expectancy** | ${summary.expectancy:.4f} | **Avg Holding Bars** | {summary.avg_holding_bars:.1f} (bars) |

## 5. Cost & Friction Drag Breakdown
| Friction Component | Dollar Drag |
| :--- | :--- |
| **Gross PnL (Before Friction)** | ${summary.gross_pnl:.2f} |
| **Total Spread Paid** | ${summary.total_spread:.2f} |
| **Total Slippage Paid** | ${summary.total_slippage:.2f} |
| **Total Commissions** | ${summary.total_commissions:.2f} |
| **Total Friction Drag** | **${summary.total_friction_cost:.2f}** |
| **Net PnL (After Friction)** | **${summary.net_pnl:.2f}** |

{bench_str}

## 6. Known Limitations & Research Risks
{limits_md}

---
*Report automatically compiled by Moneymaker Quantitative Engine.*
"""
        return report
