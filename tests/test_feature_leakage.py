"""Critical tests verifying zero future information leakage in feature computation."""

import numpy as np
import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine


def test_feature_lookahead_invariance() -> None:
    """
    Lookahead Leakage Audit:
    Perturbing future rows t+1...N must have ZERO numerical effect on features computed at row t.
    """
    df_base = HistoricalDataLoader.generate_synthetic_5m_data(symbol="NVDA", num_days=3, seed=123)
    engine = FeatureEngine()
    
    # Run features on clean dataset
    features_base = engine.compute_all_features(df_base)
    feature_cols = FeatureEngine.get_feature_columns(features_base)
    
    assert len(feature_cols) > 10, "Feature engine should produce a rich set of features"

    # Test point: bar 50 (must be after warmup period)
    t_idx = 50
    base_t_features = features_base.loc[t_idx, feature_cols].copy()

    # Create mutated dataset: heavily distort all future rows from t+1 onwards
    df_mutated = df_base.copy()
    df_mutated.loc[t_idx + 1:, "open"] *= 1.50
    df_mutated.loc[t_idx + 1:, "high"] *= 1.60
    df_mutated.loc[t_idx + 1:, "low"] *= 1.40
    df_mutated.loc[t_idx + 1:, "close"] *= 1.55
    df_mutated.loc[t_idx + 1:, "volume"] *= 10.0

    features_mutated = engine.compute_all_features(df_mutated)
    mutated_t_features = features_mutated.loc[t_idx, feature_cols].copy()

    # Check identical values (ignoring NaNs that match)
    for col in feature_cols:
        val_base = base_t_features[col]
        val_mut = mutated_t_features[col]
        if pd.isna(val_base) and pd.isna(val_mut):
            continue
        assert val_base == pytest.approx(val_mut, rel=1e-7, abs=1e-7), (
            f"LOOKAHEAD LEAKAGE DETECTED in column '{col}' at index {t_idx}! "
            f"Original: {val_base}, Mutated Future: {val_mut}"
        )


def test_available_timestamp_greater_than_event_timestamp() -> None:
    """Verifies that available_timestamp is strictly after the bar's event_timestamp."""
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="MSFT", num_days=1, seed=42)
    engine = FeatureEngine()
    features = engine.compute_all_features(df)

    assert "event_timestamp" in features.columns
    assert "available_timestamp" in features.columns

    diffs = features["available_timestamp"] - features["event_timestamp"]
    assert (diffs == pd.Timedelta(minutes=5)).all(), "Bar available_timestamp must be exactly bar_start + 5 minutes"


def test_target_features_separation() -> None:
    """Verifies targets are prefixed with 'target_' and not present in feature list."""
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=2, seed=42)
    engine = FeatureEngine(include_targets=True)
    features = engine.compute_all_features(df)

    feature_cols = FeatureEngine.get_feature_columns(features)
    target_cols = FeatureEngine.get_target_columns(features)

    assert len(target_cols) > 0
    # No overlap
    assert set(feature_cols).isdisjoint(set(target_cols))
