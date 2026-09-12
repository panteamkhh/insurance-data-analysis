"""One function per business question.

Each function takes the analyzed table (see
``feature_engineering.compute_derived_columns``) and returns plain pandas
objects -- Series / DataFrame. Rendering lives in ``visualization.py`` so the
calculations stay independent of matplotlib.

Questions covered
-----------------
Q1  Portfolio overview: policies, customers, premium, coverage, claim payout.
Q2  How do premium and coverage split across policy types?
Q3  What is the fate of claims for each policy type?
Q4  Which lines are unprofitable? (loss ratio by policy type)
Q5  What is the overall claim-status mix?
Q6  Do men and women claim differently?
Q7  How does age relate to premium and claims?
Q8  How is the book growing over time?
Q9  How large are claims, once they are paid?
Q10 Is coverage priced proportionally to premium?
"""

import pandas as pd


# Q1 -----------------------------------------------------------------
def portfolio_summary(df: pd.DataFrame) -> pd.Series:
    """Headline KPIs for the whole book of business."""
    total_premium = df["PremiumAmount"].sum()
    settled_amount = df.loc[df["IsSettled"], "ClaimAmount"].sum()
    return pd.Series(
        {
            "Policies": int(df["PolicyNumber"].nunique()),
            "Customers": int(df["CustomerID"].nunique()),
            "Total Premium": round(total_premium, 2),
            "Total Coverage": round(df["CoverageAmount"].sum(), 2),
            "Settled Claims": int(df["IsSettled"].sum()),
            "Pending Claims": int(df["IsPending"].sum()),
            "Rejected Claims": int(df["IsRejected"].sum()),
            "Settled Payout": round(settled_amount, 2),
            "Pending Payout": round(df.loc[df["IsPending"], "ClaimAmount"].sum(), 2),
            "Loss Ratio %": (
                round(settled_amount / total_premium * 100, 1) if total_premium else 0.0
            ),
        },
        dtype="object",
    )


# Q2 -----------------------------------------------------------------
def premium_and_coverage_by_policy_type(df: pd.DataFrame) -> pd.DataFrame:
    """Premium and coverage split by policy type, richest line first."""
    grouped = (
        df.groupby("PolicyType")
        .agg(
            Policies=("PolicyNumber", "nunique"),
            TotalPremium=("PremiumAmount", "sum"),
            AvgPremium=("PremiumAmount", "mean"),
            TotalCoverage=("CoverageAmount", "sum"),
            AvgCoverage=("CoverageAmount", "mean"),
        )
        .sort_values("TotalPremium", ascending=False)
    )
    grouped["AvgCoverageToPremium"] = (grouped["AvgCoverage"] / grouped["AvgPremium"]).round(1)
    return grouped.round(2)


# Q3 -----------------------------------------------------------------
def claim_outcomes_by_policy_type(df: pd.DataFrame) -> pd.DataFrame:
    """Settled / pending / rejected counts and rates per policy type."""
    counts = pd.crosstab(df["PolicyType"], df["ClaimStatus"])
    for status in ("Settled", "Pending", "Rejected"):
        if status not in counts.columns:
            counts[status] = 0
    counts = counts[["Settled", "Pending", "Rejected"]]
    rates = counts.div(counts.sum(axis=1), axis=0).mul(100).round(1)
    rates.columns = [f"{column} %" for column in rates.columns]
    result = counts.join(rates)
    return result.sort_values("Settled", ascending=False)


# Q4 -----------------------------------------------------------------
def loss_ratio_by_policy_type(df: pd.DataFrame) -> pd.DataFrame:
    """Premium collected vs. money paid out, per policy type.

    The loss ratio is ``settled payout / premium``; pending claims are
    excluded because they have not been paid yet.
    """
    premium = df.groupby("PolicyType")["PremiumAmount"].sum()
    settled = df.loc[df["IsSettled"]].groupby("PolicyType")["ClaimAmount"].sum()
    result = pd.DataFrame({"Premium": premium, "Settled Payout": settled}).fillna(0.0)
    result["Loss Ratio %"] = result["Settled Payout"] / result["Premium"].replace(0, pd.NA) * 100
    result = result.round(2)
    return result.sort_values("Loss Ratio %", ascending=False)


