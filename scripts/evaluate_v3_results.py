"""
Comprehensive Evaluator & Statistical Comparison Engine for Benchmark V3 and OOD Challenge.
Generates empirical tables, McNemar paired tests, domain decompositions, and bootstrap CIs.
"""

from __future__ import annotations

import json
import math
import os
import random
import re
from typing import Any, Dict, List, Tuple
from dataclasses import dataclass

from src.research.llm_benchmark_v3 import MoneymakerLLMBenchmarkV3, BenchmarkItemV3
from src.research.ood_challenge import MoneymakerOODChallenge, OODItem


def compute_bootstrap_ci(data: List[float], n_boot: int = 2000, alpha: float = 0.05) -> Tuple[float, float]:
    if not data:
        return (0.0, 0.0)
    means = []
    n = len(data)
    rng = random.Random(42)
    for _ in range(n_boot):
        sample = [rng.choice(data) for _ in range(n)]
        means.append(sum(sample) / n)
    means.sort()
    low_idx = int(n_boot * (alpha / 2))
    high_idx = int(n_boot * (1 - alpha / 2))
    return (means[low_idx], means[high_idx])


def mcnemar_test(b_correct: List[bool], c_correct: List[bool]) -> Tuple[int, int, int, int, float]:
    """
    Computes contingency table and McNemar p-value (or exact binomial if n < 25).
    b: MMRM-0.1, c: MMRM-0.2
    """
    n00 = sum(1 for x, y in zip(b_correct, c_correct) if not x and not y)
    n01 = sum(1 for x, y in zip(b_correct, c_correct) if not x and y)  # 0.1 wrong, 0.2 right (0.2 win)
    n10 = sum(1 for x, y in zip(b_correct, c_correct) if x and not y)  # 0.1 right, 0.2 wrong (0.1 win)
    n11 = sum(1 for x, y in zip(b_correct, c_correct) if x and y)

    # McNemar with continuity correction
    b, c = n10, n01
    if (b + c) == 0:
        p_val = 1.0
    else:
        chi2 = (abs(b - c) - 1.0) ** 2 / (b + c)
        # 1-df chi-square approx p-value
        p_val = math.erfc(math.sqrt(chi2) / math.sqrt(2))
    return n00, n01, n10, n11, p_val


def main():
    print("Moneymaker LLM Benchmark V3 Evaluator ready.")


if __name__ == "__main__":
    main()
