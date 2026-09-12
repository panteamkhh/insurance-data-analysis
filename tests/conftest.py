"""Shared pytest fixtures: a small deterministic insurance dataset."""

import pandas as pd
import pytest

from src.data_cleaning import clean_data
from src.feature_engineering import compute_derived_columns


@pytest.fixture
def raw_df() -> pd.DataFrame:
    """Four clean policies plus one exact duplicate row."""
    rows = [
        # Policy, Customer, Gender, Age, Type, start, end, premium, coverage,
        # ClaimNumber, ClaimDate, ClaimAmount, Status
        [
            "P1",
            "C1",
            "Male",
            30,
            "Health",
            "01-01-2024",
            "01-01-2025",
            100.0,
            10000.0,
            "CL1",
            "01-03-2024",
            500.0,
            "Settled",
        ],
        [
            "P2",
            "C2",
            "Female",
            40,
            "Auto",
            "01-01-2024",
            "01-01-2025",
            200.0,
            20000.0,
            "CL2",
            None,
            300.0,
            "Pending",
        ],
        [
            "P3",
            "C3",
            "Male",
            50,
            "Travel",
            "01-01-2024",
            "01-01-2025",
            300.0,
            30000.0,
            "CL3",
            None,
            0.0,
            "Rejected",
        ],
        [
            "P4",
            "C4",
            "Female",
            60,
            "Health",
            "01-01-2024",
            "01-01-2025",
            400.0,
            40000.0,
            "CL4",
            "01-04-2024",
            1000.0,
            "Settled",
        ],
        [
            "P4",
            "C4",
            "Female",
            60,
            "Health",
            "01-01-2024",
            "01-01-2025",
            400.0,
            40000.0,
            "CL4",
            "01-04-2024",
            1000.0,
            "Settled",
        ],
    ]
    columns = [
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
    return pd.DataFrame(rows, columns=columns)


@pytest.fixture
def sample_df(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Cleaned + derived version of :func:`raw_df` (4 unique policies)."""
    return compute_derived_columns(clean_data(raw_df))
