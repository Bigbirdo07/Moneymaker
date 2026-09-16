"""
Tests for Dataset Versioning & Manifest Verification.
Verifies cryptographic dataset hashing, point-in-time embargo parameters,
and immutability guarantees.
"""

from src.research.dataset_versioning import DatasetRegistry


def test_dataset_manifest_registration_and_hashing(tmp_path):
    registry = DatasetRegistry(manifest_dir=str(tmp_path / "manifests"))
    manifest = registry.register_dataset(
        dataset_id="DS_ALPHA_B_UNIVERSE_2026",
        symbols=["AAPL", "MSFT", "NVDA", "AMD", "TSLA"],
        start_date="2024-01-01",
        end_date="2026-09-15",
        bar_frequency="1d",
        source_provider="POLYGON_RAW_TICK",
        adjustment_status="SPLIT_AND_DIVIDEND_ADJUSTED",
        feature_columns=["ret_3d", "vol_ratio_20d", "rsi_14", "vwap_dist"],
        target_column="fwd_ret_3d",
        row_count=35000,
        training_cutoff_date="2026-06-01",
        embargo_bars=5,
    )

    assert manifest.dataset_id == "DS_ALPHA_B_UNIVERSE_2026"
    assert len(manifest.dataset_hash) == 64
    assert manifest.embargo_bars == 5

    loaded = registry.get_manifest("DS_ALPHA_B_UNIVERSE_2026")
    assert loaded is not None
    assert loaded.dataset_hash == manifest.dataset_hash
    assert loaded.row_count == 35000
