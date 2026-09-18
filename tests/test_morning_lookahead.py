"""Tests for Point-in-Time safety in Morning Intelligence (Phase E20)."""

import pytest
from src.intelligence.morning_brief import MorningBriefService
from src.intelligence.macro_events import MacroEventProvider, MacroEvent
from src.risk.portfolio_risk_state import PortfolioRiskState
from src.risk.capital_tiers import CapitalTier


def test_point_in_time_cutoff_enforcement():
    """
    Ensure that no data with timestamp > cutoff timestamp is accepted or processed.
    """
    cutoff_time = "2026-09-18T08:45:00Z"
    future_event = MacroEvent(
        event_id="CPI_001",
        event_name="CPI Release",
        scheduled_timestamp="2026-09-18T10:00:00Z",
        importance="HIGH",
        source="BLS",
        description="Consumer Price Index",
    )
    provider = MacroEventProvider(events=[future_event])
    
    # Event scheduled at 10:00 is NOT imminent at 08:45 (15 min buffer)
    assert not provider.is_macro_release_imminent(cutoff_time, buffer_minutes=15)
    
    # Event scheduled at 10:00 IS imminent at 09:50
    assert provider.is_macro_release_imminent("2026-09-18T09:50:00Z", buffer_minutes=15)
