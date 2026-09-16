"""Customer-feedback sentiment scoring.

Three interchangeable scorers share one interface -- ``score(texts) -> Series``
of 0-1 scores -- plus one shared label mapping:

* :class:`LexiconSentimentScorer` - VADER lexicon baseline (offline, no training).
* :class:`TransformerSentimentScorer` - pretrained RoBERTa (most accurate,
  optional: requires ``torch`` and ``transformers``).
* :class:`SklearnSentimentScorer` - TF-IDF + linear model distilled from the
  transformer (fast, runs without torch).

``score_to_label`` turns a score into ``Excellent`` / ``Good`` /
``Needs Improvement`` using the same bands as the Power BI dashboard.
"""

from __future__ import annotations

import importlib.util

import pandas as pd

from .config import EXCELLENT_MIN_SCORE, GOOD_MIN_SCORE, SENTIMENT_LABELS

# Expected-value weights used to turn class probabilities into a 0-1 score.
SCORE_WEIGHTS = {"Excellent": 1.0, "Good": 0.5, "Needs Improvement": 0.0}


def score_to_label(score: float) -> str:
    """Map a 0-1 sentiment score to a rating label."""
    if pd.isna(score):
        return SENTIMENT_LABELS[0]
    if score >= EXCELLENT_MIN_SCORE:
        return "Excellent"
    if score > GOOD_MIN_SCORE:
        return "Good"
    return "Needs Improvement"


def label_series(scores: pd.Series) -> pd.Series:
    """Vectorised :func:`score_to_label` over a Series of scores."""
    return scores.map(score_to_label)
