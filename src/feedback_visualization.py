"""Charts for the customer-feedback sentiment analysis.

Uses the shared dark theme and the label colours defined in :mod:`src.theme`.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from .config import EXCELLENT_MIN_SCORE, GOOD_MIN_SCORE
from .theme import GOLD, LABEL_COLORS, MUTED, TEXT, save_figure

LABEL_ORDER = ["Excellent", "Good", "Needs Improvement"]


def plot_sentiment_distribution(
    labels: pd.Series,
    filename: str = "feedback_01_sentiment_distribution.png",
    directory=None,
):
    """Bar chart of how many reviews fall into each sentiment label."""
    counts = labels.value_counts().reindex(LABEL_ORDER).fillna(0).astype(int)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(counts.index, counts.values, color=[LABEL_COLORS[label] for label in counts.index])
    ax.set_title("Customer Sentiment Distribution")
    ax.set_ylabel("Reviews")
    ax.grid(axis="x", visible=False)
    for index, value in enumerate(counts.values):
        ax.text(index, value, str(value), ha="center", va="bottom", color=TEXT)
    fig.tight_layout()
    save_figure(fig, filename, directory=directory)
    return fig


def plot_score_histogram(
    scores: pd.Series,
    filename: str = "feedback_02_score_histogram.png",
    directory=None,
    bins: int = 20,
):
    """Histogram of sentiment scores with the label thresholds marked."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(scores.dropna(), bins=bins, color=GOLD, edgecolor="#1b1b1b")
    ax.axvline(GOOD_MIN_SCORE, color=MUTED, linestyle="--", linewidth=1, label="Good threshold")
    ax.axvline(
        EXCELLENT_MIN_SCORE, color=TEXT, linestyle="--", linewidth=1, label="Excellent threshold"
    )
    ax.set_title("Sentiment Score Distribution")
    ax.set_xlabel("Sentiment score (0-1)")
    ax.set_ylabel("Reviews")
    ax.grid(axis="x", visible=False)
    ax.legend()
    fig.tight_layout()
    save_figure(fig, filename, directory=directory)
    return fig


def plot_score_by_label(
    scored: pd.DataFrame,
    filename: str = "feedback_03_score_by_label.png",
    directory=None,
):
    """Box plot of the score distribution within each sentiment label."""
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.boxplot(
        data=scored,
        x="sentiment_label",
        y="sentiment_score",
        order=LABEL_ORDER,
        hue="sentiment_label",
        palette=LABEL_COLORS,
        legend=False,
        ax=ax,
    )
    ax.set_title("Sentiment Score by Label")
    ax.set_xlabel("")
    ax.set_ylabel("Sentiment score (0-1)")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    save_figure(fig, filename, directory=directory)
    return fig
