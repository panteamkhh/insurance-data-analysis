"""Lightweight text preprocessing shared by the sentiment and word modules.

The functions are intentionally dependency-light (no NLTK corpora to download)
so the pipeline runs offline and reproducibly. Stop words come from
scikit-learn's built-in English list.
"""

import re

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Words that carry no signal for word clouds but are very common in feedback.
DOMAIN_STOPWORDS = frozenset(
    {
        "insurance",
        "insurances",
        "policy",
        "policies",
        "company",
        "customer",
        "customers",
        "really",
        "quite",
        "also",
        "would",
        "could",
        "get",
        "got",
    }
)

STOPWORDS = frozenset(ENGLISH_STOP_WORDS)

_TOKEN_RE = re.compile(r"[a-z]+")
_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Lowercase, drop punctuation/digits and collapse whitespace."""
    text = str(text).lower().replace("'", " ")
    text = re.sub(r"[^a-z\s]", " ", text)
    return _WHITESPACE_RE.sub(" ", text).strip()


def tokenize(text: str, min_length: int = 2) -> list[str]:
    """Split normalised text into tokens of at least ``min_length`` letters."""
    return [token for token in normalize_text(text).split() if len(token) >= min_length]


def remove_stopwords(tokens, stopwords=None) -> list[str]:
    """Filter stop words from a token list."""
    stop_set = STOPWORDS if stopwords is None else stopwords
    return [token for token in tokens if token not in stop_set]


def preprocess(text: str, remove_stops: bool = True, min_length: int = 2) -> list[str]:
    """Normalise, tokenize and optionally remove stop words."""
    tokens = tokenize(text, min_length=min_length)
    if remove_stops:
        tokens = remove_stopwords(tokens)
    return tokens


def preprocess_to_string(text: str, remove_stops: bool = True, min_length: int = 2) -> str:
    """Convenience wrapper returning the cleaned text as a single string."""
    return " ".join(preprocess(text, remove_stops=remove_stops, min_length=min_length))


def preprocess_series(
    series: pd.Series, remove_stops: bool = True, min_length: int = 2
) -> pd.Series:
    """Apply :func:`preprocess_to_string` to every row of a Series."""
    return series.astype(str).map(
        lambda text: preprocess_to_string(text, remove_stops=remove_stops, min_length=min_length)
    )
