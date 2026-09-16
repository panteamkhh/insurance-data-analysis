"""Tests for text preprocessing."""

from src.text_preprocessing import (
    DOMAIN_STOPWORDS,
    normalize_text,
    preprocess,
    preprocess_series,
    preprocess_to_string,
    remove_stopwords,
    tokenize,
)


def test_normalize_text_lowercases_and_strips_punctuation():
    assert normalize_text("Great VALUE, really!!") == "great value really"


def test_normalize_text_handles_apostrophes():
    assert normalize_text("Don't stop") == "don t stop"


def test_tokenize_drops_short_tokens():
    assert tokenize("I am a good policy holder") == ["am", "good", "policy", "holder"]


def test_remove_stopwords_removes_common_words():
    tokens = ["the", "service", "was", "great"]
    assert remove_stopwords(tokens) == ["service", "great"]


def test_preprocess_removes_stopwords_by_default():
    assert preprocess("The service was very good") == ["service", "good"]


def test_preprocess_can_keep_stopwords():
    result = preprocess("The service was good", remove_stops=False)
    assert "was" in result


def test_preprocess_to_string_roundtrip():
    assert preprocess_to_string("Excellent service!") == "excellent service"


def test_preprocess_series_returns_series():
    import pandas as pd

    series = pd.Series(["The service was great", "Bad claim handling"])
    result = preprocess_series(series)
    assert isinstance(result, pd.Series)
    assert result.iloc[0] == "service great"


def test_domain_stopwords_are_defined():
    assert "insurance" in DOMAIN_STOPWORDS
