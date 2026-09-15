"""Tests for permutation null hypothesis tests, bootstrap intervals, and deflated Sharpe ratio."""

import numpy as np
import pandas as pd
import pytest

from src.models.trees import RandomForestModel
from src.evaluation.significance import SignificanceTester
from src.backtest.engine import CompletedTrade
from datetime import datetime, timezone


def test_permutation_null_test() -> None:
    np.random.seed(42)
    X = pd.DataFrame({
        "feature_rsi_14": np.random.uniform(20, 80, size=100),
        "feature_return_1b": np.random.normal(0, 0.01, size=100),
    })
    y = np.random.binomial(1, 0.5, size=100)

    model = RandomForestModel(model_id="test_rf", n_estimators=20, max_depth=3)
    model.fit(X.iloc[:60], y[:60])

    null_results = SignificanceTester.run_permutation_null_test(
        model=model,
        X_test=X.iloc[60:],
        y_test=y[60:],
        num_permutations=30,
        seed=42,
    )

    assert "roc_auc" in null_results
    assert "pr_auc" in null_results
    assert "brier_score" in null_results
    assert 0.0 <= null_results["roc_auc"].empirical_p_value <= 1.0


def test_bootstrap_confidence_intervals() -> None:
    returns = np.random.normal(0.0002, 0.005, size=200)
    boot_ci = SignificanceTester.compute_bootstrap_ci(returns, num_bootstraps=100, block_size=10, seed=42)
    assert "sharpe_ratio" in boot_ci
    assert boot_ci["sharpe_ratio"].ci_lower_2_5 <= boot_ci["sharpe_ratio"].ci_upper_97_5


def test_trade_level_uncertainty() -> None:
    trades = [
        CompletedTrade(
            trade_id=f"T_{i}",
            symbol="AAPL",
            entry_timestamp=datetime(2026, 1, 7, 14, 0, tzinfo=timezone.utc),
            exit_timestamp=datetime(2026, 1, 7, 15, 0, tzinfo=timezone.utc),
            entry_price=100.0,
            exit_price=101.0 if i % 2 == 0 else 99.5,
            shares=10,
            gross_pnl=10.0 if i % 2 == 0 else -5.0,
            net_pnl=9.5 if i % 2 == 0 else -5.5,
            return_pct=0.0095 if i % 2 == 0 else -0.0055,
            spread_paid=0.3,
            slippage_paid=0.2,
            commission_paid=0.0,
            holding_bars=12,
            exit_reason="TP",
            strategy="xgb",
        )
        for i in range(20)
    ]
    uncertainty = SignificanceTester.compute_trade_level_uncertainty(trades)
    assert uncertainty["total_trades"] == 20
    assert uncertainty["std_error"] > 0


def test_deflated_sharpe_ratio() -> None:
    returns = np.random.normal(0.0001, 0.002, size=300)
    obs_sharpe = float(np.mean(returns) / np.std(returns))
    dsr = SignificanceTester.calculate_deflated_sharpe_ratio(
        observed_sharpe=obs_sharpe,
        returns=returns,
        num_trials=100,
        variance_of_trials=0.50,
    )
    assert 0.0 <= dsr.deflated_sharpe_p_value <= 1.0
    assert dsr.num_trials_tested == 100
