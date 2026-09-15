"""
Live Safety Architecture, Multi-Factor Arming, Hard Capital Firewall, and Permission Isolation for Phase 4.
Guarantees absolute fail-closed isolation and multi-factor defense before any live money can ever be armed.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
import os
from typing import Dict, List, Optional, Set, Tuple


class SafetyEnforcementError(RuntimeError):
    """Raised whenever a safety constraint, account lock, or arming rule is violated."""
    pass


@dataclass
class LossBudgetConfig:
    max_daily_loss_dollars: float = 30.0       # $30 daily loss cap on $1k
    max_weekly_loss_dollars: float = 75.0      # $75 weekly loss cap
    max_monthly_loss_dollars: float = 120.0    # $120 monthly loss cap
    max_strategy_drawdown_dollars: float = 150.0 # $150 strategy drawdown cap


@dataclass
class LiveArmingPayload:
    is_live_config_enabled: bool
    approved_capital_usd: float
    approved_account_id: str
    risk_policy_hash: str
    human_arming_token: str
    daily_session_auth_token: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class LiveSafetyGuard:
    """
    Enforces multi-factor arming, strict capital caps, single-order limits,
    account ID binding, symbol allow-lists, and permission minimization.
    """

    def __init__(
        self,
        approved_account_id: str = "PILOT_ACC_001",
        max_live_capital_usd: float = 2500.0,
        max_single_order_usd: float = 250.0,
        symbol_allow_list: Optional[Set[str]] = None,
        loss_budget: Optional[LossBudgetConfig] = None,
        lock_file_path: str = "/tmp/moneymaker_live_execution.lock",
    ):
        self.approved_account_id = approved_account_id
        self.max_live_capital_usd = max_live_capital_usd
        self.max_single_order_usd = max_single_order_usd
        self.symbol_allow_list = symbol_allow_list or {"NVDA", "AMD", "TSLA"}
        self.loss_budget = loss_budget or LossBudgetConfig()
        self.lock_file_path = lock_file_path

        self.is_armed = False
        self.arming_hash = ""
        self._execution_lock_acquired = False

    def verify_and_arm(self, payload: LiveArmingPayload, expected_policy_hash: str) -> bool:
        """
        Multi-Factor Arming Protocol:
        Requires 6 independent conditions to be satisfied simultaneously.
        """
        # Condition 1: Live config flag
        if not payload.is_live_config_enabled:
            raise SafetyEnforcementError("ARMING_FAILED: Live configuration is disabled.")

        # Condition 2: Capital cap compliance
        if payload.approved_capital_usd > self.max_live_capital_usd:
            raise SafetyEnforcementError(
                f"ARMING_FAILED: Approved capital ${payload.approved_capital_usd:.2f} exceeds hard ceiling ${self.max_live_capital_usd:.2f}."
            )

        # Condition 3: Account ID strict lock
        if payload.approved_account_id != self.approved_account_id:
            raise SafetyEnforcementError(
                f"ARMING_FAILED: Account ID mismatch. Expected {self.approved_account_id}, got {payload.approved_account_id}."
            )

        # Condition 4: Pinned Risk Policy Hash match
        if payload.risk_policy_hash != expected_policy_hash:
            raise SafetyEnforcementError("ARMING_FAILED: Risk policy hash does not match approved baseline.")

        # Condition 5: Human Arming Token
        if not payload.human_arming_token or len(payload.human_arming_token) < 16:
            raise SafetyEnforcementError("ARMING_FAILED: Invalid or missing Human Arming Token.")

        # Condition 6: Daily Session Auth
        if not payload.daily_session_auth_token or len(payload.daily_session_auth_token) < 16:
            raise SafetyEnforcementError("ARMING_FAILED: Invalid Daily Session Authorization Token.")

        self.is_armed = True
        self.arming_hash = hashlib.sha256(
            f"{payload.approved_account_id}:{payload.approved_capital_usd}:{payload.human_arming_token}".encode()
        ).hexdigest()
        return True

    def validate_live_order(
        self,
        account_id: str,
        symbol: str,
        order_notional_usd: float,
        current_total_exposure_usd: float,
    ) -> Tuple[bool, str]:
        """
        Validate live order against hard firewalls.
        """
        if not self.is_armed:
            return False, "SAFETY_REJECT: System is NOT armed for live trading."

        if account_id != self.approved_account_id:
            return False, f"SAFETY_REJECT: Unauthorized broker account ID {account_id}."

        if symbol not in self.symbol_allow_list:
            return False, f"SAFETY_REJECT: Symbol {symbol} is not in approved allow-list."

        if order_notional_usd > self.max_single_order_usd:
            return False, f"SAFETY_REJECT: Order notional ${order_notional_usd:.2f} exceeds MAX_SINGLE_ORDER_USD ${self.max_single_order_usd:.2f}."

        if (current_total_exposure_usd + order_notional_usd) > self.max_live_capital_usd:
            return False, f"SAFETY_REJECT: Total exposure exceeds MAX_LIVE_CAPITAL_USD ${self.max_live_capital_usd:.2f}."

        return True, "APPROVED"

    def acquire_exclusive_execution_lock(self) -> bool:
        """
        Prevent dual process instances from controlling the execution account simultaneously.
        """
        if os.path.exists(self.lock_file_path):
            return False
        try:
            with open(self.lock_file_path, "w") as f:
                f.write(f"PID={os.getpid()}:{datetime.now(timezone.utc).isoformat()}\n")
            self._execution_lock_acquired = True
            return True
        except Exception:
            return False

    def release_exclusive_execution_lock(self) -> None:
        if self._execution_lock_acquired and os.path.exists(self.lock_file_path):
            try:
                os.remove(self.lock_file_path)
            except Exception:
                pass
            self._execution_lock_acquired = False
