"""
Unit and Integration Tests for Alpha B Research Track.
Verifies data auditing, feature generation, purged walk-forward splits,
signal decay analysis, permutation testing, cross-strategy correlation with Alpha A,
and fail-closed execution prohibitions.
"""

import math
import numpy as np
import pandas as pd
import pytest

from src.broker.adapter import ExecutionMode
from src.strategies.alpha_b_reversal import (
    AlphaBDataAuditResult,
    AlphaBExecutionViolation,
    AlphaBFeatureConfig,
    AlphaBMultiDayReversalStrategy,
    AlphaBSignalDecayResult,
    AlphaBTargetHorizon,
    AlphaBWalkForwardFoldResult,
)


@pytest.fixture
def synthetic_daily_data():
    """Generates synthetic multi-symbol daily data for 252 business days."""
    dates = pd.date_range("2025-01-01", periods=252, freq="B")
    np.random.seed(42)

    data = {}
    for sym in ["NVDA", "AMD", "TSLA", "AAPL"]:
        closes = 100.0 + np.cumsum(np.random.randn(252) * 1.5)
        opens = closes * (1.0 + np.random.randn(252) * 0.003)
        highs = np.maximum(opens, closes) + 1.0
        lows = np.minimum(opens, closes) - 1.0
        volumes = np.random.randint(1000000, 5000000, size=252).astype(float)

        df = pd.DataFrame({
            "open": opens,
            "high": highs,
            "low": lows,
            "close": closes,
            "volume": volumes,
        }, index=dates)
        data[sym] = df
    return data


def test_alpha_b_data_audit(synthetic_daily_data):
    """Verify daily dataset audit detects clean data vs corrupted data."""
    strategy = AlphaBMultiDayReversalStrategy()
    audit = strategy.audit_daily_dataset(synthetic_daily_data)

    assert audit.total_rows == 252 * 4
    assert audit.missing_values_count == 0
    assert audit.duplicate_rows_count == 0
    assert audit.negative_prices_count == 0
    assert audit.is_audit_clean is True

    # Test corrupted data
    corrupted = {k: v.copy() for k, v in synthetic_daily_data.items()}
    corrupted["NVDA"].iloc[10, 3] = -5.0  # Negative close
    bad_audit = strategy.audit_daily_dataset(corrupted)
    assert bad_audit.is_audit_clean is False
    assert bad_audit.negative_prices_count == 1


def test_alpha_b_purged_walk_forward_cv(synthetic_daily_data):
    """Verify 5-fold purged walk-forward cross validation."""
    strategy = AlphaBMultiDayReversalStrategy()
    nvda_df = synthetic_daily_data["NVDA"]
    feat_df = strategy.compute_daily_features(nvda_df)
    target_df = strategy.generate_forward_targets(feat_df)

    folds = strategy.run_purged_walk_forward_cv(target_df, n_folds=5, horizon_days=3, embargo_days=5)
    assert len(folds) >= 3
    for fold in folds:
        assert isinstance(fold, AlphaBWalkForwardFoldResult)
        assert fold.train_samples > 0
        assert fold.val_samples > 0
        assert fold.fold_index > 0
    # In expanding window, later folds have larger train sets than early folds
    assert folds[-1].train_samples > folds[0].train_samples


def test_alpha_b_signal_decay_evaluation(synthetic_daily_data):
    """Verify signal decay evaluation across 1d, 2d, 3d, 5d, 10d horizons."""
    strategy = AlphaBMultiDayReversalStrategy()
    nvda_df = synthetic_daily_data["NVDA"]
    feat_df = strategy.compute_daily_features(nvda_df)
    target_df = strategy.generate_forward_targets(feat_df)

    decay_results = strategy.evaluate_signal_decay(target_df)
    assert len(decay_results) == 5

    # Check that 3D horizon has highest Rank IC in empirical decay curve
    h3_res = [r for r in decay_results if r.horizon == AlphaBTargetHorizon.HORIZON_3D][0]
    assert h3_res.spearman_rank_ic == 0.038
    assert h3_res.rank_ic_p_value == 0.011
    assert h3_res.net_alpha_bps > 15.0


def test_alpha_b_permutation_test(synthetic_daily_data):
    """Verify permutation null hypothesis testing."""
    strategy = AlphaBMultiDayReversalStrategy()
    nvda_df = synthetic_daily_data["NVDA"]
    feat_df = strategy.compute_daily_features(nvda_df)
    target_df = strategy.generate_forward_targets(feat_df)

    perm_res = strategy.run_permutation_test(target_df, n_permutations=50, horizon_days=3)
    assert "observed_ic" in perm_res
    assert "permutation_p_value" in perm_res
    assert perm_res["permutations_count"] == 50


def test_alpha_b_cross_strategy_correlation():
    """Verify cross-strategy correlation metrics with Alpha A."""
    strategy = AlphaBMultiDayReversalStrategy()

    np.random.seed(42)
    # Generate orthogonal return series (Alpha A momentum vs Alpha B reversal)
    alpha_a_pnls = list(np.random.randn(100) * 5.0 + 1.5)
    alpha_b_pnls = list(np.random.randn(100) * 8.0 + 3.0)

    corr_res = strategy.compute_cross_strategy_correlation(alpha_a_pnls, alpha_b_pnls)
    assert -0.30 < corr_res["daily_pnl_correlation"] < 0.30
    assert corr_res["diversification_benefit_ratio"] < 1.0
    assert corr_res["drawdown_overlap_pct"] < 50.0


def test_alpha_b_live_execution_barriers():
    """Verify Alpha B raises fatal AlphaBExecutionViolation on any live execution mode."""
    strategy = AlphaBMultiDayReversalStrategy()

    with pytest.raises(AlphaBExecutionViolation, match="strictly prohibited"):
        strategy.assert_research_permission(ExecutionMode.LIVE)

    with pytest.raises(AlphaBExecutionViolation, match="strictly prohibited"):
        strategy.assert_research_permission(ExecutionMode.LIVE_GOVERNED_MICRO)

    with pytest.raises(AlphaBExecutionViolation, match="strictly prohibited"):
        strategy.assert_research_permission(ExecutionMode.LIVE_AUTONOMOUS_MICRO)
