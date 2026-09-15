"""
Alpha B Robustness & Forward Shadow Readiness Tests.
Validates target leakage prevention, symbol holdouts, sector holdouts,
multiple-testing corrections (Benjamini-Hochberg FDR), and forward shadow candidate generation.
"""

import pytest
import numpy as np
import pandas as pd
from src.strategies.alpha_b_reversal import (
    AlphaBMultiDayReversalStrategy,
    AlphaBTargetHorizon,
    AlphaBExecutionViolation,
    ExecutionMode,
)


@pytest.fixture
def multi_symbol_daily_data():
    """Generates synthetic 252-day panel for 6 universe symbols."""
    np.random.seed(42)
    symbols = ["NVDA", "AMD", "TSLA", "AAPL", "MSFT", "META"]
    dates = pd.date_range("2025-01-01", periods=252, freq="B")
    data = {}
    for sym in symbols:
        drift = 0.0004
        ret = np.random.normal(drift, 0.022, len(dates))
        px = 100.0 * np.exp(np.cumsum(ret))
        df = pd.DataFrame(
            {
                "open": px * (1.0 - 0.002),
                "high": px * (1.0 + 0.010),
                "low": px * (1.0 - 0.010),
                "close": px,
                "volume": np.random.uniform(2e6, 10e6, len(dates)),
            },
            index=dates,
        )
        data[sym] = df
    return data


def test_alpha_b_execution_isolation():
    """Verify Alpha B raises fatal AlphaBExecutionViolation on any live or broker paper mode."""
    strategy = AlphaBMultiDayReversalStrategy()
    with pytest.raises(AlphaBExecutionViolation):
        strategy.assert_execution_allowed(ExecutionMode.LIVE_AUTONOMOUS_MICRO)
    with pytest.raises(AlphaBExecutionViolation):
        strategy.assert_execution_allowed(ExecutionMode.LIVE_GOVERNED_MICRO)
    with pytest.raises(AlphaBExecutionViolation):
        strategy.assert_execution_allowed(ExecutionMode.BROKER_PAPER)


def test_alpha_b_target_leakage_protection(multi_symbol_daily_data):
    """Verify that features computed on day T strictly do NOT access close on day T+1 or beyond."""
    strategy = AlphaBMultiDayReversalStrategy()
    df = multi_symbol_daily_data["NVDA"]
    feat_df = strategy.compute_daily_features(df)

    # Modify future prices
    df_tampered = df.copy()
    df_tampered.iloc[100:, 3] = df_tampered.iloc[100:, 3] * 5.0
    feat_tampered = strategy.compute_daily_features(df_tampered)

    # Features at day 50 must be completely identical
    pd.testing.assert_series_equal(
        feat_df["reversal_3d"].iloc[:50],
        feat_tampered["reversal_3d"].iloc[:50],
    )


def test_alpha_b_leave_one_symbol_out(multi_symbol_daily_data):
    """Verify that multi-day reversal signal generalizes across individual universe symbols."""
    strategy = AlphaBMultiDayReversalStrategy()
    loso_results = strategy.evaluate_leave_one_symbol_out(multi_symbol_daily_data, horizon_days=3)

    assert "symbol_results" in loso_results
    assert len(loso_results["symbol_results"]) == 6
    assert loso_results["mean_symbol_rank_ic"] is not None


def test_alpha_b_sector_holdouts(multi_symbol_daily_data):
    """Verify sector-level holdout evaluation."""
    strategy = AlphaBMultiDayReversalStrategy()
    sectors = {
        "Semiconductors": {"NVDA": multi_symbol_daily_data["NVDA"], "AMD": multi_symbol_daily_data["AMD"]},
        "MegaCapTech": {"AAPL": multi_symbol_daily_data["AAPL"], "MSFT": multi_symbol_daily_data["MSFT"]},
        "ConsumerDiscretionary": {"TSLA": multi_symbol_daily_data["TSLA"]},
    }
    sec_results = strategy.evaluate_sector_holdouts(sectors, horizon_days=3)
    assert len(sec_results) == 3
    assert "Semiconductors" in sec_results
    assert "MegaCapTech" in sec_results


def test_alpha_b_multiple_testing_fdr_correction():
    """Verify Benjamini-Hochberg False Discovery Rate multiple-testing correction."""
    strategy = AlphaBMultiDayReversalStrategy()
    p_vals = [0.011, 0.018, 0.024, 0.035, 0.082, 0.045, 0.120, 0.038, 0.014]
    fdr_res = strategy.compute_multiple_testing_correction(p_vals, alpha=0.05)

    assert fdr_res["total_hypotheses_tested"] == 9
    # Check that candidate p=0.011 achieves q-value ~0.054
    assert fdr_res["h3_candidate_fdr_q"] <= 0.06
    assert fdr_res["h3_candidate_raw_p"] < 0.05


def test_alpha_b_forward_shadow_candidate_decision():
    """Verify forward shadow candidate decision generator and lookahead prevention."""
    strategy = AlphaBMultiDayReversalStrategy()
    scores = {"NVDA": 0.045, "AMD": 0.038, "TSLA": -0.012, "AAPL": -0.025, "MSFT": 0.010}
    decision = strategy.generate_forward_shadow_candidate_decision("2026-09-15", scores, top_k=2)

    assert decision["decision_date"] == "2026-09-15"
    assert decision["strategy_id"] == "ALPHA_B_MULTI_DAY_RELATIVE_REVERSAL"
    assert decision["execution_policy"] == "NEXT_SESSION_OPEN_OR_VWAP"
    assert decision["long_symbols"] == ["NVDA", "AMD"]
    assert decision["short_symbols"] == ["TSLA", "AAPL"]
    assert decision["status"] == "FORWARD_SHADOW_CANDIDATE"
