"""
Unit tests for the August 2026 Holdout Firewall & Phase 10.5 Access Governance.
"""

from datetime import datetime
import pytest
import pandas as pd

from src.data.real_data_firewall import (
    RealDataFirewall,
    AugustHoldoutFirewallError,
    TrainingForbiddenOnHoldoutError,
    FinalHoldoutFreezeMismatchError,
)


def test_august_firewall_blocks_august_dates_by_default():
    RealDataFirewall._phase10_5_readonly_unlocked = False
    with pytest.raises(AugustHoldoutFirewallError):
        RealDataFirewall.assert_date_authorized("2026-08-01")

    with pytest.raises(AugustHoldoutFirewallError):
        RealDataFirewall.assert_date_authorized("2026-08-15")

    with pytest.raises(AugustHoldoutFirewallError):
        RealDataFirewall.assert_date_authorized("2026-08-31")


def test_august_firewall_permits_authorized_pre_august_dates():
    RealDataFirewall._phase10_5_readonly_unlocked = False
    RealDataFirewall.assert_date_authorized("2024-01-02")
    RealDataFirewall.assert_date_authorized("2025-12-31")
    RealDataFirewall.assert_date_authorized("2026-04-15")
    RealDataFirewall.assert_date_authorized("2026-07-31")


def test_august_firewall_always_blocks_post_august_dates():
    # September 2026 and beyond must ALWAYS be blocked
    with pytest.raises(AugustHoldoutFirewallError):
        RealDataFirewall.assert_date_authorized("2026-09-01")

    with pytest.raises(AugustHoldoutFirewallError):
        RealDataFirewall.assert_date_authorized("2026-10-15")


def test_august_firewall_filters_dataframe_by_default():
    RealDataFirewall._phase10_5_readonly_unlocked = False
    df = pd.DataFrame({
        "date_str": ["2026-07-30", "2026-07-31", "2026-08-01", "2026-08-15", "2026-09-01"],
        "val": [1, 2, 3, 4, 5]
    })
    filtered = RealDataFirewall.filter_authorized_dataframe(df, date_column="date_str")
    assert len(filtered) == 2
    assert "2026-08-01" not in filtered["date_str"].values
    assert "2026-08-15" not in filtered["date_str"].values
    assert "2026-09-01" not in filtered["date_str"].values
    assert "2026-07-31" in filtered["date_str"].values


def test_assert_no_training_on_holdout():
    df_aug = pd.DataFrame({"date_str": ["2026-08-05"], "val": [10.0]})
    with pytest.raises(TrainingForbiddenOnHoldoutError):
        RealDataFirewall.assert_no_training_on_holdout(df_aug, task_name="Forecaster Training")


def test_freeze_verification_and_unlock():
    # Verifies that freeze verification unlocks August strictly
    record = RealDataFirewall.unlock_phase10_5_final_holdout_for_readonly_eval(
        freeze_manifest_path="REAL_ENGINE_V2_FREEZE_MANIFEST.json"
    )
    assert record["status"] == "FREEZE_VERIFIED_100_PERCENT_PARITY"
    assert RealDataFirewall._phase10_5_readonly_unlocked is True
    # Now August is authorized for read-only evaluation
    RealDataFirewall.assert_date_authorized("2026-08-01")
    RealDataFirewall.assert_date_authorized("2026-08-31")
    # But September is still blocked
    with pytest.raises(AugustHoldoutFirewallError):
        RealDataFirewall.assert_date_authorized("2026-09-01")
    # Reset
    RealDataFirewall._phase10_5_readonly_unlocked = False
