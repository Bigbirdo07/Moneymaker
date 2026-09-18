"""
Real-Market Entry Decision Model V2 for Phase 10.4.
Enforces institutional conviction thresholds, calibrated multi-horizon net edge hurdles,
cooldown periods, daily velocity caps, and treats CASH as a first-class valid investment action.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass, PortfolioState
from src.models.real_market_multi_horizon_forecaster_v2 import MultiHorizonPredictionV2

logger = get_logger("signals.real_entry_model_v2")


@dataclass
class EntryDecisionV2:
    """Decision output for an entry opportunity evaluation under V2 rules."""
    symbol: str
    timestamp: str
    action: str  # BUY, CASH
    reason: str
    best_horizon_min: int
    expected_net_edge_bps: float
    calibrated_probability: float
    confidence_score: float
    suggested_allocation_pct: float
    is_authorized: bool
    evidence_class: str = EvidenceClass.REAL_HISTORICAL_MARKET_DATA.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RealMarketEntryModelV2:
    """
    V2 Entry Model designed and calibrated exclusively on real historical market data.
    """

    def __init__(
        self,
        min_net_edge_bps: float = 12.0,
        min_calibrated_prob: float = 0.55,
        max_daily_trades: int = 5,
        re_entry_cooldown_bars: int = 30,
        max_position_allocation_pct: float = 0.50,
        max_concurrent_positions: int = 2,
        restricted_times: Optional[List[Tuple[str, str]]] = None,
    ) -> None:
        self.min_net_edge_bps = min_net_edge_bps
        self.min_calibrated_prob = min_calibrated_prob
        self.max_daily_trades = max_daily_trades
        self.re_entry_cooldown_bars = re_entry_cooldown_bars
        self.max_position_allocation_pct = max_position_allocation_pct
        self.max_concurrent_positions = max_concurrent_positions
        self.restricted_times = restricted_times or [("15:45:00", "16:00:00")]  # Do not enter in final 15 min

        self.last_exit_bar: Dict[str, int] = {}
        self.session_trade_count: int = 0
        self.current_session_date: Optional[str] = None

    def reset_session(self, session_date: str) -> None:
        """Resets session velocity counters."""
        self.session_trade_count = 0
        self.current_session_date = session_date
        self.last_exit_bar.clear()

    def record_trade_executed(self) -> None:
        """Increments trade count."""
        self.session_trade_count += 1

    def record_symbol_exit(self, symbol: str, current_bar_index: int) -> None:
        """Records symbol exit bar index for cooldown tracking."""
        self.last_exit_bar[symbol] = current_bar_index

    def evaluate_entry(
        self,
        prediction: MultiHorizonPredictionV2,
        current_bar_index: int,
        time_str: str,
        current_active_positions_count: int,
    ) -> EntryDecisionV2:
        """
        Evaluates a candidate entry under V2 rules.
        """
        sym = prediction.symbol
        ts = prediction.timestamp
        best_h = prediction.optimal_target_horizon_min
        edge = prediction.best_expected_net_edge_bps
        prob = prediction.best_calibrated_prob
        forecast = getattr(prediction, f"forecast_{best_h}m", prediction.forecast_15m)

        # 1. Check time-of-day restrictions
        for start_t, end_t in self.restricted_times:
            if start_t <= time_str <= end_t:
                return EntryDecisionV2(
                    symbol=sym,
                    timestamp=ts,
                    action="CASH",
                    reason=f"TIME_RESTRICTION_{start_t}_TO_{end_t}",
                    best_horizon_min=best_h,
                    expected_net_edge_bps=edge,
                    calibrated_probability=prob,
                    confidence_score=forecast.confidence_score,
                    suggested_allocation_pct=0.0,
                    is_authorized=False,
                )

        # 2. Check Daily Trade Cap
        if self.session_trade_count >= self.max_daily_trades:
            return EntryDecisionV2(
                symbol=sym,
                timestamp=ts,
                action="CASH",
                reason="DAILY_TRADE_CAP_REACHED",
                best_horizon_min=best_h,
                expected_net_edge_bps=edge,
                calibrated_probability=prob,
                confidence_score=forecast.confidence_score,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 3. Check Active Position Limit
        if current_active_positions_count >= self.max_concurrent_positions:
            return EntryDecisionV2(
                symbol=sym,
                timestamp=ts,
                action="CASH",
                reason="MAX_CONCURRENT_POSITIONS_REACHED",
                best_horizon_min=best_h,
                expected_net_edge_bps=edge,
                calibrated_probability=prob,
                confidence_score=forecast.confidence_score,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 4. Check Re-Entry Cooldown
        if sym in self.last_exit_bar:
            bars_since_exit = current_bar_index - self.last_exit_bar[sym]
            if bars_since_exit < self.re_entry_cooldown_bars:
                return EntryDecisionV2(
                    symbol=sym,
                    timestamp=ts,
                    action="CASH",
                    reason=f"COOLDOWN_ACTIVE_{bars_since_exit}_OF_{self.re_entry_cooldown_bars}_BARS",
                    best_horizon_min=best_h,
                    expected_net_edge_bps=edge,
                    calibrated_probability=prob,
                    confidence_score=forecast.confidence_score,
                    suggested_allocation_pct=0.0,
                    is_authorized=False,
                )

        # 5. Check Minimum Expected Net Edge Hurdle
        if edge < self.min_net_edge_bps:
            return EntryDecisionV2(
                symbol=sym,
                timestamp=ts,
                action="CASH",
                reason=f"EDGE_INSUFFICIENT_{edge:.1f}bps_LT_{self.min_net_edge_bps:.1f}bps",
                best_horizon_min=best_h,
                expected_net_edge_bps=edge,
                calibrated_probability=prob,
                confidence_score=forecast.confidence_score,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # 6. Check Calibrated Probability Hurdle
        if prob < self.min_calibrated_prob:
            return EntryDecisionV2(
                symbol=sym,
                timestamp=ts,
                action="CASH",
                reason=f"PROB_INSUFFICIENT_{prob:.3f}_LT_{self.min_calibrated_prob:.3f}",
                best_horizon_min=best_h,
                expected_net_edge_bps=edge,
                calibrated_probability=prob,
                confidence_score=forecast.confidence_score,
                suggested_allocation_pct=0.0,
                is_authorized=False,
            )

        # Authorized BUY Decision
        return EntryDecisionV2(
            symbol=sym,
            timestamp=ts,
            action="BUY",
            reason=f"REAL_V2_AUTHORIZED_EDGE_{edge:.1f}bps_PROB_{prob:.2f}_HORIZON_{best_h}m",
            best_horizon_min=best_h,
            expected_net_edge_bps=edge,
            calibrated_probability=prob,
            confidence_score=forecast.confidence_score,
            suggested_allocation_pct=self.max_position_allocation_pct,
            is_authorized=True,
        )
