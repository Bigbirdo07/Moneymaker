"""Tests for feature contracts and runtime leakage prevention assertions."""

import pytest
import pandas as pd
from src.features.contracts import FeatureContractValidator, FORBIDDEN_PREFIXES, CANONICAL_FEATURES


def test_valid_feature_matrix_passes() -> None:
    cols = ["timestamp", "symbol", "feature_rsi_14", "feature_return_1b", "feature_volume_zscore_20b"]
    valid = FeatureContractValidator.validate_features(cols)
    assert valid == ["feature_rsi_14", "feature_return_1b", "feature_volume_zscore_20b"]


def test_forbidden_target_columns_raise_error() -> None:
    for prefix in FORBIDDEN_PREFIXES:
        cols = ["feature_rsi_14", f"{prefix}leakage_metric"]
        with pytest.raises(ValueError, match="DATA LEAKAGE ATTEMPT DETECTED"):
            FeatureContractValidator.validate_features(cols)


def test_custom_allowlist() -> None:
    cols = ["feature_rsi_14", "feature_return_1b", "feature_macd_line"]
    allowlist = ["feature_rsi_14"]
    valid = FeatureContractValidator.validate_features(cols, allowlist=allowlist)
    assert valid == ["feature_rsi_14"]
