"""
Real Data Firewall & August Holdout Access Controller for Phase 10.4 & 10.5.
Enforces programmatic security rules preventing unauthorized access to the sealed August 2026 final holdout.
Permits read-only evaluation in Phase 10.5 ONLY AFTER cryptographic freeze verification passes.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd


class AugustHoldoutFirewallError(PermissionError):
    """Raised immediately if any component attempts unauthorized access to August 2026 data."""
    pass


class FinalHoldoutFreezeMismatchError(RuntimeError):
    """Raised if frozen candidate components do not match REAL_ENGINE_V2_FREEZE_MANIFEST.json."""
    pass


class TrainingForbiddenOnHoldoutError(RuntimeError):
    """Raised if any training, fitting, tuning, or optimization is attempted on August data."""
    pass


class RealDataFirewall:
    """
    Firewall controller that strictly asserts no access to the August 2026 holdout
    during research, feature engineering, model training, threshold tuning, or development validation.
    Unlocks read-only access for Phase 10.5 single-pass evaluation only after freeze verification.
    """

    SEALED_HOLDOUT_START = "2026-08-01"
    SEALED_HOLDOUT_END = "2026-08-31"
    MAX_AUTHORIZED_DATE = "2026-08-31"

    _phase10_5_readonly_unlocked: bool = False
    _reads_logged_count: int = 0
    _freeze_verification_record: Optional[Dict[str, Any]] = None

    @classmethod
    def unlock_phase10_5_final_holdout_for_readonly_eval(
        cls,
        freeze_manifest_path: str = "REAL_ENGINE_V2_FREEZE_MANIFEST.json",
    ) -> Dict[str, Any]:
        """
        Cryptographically verifies all frozen components against REAL_ENGINE_V2_FREEZE_MANIFEST.json.
        Unlocks August 2026 strictly for read-only single-pass evaluation if and only if 100% hash parity is confirmed.
        """
        p_manifest = Path(freeze_manifest_path)
        if not p_manifest.exists():
            raise FinalHoldoutFreezeMismatchError(f"FINAL_HOLDOUT_FREEZE_MISMATCH: Manifest {freeze_manifest_path} not found!")

        with open(p_manifest, "r") as f:
            manifest = json.load(f)

        source_hashes = manifest.get("source_hashes", {})
        current_hashes = {}
        mismatches = []

        for fpath, expected_hash in source_hashes.items():
            p_file = Path(fpath)
            if not p_file.exists():
                mismatches.append(f"Missing file: {fpath}")
                continue
            cur_hash = hashlib.sha256(p_file.read_bytes()).hexdigest()
            current_hashes[fpath] = cur_hash
            if cur_hash != expected_hash:
                mismatches.append(f"Hash mismatch on {fpath}: expected {expected_hash}, got {cur_hash}")

        if mismatches:
            cls._phase10_5_readonly_unlocked = False
            raise FinalHoldoutFreezeMismatchError(
                f"FINAL_HOLDOUT_FREEZE_MISMATCH: Frozen engine components do not match manifest!\n" + "\n".join(mismatches)
            )

        verification_record = {
            "status": "FREEZE_VERIFIED_100_PERCENT_PARITY",
            "verification_timestamp": datetime.utcnow().isoformat() + "Z",
            "manifest_file": freeze_manifest_path,
            "verified_hashes": current_hashes,
            "engine_state": manifest.get("engine_state", "REAL_MARKET_ENGINE_V2_CANDIDATE_FROZEN"),
            "parameters": manifest.get("parameters", {}),
        }
        cls._freeze_verification_record = verification_record
        cls._phase10_5_readonly_unlocked = True
        return verification_record

    @classmethod
    def assert_no_training_on_holdout(cls, dataset_df: pd.DataFrame, task_name: str = "Model Training") -> None:
        """
        Asserts that no August 2026 data is passed into any model training, calibration, or tuning API.
        """
        if dataset_df.empty:
            return
        if "date_str" in dataset_df.columns:
            aug_rows = dataset_df[dataset_df["date_str"].str.startswith("2026-08")]
            if len(aug_rows) > 0:
                raise TrainingForbiddenOnHoldoutError(
                    f"TRAINING_FORBIDDEN_ON_AUGUST_HOLDOUT: {task_name} attempted on {len(aug_rows)} August rows! "
                    "August is strictly read-only evaluation data."
                )

    @classmethod
    def assert_date_authorized(cls, date_val: str | date | datetime) -> None:
        """
        Asserts that a date is authorized for access under current firewall governance.
        """
        if isinstance(date_val, (datetime, date)):
            d_str = date_val.strftime("%Y-%m-%d")
        else:
            d_str = str(date_val)[:10]

        # Always block future / post-August dates
        if d_str > cls.MAX_AUTHORIZED_DATE:
            raise AugustHoldoutFirewallError(
                f"ACCESS DENIED: Date '{d_str}' exceeds maximum authorized date '{cls.MAX_AUTHORIZED_DATE}'."
            )

        # August dates check
        if cls.SEALED_HOLDOUT_START <= d_str <= cls.SEALED_HOLDOUT_END:
            if not cls._phase10_5_readonly_unlocked:
                raise AugustHoldoutFirewallError(
                    f"ACCESS DENIED: Date '{d_str}' falls within the sealed August 2026 final holdout period "
                    f"({cls.SEALED_HOLDOUT_START} to {cls.SEALED_HOLDOUT_END}). "
                    "Phase 10.4 development cannot access the final holdout."
                )
            cls._reads_logged_count += 1

    @classmethod
    def filter_authorized_dataframe(cls, df: pd.DataFrame, date_column: str = "date_str") -> pd.DataFrame:
        """
        Filters a DataFrame according to current firewall governance.
        """
        if df.empty or date_column not in df.columns:
            return df

        if cls._phase10_5_readonly_unlocked:
            # When unlocked for Phase 10.5, allow up to 2026-08-31, but strictly block future
            mask = df[date_column] <= cls.MAX_AUTHORIZED_DATE
        else:
            # Phase 10.4 default: strictly block August and future
            mask = (df[date_column] < cls.SEALED_HOLDOUT_START) | (df[date_column] > cls.SEALED_HOLDOUT_END)
            mask = mask & (df[date_column] <= cls.MAX_AUTHORIZED_DATE)

        filtered = df[mask].copy()
        return filtered
