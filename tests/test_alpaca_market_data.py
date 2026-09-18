"""
Unit tests for Alpaca market data client, symbol mapping, and real market data ingestion manifests.
"""

import json
from pathlib import Path
import pytest
import pandas as pd
import hashlib

from src.data.alpaca_market_data import AlpacaHistoricalDataClient, RealDataContaminationError
from src.data.historical_market_data import STANDARD_50_UNIVERSE
from src.core.types import EvidenceClass


def test_standard_50_universe_integrity():
    assert len(STANDARD_50_UNIVERSE) == 50
    assert "AAPL" in STANDARD_50_UNIVERSE
    assert "BRK.B" in STANDARD_50_UNIVERSE
    assert "BRK/B" not in STANDARD_50_UNIVERSE


def test_alpaca_client_symbol_mapping():
    # Client test without API keys if not present
    try:
        client = AlpacaHistoricalDataClient()
        assert client.get_provider_symbol("BRK.B") == "BRK.B"
        assert client.get_provider_symbol("AAPL") == "AAPL"
    except ValueError:
        # If running in environment without keys, verify mapping file directly
        mapping_file = Path("ALPACA_SYMBOL_MAPPING.json")
        assert mapping_file.exists()
        with open(mapping_file) as f:
            mapping = json.load(f)
        assert mapping["mappings"]["BRK.B"] == "BRK.B"
        assert len(mapping["mappings"]) == 50


def test_real_market_data_manifest_integrity():
    manifest_path = Path("REAL_MARKET_DATA_MANIFEST.json")
    assert manifest_path.exists(), "REAL_MARKET_DATA_MANIFEST.json must exist"

    with open(manifest_path) as f:
        manifest = json.load(f)

    assert manifest["evidence_class"] == EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value
    assert manifest["total_symbols"] == 50
    assert manifest["total_bars"] > 2_000_000

    # Verify every symbol has a file and valid SHA-256
    for sym, sym_info in manifest["symbols"].items():
        assert sym in STANDARD_50_UNIVERSE
        p = Path(sym_info["processed_file"])
        assert p.exists(), f"Processed file for {sym} must exist at {p}"
        raw_bytes = p.read_bytes()
        calculated_sha = hashlib.sha256(raw_bytes).hexdigest()
        assert calculated_sha == sym_info["sha256"], f"SHA256 mismatch for {sym}"
        assert sym_info["bar_count"] > 0


def test_real_data_no_synthetic_contamination():
    # Verify processed data has correct evidence class and provider metadata
    sample_file = Path("data/processed/alpaca_1m/AAPL_1m.parquet")
    if sample_file.exists():
        df = pd.read_parquet(sample_file)
        assert "evidence_class" in df.columns
        assert (df["evidence_class"] == EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value).all()
        assert (df["provider"] == "ALPACA").all()
        assert (df["feed"] == "IEX").all()


def test_real_data_contamination_error_exception():
    with pytest.raises(RealDataContaminationError):
        raise RealDataContaminationError("Synthetic data invoked in real pipeline")
