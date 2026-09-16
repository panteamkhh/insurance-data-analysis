"""Tests for word-frequency analysis and word clouds."""

import pandas as pd

from src.text_preprocessing import DOMAIN_STOPWORDS
from src.word_analysis import (
    build_wordcloud,
    plot_top_words,
    plot_wordcloud,
    top_words,
    word_frequencies,
)


def test_word_frequencies_counts_and_sorts():
    texts = pd.Series(["great service great", "great value"])
    frequencies = word_frequencies(texts)

    assert frequencies.index[0] == "great"
    assert frequencies["great"] == 3
    assert frequencies["service"] == 1


def test_word_frequencies_removes_stopwords():
    frequencies = word_frequencies(pd.Series(["the service was very good"]))
    assert "the" not in frequencies.index
    assert "service" in frequencies.index


def test_word_frequencies_extra_stopwords():
    frequencies = word_frequencies(pd.Series(["policy service"]), extra_stopwords=DOMAIN_STOPWORDS)
    assert "policy" not in frequencies.index
    assert "service" in frequencies.index


def test_word_frequencies_empty_input():
    frequencies = word_frequencies(pd.Series(["the and of"]))
    assert frequencies.empty


def test_top_words_limits_results():
    texts = pd.Series(["alpha beta gamma delta epsilon"])
    assert len(top_words(texts, n=3)) == 3


def test_build_wordcloud_returns_cloud():
    frequencies = word_frequencies(pd.Series(["excellent service", "great service"]))
    cloud = build_wordcloud(frequencies)
    assert cloud.words_


def test_plot_wordcloud_writes_file(tmp_path):
    frequencies = word_frequencies(pd.Series(["excellent service", "great service"]))
    fig = plot_wordcloud(frequencies, "cloud.png", "Cloud", directory=tmp_path)
    assert (tmp_path / "cloud.png").exists()
    assert fig is not None


def test_plot_top_words_writes_file(tmp_path):
    frequencies = word_frequencies(pd.Series(["excellent service", "great service"]))
    plot_top_words(frequencies, "top.png", "Top words", directory=tmp_path)
    assert (tmp_path / "top.png").exists()
