"""Tests for the sentiment training utilities."""

import json

import pandas as pd

from src import train_sentiment as ts


class StubScorer:
    name = "stub"

    def score(self, texts):
        return pd.Series(texts).map(lambda text: 0.9 if "great" in text else 0.1)


def _dataset():
    texts, labels = [], []
    for index in range(10):
        texts.append(f"great excellent satisfied {index}")
        labels.append("Excellent")
        texts.append(f"good okay fine {index}")
        labels.append("Good")
        texts.append(f"bad terrible slow {index}")
        labels.append("Needs Improvement")
    return pd.Series(texts), pd.Series(labels)


def test_build_teacher_labels_returns_expected_columns():
    result = ts.build_teacher_labels(
        pd.Series(["great service", "bad service"]), scorer=StubScorer()
    )

    assert list(result.columns) == ["teacher_score", "teacher_label"]
    assert result["teacher_label"].tolist() == ["Excellent", "Needs Improvement"]


def test_cross_validate_models_returns_ranked_metrics():
    texts, labels = _dataset()

    results = ts.cross_validate_models(texts, labels, cv=5)

    assert set(results.columns) == {"vectorizer", "classifier", "accuracy", "macro_f1"}
    assert len(results) == 6
    assert results["macro_f1"].is_monotonic_decreasing
    assert results["macro_f1"].max() > 0.8


def test_best_candidate_picks_the_top_row():
    texts, labels = _dataset()
    results = ts.cross_validate_models(texts, labels)

    best = ts.best_candidate(results)

    assert best["macro_f1"] == results["macro_f1"].max()


def test_train_final_model_is_calibrated():
    texts, labels = _dataset()

    model = ts.train_final_model(texts, labels)

    assert hasattr(model, "predict_proba")
    assert model.predict_proba(["great service"]).shape[1] == 3


def test_save_model_and_metrics(tmp_path):
    texts, labels = _dataset()
    model = ts.train_final_model(texts, labels)

    model_path = ts.save_model(model, tmp_path / "model.joblib")
    metrics_path = ts.save_metrics({"accuracy": 0.9}, tmp_path / "metrics.json")

    assert model_path.exists()
    assert json.loads(metrics_path.read_text(encoding="utf-8"))["accuracy"] == 0.9
