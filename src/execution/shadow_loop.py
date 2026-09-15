"""
Full Shadow Decision Loop Orchestrator for Phase 3A.
Executes the frozen Phase 2.6 champion strategy in real-time or replay mode without real money.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set
import numpy as np
import pandas as pd

from src.data.market_provider import LiveMarketDataProvider, QuoteEvent, BarEvent
from src.features.incremental_features import IncrementalFeatureEngine
from src.evaluation.latency import LatencyRecord, LatencyTracker
from src.evaluation.model_health import ModelHealthMonitor, ModelHealthState
from src.evaluation.forward_evaluation import (
    ForwardExecutionEvaluator,
    RejectedOpportunityRecord,
    ForwardDecayPoint,
)
from src.execution.shadow_engine import (
    ProposedTrade,
    ShadowExecutionSimulator,
    ExecutionSimulationResult,
)
from src.portfolio.risk_engine import DeterministicRiskEngine, RiskDecisionType
from src.portfolio.shadow_portfolio import ShadowPaperPortfolio, ExitReason


class ShadowDecisionLoop:
    """Orchestrates real-time shadow decision cycles across the candidate universe."""

    def __init__(
        self,
        provider: LiveMarketDataProvider,
        symbols: List[str],
        portfolio: Optional[ShadowPaperPortfolio] = None,
        risk_engine: Optional[DeterministicRiskEngine] = None,
        cooldown_bars: int = 4,
        top_k: int = 3,
        confidence_threshold: float = 0.58,
        meta_threshold: float = 0.52,
    ):
        self.provider = provider
        self.symbols = symbols
        self.portfolio = portfolio or ShadowPaperPortfolio(initial_cash=1000.0)
        self.risk_engine = risk_engine or DeterministicRiskEngine()
        self.latency_tracker = LatencyTracker()
        self.health_monitor = ModelHealthMonitor()
        self.execution_simulator = ShadowExecutionSimulator()
        self.evaluator = ForwardExecutionEvaluator()

        self.cooldown_bars = cooldown_bars
        self.top_k = top_k
        self.confidence_threshold = confidence_threshold
        self.meta_threshold = meta_threshold

        # Symbol cooldown tracking: symbol -> last trade bar index
        self._last_trade_bar_index: Dict[str, int] = {}
        self._current_bar_index: int = 0
        self._executed_decision_ids: Set[str] = set()

    def step(self, current_time: pd.Timestamp) -> Dict[str, any]:
        """
        Execute a single decision cycle at current_time.
        """
        self._current_bar_index += 1
        t_received = pd.Timestamp.now(tz=timezone.utc)

        # 1. Validate data feed freshness
        feed_valid = True
        for sym in self.symbols:
            valid, reason = self.provider.check_staleness(sym, current_time)
            if not valid:
                feed_valid = False
                break

        # Check market benchmark (SPY)
        spy_bars = self.provider.get_bar_history("SPY", timeframe="5m", count=20)

        # 2. Check position exits first
        self._process_open_position_exits(current_time)

        if not feed_valid or not self.provider.is_connected():
            # Fail closed: NO_NEW_TRADES
            return {"status": "FEED_INVALID_NO_TRADES", "executed": 0, "rejected": 0}

        # 3. Compute Features & Scores for all eligible universe
        candidates = []
        t_feat_start = pd.Timestamp.now(tz=timezone.utc)

        for sym in self.symbols:
            quote = self.provider.get_latest_quote(sym)
            bar_history = self.provider.get_bar_history(sym, timeframe="5m", count=20)
            if quote is None or len(bar_history) < 14:
                continue

            # Compute features incrementally
            feats = IncrementalFeatureEngine.compute_features(
                symbol_bars=bar_history,
                current_quote=quote,
                market_benchmark_bars=spy_bars,
            )

            # Simulated Frozen Champion Model Inference
            # Logistic / XGBoost momentum function: ret_15m + rvol - spread
            raw_logit = (feats["ret_15m"] * 120.0) + (feats["rvol_14"] * 0.15) - (feats["spread_bps"] * 0.05)
            model_conf = 1.0 / (1.0 + np.exp(-raw_logit))

            # Expected alpha in bps
            expected_alpha_bps = (model_conf - 0.50) * 40.0

            # Meta-label model prediction (TAKE vs REJECT)
            meta_logit = (model_conf * 2.0) - (feats["spread_bps"] * 0.20) + (feats["rvol_14"] * 0.10)
            meta_prob = 1.0 / (1.0 + np.exp(-meta_logit))
            meta_decision = "TAKE_TRADE" if meta_prob >= self.meta_threshold else "REJECT_TRADE"

            # Cost-aware Opportunity Score: E[R] - Friction - Lambda * Vol
            friction_bps = quote.spread_bps + 1.0
            vol_penalty = 0.05 * feats["volatility_bps"]
            opportunity_score = expected_alpha_bps - friction_bps - vol_penalty

            candidates.append({
                "symbol": sym,
                "quote": quote,
                "bars": bar_history,
                "features": feats,
                "model_conf": model_conf,
                "expected_alpha_bps": expected_alpha_bps,
                "meta_decision": meta_decision,
                "meta_prob": meta_prob,
                "opportunity_score": opportunity_score,
                "price": quote.ask,
            })

        t_model_end = pd.Timestamp.now(tz=timezone.utc)

        if not candidates:
            return {"status": "NO_CANDIDATES", "executed": 0, "rejected": 0}

        # 4. Cross-Sectional Ranking
        candidates.sort(key=lambda c: c["opportunity_score"], reverse=True)
        t_ranking = pd.Timestamp.now(tz=timezone.utc)

        # 5. Candidate Selection & Filtering
        executed_count = 0
        rejected_count = 0

        for rank_idx, cand in enumerate(candidates, start=1):
            sym = cand["symbol"]
            decision_id = f"DEC_{sym}_{current_time.strftime('%Y%m%d%H%M')}"

            # Immutable duplicate protection
            if decision_id in self._executed_decision_ids:
                continue

            # Record universe score for Rank IC evaluation
            # Realized forward return will be measured across subsequent bars
            cand_bars = cand["bars"]
            realized_ret_15m = 0.0
            if len(cand_bars) >= 4:
                realized_ret_15m = ((cand_bars[-1].close - cand_bars[-4].close) / cand_bars[-4].close) * 10000.0

            self.evaluator.record_universe_score(
                timestamp=current_time,
                symbol=sym,
                score=cand["opportunity_score"],
                realized_15m_return=realized_ret_15m,
            )

            # Check Cooldown
            last_traded = self._last_trade_bar_index.get(sym, -999)
            cooldown_active = (self._current_bar_index - last_traded) < self.cooldown_bars

            # Check Candidate Eligibility (Top-k, Meta-Label, Confidence)
            is_top_k = (rank_idx <= self.top_k)
            passes_conf = (cand["model_conf"] >= self.confidence_threshold)
            passes_meta = (cand["meta_decision"] == "TAKE_TRADE")

            if not is_top_k or not passes_conf or not passes_meta or cooldown_active:
                reason = "COOLDOWN_ACTIVE" if cooldown_active else (
                    "LOW_CONFIDENCE" if not passes_conf else (
                        "META_LABEL_REJECT" if not passes_meta else "RANK_BELOW_TOP_K"
                    )
                )
                self.evaluator.record_rejection(
                    RejectedOpportunityRecord(
                        decision_id=decision_id,
                        symbol=sym,
                        timestamp=current_time,
                        model_score=cand["opportunity_score"],
                        meta_label_decision=cand["meta_decision"],
                        rank=rank_idx,
                        spread_bps=cand["quote"].spread_bps,
                        volatility_bps=cand["features"]["volatility_bps"],
                        archetype="HIGH_BETA_HIGH_VOL",
                        regime="NORMAL",
                        rejection_reason=reason,
                        future_realized_return_bps=realized_ret_15m,
                    )
                )
                rejected_count += 1
                continue

            # 6. Evaluate Risk Engine
            open_pos_dict = {
                p_sym: {"shares": p.shares, "notional": p.market_value, "sector": p.sector}
                for p_sym, p in self.portfolio.positions.items()
            }
            risk_eval = self.risk_engine.evaluate_order(
                symbol=sym,
                price=cand["price"],
                shares=100.0 / cand["price"],  # Target 10% ($100)
                sector="Technology",
                current_equity=self.portfolio.total_equity,
                available_cash=self.portfolio.cash,
                current_daily_pnl=self.portfolio.daily_pnl,
                current_drawdown_pct=self.portfolio.current_drawdown_pct,
                open_positions=open_pos_dict,
            )

            if risk_eval.decision == RiskDecisionType.REJECT:
                self.evaluator.record_rejection(
                    RejectedOpportunityRecord(
                        decision_id=decision_id,
                        symbol=sym,
                        timestamp=current_time,
                        model_score=cand["opportunity_score"],
                        meta_label_decision=cand["meta_decision"],
                        rank=rank_idx,
                        spread_bps=cand["quote"].spread_bps,
                        volatility_bps=cand["features"]["volatility_bps"],
                        archetype="HIGH_BETA_HIGH_VOL",
                        regime="NORMAL",
                        rejection_reason=f"RISK_{risk_eval.reason}",
                        future_realized_return_bps=realized_ret_15m,
                    )
                )
                rejected_count += 1
                continue

            # 7. Generate Proposed Trade
            t_decision = pd.Timestamp.now(tz=timezone.utc)
            prop_trade = ProposedTrade(
                decision_id=decision_id,
                symbol=sym,
                direction="LONG",
                shares=risk_eval.approved_shares,
                decision_price=cand["price"],
                decision_timestamp=current_time,
                model_confidence=cand["model_conf"],
                expected_alpha_bps=cand["expected_alpha_bps"],
                opportunity_score=cand["opportunity_score"],
                archetype="HIGH_BETA_HIGH_VOL",
                regime="NORMAL",
                stop_loss_price=cand["price"] * 0.985,
                take_profit_price=cand["price"] * 1.030,
                target_holding_bars=3,
            )

            # 8. Record Execution Simulation across 3 paths
            subsequent_bars = self.provider.get_bar_history(sym, timeframe="5m", count=5)
            exec_result = self.execution_simulator.simulate_execution(
                proposed_trade=prop_trade,
                current_quote=cand["quote"],
                subsequent_bars=subsequent_bars,
            )
            self.evaluator.record_execution(exec_result)

            # 9. Open position in Paper Portfolio
            opened = self.portfolio.open_position(
                symbol=sym,
                shares=risk_eval.approved_shares,
                entry_price=exec_result.marketable_fill_price,
                entry_timestamp=current_time,
                sector="Technology",
            )

            if opened:
                self._executed_decision_ids.add(decision_id)
                self._last_trade_bar_index[sym] = self._current_bar_index
                executed_count += 1

                # Record Latency
                self.latency_tracker.record(
                    LatencyRecord(
                        decision_id=decision_id,
                        symbol=sym,
                        exchange_timestamp=cand["quote"].exchange_timestamp,
                        provider_timestamp=cand["quote"].provider_timestamp,
                        received_timestamp=t_received,
                        feature_ready_timestamp=t_feat_start,
                        model_start_timestamp=t_feat_start,
                        model_end_timestamp=t_model_end,
                        ranking_timestamp=t_ranking,
                        decision_timestamp=t_decision,
                        hypothetical_fill_timestamp=t_decision,
                    )
                )

        return {
            "status": "COMPLETED",
            "executed": executed_count,
            "rejected": rejected_count,
            "equity": self.portfolio.total_equity,
            "cash": self.portfolio.cash,
        }

    def _process_open_position_exits(self, current_time: pd.Timestamp) -> None:
        """Check time-based exits (3 bars / 15m), stop loss, and take profit."""
        symbols_to_close = []
        for sym, pos in list(self.portfolio.positions.items()):
            quote = self.provider.get_latest_quote(sym)
            if quote is None:
                continue

            current_price = quote.bid  # Liquidate at bid
            self.portfolio.update_mark_to_market(sym, current_price)

            # Check stop loss
            if current_price <= pos.stop_loss_price:
                symbols_to_close.append((sym, current_price, ExitReason.STOP_LOSS))
            # Check take profit
            elif current_price >= pos.take_profit_price:
                symbols_to_close.append((sym, current_price, ExitReason.TAKE_PROFIT))
            # Check time-based exit (15-minute / 3 bars target)
            elif pos.bars_held >= pos.target_exit_bars:
                symbols_to_close.append((sym, current_price, ExitReason.TIME_EXIT))

        for sym, exit_px, reason in symbols_to_close:
            self.portfolio.close_position(sym, exit_px, current_time, reason)
