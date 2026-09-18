"""
Unit tests for Missed-Opportunity & Counterfactual Rejection Audit.
"""

from pathlib import Path
import pytest
from scripts.run_missed_opportunity_audit import run_full_missed_opportunity_audit


def test_run_missed_opportunity_audit_end_to_end(tmp_path):
    res = run_full_missed_opportunity_audit(
        rehearsal_date="2026-09-01",
        output_dir=tmp_path,
    )
    
    assert res["total_rejected"] > 0
    assert res["profitable_pct"] >= 0.0
    assert "net_value_of_rejections" in res
    assert "cf_profit_factor" in res
    
    # Check all markdown artifacts
    assert (tmp_path / "MISSED_OPPORTUNITY_AUDIT.md").exists()
    assert (tmp_path / "REJECTION_REASON_ANALYSIS.md").exists()
    assert (tmp_path / "EDGE_CALIBRATION_ANALYSIS.md").exists()
    assert (tmp_path / "CAUTION_THRESHOLD_DIAGNOSTIC.md").exists()
    assert (tmp_path / "COUNTERFACTUAL_TRADE_ANALYSIS.md").exists()
    
    # Check all parquet ledgers
    assert (tmp_path / "rejected_candidate_outcomes.parquet").exists()
    assert (tmp_path / "counterfactual_trades.parquet").exists()
    assert (tmp_path / "rejection_reason_results.parquet").exists()
    assert (tmp_path / "edge_bucket_results.parquet").exists()
    assert (tmp_path / "threshold_diagnostic_results.parquet").exists()
