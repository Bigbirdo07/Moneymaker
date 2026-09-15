"""Adversarial validation tests for purged walk-forward splitting and leakage prevention."""

from datetime import timedelta
import numpy as np
import pandas as pd
import pytest

from src.data.loader import HistoricalDataLoader
from src.features.engine import FeatureEngine
from src.validation.purged_split import PurgedTimeSeriesSplitter
from src.validation.walk_forward import WalkForwardEngine, WalkForwardFold


@pytest.fixture
def sample_dataset() -> pd.DataFrame:
    df = HistoricalDataLoader.generate_synthetic_5m_data(symbol="AAPL", num_days=10, seed=42)
    engine = FeatureEngine(include_targets=True)
    return engine.compute_all_features(df)


def test_A_overlapping_labels_are_removed(sample_dataset: pd.DataFrame) -> None:
    """Test A: Samples whose forward label horizon overlaps the next fold are purged."""
    engine = WalkForwardEngine(n_splits=2, label_duration=timedelta(minutes=60), embargo_duration=timedelta(minutes=60))
    folds = engine.generate_folds(sample_dataset)
    assert len(folds) > 0

    timestamps = pd.to_datetime(sample_dataset["timestamp"], utc=True)
    for fold in folds:
        train_ts = timestamps.iloc[fold.train_indices]
        val_start = fold.val_start
        # Max label end of all training samples must not exceed val_start
        max_label_end = train_ts.max() + timedelta(minutes=60)
        assert max_label_end <= val_start, f"Overlapping label in Fold {fold.fold_id}: {max_label_end} > {val_start}"


def test_B_embargoed_observations_are_removed(sample_dataset: pd.DataFrame) -> None:
    """Test B: Test observations within embargo duration after validation end are removed."""
    engine = WalkForwardEngine(n_splits=2, label_duration=timedelta(minutes=60), embargo_duration=timedelta(minutes=60))
    folds = engine.generate_folds(sample_dataset)

    timestamps = pd.to_datetime(sample_dataset["timestamp"], utc=True)
    for fold in folds:
        val_end = fold.val_end
        test_ts = timestamps.iloc[fold.test_indices]
        min_test_ts = test_ts.min()
        assert min_test_ts >= val_end + timedelta(minutes=60), (
            f"Embargo violation in Fold {fold.fold_id}: {min_test_ts} < {val_end + timedelta(minutes=60)}"
        )


def test_C_and_D_chronological_ordering_guarantee(sample_dataset: pd.DataFrame) -> None:
    """Tests C & D: Train < Val < Test strict chronological ordering."""
    engine = WalkForwardEngine(n_splits=3)
    folds = engine.generate_folds(sample_dataset)

    for fold in folds:
        assert fold.train_end < fold.val_start
        assert fold.val_end < fold.test_start


def test_E_zero_target_window_overlap(sample_dataset: pd.DataFrame) -> None:
    """Test E: Zero target-window overlap exists across split boundaries."""
    label_dur = timedelta(minutes=60)
    engine = WalkForwardEngine(n_splits=2, label_duration=label_dur)
    folds = engine.generate_folds(sample_dataset)

    timestamps = pd.to_datetime(sample_dataset["timestamp"], utc=True)
    for fold in folds:
        last_train_t = timestamps.iloc[fold.train_indices[-1]]
        first_val_t = timestamps.iloc[fold.val_indices[0]]
        assert (last_train_t + label_dur) <= first_val_t


def test_F_changing_test_labels_does_not_affect_training(sample_dataset: pd.DataFrame) -> None:
    """Test F: Mutating test targets/labels does not alter training set indices or fold splits."""
    engine = WalkForwardEngine(n_splits=2)
    folds_orig = engine.generate_folds(sample_dataset)

    mutated_df = sample_dataset.copy()
    target_cols = [c for c in mutated_df.columns if c.startswith("target_")]
    for col in target_cols:
        mutated_df[col] = mutated_df[col] * 100.0

    folds_mutated = engine.generate_folds(mutated_df)
    assert len(folds_orig) == len(folds_mutated)
    for f1, f2 in zip(folds_orig, folds_mutated):
        np.testing.assert_array_equal(f1.train_indices, f2.train_indices)
        np.testing.assert_array_equal(f1.val_indices, f2.val_indices)
        np.testing.assert_array_equal(f1.test_indices, f2.test_indices)


def test_G_changing_future_features_does_not_alter_historical_folds(sample_dataset: pd.DataFrame) -> None:
    """Test G: Modifying future feature rows does not affect earlier fold definitions."""
    engine = WalkForwardEngine(n_splits=2)
    folds_orig = engine.generate_folds(sample_dataset)

    mutated_df = sample_dataset.copy()
    split_point = len(mutated_df) // 2
    mutated_df.loc[split_point:, "close"] *= 2.0

    engine_mutated = FeatureEngine(include_targets=True)
    recalc_df = engine_mutated.compute_all_features(mutated_df)
    folds_recalc = engine.generate_folds(recalc_df)

    # First fold training indices must remain identical
    np.testing.assert_array_equal(folds_orig[0].train_indices, folds_recalc[0].train_indices)


def test_H_all_folds_are_deterministic(sample_dataset: pd.DataFrame) -> None:
    """Test H: Generating folds multiple times returns identical indices."""
    engine = WalkForwardEngine(n_splits=3)
    folds_1 = engine.generate_folds(sample_dataset)
    folds_2 = engine.generate_folds(sample_dataset)

    for f1, f2 in zip(folds_1, folds_2):
        np.testing.assert_array_equal(f1.train_indices, f2.train_indices)
        np.testing.assert_array_equal(f1.val_indices, f2.val_indices)
        np.testing.assert_array_equal(f1.test_indices, f2.test_indices)
