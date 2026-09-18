"""
Security Eligibility Policy for Moneymaker Platform (Phase B).
Defines deterministic point-in-time security classification and eligibility filters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class SecurityType(str, Enum):
    COMMON_STOCK = "cs"
    ETF = "etf"
    ADR = "adr"
    PREFERRED_STOCK = "ps"
    WARRANT = "warrant"
    RIGHT = "right"
    CLOSED_END_FUND = "cef"
    MUTUAL_FUND = "mf"
    UNKNOWN = "unknown"


class Exchange(str, Enum):
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    ARCA = "ARCA"
    AMEX = "AMEX"
    BATS = "BATS"
    OTC = "OTC"
    UNKNOWN = "UNKNOWN"


class EligibilityReasonCode(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    UNSUPPORTED_SECURITY_TYPE = "UNSUPPORTED_SECURITY_TYPE"
    UNSUPPORTED_EXCHANGE = "UNSUPPORTED_EXCHANGE"
    LEVERAGED_INVERSE_PRODUCT = "LEVERAGED_INVERSE_PRODUCT"
    PENNY_STOCK_EXCLUSION = "PENNY_STOCK_EXCLUSION"
    BANKRUPTCY_DELISTING = "BANKRUPTCY_DELISTING"
    SPECIAL_PURPOSE_ACQUISITION = "SPECIAL_PURPOSE_ACQUISITION"
    NOT_ACTIVE_STATUS = "NOT_ACTIVE_STATUS"
    NOT_TRADABLE = "NOT_TRADABLE"


@dataclass
class SecurityMetadata:
    """Canonical point-in-time metadata for a U.S. security."""
    symbol: str
    security_type: SecurityType
    exchange: Exchange
    is_tradable: bool
    is_active: bool
    is_fractionable: bool = False
    is_shortable: bool = False
    is_leveraged_or_inverse: bool = False
    is_spac: bool = False
    name: str = ""
    listing_date: Optional[str] = None
    delisting_date: Optional[str] = None


@dataclass
class EligibilityDecision:
    """Deterministic eligibility classification result."""
    symbol: str
    is_eligible: bool
    reason_code: EligibilityReasonCode
    explanation: str
    metadata: Optional[SecurityMetadata] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "is_eligible": self.is_eligible,
            "reason_code": self.reason_code.value,
            "explanation": self.explanation,
        }


class SecurityEligibilityPolicy:
    """
    Deterministic security eligibility policy engine.
    Enforces exchange, asset class, and vehicle structure constraints.
    """

    ALLOWED_EXCHANGES: Set[Exchange] = {
        Exchange.NASDAQ,
        Exchange.NYSE,
        Exchange.ARCA,
        Exchange.AMEX,
        Exchange.BATS,
    }

    ALLOWED_SECURITY_TYPES: Set[SecurityType] = {
        SecurityType.COMMON_STOCK,
        SecurityType.ETF,
        SecurityType.ADR,
    }

    KNOWN_LEVERAGED_PATTERNS = {
        "2X", "3X", "ULTRA", "BEAR", "BULL", "SHORT", "INVERSE", "DAILY", "LEVERAGED"
    }

    def __init__(
        self,
        allow_etfs: bool = True,
        allow_adrs: bool = True,
        strict_major_exchanges_only: bool = True,
    ) -> None:
        self.allow_etfs = allow_etfs
        self.allow_adrs = allow_adrs
        self.strict_major_exchanges_only = strict_major_exchanges_only

    def evaluate_security(self, metadata: SecurityMetadata) -> EligibilityDecision:
        """Evaluates a single security for point-in-time eligibility."""
        sym = metadata.symbol.upper()

        if not metadata.is_active:
            return EligibilityDecision(
                symbol=sym,
                is_eligible=False,
                reason_code=EligibilityReasonCode.NOT_ACTIVE_STATUS,
                explanation=f"Asset {sym} is not active in exchange directory.",
                metadata=metadata,
            )

        if not metadata.is_tradable:
            return EligibilityDecision(
                symbol=sym,
                is_eligible=False,
                reason_code=EligibilityReasonCode.NOT_TRADABLE,
                explanation=f"Asset {sym} is marked untradable by broker.",
                metadata=metadata,
            )

        if self.strict_major_exchanges_only and metadata.exchange not in self.ALLOWED_EXCHANGES:
            return EligibilityDecision(
                symbol=sym,
                is_eligible=False,
                reason_code=EligibilityReasonCode.UNSUPPORTED_EXCHANGE,
                explanation=f"Exchange {metadata.exchange.value} is outside allowed major exchanges.",
                metadata=metadata,
            )

        if metadata.security_type not in self.ALLOWED_SECURITY_TYPES:
            return EligibilityDecision(
                symbol=sym,
                is_eligible=False,
                reason_code=EligibilityReasonCode.UNSUPPORTED_SECURITY_TYPE,
                explanation=f"Security type {metadata.security_type.value} is not authorized.",
                metadata=metadata,
            )

        if metadata.security_type == SecurityType.ETF and not self.allow_etfs:
            return EligibilityDecision(
                symbol=sym,
                is_eligible=False,
                reason_code=EligibilityReasonCode.UNSUPPORTED_SECURITY_TYPE,
                explanation="ETFs are disabled by policy configuration.",
                metadata=metadata,
            )

        if metadata.is_leveraged_or_inverse or any(p in metadata.name.upper().split() for p in self.KNOWN_LEVERAGED_PATTERNS):
            return EligibilityDecision(
                symbol=sym,
                is_eligible=False,
                reason_code=EligibilityReasonCode.LEVERAGED_INVERSE_PRODUCT,
                explanation=f"Asset {sym} is a leveraged or inverse derivative vehicle.",
                metadata=metadata,
            )

        if metadata.is_spac or "ACQUISITION CORP" in metadata.name.upper() or "SPAC" in metadata.name.upper():
            return EligibilityDecision(
                symbol=sym,
                is_eligible=False,
                reason_code=EligibilityReasonCode.SPECIAL_PURPOSE_ACQUISITION,
                explanation=f"Asset {sym} is a SPAC structure.",
                metadata=metadata,
            )

        return EligibilityDecision(
            symbol=sym,
            is_eligible=True,
            reason_code=EligibilityReasonCode.ELIGIBLE,
            explanation=f"Asset {sym} satisfies all base security eligibility criteria.",
            metadata=metadata,
        )
