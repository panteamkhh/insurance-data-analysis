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
