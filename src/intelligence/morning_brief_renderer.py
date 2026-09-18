"""
Deterministic Morning Brief Renderer (Phase E).

Renders canonical markdown briefings directly from structured MorningMarketState
without requiring LLM execution.
"""

from src.intelligence.morning_market_state import MorningMarketState


class DeterministicMorningBriefRenderer:
    """
    Guaranteed deterministic formatter producing canonical senior PM morning briefings.
    """
    @staticmethod
    def render(state: MorningMarketState) -> str:
        sec_strong = "\n".join([f"{i+1}. {s.sector} (+{s.premarket_return_pct:.2f}%, Rel: +{s.relative_return_vs_spy_bps:.0f} bps)" for i, s in enumerate(state.strongest_sectors)]) or "1. None"
        sec_weak = "\n".join([f"{i+1}. {s.sector} ({s.premarket_return_pct:.2f}%)" for i, s in enumerate(state.weakest_sectors)]) or "1. None"

        top_cand = "\n".join([f"{i+1}. {c.symbol} ({c.sector}, Pre: {c.premarket_return_pct:+.2f}%, RelVol: {c.relative_volume:.1f}x) [{c.event_risk_status}]" for i, c in enumerate(state.top_candidates)]) or "1. None"
        risks = "\n".join([f"- {r}" for r in state.risk_summary.primary_risks]) or "- None"

        lines = [
            "------------------------------------------------------------",
            "MONEYMAKER MORNING BRIEF",
            "",
            f"Date:\n{state.date_str}",
            "",
            f"Portfolio Equity:\n${state.portfolio_equity:,.2f}",
            "",
            f"Capital Tier:\n{state.capital_tier}",
            "",
            f"Portfolio Risk State:\n{state.portfolio_risk_state}",
            "",
            f"Market Regime:\n{state.market_regime.value}",
            "",
            f"Session Gate:\n{state.session_gate.value}",
            "",
            f"SPY Premarket:\n{state.spy_premarket_return_pct:+.2f}%",
            "",
            f"Market Breadth:\n{state.breadth.pct_above_vwap:.0f}%",
            "",
            f"Volatility State:\n{state.risk_summary.volatility_risk_level}",
            "",
            f"Cross-Sectional Dispersion:\n{state.breadth.dispersion_state.value}",
            "",
            "Strongest Sectors:",
            sec_strong,
            "",
            "Weakest Sectors:",
            sec_weak,
            "",
            f"Raw Listed Universe:\n{state.raw_universe_count}",
            "",
            f"Security-Type Eligible:\n{state.eligible_universe_count}",
            "",
            f"Liquid Eligible:\n{state.liquid_universe_count}",
            "",
            f"Data-Quality Eligible:\n{state.quality_pass_count}",
            "",
            f"Event Vetoes:\n{state.event_veto_count}",
            "",
            f"FastScanner Survivors:\n{state.fast_scanner_count}",
            "",
            f"Deep-Ranking Candidates:\n{state.deep_rank_count}",
            "",
            f"Entry-Qualified Now:\n{state.entry_qualified_count}",
            "",
            "Top Research Candidates:",
            top_cand,
            "",
            "Primary Risks Today:",
            risks,
            "",
            "Current Decision:",
            "NO TRADE" if state.entry_qualified_count == 0 else "WATCH FOR OPEN CONFIRMATION",
            "",
            "Reason:",
            "No candidate currently exceeds required executable net-edge and risk criteria." if state.entry_qualified_count == 0 else "Candidates qualify for live intraday scan.",
            "------------------------------------------------------------",
        ]
        return "\n".join(lines)
