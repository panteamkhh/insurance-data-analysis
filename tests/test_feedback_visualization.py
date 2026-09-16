"""Tests for the feedback sentiment charts."""

import pandas as pd

from src.feedback_visualization import (
    plot_score_by_label,
    plot_score_histogram,
    plot_sentiment_distribution,
)


def _scored():
    return pd.DataFrame(
        {
            "sentiment_score": [0.95, 0.9, 0.6, 0.1, 0.05],
            "sentiment_label": [
                "Excellent",
                "Excellent",
                "Good",
                "Needs Improvement",
                "Needs Improvement",
            ],
        }
    )


def test_plot_sentiment_distribution_writes_file(tmp_path):
    fig = plot_sentiment_distribution(_scored()["sentiment_label"], directory=tmp_path)
    assert (tmp_path / "feedback_01_sentiment_distribution.png").exists()
    assert fig is not None


def test_plot_score_histogram_writes_file(tmp_path):
    plot_score_histogram(_scored()["sentiment_score"], directory=tmp_path)
    assert (tmp_path / "feedback_02_score_histogram.png").exists()


def test_plot_score_by_label_writes_file(tmp_path):
    plot_score_by_label(_scored(), directory=tmp_path)
    assert (tmp_path / "feedback_03_score_by_label.png").exists()
