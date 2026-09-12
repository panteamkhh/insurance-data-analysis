"""Tests for cleaning and validation."""

import pandas as pd

from src.data_cleaning import clean_data, validate_data


def test_clean_data_drops_exact_duplicates(raw_df):
    cleaned = clean_data(raw_df)
    assert len(cleaned) == 4
    assert cleaned["PolicyNumber"].is_unique


def test_clean_data_parses_dates(raw_df):
    cleaned = clean_data(raw_df)
    assert pd.api.types.is_datetime64_any_dtype(cleaned["PolicyStartDate"])
    assert cleaned["PolicyStartDate"].iloc[0] == pd.Timestamp("2024-01-01")


def test_clean_data_normalises_rejected_claim_amount(raw_df):
    cleaned = clean_data(raw_df)
    rejected = cleaned.loc[cleaned["ClaimStatus"] == "Rejected"]
    assert rejected["ClaimAmount"].iloc[0] == 0.0


def test_validate_data_keeps_valid_rows(raw_df):
    cleaned = clean_data(raw_df)
    validated = validate_data(cleaned)
    assert len(validated) == 4


def test_validate_data_drops_claim_outside_policy_window(raw_df):
    cleaned = clean_data(raw_df)
    cleaned.loc[0, "ClaimDate"] = pd.Timestamp("2026-01-01")  # after policy end

    validated = validate_data(cleaned)

    assert "P1" not in validated["PolicyNumber"].tolist()


def test_validate_data_drops_inverted_policy_dates(raw_df):
    cleaned = clean_data(raw_df)
    cleaned.loc[1, "PolicyEndDate"] = cleaned.loc[1, "PolicyStartDate"] - pd.Timedelta(days=1)

    validated = validate_data(cleaned)

    assert "P2" not in validated["PolicyNumber"].tolist()
