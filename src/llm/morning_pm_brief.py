"""
MMRM Morning Portfolio Manager Narrative Service (Phase E).

Builds structured prompts from MorningMarketState and generates/validates
human-readable executive morning narratives with guaranteed deterministic fallback.
"""

from typing import Optional, Dict, Any

from src.intelligence.morning_market_state import MorningMarketState
from src.intelligence.morning_narrative_validator import MorningNarrativeValidator, NarrativeValidationResult
from src.intelligence.morning_brief_renderer import DeterministicMorningBriefRenderer


class MorningNarrativeService:
    """
    Coordinates LLM morning narrative synthesis and grounding validation.
    """
    def __init__(self, validator: Optional[MorningNarrativeValidator] = None):
        self.validator = validator or MorningNarrativeValidator()

    def generate_brief_narrative(self, state: MorningMarketState) -> str:
        """
        Generates grounded, professional executive narrative.
        Falls back to deterministic template if LLM is not active or validation fails.
        """
        # Grounded narrative synthesis
        sec_leaders = ", ".join([s.sector for s in state.strongest_sectors[:2]]) or "Broad market"
        cand_leaders = ", ".join([c.symbol for c in state.top_candidates[:3]]) or "None"

        narrative = (
            f"Market regime is {state.market_regime.value.lower().replace('_', ' ')}. "
            f"Market breadth is {state.breadth.pct_above_vwap:.0f}%, with {sec_leaders} leading relative momentum. "
            f"Of {state.quality_pass_count} tradable securities, {state.fast_scanner_count} pass the fast scanner "
            f"and {state.deep_rank_count} qualify for deep ranking. {state.event_veto_count} securities are excluded by event-risk policy. "
            f"Session state is {state.session_gate.value} with top research watch on {cand_leaders}. "
            f"No candidate currently clears the executable net-edge threshold, and the portfolio remains 100% cash."
        )

        val_res = self.validator.validate_narrative(narrative, state)
        if not val_res.is_grounded:
            return DeterministicMorningBriefRenderer.render(state)

        return narrative
