"""Train the distilled sentiment model.

Workflow (knowledge distillation):

1. Label every feedback with the pretrained transformer "teacher"
   (:func:`build_teacher_labels`). If torch is unavailable the VADER lexicon is
   used as a weaker teacher instead.
2. Compare several TF-IDF + linear-model candidates with stratified
   cross-validation (:func:`cross_validate_models`).
3. Refit the best candidate on all data and wrap it in a probability
   calibrator, then persist it to ``models/sentiment_model.joblib``.

Run with::

    python -m src.train_sentiment
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.base import clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.naive_bayes import ComplementNB
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from .config import (
    FEEDBACK_FILE,
    RANDOM_SEED,
    SENTIMENT_METRICS_FILE,
    SENTIMENT_MODEL_FILE,
)
from .data_loader import load_feedback
from .sentiment import (
    LexiconSentimentScorer,
    TransformerSentimentScorer,
    label_series,
    transformer_available,
)

VECTORIZERS = {
    "word": TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english"),
    "char": TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True),
}

CLASSIFIERS = {
    "logreg": LogisticRegression(max_iter=3000, C=4.0, random_state=RANDOM_SEED),
    "linearsvc": LinearSVC(C=1.0, random_state=RANDOM_SEED),
    "complementnb": ComplementNB(),
}


def build_teacher_labels(texts: pd.Series, scorer=None) -> pd.DataFrame:
    """Return ``teacher_score`` and ``teacher_label`` for each feedback text."""
    if scorer is None:
        scorer = (
            TransformerSentimentScorer() if transformer_available() else LexiconSentimentScorer()
        )
    scores = scorer.score(texts)
    return pd.DataFrame(
        {"teacher_score": scores, "teacher_label": label_series(scores)},
        index=pd.Series(texts).index,
    )


def cross_validate_models(texts: pd.Series, labels: pd.Series, cv: int = 5) -> pd.DataFrame:
    """Score every vectorizer/classifier combination with cross-validation."""
    splitter = StratifiedKFold(n_splits=cv, shuffle=True, random_state=RANDOM_SEED)
    rows = []
    for vectorizer_name, vectorizer in VECTORIZERS.items():
        for classifier_name, classifier in CLASSIFIERS.items():
            pipeline = Pipeline([("tfidf", clone(vectorizer)), ("clf", clone(classifier))])
            predictions = cross_val_predict(pipeline, texts, labels, cv=splitter)
            rows.append(
                {
                    "vectorizer": vectorizer_name,
                    "classifier": classifier_name,
                    "accuracy": round(accuracy_score(labels, predictions), 4),
                    "macro_f1": round(f1_score(labels, predictions, average="macro"), 4),
                }
            )
    return pd.DataFrame(rows).sort_values("macro_f1", ascending=False).reset_index(drop=True)


def best_candidate(results: pd.DataFrame) -> dict:
    """Return the highest-scoring candidate as a plain dict."""
    return results.iloc[0].to_dict()


def train_final_model(
    texts: pd.Series,
    labels: pd.Series,
    vectorizer_name: str = "word",
    classifier_name: str = "linearsvc",
):
    """Refit the chosen candidate on all data, wrapped in a probability calibrator."""
    pipeline = Pipeline(
        [
            ("tfidf", clone(VECTORIZERS[vectorizer_name])),
            ("clf", clone(CLASSIFIERS[classifier_name])),
        ]
    )
    folds = max(2, min(5, int(labels.value_counts().min())))
    model = CalibratedClassifierCV(pipeline, method="sigmoid", cv=folds)
    model.fit(texts, labels)
    return model


def save_model(model, path=SENTIMENT_MODEL_FILE) -> Path:
    """Persist the trained model with joblib and return the path."""
    import joblib

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)
    return path


def save_metrics(metrics: dict, path=SENTIMENT_METRICS_FILE) -> Path:
    """Write the training metrics as JSON and return the path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return path


def train(
    filepath=FEEDBACK_FILE,
    model_path=SENTIMENT_MODEL_FILE,
    metrics_path=SENTIMENT_METRICS_FILE,
):
    """Full distillation run: teacher labels -> model selection -> saved model."""
    feedback = load_feedback(filepath)
    texts = feedback["Feedback"]
    teacher = build_teacher_labels(texts)

    results = cross_validate_models(texts, teacher["teacher_label"])
    best = best_candidate(results)
    model = train_final_model(
        texts, teacher["teacher_label"], best["vectorizer"], best["classifier"]
    )
    save_model(model, model_path)

    metrics = {
        "dataset_size": int(len(feedback)),
        "teacher": "transformer" if transformer_available() else "vader",
        "label_counts": {
            str(label): int(count)
            for label, count in teacher["teacher_label"].value_counts().items()
        },
        "candidates": results.to_dict(orient="records"),
        "best": {
            "vectorizer": best["vectorizer"],
            "classifier": best["classifier"],
            "accuracy": float(best["accuracy"]),
            "macro_f1": float(best["macro_f1"]),
        },
    }
    save_metrics(metrics, metrics_path)

    print(results.to_string(index=False))
    print(
        f"Best: {best['vectorizer']} + {best['classifier']} "
        f"(accuracy={best['accuracy']}, macro F1={best['macro_f1']})"
    )
    print(f"Model saved to: {model_path}")
    return model, metrics


def main(argv=None) -> int:
    train()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
