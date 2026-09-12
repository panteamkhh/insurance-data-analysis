"""Tests for the business-question analysis functions."""

import pytest

from src import analysis


def test_portfolio_summary(sample_df):
    summary = analysis.portfolio_summary(sample_df)
    assert summary["Policies"] == 4
    assert summary["Customers"] == 4
    assert summary["Total Premium"] == pytest.approx(1000.0)
    assert summary["Total Coverage"] == pytest.approx(100000.0)
    assert summary["Settled Claims"] == 2
    assert summary["Pending Claims"] == 1
    assert summary["Rejected Claims"] == 1
    assert summary["Settled Payout"] == pytest.approx(1500.0)
    assert summary["Loss Ratio %"] == pytest.approx(150.0)


def test_premium_and_coverage_by_policy_type(sample_df):
    result = analysis.premium_and_coverage_by_policy_type(sample_df)
    assert list(result.index) == ["Health", "Travel", "Auto"]
    assert result.loc["Health", "Policies"] == 2
    assert result.loc["Health", "TotalPremium"] == pytest.approx(500.0)


def test_loss_ratio_by_policy_type(sample_df):
    result = analysis.loss_ratio_by_policy_type(sample_df)
    assert result.loc["Health", "Loss Ratio %"] == pytest.approx(300.0)
    assert result.loc["Auto", "Loss Ratio %"] == pytest.approx(0.0)


def test_claim_status_distribution(sample_df):
    result = analysis.claim_status_distribution(sample_df)
    assert result["Settled"] == 2
    assert result["Pending"] == 1
    assert result["Rejected"] == 1


def test_claim_outcomes_by_policy_type(sample_df):
    result = analysis.claim_outcomes_by_policy_type(sample_df)
    assert result.loc["Health", "Settled"] == 2
    assert result.loc["Health", "Settled %"] == pytest.approx(100.0)


def test_claims_by_gender(sample_df):
    result = analysis.claims_by_gender(sample_df)
    assert result.loc["Male", "TotalPremium"] == pytest.approx(400.0)
    assert result.loc["Female", "TotalPremium"] == pytest.approx(600.0)


def test_age_band_analysis_covers_all_policies(sample_df):
    result = analysis.age_band_analysis(sample_df)
    assert result["Policies"].sum() == 4


def test_policies_over_time_returns_monthly_series(sample_df):
    result = analysis.policies_over_time(sample_df)
    assert result.sum() == 4


def test_claims_over_time_returns_settled_payout(sample_df):
    result = analysis.claims_over_time(sample_df)
    assert result.sum() == pytest.approx(1500.0)


def test_claim_severity_by_policy_type(sample_df):
    result = analysis.claim_severity_by_policy_type(sample_df)
    assert result.loc["Health", "Claims"] == 2
    assert result.loc["Health", "Mean"] == pytest.approx(750.0)


def test_premium_coverage_correlation_is_defined(sample_df):
    assert analysis.premium_coverage_correlation(sample_df) == pytest.approx(1.0)
