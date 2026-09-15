"""Statistical significance testing, permutation null hypothesis models, and bootstrap uncertainty."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import norm, skew, kurtosis
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss

from src.models.base import BaseMLModel
from src.backtest.engine import BacktestEngine, CompletedTrade
from src.backtest.costs import TransactionCostModel
from src.evaluation.metrics import MetricsCalculator, PerformanceSummary
from src.strategies.ml_strategy import MLSignalStrategy


@dataclass
class BootstrapConfidenceInterval:
    """Bootstrap confidence intervals (point estimate, 2.5th, 97.5th percentiles)."""
    metric_name: str
    point_estimate: float
    ci_lower_2_5: float
    ci_upper_97_5: float
    standard_error: float


@dataclass
class PermutationNullResult:
    """Results from permutation null hypothesis testing."""
    metric_name: str
    observed_value: float
    null_mean: float
    null_std: float
    empirical_p_value: float
    num_permutations: int
    is_statistically_significant: bool # p < 0.05


@dataclass
class DeflatedSharpeReport:
    """Deflated Sharpe Ratio (DSR) report accounting for multiple testing and non-normality."""
    observed_sharpe: float
    estimated_annualized_sharpe: float
    deflated_sharpe_p_value: float
    num_trials_tested: int
    variance_of_trials: float
    skewness: float
    kurtosis: float
    is_significant: bool


class SignificanceTester:
    """Statistical significance, block permutation, and bootstrap inference engine."""

    @staticmethod
    def run_permutation_null_test(
        model: BaseMLModel,
        X_test: pd.DataFrame,
        y_test: pd.Series | np.ndarray,
        num_permutations: int = 100,
        block_size: Optional[int] = None,
        seed: int = 42,
    ) -> Dict[str, PermutationNullResult]:
        """
        Runs label permutation null hypothesis testing.
        Preserves the feature matrix X and timestamps while randomly shuffling (or block-shuffling) y.
        """
        rng = np.random.default_rng(seed)
        y_arr = np.asarray(y_test)
        n_samples = len(y_arr)

        # 1. Evaluate observed model on true labels
        observed_probs = model.predict_proba(X_test)
        p_up = observed_probs[:, 1] if observed_probs.ndim > 1 else observed_probs.flatten()
        
        obs_roc = float(roc_auc_score(y_arr, p_up)) if len(np.unique(y_arr)) > 1 else 0.5
        obs_pr = float(average_precision_score(y_arr, p_up)) if len(np.unique(y_arr)) > 1 else 0.5
        obs_brier = float(brier_score_loss(y_arr, p_up))

        null_rocs: List[float] = []
        null_prs: List[float] = []
        null_briers: List[float] = []

        for _ in range(num_permutations):
            if block_size is not None and block_size > 1:
                # Block permutation
                n_blocks = int(np.ceil(n_samples / block_size))
                block_indices = list(range(n_blocks))
                rng.shuffle(block_indices)
                shuffled_idx = []
                for b in block_indices:
                    shuffled_idx.extend(range(b * block_size, min(n_samples, (b + 1) * block_size)))
                shuffled_y = y_arr[shuffled_idx]
            else:
                shuffled_y = rng.permutation(y_arr)

            try:
                null_roc = float(roc_auc_score(shuffled_y, p_up)) if len(np.unique(shuffled_y)) > 1 else 0.5
            except Exception:
                null_roc = 0.5
            try:
                null_pr = float(average_precision_score(shuffled_y, p_up)) if len(np.unique(shuffled_y)) > 1 else 0.5
            except Exception:
                null_pr = 0.5
            null_brier = float(brier_score_loss(shuffled_y, p_up))

            null_rocs.append(null_roc)
            null_prs.append(null_pr)
            null_briers.append(null_brier)

        # Empirical p-values: P(null >= observed)
        p_roc = (np.sum(np.array(null_rocs) >= obs_roc) + 1.0) / (num_permutations + 1.0)
        p_pr = (np.sum(np.array(null_prs) >= obs_pr) + 1.0) / (num_permutations + 1.0)
        # For Brier score, lower is better: P(null <= observed)
        p_brier = (np.sum(np.array(null_briers) <= obs_brier) + 1.0) / (num_permutations + 1.0)

        return {
            "roc_auc": PermutationNullResult(
                metric_name="ROC-AUC",
                observed_value=round(obs_roc, 4),
                null_mean=round(float(np.mean(null_rocs)), 4),
                null_std=round(float(np.std(null_rocs)), 4),
                empirical_p_value=round(float(p_roc), 4),
                num_permutations=num_permutations,
                is_statistically_significant=p_roc < 0.05,
            ),
            "pr_auc": PermutationNullResult(
                metric_name="PR-AUC",
                observed_value=round(obs_pr, 4),
                null_mean=round(float(np.mean(null_prs)), 4),
                null_std=round(float(np.std(null_prs)), 4),
                empirical_p_value=round(float(p_pr), 4),
                num_permutations=num_permutations,
                is_statistically_significant=p_pr < 0.05,
            ),
            "brier_score": PermutationNullResult(
                metric_name="Brier Score",
                observed_value=round(obs_brier, 4),
                null_mean=round(float(np.mean(null_briers)), 4),
                null_std=round(float(np.std(null_briers)), 4),
                empirical_p_value=round(float(p_brier), 4),
                num_permutations=num_permutations,
                is_statistically_significant=p_brier < 0.05,
            ),
        }

    @staticmethod
    def compute_bootstrap_ci(
        returns: np.ndarray,
        num_bootstraps: int = 1000,
        block_size: int = 12, # 12 5-min bars = 1 hour blocks
        seed: int = 42,
    ) -> Dict[str, BootstrapConfidenceInterval]:
        """
        Computes Stationary Block Bootstrap confidence intervals for return distribution metrics.
        """
        if len(returns) < 10:
            return {}

        rng = np.random.default_rng(seed)
        n = len(returns)
        n_blocks = int(np.ceil(n / block_size))

        boot_means: List[float] = []
        boot_vols: List[float] = []
        boot_sharpes: List[float] = []

        for _ in range(num_bootstraps):
            # Sample random blocks with replacement
            block_starts = rng.integers(0, max(1, n - block_size + 1), size=n_blocks)
            sampled_idx = []
            for start in block_starts:
                sampled_idx.extend(range(start, min(n, start + block_size)))
            boot_sample = returns[sampled_idx[:n]]

            mean_r = float(np.mean(boot_sample))
            std_r = float(np.std(boot_sample, ddof=1)) if len(boot_sample) > 1 else 1e-6
            sharpe_r = (mean_r / (std_r + 1e-8)) * np.sqrt(252.0 * 78.0)

            boot_means.append(mean_r * 252.0 * 78.0) # Annualized return
            boot_vols.append(std_r * np.sqrt(252.0 * 78.0))
            boot_sharpes.append(sharpe_r)

        obs_mean = float(np.mean(returns)) * 252.0 * 78.0
        obs_vol = float(np.std(returns, ddof=1)) * np.sqrt(252.0 * 78.0)
        obs_sharpe = (float(np.mean(returns)) / (float(np.std(returns, ddof=1)) + 1e-8)) * np.sqrt(252.0 * 78.0)

        return {
            "annualized_return": BootstrapConfidenceInterval(
                metric_name="Annualized Return",
                point_estimate=round(obs_mean, 4),
                ci_lower_2_5=round(float(np.percentile(boot_means, 2.5)), 4),
                ci_upper_97_5=round(float(np.percentile(boot_means, 97.5)), 4),
                standard_error=round(float(np.std(boot_means)), 4),
            ),
            "annualized_volatility": BootstrapConfidenceInterval(
                metric_name="Annualized Volatility",
                point_estimate=round(obs_vol, 4),
                ci_lower_2_5=round(float(np.percentile(boot_vols, 2.5)), 4),
                ci_upper_97_5=round(float(np.percentile(boot_vols, 97.5)), 4),
                standard_error=round(float(np.std(boot_vols)), 4),
            ),
            "sharpe_ratio": BootstrapConfidenceInterval(
                metric_name="Sharpe Ratio",
                point_estimate=round(obs_sharpe, 4),
                ci_lower_2_5=round(float(np.percentile(boot_sharpes, 2.5)), 4),
                ci_upper_97_5=round(float(np.percentile(boot_sharpes, 97.5)), 4),
                standard_error=round(float(np.std(boot_sharpes)), 4),
            ),
        }

    @staticmethod
    def compute_trade_level_uncertainty(trades: List[CompletedTrade]) -> Dict[str, Any]:
        """Calculates trade-level expectancy, standard error, and 95% confidence intervals."""
        if not trades:
            return {"total_trades": 0, "expectancy": 0.0, "se": 0.0, "ci_lower": 0.0, "ci_upper": 0.0}

        pnls = np.array([t.net_pnl for t in trades])
        n = len(pnls)
        mean_pnl = float(np.mean(pnls))
        std_pnl = float(np.std(pnls, ddof=1)) if n > 1 else 0.0
        se_pnl = std_pnl / np.sqrt(n) if n > 0 else 0.0

        ci_lower = mean_pnl - 1.96 * se_pnl
        ci_upper = mean_pnl + 1.96 * se_pnl

        return {
            "total_trades": n,
            "avg_trade_pnl": round(mean_pnl, 4),
            "std_error": round(se_pnl, 4),
            "ci_lower_95": round(ci_lower, 4),
            "ci_upper_95": round(ci_upper, 4),
            "t_statistic": round(mean_pnl / (se_pnl + 1e-8), 4) if se_pnl > 0 else 0.0,
            "is_significant": ci_lower > 0.0,
        }

    @staticmethod
    def calculate_deflated_sharpe_ratio(
        observed_sharpe: float,
        returns: np.ndarray,
        num_trials: int = 50,
        variance_of_trials: float = 0.50,
        benchmark_sharpe: float = 0.0,
    ) -> DeflatedSharpeReport:
        """
        Calculates López de Prado's Deflated Sharpe Ratio (DSR) correcting for
        multiple testing, positive variance across trial configurations, skewness, and kurtosis.
        """
        n_obs = len(returns)
        if n_obs < 10:
            return DeflatedSharpeReport(
                observed_sharpe=observed_sharpe,
                estimated_annualized_sharpe=observed_sharpe,
                deflated_sharpe_p_value=1.0,
                num_trials_tested=num_trials,
                variance_of_trials=variance_of_trials,
                skewness=0.0,
                kurtosis=3.0,
                is_significant=False,
            )

        skew_val = float(skew(returns))
        kurt_val = float(kurtosis(returns, fisher=False)) # Pearson kurtosis (normal = 3)

        # Expected maximum Sharpe under the null of multiple independent trials
        # E[max(Z)] approx (1 - EulerGamma)*Z^{-1}(1 - 1/K) + EulerGamma*Z^{-1}(1 - 1/(K*e))
        euler_gamma = 0.5772156649
        z_1 = norm.ppf(1.0 - 1.0 / num_trials)
        z_2 = norm.ppf(1.0 - 1.0 / (num_trials * np.e))
        expected_max_sharpe = np.sqrt(variance_of_trials) * ((1.0 - euler_gamma) * z_1 + euler_gamma * z_2)

        # Standard error of Sharpe ratio under non-normality
        # Var(SR) approx (1 - skew*SR + (kurt - 1)/4 * SR^2) / N
        var_sr = (1.0 - skew_val * observed_sharpe + ((kurt_val - 1.0) / 4.0) * (observed_sharpe ** 2)) / n_obs
        se_sr = np.sqrt(max(1e-6, var_sr))

        # DSR statistic
        dsr_stat = (observed_sharpe - expected_max_sharpe) / se_sr
        p_val = float(1.0 - norm.cdf(dsr_stat))

        return DeflatedSharpeReport(
            observed_sharpe=round(observed_sharpe, 4),
            estimated_annualized_sharpe=round(observed_sharpe * np.sqrt(252.0 * 78.0), 4),
            deflated_sharpe_p_value=round(p_val, 4),
            num_trials_tested=num_trials,
            variance_of_trials=round(variance_of_trials, 4),
            skewness=round(skew_val, 4),
            kurtosis=round(kurt_val, 4),
            is_significant=p_val < 0.05,
        )
