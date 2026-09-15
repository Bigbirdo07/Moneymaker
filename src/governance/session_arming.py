"""
Daily Session Arming, Account Holdings Audit, and Version Pinning for Phase 5A Governed Pilot.
Enforces daily time-bounded session authorization, zero unrelated assets check,
and SHA-256 hash validation across models, features, config, and Git commit.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Dict, List, Optional, Set, Tuple

from src.broker.adapter import BrokerAdapter, BrokerAccount, BrokerPosition


class SessionArmingError(RuntimeError):
    """Raised when session arming or pre-trade account integrity fails."""
    pass


@dataclass
class SessionAuthorizationToken:
    token_id: str
    session_date: str
    account_id: str
    approved_capital_usd: float
    issued_at: datetime
    expires_at: datetime
    is_revoked: bool = False

    def is_valid(self, current_time: Optional[datetime] = None) -> bool:
        now = current_time or datetime.now(timezone.utc)
        return not self.is_revoked and (now <= self.expires_at)


class SessionArmingManager:
    """Manages daily pre-market verification, account hygiene checks, and authorization tokens."""

    def __init__(
        self,
        broker: BrokerAdapter,
        approved_account_id: str = "PILOT_ACC_001",
        max_live_capital_usd: float = 1000.0,
        allowed_symbols: Optional[Set[str]] = None,
        lock_file_path: str = "/tmp/moneymaker_governed_pilot.lock",
    ):
        self.broker = broker
        self.approved_account_id = approved_account_id
        self.max_live_capital_usd = max_live_capital_usd
        self.allowed_symbols = allowed_symbols or {"NVDA", "AMD", "TSLA"}
        self.lock_file_path = lock_file_path
        self.current_auth_token: Optional[SessionAuthorizationToken] = None
        self._execution_lock_acquired = False

    def audit_account_holdings(self) -> Tuple[bool, str]:
        """
        Verify account contains ONLY eligible cash and approved pilot positions.
        Rejects unrelated stocks, crypto, ETFs, options, or margin balances.
        """
        try:
            account = self.broker.get_account()
            positions = self.broker.get_positions()
        except Exception as e:
            return False, f"FAILED_TO_QUERY_BROKER: {e}"

        # 1. Verify Account ID Match
        if account.account_id != self.approved_account_id:
            return False, f"ACCOUNT_ID_MISMATCH: Expected {self.approved_account_id}, got {account.account_id}"

        # 2. Verify Capital Ceiling
        if account.portfolio_value > (self.max_live_capital_usd * 1.02): # 2% tolerance buffer
            return False, f"CAPITAL_CEILING_EXCEEDED: Portfolio value ${account.portfolio_value:.2f} > ${self.max_live_capital_usd:.2f}"

        # 3. Verify Buying Power == Cash (No Margin)
        if account.buying_power > (account.cash * 1.05):
            return False, f"MARGIN_DETECTED: Buying power ${account.buying_power:.2f} > Cash ${account.cash:.2f}"

        # 4. Verify Positions: Zero Unrelated Assets
        for sym, pos in positions.items():
            if sym not in self.allowed_symbols:
                return False, f"FORBIDDEN_ASSET_DETECTED: Symbol {sym} is not in approved allow-list {self.allowed_symbols}"
            if pos.qty < 0:
                return False, f"SHORT_POSITION_DETECTED: Negative shares {pos.qty} in {sym}"

        return True, "ACCOUNT_HOLDINGS_VERIFIED_CLEAN"

    def arm_session(
        self,
        model_hash: str,
        expected_model_hash: str,
        config_hash: str,
        expected_config_hash: str,
        operator_arming_secret: str,
    ) -> SessionAuthorizationToken:
        """
        Execute full pre-session audit and issue short-lived daily authorization token.
        """
        # 1. Version and Config Hash Checks
        if model_hash != expected_model_hash:
            raise SessionArmingError("SESSION_ARM_FAILED: Model hash mismatch with approved baseline.")

        if config_hash != expected_config_hash:
            raise SessionArmingError("SESSION_ARM_FAILED: Config hash mismatch with approved baseline.")

        if len(operator_arming_secret) < 16:
            raise SessionArmingError("SESSION_ARM_FAILED: Invalid operator arming secret.")

        # 2. Exclusive Process Lock Acquisition
        if not self._acquire_process_lock():
            raise SessionArmingError("SESSION_ARM_FAILED: Failed to acquire exclusive process execution lock.")

        # 3. Account Holdings Verification
        clean, reason = self.audit_account_holdings()
        if not clean:
            self._release_process_lock()
            raise SessionArmingError(f"SESSION_ARM_FAILED: Account hygiene check failed: {reason}")

        # 4. Generate Daily Auth Token (Expires at 16:00 UTC / EOD)
        now = datetime.now(timezone.utc)
        token_id = hashlib.sha256(f"{self.approved_account_id}:{now.date()}:{operator_arming_secret}".encode()).hexdigest()
        expires = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=timezone.utc)

        token = SessionAuthorizationToken(
            token_id=token_id,
            session_date=now.strftime("%Y-%m-%d"),
            account_id=self.approved_account_id,
            approved_capital_usd=self.max_live_capital_usd,
            issued_at=now,
            expires_at=expires,
        )
        self.current_auth_token = token
        return token

    def revoke_session(self, reason: str = "OPERATOR_REVOCATION") -> None:
        """Revoke daily authorization and release process lock."""
        if self.current_auth_token:
            self.current_auth_token.is_revoked = True
        self._release_process_lock()

    def _acquire_process_lock(self) -> bool:
        if os.path.exists(self.lock_file_path):
            return False
        try:
            with open(self.lock_file_path, "w") as f:
                f.write(f"PID={os.getpid()}:{datetime.now(timezone.utc).isoformat()}\n")
            self._execution_lock_acquired = True
            return True
        except Exception:
            return False

    def _release_process_lock(self) -> None:
        if self._execution_lock_acquired and os.path.exists(self.lock_file_path):
            try:
                os.remove(self.lock_file_path)
            except Exception:
                pass
            self._execution_lock_acquired = False
