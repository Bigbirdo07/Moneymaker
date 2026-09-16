"""
Moneymaker LLM Training Dataset Builder.
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
10. Tool-Use Examples
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from typing import Any, Dict, List


@dataclass
class LLMTrainingExample:
    example_id: str
    domain: str  # One of A-J
    system_prompt: str
    instruction: str
    context: Dict[str, Any]
    response: str
    tool_calls: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "example_id": self.example_id,
            "domain": self.domain,
            "system_prompt": self.system_prompt,
            "instruction": self.instruction,
            "context": self.context,
            "response": self.response,
            "tool_calls": self.tool_calls,
        }


class LLMDatasetBuilder:
    """
    Builds train/val/test splits for fine-tuning the Moneymaker Research Model (MMRM-0.1).
    """

    SYSTEM_PROMPT = (
        "You are Moneymaker AI Copilot, a grounded quantitative assistant. "
        "You have strict read-only tool access to Moneymaker platform telemetry. "
        "You never fabricate P&L or trade data, never execute unauthorized orders, "
        "and always tag your conclusions with explicit empirical provenance."
    )

    @classmethod
    def generate_all_examples(cls) -> List[LLMTrainingExample]:
        examples: List[LLMTrainingExample] = []

        # Category A: Quantitative Reasoning
        examples.append(
            LLMTrainingExample(
                example_id="EX-A-001",
                domain="A_QUANTITATIVE_REASONING",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Explain the canonical friction identity for Alpha B Tier 2.",
                context={"gross_alpha_bps": 15.980, "canonical_friction_bps": 5.580, "net_expectancy_bps": 10.400},
                response="Under Moneymaker's canonical accounting standard, Net Expectancy is defined exactly as Gross Alpha minus Canonical Friction:\n\nNet = Gross - Friction\n+10.400 bps = +15.980 bps - 5.580 bps\n\nThere is zero residual discrepancy ($0.00 accounting break). Cost break-even multiplier is 2.863x.",
                tool_calls=[],
            )
        )

        # Category B: Trade Explanations
        examples.append(
            LLMTrainingExample(
                example_id="EX-B-001",
                domain="B_TRADE_EXPLANATIONS",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Why did we buy AMD in Trade TRD-20260915-001?",
                context={"trade_id": "TRD-20260915-001", "symbol": "AMD", "strategy": "ALPHA_A"},
                response="Trade Explanation for AMD (TRD-20260915-001):\n- Strategy: Alpha A (Intraday Relative Momentum)\n- Signal: Rank #1 cross-sectional breakout score (+0.884)\n- Why Selected: Surged +0.65% above 15m opening VWAP on 2.4x volume\n- Expected Edge: +1.11 bps net edge\n- Risk Checks: Limit order, no earnings release within 2 hours, portfolio concentration approved\n- Result: Realized +$16.42 USD (+1.12%).",
                tool_calls=[{"tool": "explain_trade", "params": {"trade_id": "TRD-20260915-001"}}],
            )
        )

        # Category C: Strategy Diagnostics
        examples.append(
            LLMTrainingExample(
                example_id="EX-C-001",
                domain="C_STRATEGY_DIAGNOSTICS",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Is Alpha A degrading?",
                context={"strategy": "ALPHA_A", "net_expectancy_bps": 1.110, "retention_pct": 70.70, "verdict": "CAPACITY_HOLD_WATCH"},
                response="Alpha A is not in failure state, but remains in CAPACITY_HOLD_WATCH at $10,000 USD capital. Net expectancy is +1.110 bps / trade (95% CI: [+0.58, +1.64] bps) and edge retention is 70.70%. Capital is permanently frozen to prevent further spread/impact decay.",
                tool_calls=[{"tool": "get_strategy_health", "params": {"strategy_id": "ALPHA_A"}}],
            )
        )

        # Category D: Risk Diagnostics
        examples.append(
            LLMTrainingExample(
                example_id="EX-D-001",
                domain="D_RISK_DIAGNOSTICS",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="What happens if the broader market drops 5%?",
                context={"gross_exposure": 5227.30, "cash": 6096.00, "beta": 1.04},
                response="Under a -5.0% broader market shock, the projected mark-to-market drawdown impact is -$261.37 USD (-1.74% on $15k portfolio basis). This is fully absorbable by our $6,096.00 USD unallocated cash buffer without breaching the 6.0% portfolio circuit-breaker threshold.",
                tool_calls=[{"tool": "get_portfolio_risk", "params": {}}],
            )
        )

        # Category E: Capacity Analysis
        examples.append(
            LLMTrainingExample(
                example_id="EX-E-001",
                domain="E_CAPACITY_ANALYSIS",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="What is the bottleneck mechanism for Alpha B capacity?",
                context={"tier0": 10.67, "tier1": 10.56, "tier2": 10.40, "slope": -0.0675},
                response="Alpha B's capacity bottleneck is Capital Utilization and Signal Scarcity rather than market impact. Because it trades a 3-day holding period in large-cap liquid equities (ADV > $85M), market impact is only 0.18 bps. However, the Top-2 candidate selection rule creates idle cash when market breadth contracts.",
                tool_calls=[{"tool": "get_strategy_capacity", "params": {"strategy_id": "ALPHA_B"}}],
            )
        )

        # Category F: Portfolio Reasoning
        examples.append(
            LLMTrainingExample(
                example_id="EX-F-001",
                domain="F_PORTFOLIO_REASONING",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Are Alpha A and Alpha B becoming correlated?",
                context={"rolling_20d_pearson": -0.031, "downside_corr": -0.068},
                response="No. Alpha A (intraday momentum) and Alpha B (multi-day reversal) exhibit near-zero rolling correlation (Pearson r = -0.031, Downside r = -0.068). Joint loss frequency is only 13.33%, lower than the independent expectation of 15.28%. Portfolio diversification remains stable.",
                tool_calls=[{"tool": "compare_strategies", "params": {}}],
            )
        )

        # Category G: Experiment Review
        examples.append(
            LLMTrainingExample(
                example_id="EX-G-001",
                domain="G_EXPERIMENT_REVIEW",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Review experiment EXP_WALKFORWARD_042 and determine readiness.",
                context={"rank_ic": 0.048, "p_val": 0.008, "loso_min_ic": 0.031, "embargo_pass": True},
                response="Experiment EXP_WALKFORWARD_042 demonstrates statistically significant predictive power with Rank IC +0.048 (p=0.008) and positive Leave-One-Sector-Out generalization across all sectors. Embargo and purging gates are verified with zero lookahead leak. Ready for CANDIDATE queue.",
                tool_calls=[],
            )
        )

        # Category H: Leakage Identification
        examples.append(
            LLMTrainingExample(
                example_id="EX-H-001",
                domain="H_LEAKAGE_IDENTIFICATION",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Audit feature table `feat_daily_close_pct` for timestamp integrity.",
                context={"feature_timestamp": "16:00:00", "signal_timestamp": "09:30:00"},
                response="FATAL LEAK DETECTED: `feat_daily_close_pct` is computed using the 16:00:00 market close timestamp, but the strategy signal is evaluated at 09:30:00 market open. This incorporates future session data into the entry decision. Experiment rejected.",
                tool_calls=[],
            )
        )

        # Category I: Overfitting Identification
        examples.append(
            LLMTrainingExample(
                example_id="EX-I-001",
                domain="I_OVERFITTING_IDENTIFICATION",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="Evaluate a model with In-Sample Sharpe 8.5 and Out-of-Sample Sharpe 0.8.",
                context={"is_sharpe": 8.5, "oos_sharpe": 0.8, "param_count": 480},
                response="SEVERE OVERFITTING IDENTIFIED: The 90.6% Sharpe degradation between in-sample (8.5) and out-of-sample (0.8), coupled with a high parameter count (480), indicates data snooping and hyperparameter curve-fitting. The Deflated Sharpe Ratio test fails.",
                tool_calls=[],
            )
        )

        # Category J: Tool-Use Examples
        examples.append(
            LLMTrainingExample(
                example_id="EX-J-001",
                domain="J_TOOL_USE",
                system_prompt=cls.SYSTEM_PROMPT,
                instruction="How much money did I make today?",
                context={},
                response="Today's total net realized P&L is +$142.50 USD (+0.87%), with Alpha A contributing +$22.20 USD and Alpha B contributing +$120.30 USD. Total account equity stands at $16,576.00 USD.",
                tool_calls=[{"tool": "get_today_pnl", "params": {}}, {"tool": "get_account_summary", "params": {}}],
            )
        )

        return examples

    @classmethod
    def export_dataset(cls, output_dir: str = "data/moneymaker_llm") -> Dict[str, str]:
        os.makedirs(output_dir, exist_ok=True)
        examples = cls.generate_all_examples()

        # Split 70% train, 15% val, 15% test
        n = len(examples)
        train = examples[: int(0.7 * n) or 7]
        val = examples[int(0.7 * n) : int(0.85 * n) or 8]
        test = examples[int(0.85 * n) :] or examples[-2:]

        train_path = os.path.join(output_dir, "train.jsonl")
        val_path = os.path.join(output_dir, "val.jsonl")
        test_path = os.path.join(output_dir, "test.jsonl")

        for p, data in [(train_path, train), (val_path, val), (test_path, test)]:
            with open(p, "w") as f:
                for ex in data:
                    f.write(json.dumps(ex.to_dict()) + "\n")

        return {"train": train_path, "val": val_path, "test": test_path}
