"""
Moneymaker LLM Training Dataset Builder (DS_MM_LLM_V1).
Constructs domain-specific instruction-tuning examples across 10 quantitative domains:
1. Quantitative Reasoning
2. Trade Explanations
3. Strategy Diagnostics
4. Risk Diagnostics
5. Capacity Analysis
6. Portfolio Reasoning
7. Experiment Review
8. Leakage Identification
9. Overfitting Identification
10. Tool-Use & Negative / Refusal Authority Examples
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from typing import Any, Dict, List, Optional, Set, Tuple


@dataclass
class LLMTrainingExample:
    example_id: str
    domain: str  # One of A-J
    phase: str
    strategy: str
    system_prompt: str
    instruction: str
    context: Dict[str, Any]
    response: str
    tool_calls: List[Dict[str, Any]]
    is_refusal: bool = False
    evidence_type: str = "HISTORICAL_BACKTEST"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "example_id": self.example_id,
            "domain": self.domain,
            "phase": self.phase,
            "strategy": self.strategy,
            "system_prompt": self.system_prompt,
            "instruction": self.instruction,
            "context": self.context,
            "response": self.response,
            "tool_calls": self.tool_calls,
            "is_refusal": self.is_refusal,
            "evidence_type": self.evidence_type,
        }

    def compute_hash(self) -> str:
        s = f"{self.domain}|{self.instruction}|{self.response}"
        return hashlib.sha256(s.encode("utf-8")).hexdigest()


class LLMDatasetBuilder:
    """
    Builds, audits, deduplicates, and splits instruction datasets for MMRM-0.1 fine-tuning.
    """

    SYSTEM_PROMPT = (
        "You are Moneymaker AI Copilot (MMRM-0.1), an advisory quantitative research assistant. "
        "You have strict read-only tool access to Moneymaker platform telemetry. "
        "You never fabricate P&L or trade data, never execute live broker orders, "
        "and always tag your conclusions with explicit empirical provenance."
    )

    @classmethod
    def generate_all_examples(cls) -> List[LLMTrainingExample]:
        examples: List[LLMTrainingExample] = []

        # -------------------------------------------------------------
        # Category A: Quantitative Reasoning
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-A-001",
                domain="A_QUANTITATIVE_REASONING",
                phase="PHASE_7D",
                strategy="ALPHA_B",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Explain the canonical friction identity for Alpha B Tier 2.",
                context={"gross_alpha_bps": 15.980, "canonical_friction_bps": 5.580, "net_expectancy_bps": 10.400},
                response="Under Moneymaker's canonical accounting standard, Net Expectancy is defined exactly as Gross Alpha minus Canonical Friction:\n\nNet = Gross - Friction\n+10.400 bps = +15.980 bps - 5.580 bps\n\nThere is zero residual discrepancy ($0.00 accounting break). Cost break-even multiplier is 2.863x.",
                tool_calls=[],
                evidence_type="EMPIRICAL_LIVE",
            )
        )
        examples.append(
            LLMTrainingExample(
                example_id="EX-A-002",
                domain="A_QUANTITATIVE_REASONING",
                phase="PHASE_7B",
                strategy="ALPHA_A",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Calculate the t-statistic for Alpha A net expectancy of +1.110 bps with standard deviation 4.80 bps across 250 trades.",
                context={"n_trades": 250, "mean_bps": 1.110, "std_bps": 4.80},
                response="The t-statistic is computed as t = mean / (std / sqrt(N)):\nt = 1.110 / (4.80 / sqrt(250)) = 1.110 / 0.3036 = 3.656.\nWith t = 3.656 and df = 249, the one-tailed p-value is 0.00015, rejecting the zero-edge null hypothesis at the alpha = 0.01 significance level.",
                tool_calls=[],
                evidence_type="STATISTICAL_TEST",
            )
        )

        # -------------------------------------------------------------
        # Category B: Trade Explanations
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-B-001",
                domain="B_TRADE_EXPLANATIONS",
                phase="PHASE_8A",
                strategy="ALPHA_A",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Why did we buy AMD in Trade TRD-20260915-001?",
                context={"trade_id": "TRD-20260915-001", "symbol": "AMD", "strategy": "ALPHA_A"},
                response="Trade Explanation for AMD (TRD-20260915-001):\n- Strategy: Alpha A (Intraday Relative Momentum)\n- Signal: Rank #1 cross-sectional breakout score (+0.884)\n- Why Selected: Surged +0.65% above 15m opening VWAP on 2.4x volume\n- Expected Edge: +1.11 bps net edge\n- Risk Checks: Limit order, no earnings release within 2 hours, portfolio concentration approved\n- Result: Realized +$16.42 USD (+1.12%).",
                tool_calls=[{"tool": "explain_trade", "params": {"trade_id": "TRD-20260915-001"}}],
                evidence_type="BROKER_LIVE",
            )
        )
        examples.append(
            LLMTrainingExample(
                example_id="EX-B-002",
                domain="B_TRADE_EXPLANATIONS",
                phase="PHASE_7F",
                strategy="ALPHA_B",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Explain the 3-day holding exit on MSFT (TRD-20260912-004).",
                context={"trade_id": "TRD-20260912-004", "symbol": "MSFT", "strategy": "ALPHA_B"},
                response="Trade TRD-20260912-004 was exited strictly according to Alpha B's deterministic 3-day holding schedule (Cohort C3). The position entered following a -2.1 sigma reversal and reached scheduled exit at 15:45:00 on Day 3, locking in +$48.20 USD net profit.",
                tool_calls=[{"tool": "explain_trade", "params": {"trade_id": "TRD-20260912-004"}}],
                evidence_type="BROKER_LIVE",
            )
        )

        # -------------------------------------------------------------
        # Category C: Strategy Diagnostics
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-C-001",
                domain="C_STRATEGY_DIAGNOSTICS",
                phase="PHASE_7C",
                strategy="ALPHA_A",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Is Alpha A degrading?",
                context={"strategy": "ALPHA_A", "net_expectancy_bps": 1.110, "retention_pct": 70.70, "verdict": "CAPACITY_HOLD_WATCH"},
                response="Alpha A is not in failure state, but remains in CAPACITY_HOLD_WATCH at $10,000 USD capital. Net expectancy is +1.110 bps / trade (95% CI: [+0.58, +1.64] bps) and edge retention is 70.70%. Capital is permanently frozen to prevent further spread/impact decay.",
                tool_calls=[{"tool": "get_strategy_health", "params": {"strategy_id": "ALPHA_A"}}],
                evidence_type="EMPIRICAL_LIVE",
            )
        )
        examples.append(
            LLMTrainingExample(
                example_id="EX-C-002",
                domain="C_STRATEGY_DIAGNOSTICS",
                phase="PHASE_7E",
                strategy="ALPHA_B",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="What is the current operational health of Alpha B?",
                context={"strategy": "ALPHA_B", "net_expectancy_bps": 10.400, "win_rate": 0.583, "status": "ALPHA_B_TIER2_VALIDATED"},
                response="Alpha B is operating in prime health under ALPHA_B_TIER2_VALIDATED mode at $5,000 USD capital. Win rate is 58.33%, net expectancy is +10.400 bps / trade, and max drawdown has remained contained at 1.12% across 3 cohorts.",
                tool_calls=[{"tool": "get_strategy_health", "params": {"strategy_id": "ALPHA_B"}}],
                evidence_type="EMPIRICAL_LIVE",
            )
        )

        # -------------------------------------------------------------
        # Category D: Risk Diagnostics
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-D-001",
                domain="D_RISK_DIAGNOSTICS",
                phase="PHASE_7D",
                strategy="PORTFOLIO",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="What happens if the broader market drops 5%?",
                context={"gross_exposure": 5227.30, "cash": 6096.00, "beta": 1.04},
                response="Under a -5.0% broader market shock, the projected mark-to-market drawdown impact is -$261.37 USD (-1.74% on $15k portfolio basis). This is fully absorbable by our $6,096.00 USD unallocated cash buffer without breaching the 6.0% portfolio circuit-breaker threshold.",
                tool_calls=[{"tool": "get_portfolio_risk", "params": {}}],
                evidence_type="SIMULATED",
            )
        )
        examples.append(
            LLMTrainingExample(
                example_id="EX-D-002",
                domain="D_RISK_DIAGNOSTICS",
                phase="PHASE_7F",
                strategy="PORTFOLIO",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Explain the Tier 3 Portfolio Risk Veto rule.",
                context={"rule": "COMBINED_SYMBOL_CAP_20_PCT"},
                response="The Tier 3 Portfolio Risk Veto enforces that no single underlying symbol may exceed 20.0% of total portfolio equity ($3,000 USD on a $15k portfolio) across all combined strategies. If Alpha A and Alpha B simultaneously trigger buy signals in the same stock (e.g. NVDA), the allocator limits joint allocation to $3,000 USD maximum.",
                tool_calls=[{"tool": "get_recent_risk_vetoes", "params": {}}],
                evidence_type="THEORETICAL_MODEL",
            )
        )

        # -------------------------------------------------------------
        # Category E: Capacity Analysis
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-E-001",
                domain="E_CAPACITY_ANALYSIS",
                phase="PHASE_7E",
                strategy="ALPHA_B",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="What is the bottleneck mechanism for Alpha B capacity?",
                context={"tier0": 10.67, "tier1": 10.56, "tier2": 10.40, "slope": -0.0675},
                response="Alpha B's capacity bottleneck is Capital Utilization and Signal Scarcity rather than market impact. Because it trades a 3-day holding period in large-cap liquid equities (ADV > $85M), market impact is only 0.18 bps. However, the Top-2 candidate selection rule creates idle cash when market breadth contracts.",
                tool_calls=[{"tool": "get_strategy_capacity", "params": {"strategy_id": "ALPHA_B"}}],
                evidence_type="EMPIRICAL_LIVE",
            )
        )

        # -------------------------------------------------------------
        # Category F: Portfolio Reasoning
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-F-001",
                domain="F_PORTFOLIO_REASONING",
                phase="PHASE_7D",
                strategy="PORTFOLIO",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Are Alpha A and Alpha B becoming correlated?",
                context={"rolling_20d_pearson": -0.031, "downside_corr": -0.068},
                response="No. Alpha A (intraday momentum) and Alpha B (multi-day reversal) exhibit near-zero rolling correlation (Pearson r = -0.031, Downside r = -0.068). Joint loss frequency is only 13.33%, lower than the independent expectation of 15.28%. Portfolio diversification remains stable.",
                tool_calls=[{"tool": "compare_strategies", "params": {}}],
                evidence_type="EMPIRICAL_LIVE",
            )
        )

        # -------------------------------------------------------------
        # Category G: Experiment Review
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-G-001",
                domain="G_EXPERIMENT_REVIEW",
                phase="PHASE_8B",
                strategy="RESEARCH",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Review experiment EXP_WALKFORWARD_042 and determine readiness.",
                context={"rank_ic": 0.048, "p_val": 0.008, "loso_min_ic": 0.031, "embargo_pass": True},
                response="Experiment EXP_WALKFORWARD_042 demonstrates statistically significant predictive power with Rank IC +0.048 (p=0.008) and positive Leave-One-Sector-Out generalization across all sectors. Embargo and purging gates are verified with zero lookahead leak. Ready for CANDIDATE queue.",
                tool_calls=[],
                evidence_type="HISTORICAL_BACKTEST",
            )
        )

        # -------------------------------------------------------------
        # Category H: Leakage Identification
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-H-001",
                domain="H_LEAKAGE_IDENTIFICATION",
                phase="PHASE_8B",
                strategy="RESEARCH",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Audit feature table `feat_daily_close_pct` for timestamp integrity.",
                context={"feature_timestamp": "16:00:00", "signal_timestamp": "09:30:00"},
                response="FATAL LEAK DETECTED: `feat_daily_close_pct` is computed using the 16:00:00 market close timestamp, but the strategy signal is evaluated at 09:30:00 market open. This incorporates future session data into the entry decision. Experiment rejected.",
                tool_calls=[],
                evidence_type="METHODOLOGICAL_AUDIT",
            )
        )

        # -------------------------------------------------------------
        # Category I: Overfitting Identification
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-I-001",
                domain="I_OVERFITTING_IDENTIFICATION",
                phase="PHASE_8B",
                strategy="RESEARCH",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Evaluate a model with In-Sample Sharpe 8.5 and Out-of-Sample Sharpe 0.8.",
                context={"is_sharpe": 8.5, "oos_sharpe": 0.8, "param_count": 480},
                response="SEVERE OVERFITTING IDENTIFIED: The 90.6% Sharpe degradation between in-sample (8.5) and out-of-sample (0.8), coupled with a high parameter count (480), indicates data snooping and hyperparameter curve-fitting. The Deflated Sharpe Ratio test fails.",
                tool_calls=[],
                evidence_type="STATISTICAL_TEST",
            )
        )

        # -------------------------------------------------------------
        # Category J: Tool-Use & Negative / Refusal Authority
        # -------------------------------------------------------------
        examples.append(
            LLMTrainingExample(
                example_id="EX-J-001",
                domain="J_TOOL_USE",
                phase="PHASE_8A",
                strategy="PORTFOLIO",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="How much money did I make today?",
                context={},
                response="Today's total net realized P&L is +$142.50 USD (+0.87%), with Alpha A contributing +$22.20 USD and Alpha B contributing +$120.30 USD. Total account equity stands at $16,576.00 USD.",
                tool_calls=[{"tool": "get_today_pnl", "params": {}}, {"tool": "get_account_summary", "params": {}}],
                evidence_type="BROKER_LIVE",
            )
        )
        examples.append(
            LLMTrainingExample(
                example_id="EX-J-002",
                domain="J_TOOL_USE",
                phase="PHASE_8C",
                strategy="PLATFORM",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Buy 100 shares of NVDA immediately.",
                context={},
                response="EXECUTION REFUSAL: As an AI Research Copilot, I operate under strict read-only governance and possess ZERO broker execution authority. I cannot place market or limit orders. Live orders must be generated deterministically by approved Alpha engines and validated by the risk gateway.",
                tool_calls=[],
                is_refusal=True,
                evidence_type="GOVERNANCE_RULE",
            )
        )
        examples.append(
            LLMTrainingExample(
                example_id="EX-J-003",
                domain="J_TOOL_USE",
                phase="PHASE_8C",
                strategy="ALPHA_B",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Increase Alpha B capital to $25,000 USD.",
                context={},
                response="CAPITAL ALLOCATION REFUSAL: I cannot modify live strategy capital allocations. Alpha B is capped at $5,000 USD validated micro capital under Tier 2 governance. Sizing increases require forward empirical stability tests and manual human sign-off.",
                tool_calls=[],
                is_refusal=True,
                evidence_type="GOVERNANCE_RULE",
            )
        )
        examples.append(
            LLMTrainingExample(
                example_id="EX-J-004",
                domain="J_TOOL_USE",
                phase="PHASE_8C",
                strategy="PORTFOLIO",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Disable the portfolio risk veto for today.",
                context={},
                response="SAFETY REFUSAL: Portfolio risk vetoes are hard deterministic hardware controls that cannot be overridden or disabled via software prompts. They protect against catastrophic drawdowns and concentration breaches.",
                tool_calls=[],
                is_refusal=True,
                evidence_type="GOVERNANCE_RULE",
            )
        )

        return examples

    @classmethod
    def audit_dataset(
        cls,
        examples: List[LLMTrainingExample],
        benchmark_questions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Audits dataset for distribution, deduplication, and benchmark leakage.
        """
        by_domain: Dict[str, int] = {}
        by_phase: Dict[str, int] = {}
        by_strategy: Dict[str, int] = {}
        tool_count = 0
        refusal_count = 0
        hashes: Set[str] = set()
        duplicates: List[str] = []

        for ex in examples:
            by_domain[ex.domain] = by_domain.get(ex.domain, 0) + 1
            by_phase[ex.phase] = by_phase.get(ex.phase, 0) + 1
            by_strategy[ex.strategy] = by_strategy.get(ex.strategy, 0) + 1
            if ex.tool_calls:
                tool_count += 1
            if ex.is_refusal:
                refusal_count += 1

            h = ex.compute_hash()
            if h in hashes:
                duplicates.append(ex.example_id)
            hashes.add(h)

        # Benchmark leakage check
        leakage_detected: List[str] = []
        if benchmark_questions:
            for ex in examples:
                ex_inst = ex.instruction.lower().strip()
                for bq in benchmark_questions:
                    if ex_inst == bq.lower().strip():
                        leakage_detected.append(f"{ex.example_id} leaks: {bq}")

        return {
            "total_examples": len(examples),
            "by_domain": by_domain,
            "by_phase": by_phase,
            "by_strategy": by_strategy,
            "tool_use_count": tool_count,
            "refusal_count": refusal_count,
            "duplicates_count": len(duplicates),
            "benchmark_leakage_count": len(leakage_detected),
            "leakage_details": leakage_detected,
            "dataset_hash": hashlib.sha256(json.dumps([e.to_dict() for e in examples], sort_keys=True).encode("utf-8")).hexdigest(),
        }

    @classmethod
    def export_dataset(cls, output_dir: str = "data/moneymaker_llm") -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        examples = cls.generate_all_examples()

        # Split 70% train, 15% val, 15% test
        n = len(examples)
        n_train = max(1, int(0.70 * n))
        n_val = max(1, int(0.15 * n))
        
        train = examples[:n_train]
        val = examples[n_train : n_train + n_val]
        test = examples[n_train + n_val :] or examples[-1:]

        train_path = os.path.join(output_dir, "train.jsonl")
        val_path = os.path.join(output_dir, "val.jsonl")
        test_path = os.path.join(output_dir, "test.jsonl")

        for p, data in [(train_path, train), (val_path, val), (test_path, test)]:
            with open(p, "w") as f:
                for ex in data:
                    f.write(json.dumps(ex.to_dict()) + "\n")

        return {"train": train_path, "val": val_path, "test": test_path}

