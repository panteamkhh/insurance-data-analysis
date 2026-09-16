"""Word-frequency analysis and dark-theme word clouds for customer feedback.

The word clouds use the same dark background and gold/teal accents as the rest
of the project. ``plot_wordcloud`` and ``plot_top_words`` save a PNG and return
the figure so they also render inline in the notebook.
"""

from __future__ import annotations

from collections import Counter

import matplotlib.pyplot as plt
import pandas as pd
from wordcloud import WordCloud

from .config import RANDOM_SEED
from .text_preprocessing import STOPWORDS, preprocess
from .theme import AMBER, BACKGROUND, GOLD, GREEN, TEAL, save_figure

CLOUD_COLORS = [GOLD, TEAL, GREEN, AMBER, "#f5e6a8", "#8ecae6", "#ffffff"]


def _color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    """Deterministic colour assignment so word clouds are reproducible."""
    return CLOUD_COLORS[sum(map(ord, word)) % len(CLOUD_COLORS)]


def word_frequencies(
    texts,
    stopwords=None,
    extra_stopwords=None,
    min_length: int = 2,
) -> pd.Series:
    """Count words across ``texts``, most frequent first.

    Stop words are removed. Pass ``extra_stopwords`` (e.g.
    ``DOMAIN_STOPWORDS``) to also drop generic domain words.
    """
    stop_set = set(STOPWORDS if stopwords is None else stopwords)
    if extra_stopwords:
        stop_set |= set(extra_stopwords)

    counter: Counter[str] = Counter()
    for text in pd.Series(texts).astype(str):
        counter.update(
            token
            for token in preprocess(text, remove_stops=False, min_length=min_length)
            if token not in stop_set
        )

    if not counter:
        return pd.Series(dtype="int64")
    return pd.Series(counter, dtype="int64").sort_values(ascending=False)


def top_words(texts, n: int = 20, **kwargs) -> pd.Series:
    """Return the ``n`` most common words."""
    return word_frequencies(texts, **kwargs).head(n)


def build_wordcloud(
    frequencies: pd.Series,
    width: int = 1200,
    height: int = 600,
    max_words: int = 150,
    background: str = BACKGROUND,
) -> WordCloud:
    """Build a :class:`~wordcloud.WordCloud` from a frequency Series."""
    if len(frequencies) == 0:
        raise ValueError("Cannot build a word cloud from an empty frequency table.")

    cloud = WordCloud(
        width=width,
        height=height,
        background_color=background,
        color_func=_color_func,
        prefer_horizontal=0.95,
        max_words=max_words,
        margin=2,
        random_state=RANDOM_SEED,
    )
    return cloud.generate_from_frequencies({str(k): float(v) for k, v in frequencies.items()})


def plot_wordcloud(
    frequencies: pd.Series,
    filename: str,
    title: str,
    width: int = 1200,
    height: int = 600,
    max_words: int = 150,
    directory=None,
):
    """Render and save a word cloud, returning the figure."""
    cloud = build_wordcloud(frequencies, width=width, height=height, max_words=max_words)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(cloud, interpolation="bilinear")
    ax.axis("off")
    ax.set_title(title)
    fig.tight_layout()
    save_figure(fig, filename, directory=directory)
    return fig


def plot_top_words(frequencies: pd.Series, filename: str, title: str, n: int = 20, directory=None):
    """Render and save a horizontal bar chart of the top words, returning the figure."""
    top = frequencies.head(n).sort_values()
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top.index, top.values, color=GOLD)
    ax.set_title(title)
    ax.set_xlabel("Frequency")
    ax.grid(axis="y", visible=False)
    fig.tight_layout()
    save_figure(fig, filename, directory=directory)
    return fig
