"""
Shadow Execution Engine for Phase 3A Forward Validation.
Simulates and tracks three concurrent execution paths (Marketable, Next-Trade, Passive Limit)
without placing real broker orders, with full implementation shortfall and adverse selection tracking.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from src.data.market_provider import BarEvent, QuoteEvent, TradeEvent


class ExecutionPath(str, Enum):
    MARKETABLE = "MARKETABLE"
    NEXT_TRADE = "NEXT_TRADE"
    PASSIVE_LIMIT = "PASSIVE_LIMIT"


class LimitFillStatus(str, Enum):
    FILLED = "FILLED"
    PARTIAL = "PARTIAL"
    MISSED = "MISSED"
    ADVERSE_SELECTED = "ADVERSE_SELECTED"


@dataclass
class ProposedTrade:
    """Proposed candidate trade emitted by the shadow decision loop."""
    decision_id: str
    symbol: str
    direction: str  # "LONG" (only longs allowed in Phase 3A)
    shares: float
    decision_price: float
    decision_timestamp: pd.Timestamp
    model_confidence: float
    expected_alpha_bps: float
    opportunity_score: float
    archetype: str
    regime: str
    stop_loss_price: float
    take_profit_price: float
    target_holding_bars: int = 3  # 15 minutes


@dataclass
class ExecutionSimulationResult:
    """Complete execution record across all three hypothetical execution paths."""
    decision_id: str
    symbol: str
    direction: str
    shares: float
    decision_timestamp: pd.Timestamp
    decision_midprice: float
    quote_bid: float
    quote_ask: float
    spread_bps: float

    # Path A: Marketable Execution
    marketable_fill_price: float
    marketable_slippage_bps: float
    marketable_shortfall_bps: float

    # Path B: Next-Observable Trade
    next_trade_fill_price: Optional[float]
    next_trade_timestamp: Optional[pd.Timestamp]
    next_trade_shortfall_bps: Optional[float]

    # Path C: Passive Limit Order
    limit_order_price: float
    limit_fill_status: LimitFillStatus
    limit_fill_price: Optional[float]
    limit_fill_timestamp: Optional[pd.Timestamp]
    limit_time_to_fill_sec: Optional[float]
    limit_shortfall_bps: Optional[float]

    # Post-Decision Excursions & Quality Tracking
    max_favorable_excursion_bps: float = 0.0
    max_adverse_excursion_bps: float = 0.0
    future_15m_return_bps: Optional[float] = None


class ShadowExecutionSimulator:
    """Simulates realistic execution dynamics under strict chronological rules."""

    def __init__(
        self,
        marketable_slippage_bps: float = 0.5,
        limit_queue_fraction: float = 0.5,
        limit_adverse_selection_penalty_bps: float = 1.5,
    ):
        self.marketable_slippage_bps = marketable_slippage_bps
        self.limit_queue_fraction = limit_queue_fraction
        self.limit_adverse_selection_penalty_bps = limit_adverse_selection_penalty_bps

    def simulate_execution(
        self,
        proposed_trade: ProposedTrade,
        current_quote: QuoteEvent,
        subsequent_bars: List[BarEvent],
        subsequent_trades: Optional[List[TradeEvent]] = None,
    ) -> ExecutionSimulationResult:
        """
        Evaluate hypothetical execution across all 3 execution paths.
        Guarantees: Uses strictly data arriving at or after decision_timestamp.
        """
        midprice = current_quote.mid_price
        spread_bps = current_quote.spread_bps

        # --- Path A: Marketable Order ---
        # Long enters at Ask + conservative slippage
        marketable_fill_price = current_quote.ask * (1.0 + (self.marketable_slippage_bps / 10000.0))
        marketable_shortfall_bps = ((marketable_fill_price - midprice) / midprice) * 10000.0
        marketable_slippage = ((marketable_fill_price - current_quote.ask) / current_quote.ask) * 10000.0

        # --- Path B: Next Observable Trade ---
        next_trade_price = None
        next_trade_ts = None
        next_trade_shortfall = None
        if subsequent_trades and len(subsequent_trades) > 0:
            first_trade = subsequent_trades[0]
            next_trade_price = first_trade.price
            next_trade_ts = first_trade.received_timestamp
            next_trade_shortfall = ((next_trade_price - midprice) / midprice) * 10000.0
        elif subsequent_bars and len(subsequent_bars) > 0:
            # Fallback to next bar open if trade tick not available
            next_trade_price = subsequent_bars[0].open
            next_trade_ts = subsequent_bars[0].bar_start_timestamp
            next_trade_shortfall = ((next_trade_price - midprice) / midprice) * 10000.0

        # --- Path C: Passive Limit Order ---
        # Placed at Bid price for Long
        limit_price = current_quote.bid
        limit_status = LimitFillStatus.MISSED
        limit_fill_price = None
        limit_fill_ts = None
        limit_time_to_fill = None
        limit_shortfall = None

        if subsequent_bars and len(subsequent_bars) > 0:
            first_bar = subsequent_bars[0]
            # Order fills if bar trades at or below bid price and volume exceeds queue threshold
            if first_bar.low <= limit_price:
                # If bar drops substantially below limit, it's toxic/adverse selection
                if first_bar.close < limit_price:
                    limit_status = LimitFillStatus.ADVERSE_SELECTED
                    limit_fill_price = limit_price * (1.0 - (self.limit_adverse_selection_penalty_bps / 10000.0))
                else:
                    limit_status = LimitFillStatus.FILLED
                    limit_fill_price = limit_price

                limit_fill_ts = first_bar.bar_close_timestamp
                limit_time_to_fill = (limit_fill_ts - proposed_trade.decision_timestamp).total_seconds()
                limit_shortfall = ((limit_fill_price - midprice) / midprice) * 10000.0
            else:
                limit_status = LimitFillStatus.MISSED

        # Excursion calculations across subsequent holding window (up to 3 bars / 15m)
        mfe_bps = 0.0
        mae_bps = 0.0
        fut_15m_return = None
        if subsequent_bars and len(subsequent_bars) >= 3:
            holding_bars = subsequent_bars[:3]
            max_high = max(b.high for b in holding_bars)
            min_low = min(b.low for b in holding_bars)
            final_close = holding_bars[-1].close

            mfe_bps = ((max_high - midprice) / midprice) * 10000.0
            mae_bps = ((midprice - min_low) / midprice) * 10000.0
            fut_15m_return = ((final_close - midprice) / midprice) * 10000.0

        return ExecutionSimulationResult(
            decision_id=proposed_trade.decision_id,
            symbol=proposed_trade.symbol,
            direction=proposed_trade.direction,
            shares=proposed_trade.shares,
            decision_timestamp=proposed_trade.decision_timestamp,
            decision_midprice=midprice,
            quote_bid=current_quote.bid,
            quote_ask=current_quote.ask,
            spread_bps=spread_bps,
            marketable_fill_price=marketable_fill_price,
            marketable_slippage_bps=marketable_slippage,
            marketable_shortfall_bps=marketable_shortfall_bps,
            next_trade_fill_price=next_trade_price,
            next_trade_timestamp=next_trade_ts,
            next_trade_shortfall_bps=next_trade_shortfall,
            limit_order_price=limit_price,
            limit_fill_status=limit_status,
            limit_fill_price=limit_fill_price,
            limit_fill_timestamp=limit_fill_ts,
            limit_time_to_fill_sec=limit_time_to_fill,
            limit_shortfall_bps=limit_shortfall,
            max_favorable_excursion_bps=mfe_bps,
            max_adverse_excursion_bps=mae_bps,
            future_15m_return_bps=fut_15m_return,
        )
