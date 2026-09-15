"""Comprehensive machine learning classification metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    log_loss,
    brier_score_loss,
)


@dataclass
class MLClassificationMetrics:
    """Standardized quantitative evaluation metrics for directional classifiers."""
    accuracy: float
    balanced_accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: float
    pr_auc: float
    log_loss: float
    brier_score: float
    sample_count: int
    positive_class_ratio: float


def compute_classification_metrics(
    y_true: np.ndarray | pd.Series,
    y_pred: np.ndarray | pd.Series,
    y_prob: np.ndarray | pd.Series,
) -> MLClassificationMetrics:
    """Computes all required statistical and probabilistic classification metrics."""
    y_t = np.asarray(y_true)
    y_p = np.asarray(y_pred)
    y_pr = np.asarray(y_prob)

    if y_pr.ndim > 1:
        y_pr = y_pr[:, 1]

    n_samples = len(y_t)
    pos_ratio = float(np.mean(y_t)) if n_samples > 0 else 0.0

    acc = float(accuracy_score(y_t, y_p))
    bal_acc = float(balanced_accuracy_score(y_t, y_p))
    prec = float(precision_score(y_t, y_p, zero_division=0))
    rec = float(recall_score(y_t, y_p, zero_division=0))
    f1 = float(f1_score(y_t, y_p, zero_division=0))

    try:
        roc = float(roc_auc_score(y_t, y_pr))
    except Exception:
        roc = 0.5

    try:
        pr_auc = float(average_precision_score(y_t, y_pr))
    except Exception:
        pr_auc = pos_ratio

    try:
        ll = float(log_loss(y_t, np.clip(y_pr, 1e-7, 1 - 1e-7)))
    except Exception:
        ll = 0.693

    brier = float(brier_score_loss(y_t, y_pr))

    return MLClassificationMetrics(
        accuracy=round(acc, 4),
        balanced_accuracy=round(bal_acc, 4),
        precision=round(prec, 4),
        recall=round(rec, 4),
        f1=round(f1, 4),
        roc_auc=round(roc, 4),
        pr_auc=round(pr_auc, 4),
        log_loss=round(ll, 4),
        brier_score=round(brier, 4),
        sample_count=n_samples,
        positive_class_ratio=round(pos_ratio, 4),
    )
