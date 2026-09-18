"""
Execution Environment & Live Real-Money Firewall (Phase F).

Strictly regulates runtime execution modes. Live real-money deployment is
permanently hard-blocked at the class definition and initialization level.
"""

from enum import Enum


class RealMoneyAuthorizationError(PermissionError):
    """
    Raised whenever any attempt is made to configure, initialize,
    or execute real-money live trading without cryptographically verified authorization.
    """
    pass


class ExecutionEnvironment(str, Enum):
    SIMULATION = "SIMULATION"   # Hermetic in-memory simulation for tests & validation
    DRY_RUN = "DRY_RUN"         # Live data ingestion + real decisions with 0 order submissions
    PAPER = "PAPER"             # Autonomous broker paper execution (Alpaca paper trading)
    LIVE = "LIVE"               # Real money execution (HARD-BLOCKED)


def validate_execution_environment(env: ExecutionEnvironment) -> None:
    """
    Guarantees that live real-money execution cannot be initialized.
    """
    if env == ExecutionEnvironment.LIVE or env == "LIVE":
        raise RealMoneyAuthorizationError(
            "FATAL SECURITY VIOLATION: ExecutionEnvironment.LIVE is strictly unauthorized. "
            "Governance status: REAL_MONEY_NOT_AUTHORIZED."
        )
