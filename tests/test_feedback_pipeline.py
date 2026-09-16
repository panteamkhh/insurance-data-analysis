"""Integration tests for the customer-feedback pipeline."""

import pandas as pd

from src import config
from src.run_feedback_analysis import analyze, run


class StubScorer:
    name = "stub"

    def score(self, texts):
        positive = ("great", "excellent")
        return pd.Series(texts).map(
            lambda text: 0.9 if any(word in text.lower() for word in positive) else 0.1
        )


def _feedback_file(tmp_path):
    path = tmp_path / "feedback.csv"
    pd.DataFrame(
        {
            "Customer Name": ["A", "B", "C", "D"],
            "Feedback": [
                "Great service, very satisfied",
                "Excellent and fast handling",
                "Bad claim handling, very slow",
                "Poor communication and confusing",
            ],
        }
    ).to_csv(path, index=False)
    return path


def test_analyze_adds_sentiment_columns(tmp_path):
    scored = analyze(filepath=_feedback_file(tmp_path), scorer=StubScorer())

    assert {"sentiment_score", "sentiment_label"}.issubset(scored.columns)
    assert scored["sentiment_label"].tolist() == [
        "Excellent",
        "Excellent",
        "Needs Improvement",
        "Needs Improvement",
    ]


def test_run_writes_exports_and_charts(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SCREENSHOTS_DIR", tmp_path / "shots")

    scored = run(
        filepath=_feedback_file(tmp_path),
        output_dir=tmp_path / "out",
        scorer=StubScorer(),
    )

    assert len(scored) == 4
    assert (tmp_path / "out" / "customer_feedback_scored.csv").exists()
    assert (tmp_path / "out" / "feedback_word_frequencies.csv").exists()
    assert (tmp_path / "shots" / "feedback_01_sentiment_distribution.png").exists()
    assert (tmp_path / "shots" / "feedback_04_wordcloud_all.png").exists()
