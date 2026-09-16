"""
Moneymaker Workstation Package.
Local-first quantitative trading workstation, real-time analytics,
and tool-based conversational AI Copilot.
"""

from src.workstation.models import (
    AccountSummary,
    EvidenceSource,
    MarketQuote,
    PositionItem,
    PortfolioExposure,
    PortfolioRiskTelemetry,
    StrategyCard,
    TradeRecord,
)
from src.workstation.service import WorkstationService
from src.workstation.copilot_tools import CopilotToolRegistry, CopilotExecutionFirewallViolation
from src.workstation.copilot_engine import MoneymakerCopilotEngine
from src.workstation.provenance import DataProvenanceEngine

__all__ = [
    "AccountSummary",
    "EvidenceSource",
    "MarketQuote",
    "PositionItem",
    "PortfolioExposure",
    "PortfolioRiskTelemetry",
    "StrategyCard",
    "TradeRecord",
    "WorkstationService",
    "CopilotToolRegistry",
    "CopilotExecutionFirewallViolation",
    "MoneymakerCopilotEngine",
    "DataProvenanceEngine",
]
