"""Tests for the sentiment score-to-label mapping."""

import numpy as np
import pandas as pd
import pytest

from src.sentiment import label_series, score_to_label


@pytest.mark.parametrize(
    "score, expected",
    [
        (1.0, "Excellent"),
        (0.80, "Excellent"),
        (0.79, "Good"),
        (0.51, "Good"),
        (0.50, "Needs Improvement"),
        (0.0, "Needs Improvement"),
    ],
)
def test_score_to_label_thresholds(score, expected):
    assert score_to_label(score) == expected


def test_score_to_label_handles_nan():
    assert score_to_label(float("nan")) == "Needs Improvement"


def test_label_series_is_vectorised():
    scores = pd.Series([0.9, 0.6, 0.1])
    labels = label_series(scores)
    assert labels.tolist() == ["Excellent", "Good", "Needs Improvement"]


def test_label_series_handles_missing_values():
    scores = pd.Series([0.9, np.nan])
    assert label_series(scores).iloc[1] == "Needs Improvement"


def test_lexicon_scorer_returns_bounded_scores():
    from src.sentiment import LexiconSentimentScorer

    scorer = LexiconSentimentScorer()
    scores = scorer.score(["Excellent service, very satisfied!", "Terrible, very disappointed."])

    assert scores.between(0, 1).all()
    assert scores.iloc[0] > scores.iloc[1]


def test_lexicon_scorer_preserves_index():
    from src.sentiment import LexiconSentimentScorer

    texts = pd.Series(["Great value", "Poor service"], index=[10, 20])
    scores = LexiconSentimentScorer().score(texts)

    assert scores.index.tolist() == [10, 20]


def test_sklearn_scorer_scores_from_a_saved_model(tmp_path):
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    from src.sentiment import SklearnSentimentScorer

    texts = [
        "excellent great satisfied",
        "wonderful amazing recommend",
        "good fine okay",
        "decent acceptable",
        "bad terrible awful",
        "poor disappointing slow",
        "horrible frustrating",
        "worst unacceptable",
    ]
    labels = [
        "Excellent",
        "Excellent",
        "Good",
        "Good",
        "Needs Improvement",
        "Needs Improvement",
        "Needs Improvement",
        "Needs Improvement",
    ]
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer()),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    ).fit(texts, labels)
    path = tmp_path / "model.joblib"
    joblib.dump(model, path)

    scorer = SklearnSentimentScorer(model_path=str(path))
    scores = scorer.score(["excellent great", "terrible awful"])

    assert scores.between(0, 1).all()
    assert scores.iloc[0] > scores.iloc[1]


def test_get_default_scorer_can_select_vader():
    from src.sentiment import get_default_scorer

    assert get_default_scorer(prefer=("vader",)).name == "vader"


def test_add_sentiment_columns():
    from src.sentiment import add_sentiment_columns

    class StubScorer:
        name = "stub"

        def score(self, texts):
            return pd.Series([0.9, 0.1], index=pd.Series(texts).index)

    df = pd.DataFrame({"Feedback": ["Great", "Bad"]})
    result = add_sentiment_columns(df, scorer=StubScorer())

    assert result["sentiment_label"].tolist() == ["Excellent", "Needs Improvement"]
    assert "sentiment_score" in result.columns
    assert "sentiment_score" not in df.columns
