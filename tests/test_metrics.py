"""Tests for performance evaluation and metrics calculations."""

from datetime import datetime, timedelta, timezone
import numpy as np
import pandas as pd
import pytest

from src.backtest.engine import BacktestResult, CompletedTrade
from src.evaluation.metrics import MetricsCalculator


def test_metrics_calculator_with_trades() -> None:
    start_t = datetime(2026, 1, 7, 14, 0, tzinfo=timezone.utc)
    eq_curve = pd.DataFrame({
        "timestamp": [start_t + timedelta(minutes=i) for i in range(100)],
        "portfolio_value": np.linspace(1000.0, 1050.0, 100),
        "drawdown_pct": np.zeros(100),
        "returns": np.full(100, 0.0005),
    })
    
    trades = [
        CompletedTrade(
            trade_id="T_01",
            symbol="AAPL",
            entry_timestamp=datetime(2026, 1, 7, 14, 0, tzinfo=timezone.utc),
            exit_timestamp=datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc),
            entry_price=100.0,
            exit_price=102.0,
            shares=10,
            gross_pnl=20.0,
            net_pnl=19.5,
            return_pct=0.0195,
            spread_paid=0.30,
            slippage_paid=0.20,
            commission_paid=0.0,
            holding_bars=12,
            exit_reason="TAKE_PROFIT",
            strategy="momentum",
        ),
        CompletedTrade(
            trade_id="T_02",
            symbol="AAPL",
            entry_timestamp=datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc),
            exit_timestamp=datetime(2026, 1, 7, 15, 30, tzinfo=timezone.utc),
            entry_price=100.0,
            exit_price=99.5,
            shares=10,
            gross_pnl=-5.0,
            net_pnl=-5.5,
            return_pct=-0.0055,
            spread_paid=0.30,
            slippage_paid=0.20,
            commission_paid=0.0,
            holding_bars=6,
            exit_reason="STOP_LOSS",
            strategy="momentum",
        ),
    ]

    result = BacktestResult(
        strategy_name="test_momentum",
        initial_capital=1000.0,
        final_capital=1050.0,
        equity_curve=eq_curve,
        trades=trades,
        portfolio_states=[],
        total_signals=100,
        executed_trades=2,
        rejected_signals=0,
        total_friction_cost=1.0,
    )

    calc = MetricsCalculator()
    summary = calc.compute_summary(result)

    assert summary.total_trades == 2
    assert summary.winning_trades == 1
    assert summary.losing_trades == 1
    assert summary.win_rate_pct == 50.0
    assert summary.total_return_pct == 5.0
    assert summary.profit_factor == pytest.approx(19.5 / 5.5, rel=1e-2)
