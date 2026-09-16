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


class LexiconSentimentScorer:
    """VADER lexicon scorer -- fast, offline and training-free.

    The raw VADER compound score (-1..1) is rescaled to 0..1 so every scorer in
    this module speaks the same language.
    """

    name = "vader"

    def __init__(self) -> None:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        self._analyzer = SentimentIntensityAnalyzer()

    def score(self, texts) -> pd.Series:
        series = pd.Series(texts).astype(str)
        return series.map(lambda text: (self._analyzer.polarity_scores(text)["compound"] + 1) / 2)


def transformer_available() -> bool:
    """True when both ``torch`` and ``transformers`` can be imported."""
    return all(importlib.util.find_spec(name) is not None for name in ("torch", "transformers"))


class TransformerSentimentScorer:
    """Pretrained RoBERTa sentiment model (positive / neutral / negative).

    The score is ``P(positive) + 0.5 * P(neutral)`` so neutral text lands in the
    middle of the 0-1 range. This is the most accurate scorer in the module and
    is used to create the "teacher" labels for the distilled sklearn model.
    """

    name = "transformer"

    def __init__(self, model_name: str | None = None) -> None:
        from transformers import pipeline

        from .config import SENTIMENT_MODEL_NAME

        self.model_name = model_name or SENTIMENT_MODEL_NAME
        self._pipeline = pipeline(
            "sentiment-analysis", model=self.model_name, top_k=None, truncation=True
        )

    def score(self, texts) -> pd.Series:
        series = pd.Series(texts).astype(str)

        def _one(text: str) -> float:
            result = {item["label"].lower(): item["score"] for item in self._pipeline(text)[0]}
            return result.get("positive", 0.0) + 0.5 * result.get("neutral", 0.0)

        return series.map(_one)