# Q5 -----------------------------------------------------------------
def claim_status_distribution(df: pd.DataFrame) -> pd.Series:
    """Number of claims in each status, largest first."""
    return df["ClaimStatus"].value_counts()


# Q6 -----------------------------------------------------------------
def claims_by_gender(df: pd.DataFrame) -> pd.DataFrame:
    """Premium and claim behaviour split by customer gender."""
    grouped = df.groupby("Gender").agg(
        Policies=("PolicyNumber", "nunique"),
        TotalPremium=("PremiumAmount", "sum"),
        AvgPremium=("PremiumAmount", "mean"),
        ValidClaimRate=("HasValidClaim", "mean"),
    )
    settled = df.loc[df["IsSettled"]].groupby("Gender")["ClaimAmount"].sum()
    grouped["SettledPayout"] = settled.reindex(grouped.index).fillna(0.0)
    grouped["ValidClaimRate"] = (grouped["ValidClaimRate"] * 100).round(1)
    grouped["Loss Ratio %"] = (
        grouped["SettledPayout"] / grouped["TotalPremium"].replace(0, pd.NA) * 100
    ).round(1)
    return grouped.round(2)


# Q7 -----------------------------------------------------------------
def age_band_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Premium, claim frequency and claim size across age bands."""
    grouped = df.groupby("AgeBand", observed=True).agg(
        Policies=("PolicyNumber", "nunique"),
        AvgPremium=("PremiumAmount", "mean"),
        ValidClaimRate=("HasValidClaim", "mean"),
    )
    settled = df.loc[df["IsSettled"]].groupby("AgeBand", observed=True)["ClaimAmount"].sum()
    premiums = df.groupby("AgeBand", observed=True)["PremiumAmount"].sum()
    grouped["SettledPayout"] = settled.reindex(grouped.index).fillna(0.0)
    grouped["ValidClaimRate"] = (grouped["ValidClaimRate"] * 100).round(1)
    grouped["Loss Ratio %"] = (
        grouped["SettledPayout"] / premiums.reindex(grouped.index).replace(0, pd.NA) * 100
    ).round(1)
    return grouped.round(2)


# Q8 -----------------------------------------------------------------
def policies_over_time(df: pd.DataFrame, freq: str = "ME") -> pd.Series:
    """Policies started per period (``freq`` uses pandas offset aliases)."""
    series = df.set_index("PolicyStartDate")["PolicyNumber"].resample(freq).nunique()
    return series[series.index.notna()]


def claims_over_time(df: pd.DataFrame, freq: str = "ME") -> pd.Series:
    """Settled payout and claim count per period, keyed by claim date."""
    claims = df.loc[df["IsSettled"]].set_index("ClaimDate")
    payouts = claims["ClaimAmount"].resample(freq).sum()
    return payouts[payouts.index.notna()]


# Q9 -----------------------------------------------------------------
def claim_severity_by_policy_type(df: pd.DataFrame) -> pd.DataFrame:
    """Distribution of paid claim amounts, per policy type."""
    settled = df.loc[df["IsSettled"]]
    result = settled.groupby("PolicyType")["ClaimAmount"].agg(
        Claims="count",
        Mean="mean",
        Median="median",
        P90=lambda s: s.quantile(0.90),
        Max="max",
    )
    return result.round(2).sort_values("Mean", ascending=False)


# Q10 ----------------------------------------------------------------
def premium_coverage_correlation(df: pd.DataFrame) -> float:
    """Pearson correlation between premium and coverage."""
    return df["PremiumAmount"].corr(df["CoverageAmount"])


def claim_lag_summary(df: pd.DataFrame) -> pd.Series:
    """Summary of the days between a policy starting and a claim being filed."""
    return df["ClaimLagDays"].describe().round(1)
