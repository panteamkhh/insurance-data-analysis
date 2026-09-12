"""Tests for derived columns."""

import pandas as pd


def test_derived_columns_exist(sample_df):
    expected = {
        "PolicyYear",
        "PolicyMonth",
        "PolicyQuarter",
        "PolicyDurationDays",
        "AgeBand",
        "IsSettled",
        "IsPending",
        "IsRejected",
        "HasValidClaim",
        "CoverageToPremiumRatio",
        "ClaimToPremiumRatio",
        "ClaimToCoverageRatio",
        "ClaimLagDays",
    }
    assert expected.issubset(sample_df.columns)


def test_has_valid_claim_flag(sample_df):
    assert sample_df["HasValidClaim"].sum() == 3


def test_policy_duration_is_one_year(sample_df):
    assert (sample_df["PolicyDurationDays"] == 366).all()


def test_claim_lag_days(sample_df):
    lag = sample_df.set_index("PolicyNumber")["ClaimLagDays"]
    assert lag["P1"] == 60
    assert pd.isna(lag["P3"])


def test_coverage_to_premium_ratio(sample_df):
    ratio = sample_df.set_index("PolicyNumber")["CoverageToPremiumRatio"]
    assert ratio["P1"] == 100.0
    assert ratio["P4"] == 100.0


def test_age_band_assignment(sample_df):
    bands = sample_df.set_index("PolicyNumber")["AgeBand"]
    assert str(bands["P1"]) == "26-35"
    assert str(bands["P4"]) == "56-65"
