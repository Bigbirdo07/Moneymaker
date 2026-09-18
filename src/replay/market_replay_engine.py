"""
Historical Market Replay Engine with Strict Minute-by-Minute Clock Invariance,
Leakage Assertions, and Immutable Event Logging.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd

from src.core.logging import get_logger
from src.core.types import EvidenceClass, PortfolioState, Position, SessionType
from src.data.calendar import ET_TZ, UTC_TZ, TradingCalendar, REGULAR_OPEN, REGULAR_CLOSE
from src.data.historical_market_data import HistoricalMarketDataManager

logger = get_logger("replay.engine")


class FutureDataLeakageError(RuntimeError):
    """Raised immediately when any component attempts to access data beyond the simulated clock."""
    pass


@dataclass
class ReplayEventLog:
    """Immutable record of an autonomous decision and its full environmental context at time T."""
    decision_id: str
    decision_timestamp: str
    simulated_clock: str
    visible_data_max_timestamp: str
    symbol: str
    event_type: str  # PREMARKET_SCAN, OPPORTUNITY_RANK, ENTRY_DECISION, EXIT_DECISION, ALLOCATION, FILL
    features_snapshot: Dict[str, Any]
    signal_snapshot: Dict[str, Any]
    portfolio_state_snapshot: Dict[str, Any]
    risk_state_snapshot: Dict[str, Any]
    decision_action: str
    decision_rationale: str
    execution_result: Optional[Dict[str, Any]] = None
    later_outcome: Optional[Dict[str, Any]] = None
    evidence_class: str = EvidenceClass.HISTORICAL_REPLAY.value

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ReplaySessionSummary:
    """End-of-day summary for a single replayed trading day."""
    session_date: str
    start_time: str
    end_time: str
    total_minutes_replayed: int
    total_decisions_logged: int
    starting_equity: float
    ending_equity: float
    net_pnl: float
    gross_pnl: float
    total_friction: float
    trades_executed: int
    leakage_checks_passed: int


class HistoricalMarketReplayEngine:
    """
    Chronological minute-by-minute historical market replay engine.
    Maintains an absolute simulated clock and strictly prohibits future data leakage.
    """

    def __init__(
        self,
        market_data_manager: HistoricalMarketDataManager,
        calendar: Optional[TradingCalendar] = None,
        event_log_dir: Path | str = "artifacts/provenance/replay_event_logs",
    ) -> None:
        self.data_manager = market_data_manager
        self.calendar = calendar or TradingCalendar()
        self.event_log_dir = Path(event_log_dir)
        self.event_log_dir.mkdir(parents=True, exist_ok=True)

        self._simulated_clock: Optional[datetime] = None
        self._universe_dfs: Dict[str, pd.DataFrame] = {}
        self._universe_ts_arrays: Dict[str, np.ndarray] = {}
        self._event_logs: List[ReplayEventLog] = []
        self._leakage_checks_count: int = 0
        self._is_running: bool = False

    @property
    def simulated_clock(self) -> datetime:
        """Returns the current simulated clock timestamp."""
        if self._simulated_clock is None:
            raise RuntimeError("Replay engine simulated clock has not been initialized.")
        return self._simulated_clock

    def load_universe(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> None:
        """Loads and pre-indexes historical data for the active replay universe."""
        self._universe_dfs.clear()
        self._universe_ts_arrays.clear()
        for sym in symbols:
            df = self.data_manager.load_symbol_bars(
                sym,
                start_date=start_date,
                end_date=end_date,
                include_premarket=True,
            )
            self._universe_dfs[sym] = df
            self._universe_ts_arrays[sym] = pd.to_datetime(df["timestamp"], utc=True).values
        logger.info(f"Loaded {len(self._universe_dfs)} symbols for historical replay.")

    def assert_no_future_leakage(self, data_timestamps: pd.Series | List[datetime] | datetime) -> None:
        """
        Validates that max(data_timestamp_used) <= simulated_clock.
        Raises FutureDataLeakageError if violated.
        """
        if self._simulated_clock is None:
            return

        self._leakage_checks_count += 1
        if isinstance(data_timestamps, datetime):
            max_ts = data_timestamps
        elif isinstance(data_timestamps, (pd.Series, pd.Index)):
            if len(data_timestamps) == 0:
                return
            max_ts = pd.to_datetime(data_timestamps.max(), utc=True).to_pydatetime()
        elif isinstance(data_timestamps, list):
            if not data_timestamps:
                return
            max_ts = max(data_timestamps)
        else:
            return

        if max_ts > self._simulated_clock:
            diff_sec = (max_ts - self._simulated_clock).total_seconds()
            err_msg = (
                f"FUTURE_DATA_LEAKAGE_ERROR: Attempted to access data with timestamp {max_ts.isoformat()} "
                f"which is {diff_sec:.1f}s beyond simulated clock {self._simulated_clock.isoformat()}!"
            )
            logger.error(err_msg)
            raise FutureDataLeakageError(err_msg)

    def get_visible_bars(
        self,
        symbol: str,
        lookback_bars: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        Retrieves all bars for a symbol timestamped <= simulated_clock.
        Guarantees strict leakage invariance.
        """
        if symbol not in self._universe_dfs:
            raise KeyError(f"Symbol {symbol} not in loaded replay universe.")

        df = self._universe_dfs[symbol]
        ts_arr = self._universe_ts_arrays[symbol]
        curr_ts = pd.to_datetime(self.simulated_clock, utc=True).to_datetime64()
        idx = int(np.searchsorted(ts_arr, curr_ts, side="right"))

        if idx == 0:
            return df.iloc[0:0].copy()

        if lookback_bars is not None and lookback_bars > 0:
            start_idx = max(0, idx - lookback_bars)
            visible_df = df.iloc[start_idx:idx].copy()
        else:
            visible_df = df.iloc[:idx].copy()

        if not visible_df.empty:
            self.assert_no_future_leakage(visible_df["timestamp"])

        return visible_df

    def get_current_bar(self, symbol: str) -> Optional[pd.Series]:
        """Returns the bar exactly matching the current simulated clock, if one exists."""
        if symbol not in self._universe_dfs:
            return None
        df = self._universe_dfs[symbol]
        ts_arr = self._universe_ts_arrays[symbol]
        curr_ts = pd.to_datetime(self.simulated_clock, utc=True).to_datetime64()
        idx = int(np.searchsorted(ts_arr, curr_ts, side="right"))
        if idx > 0 and ts_arr[idx - 1] == curr_ts:
            return df.iloc[idx - 1]
        return None

    def record_decision_event(
        self,
        symbol: str,
        event_type: str,
        decision_action: str,
        decision_rationale: str,
        features_snapshot: Optional[Dict[str, Any]] = None,
        signal_snapshot: Optional[Dict[str, Any]] = None,
        portfolio_state_snapshot: Optional[Dict[str, Any]] = None,
        risk_state_snapshot: Optional[Dict[str, Any]] = None,
        execution_result: Optional[Dict[str, Any]] = None,
    ) -> ReplayEventLog:
        """Records an immutable, audited event in the replay event ledger."""
        if symbol in self._universe_dfs:
            vis_df = self.get_visible_bars(symbol)
            max_vis_ts = str(vis_df["timestamp"].max()) if not vis_df.empty else "NONE"
        else:
            max_vis_ts = self.simulated_clock.isoformat()

        decision_id = f"DEC_{len(self._event_logs)+1:06d}"
        log = ReplayEventLog(
            decision_id=decision_id,
            decision_timestamp=datetime.now(timezone.utc).isoformat(),
            simulated_clock=self.simulated_clock.isoformat(),
            visible_data_max_timestamp=max_vis_ts,
            symbol=symbol,
            event_type=event_type,
            features_snapshot=features_snapshot or {},
            signal_snapshot=signal_snapshot or {},
            portfolio_state_snapshot=portfolio_state_snapshot or {},
            risk_state_snapshot=risk_state_snapshot or {},
            decision_action=decision_action,
            decision_rationale=decision_rationale,
            execution_result=execution_result,
        )
        self._event_logs.append(log)
        return log

    def iterate_session_minutes(
        self,
        session_date: date | str,
        include_premarket: bool = True,
    ):
        """
        Yields control for each 1-minute simulated timestep across the trading session.
        Premarket: 08:30 to 09:29 ET.
        Regular Session: 09:30 to 16:00 ET.
        """
        if isinstance(session_date, str):
            session_date = datetime.strptime(session_date, "%Y-%m-%d").date()

        start_time = time(8, 30) if include_premarket else time(9, 30)
        end_time = time(16, 0)

        dt_et_start = datetime.combine(session_date, start_time, tzinfo=ET_TZ)
        dt_et_end = datetime.combine(session_date, end_time, tzinfo=ET_TZ)

        total_minutes = int((dt_et_end - dt_et_start).total_seconds() // 60) + 1

        self._is_running = True
        for m in range(total_minutes):
            curr_et = dt_et_start + timedelta(minutes=m)
            self._simulated_clock = curr_et.astimezone(UTC_TZ)
            yield self._simulated_clock, curr_et

        self._is_running = False

    def save_event_logs(self, filename: Optional[str] = None) -> Path:
        """Saves accumulated event logs to disk as JSONL."""
        if not filename:
            filename = f"replay_events_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.jsonl"
        out_path = self.event_log_dir / filename
        with open(out_path, "w") as f:
            for log in self._event_logs:
                f.write(json.dumps(log.to_dict()) + "\n")
        return out_path
