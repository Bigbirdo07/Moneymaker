"""
Unit tests for Historical Dress Rehearsal Pipeline (Phase F Operational Validation).
"""

from pathlib import Path
import pytest
from scripts.run_historical_dress_rehearsal import run_historical_dress_rehearsal


def test_run_historical_dress_rehearsal_end_to_end(tmp_path):
    output_dir = tmp_path / "rehearsal_output"
    provenance = run_historical_dress_rehearsal(
        target_date_requested="2026-09-17",
        output_dir=output_dir,
    )
    
    # Verify governance verdicts
    assert provenance["verdict"] == "HISTORICAL_DRESS_REHEARSAL_COMPLETED"
    assert provenance["evidence_classification"] == "HISTORICAL_OPERATIONAL_REHEARSAL"
    assert provenance["counts_toward_20_session_forward_block"] is False
    assert provenance["real_money_authorized"] is False
    assert provenance["is_flat_at_close"] is True
    assert provenance["reconciliation_status"] == "CLEAN"
    
    # Verify universe metrics (dynamic > 50)
    u_metrics = provenance["universe_metrics"]
    assert u_metrics["raw_listed_count"] > 50
    assert u_metrics["liquid_eligible_count"] > 50
    assert u_metrics["top_100_count"] == 100
    assert u_metrics["top_250_count"] == 250
    
    # Verify all artifacts generated
    assert (output_dir / "REHEARSAL_MORNING_BRIEF.md").exists()
    assert (output_dir / "REHEARSAL_SESSION_REPORT.md").exists()
    assert (output_dir / "REHEARSAL_PROVENANCE.json").exists()
    assert (output_dir / "rehearsal_decisions.parquet").exists()
    assert (output_dir / "rehearsal_order_intents.parquet").exists()
    assert (output_dir / "rehearsal_orders.parquet").exists()
    assert (output_dir / "rehearsal_fills.parquet").exists()
    assert (output_dir / "rehearsal_positions.parquet").exists()
    assert (output_dir / "rehearsal_runtime_events.parquet").exists()
    assert (output_dir / "rehearsal_operational_incidents.parquet").exists()
    assert (output_dir / "rehearsal_reconciliation.parquet").exists()
