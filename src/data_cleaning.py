"""Cleans the raw insurance data.

Responsibilities
----------------
* Drop exact duplicate rows (the source file repeats a handful of policies).
* Strip stray whitespace from text fields.
* Parse the three date columns, which are stored as ``DD-MM-YYYY`` strings.
* Coerce the numeric columns and apply sane defaults for rows without a claim.
"""

import pandas as pd

TEXT_COLUMNS = ("PolicyNumber", "CustomerID", "Gender", "PolicyType", "ClaimNumber", "ClaimStatus")
DATE_COLUMNS = ("PolicyStartDate", "PolicyEndDate", "ClaimDate")
NUMERIC_COLUMNS = ("Age", "PremiumAmount", "CoverageAmount", "ClaimAmount")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy of the raw insurance ``DataFrame``."""
    df = df.copy()

    # 1. Exact duplicate rows carry no extra information.
    df = df.drop_duplicates()

    # 2. Whitespace in categorical/text fields causes silent groupby splits.
    for column in TEXT_COLUMNS:
        if column in df.columns:
            df[column] = df[column].astype(str).str.strip()

    # 3. Dates are day-first; anything unparseable becomes NaT.
    for column in DATE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], format="%d-%m-%Y", errors="coerce")

    # 4. Numeric coercion. Rejected claims have no amount/date, so both are
    #    normalised to 0 / NaT rather than left as junk.
    for column in NUMERIC_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Age"] = df["Age"].astype("Int64")
    df["PremiumAmount"] = df["PremiumAmount"].fillna(0.0)
    df["CoverageAmount"] = df["CoverageAmount"].fillna(0.0)
    df["ClaimAmount"] = df["ClaimAmount"].fillna(0.0)
    df.loc[df["ClaimAmount"] < 0, "ClaimAmount"] = 0.0

    return df.reset_index(drop=True)


def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """Drop rows that violate basic business rules and return the result.

    * A policy must start before it ends.
    * A claim, when dated, must fall inside its policy window.
    * Premium, coverage and claim amounts cannot be negative.
    """
    valid = (
        (df["PolicyStartDate"].notna())
        & (df["PolicyEndDate"].notna())
        & (df["PolicyEndDate"] >= df["PolicyStartDate"])
        & (df["ClaimDate"].isna() | (df["ClaimDate"] >= df["PolicyStartDate"]))
        & (df["ClaimDate"].isna() | (df["ClaimDate"] <= df["PolicyEndDate"]))
        & (df["PremiumAmount"] >= 0)
        & (df["CoverageAmount"] >= 0)
        & (df["ClaimAmount"] >= 0)
    )
    return df.loc[valid].reset_index(drop=True)
