"""End-to-end customer-feedback runner: load -> score -> label -> words -> export.

Usage::

    python -m src.run_feedback_analysis
    python -m src.run_feedback_analysis --scorer transformer
    python -m src.run_feedback_analysis --input data/customer_feedback.csv --no-export
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import FEEDBACK_FILE, OUTPUT_DIR
from .data_loader import load_feedback
from .feedback_visualization import (
    plot_score_by_label,
    plot_score_histogram,
    plot_sentiment_distribution,
)
from .sentiment import (
    LexiconSentimentScorer,
    SklearnSentimentScorer,
    TransformerSentimentScorer,
    add_sentiment_columns,
    get_default_scorer,
)
from .word_analysis import plot_top_words, plot_wordcloud, word_frequencies

POSITIVE_LABELS = ("Excellent", "Good")
NEGATIVE_LABELS = ("Needs Improvement",)


def resolve_scorer(name: str = "auto"):
    """Return a sentiment scorer by name, or the best available one for ``auto``."""
    if name == "auto":
        return get_default_scorer()
    if name == "sklearn":
        return SklearnSentimentScorer()
    if name == "transformer":
        return TransformerSentimentScorer()
    if name == "vader":
        return LexiconSentimentScorer()
    raise ValueError(f"Unknown scorer '{name}'.")


def analyze(filepath=FEEDBACK_FILE, scorer=None) -> pd.DataFrame:
    """Load the feedback and add ``sentiment_score`` / ``sentiment_label``."""
    feedback = load_feedback(filepath)
    return add_sentiment_columns(feedback, scorer=scorer)


def run(filepath=FEEDBACK_FILE, output_dir=OUTPUT_DIR, scorer=None, export: bool = True):
    """Score the feedback, render every chart and export the results."""
    scored = analyze(filepath, scorer=scorer)

    plot_sentiment_distribution(scored["sentiment_label"])
    plot_score_histogram(scored["sentiment_score"])
    plot_score_by_label(scored)

    all_words = word_frequencies(scored["Feedback"])
    positive_words = word_frequencies(
        scored.loc[scored["sentiment_label"].isin(POSITIVE_LABELS), "Feedback"]
    )
    negative_words = word_frequencies(
        scored.loc[scored["sentiment_label"].isin(NEGATIVE_LABELS), "Feedback"]
    )

    plot_wordcloud(
        all_words,
        "feedback_04_wordcloud_all.png",
        "Most Common Words in Customer Feedback",
    )
    if len(positive_words):
        plot_wordcloud(
            positive_words, "feedback_05_wordcloud_positive.png", "What Happy Customers Say"
        )
    if len(negative_words):
        plot_wordcloud(
            negative_words, "feedback_06_wordcloud_negative.png", "What Unhappy Customers Say"
        )
    plot_top_words(all_words, "feedback_07_top_words.png", "Top 20 Words in Feedback", n=20)

    if export:
        export_dir = Path(output_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        scored.to_csv(export_dir / "customer_feedback_scored.csv", index=False)
        all_words.to_frame("frequency").to_csv(export_dir / "feedback_word_frequencies.csv")

    counts = scored["sentiment_label"].value_counts()
    print(f"Reviews analysed: {len(scored):,}")
    for label in ("Excellent", "Good", "Needs Improvement"):
        print(f"  {label}: {int(counts.get(label, 0)):,}")
    print(f"Mean sentiment score: {scored['sentiment_score'].mean():.3f}")
    print(f"Top words: {', '.join(all_words.head(8).index)}")
    return scored


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run the customer-feedback analysis end-to-end.")
    parser.add_argument("--input", default=str(FEEDBACK_FILE), help="Path to the feedback CSV")
    parser.add_argument(
        "--output-dir", default=str(OUTPUT_DIR), help="Where to write the CSV exports"
    )
    parser.add_argument(
        "--scorer",
        default="auto",
        choices=["auto", "sklearn", "transformer", "vader"],
        help="Sentiment engine to use (default: auto).",
    )
    parser.add_argument("--no-export", action="store_true", help="Skip writing CSV exports")
    args = parser.parse_args(argv)

    run(
        filepath=args.input,
        output_dir=args.output_dir,
        scorer=resolve_scorer(args.scorer),
        export=not args.no_export,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
