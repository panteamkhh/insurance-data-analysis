"""Reads and validates the raw insurance CSV.

The loader is intentionally strict: a missing or renamed column should fail
loudly at load time rather than surface later as a confusing ``KeyError``
halfway through the analysis.
"""

import os

import pandas as pd

from .config import DATA_FILE

REQUIRED_COLUMNS = [
    "PolicyNumber",
    "CustomerID",
    "Gender",
    "Age",
    "PolicyType",
    "PolicyStartDate",
    "PolicyEndDate",
    "PremiumAmount",
    "CoverageAmount",
    "ClaimNumber",
    "ClaimDate",
    "ClaimAmount",
    "ClaimStatus",
]


def load_data(filepath: str | os.PathLike | None = None) -> pd.DataFrame:
    """Load the raw insurance CSV and return only the expected columns.

    Parameters
    ----------
    filepath:
        Path to the source CSV. Defaults to ``data/insurance_data.csv``.
    """
    path = os.fspath(DATA_FILE if filepath is None else filepath)
    raw = pd.read_csv(path)

    missing = [column for column in REQUIRED_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(
            f"Missing required column(s) {missing} in '{path}'. "
            f"Found columns: {list(raw.columns)}"
        )

    return raw[REQUIRED_COLUMNS].copy()
