"""Derives analytical columns from the cleaned insurance data.

The raw file only holds policy dates, amounts and a claim status. Everything
this project actually reports on -- age bands, claim lag, loss ratios, claim
outcomes -- is derived here so the analysis functions stay declarative.
"""

import numpy as np
import pandas as pd

from .config import AGE_BINS, AGE_LABELS


def compute_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add the derived columns used throughout the analysis."""
    df = df.copy()

    # --- time dimensions ------------------------------------------------
    df["PolicyYear"] = df["PolicyStartDate"].dt.year
    df["PolicyMonth"] = df["PolicyStartDate"].dt.to_period("M").astype(str)
    df["PolicyQuarter"] = df["PolicyStartDate"].dt.to_period("Q").astype(str)
    df["PolicyDurationDays"] = (df["PolicyEndDate"] - df["PolicyStartDate"]).dt.days

    # --- customer segments ---------------------------------------------
    df["AgeBand"] = pd.cut(df["Age"], bins=AGE_BINS, labels=AGE_LABELS, right=True)

    # --- claim outcomes -------------------------------------------------
    df["IsSettled"] = df["ClaimStatus"] == "Settled"
    df["IsPending"] = df["ClaimStatus"] == "Pending"
    df["IsRejected"] = df["ClaimStatus"] == "Rejected"
    # A "valid" claim was accepted or is still open; rejected claims are not.
    df["HasValidClaim"] = df["IsSettled"] | df["IsPending"]

    # --- ratios and lags ------------------------------------------------
    df["CoverageToPremiumRatio"] = df["CoverageAmount"] / df["PremiumAmount"].replace(0, np.nan)
    df["ClaimToPremiumRatio"] = df["ClaimAmount"] / df["PremiumAmount"].replace(0, np.nan)
    df["ClaimToCoverageRatio"] = df["ClaimAmount"] / df["CoverageAmount"].replace(0, np.nan)
    df["ClaimLagDays"] = (df["ClaimDate"] - df["PolicyStartDate"]).dt.days

    return df


def build_analysis_table(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper: clean is expected to have run, derive here."""
    return compute_derived_columns(df)
