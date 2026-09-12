"""Chart-rendering functions, one per business question.

Every function saves a PNG into ``screenshots/`` (used by the README and the
notebook) and returns the matplotlib ``Figure`` so it also renders inline in
Jupyter.
"""

import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

from .config import SCREENSHOTS_DIR

sns.set_theme(style="whitegrid", palette="viridis")
plt.rcParams["figure.figsize"] = (11, 5)
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.titleweight"] = "bold"

NUMBER_FORMAT = "{x:,.0f}"


def _save(fig, filename: str):
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    fig.savefig(os.path.join(SCREENSHOTS_DIR, filename), dpi=150, bbox_inches="tight")


def _format_number(axis, which: str = "x"):
    formatter = mticker.StrMethodFormatter(NUMBER_FORMAT)
    target = axis.xaxis if which == "x" else axis.yaxis
    target.set_major_formatter(formatter)


# Q2 -----------------------------------------------------------------
def plot_policies_and_premium(by_type):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    sns.barplot(
        x=by_type["Policies"].values,
        y=by_type.index,
        hue=by_type.index,
        legend=False,
        palette="crest",
        ax=axes[0],
    )
    axes[0].set_title("Policies by Type")
    axes[0].set_xlabel("Policies")

    sns.barplot(
        x=by_type["TotalPremium"].values,
        y=by_type.index,
        hue=by_type.index,
        legend=False,
        palette="flare",
        ax=axes[1],
    )
    axes[1].set_title("Total Premium by Type")
    axes[1].set_xlabel("Premium")
    _format_number(axes[1])

    fig.tight_layout()
    _save(fig, "01_policies_and_premium_by_type.png")
    return fig


# Q2 -----------------------------------------------------------------
def plot_premium_and_coverage(by_type):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].barh(by_type.index, by_type["AvgPremium"], color="#2c7fb8")
    axes[0].set_title("Average Premium by Type")
    axes[0].set_xlabel("Average Premium")
    _format_number(axes[0])

    axes[1].barh(by_type.index, by_type["AvgCoverage"], color="#31a354")
    axes[1].set_title("Average Coverage by Type")
    axes[1].set_xlabel("Average Coverage")
    _format_number(axes[1])

    fig.tight_layout()
    _save(fig, "02_premium_and_coverage_by_type.png")
    return fig


# Q3 -----------------------------------------------------------------
def plot_claim_outcomes(by_type):
    rate_columns = [column for column in by_type.columns if column.endswith(" %")]
    rates = by_type[rate_columns].copy()
    rates.columns = [column.replace(" %", "") for column in rate_columns]

    fig, ax = plt.subplots(figsize=(11, 6))
    rates.plot(kind="barh", stacked=True, ax=ax, color=["#2ca25f", "#fec44f", "#de2d26"])
    ax.set_title("Claim Outcome Mix by Policy Type")
    ax.set_xlabel("Share of policies (%)")
    ax.set_ylabel("")
    ax.legend(title="Claim status", loc="lower right")
    fig.tight_layout()
    _save(fig, "03_claim_outcomes_by_type.png")
    return fig


# Q4 -----------------------------------------------------------------
def plot_loss_ratio(loss_ratio):
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(
        x=loss_ratio["Loss Ratio %"].values,
        y=loss_ratio.index,
        hue=loss_ratio.index,
        legend=False,
        palette="rocket_r",
        ax=ax,
    )
    ax.axvline(100, color="black", linestyle="--", linewidth=1, label="Break-even (100%)")
    ax.set_title("Loss Ratio by Policy Type (settled payout / premium)")
    ax.set_xlabel("Loss Ratio (%)")
    ax.legend()
    fig.tight_layout()
    _save(fig, "04_loss_ratio_by_type.png")
    return fig


# Q5 -----------------------------------------------------------------
def plot_claim_status_distribution(status_counts):
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = {"Settled": "#2ca25f", "Pending": "#fec44f", "Rejected": "#de2d26"}
    ax.pie(
        status_counts.values,
        labels=status_counts.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=[colors.get(label, "#888888") for label in status_counts.index],
        wedgeprops={"edgecolor": "white"},
    )
    ax.set_title("Claim Status Distribution")
    fig.tight_layout()
    _save(fig, "05_claim_status_distribution.png")
    return fig


# Q6 -----------------------------------------------------------------
def plot_claims_by_gender(by_gender):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    by_gender["ValidClaimRate"].plot(kind="bar", ax=axes[0], color="#6baed6")
    axes[0].set_title("Accepted Claim Rate by Gender")
    axes[0].set_ylabel("Rate (%)")
    axes[0].tick_params(axis="x", rotation=0)

    by_gender["Loss Ratio %"].plot(kind="bar", ax=axes[1], color="#fd8d3c")
    axes[1].set_title("Loss Ratio by Gender")
    axes[1].set_ylabel("Loss Ratio (%)")
    axes[1].tick_params(axis="x", rotation=0)

    fig.tight_layout()
    _save(fig, "06_claims_by_gender.png")
    return fig


# Q7 -----------------------------------------------------------------
def plot_age_bands(by_age):
    fig, ax = plt.subplots(figsize=(11, 5))
    x = by_age.index.astype(str)

    ax.plot(
        x, by_age["ValidClaimRate"], marker="o", color="#e6550d", label="Accepted claim rate (%)"
    )
    ax.set_ylabel("Accepted claim rate (%)", color="#e6550d")
    ax.tick_params(axis="y", labelcolor="#e6550d")
    ax.set_title("Accepted Claim Rate and Average Premium by Age Band")

    ax2 = ax.twinx()
    ax2.bar(x, by_age["AvgPremium"], alpha=0.3, color="#3182bd", label="Average premium")
    ax2.set_ylabel("Average premium", color="#3182bd")
    ax2.tick_params(axis="y", labelcolor="#3182bd")

    lines, labels = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines + lines2, labels + labels2, loc="upper right")
    ax.set_xlabel("Age band")
    fig.tight_layout()
    _save(fig, "07_age_band_analysis.png")
    return fig


# Q8 -----------------------------------------------------------------
def plot_policies_over_time(policies, claims):
    fig, axes = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    axes[0].plot(policies.index, policies.values, marker="o", color="#2c7fb8")
    axes[0].set_title("Policies Started per Month")
    axes[0].set_ylabel("Policies")

    axes[1].plot(claims.index, claims.values, marker="s", color="#31a354")
    axes[1].set_title("Settled Payout per Month")
    axes[1].set_ylabel("Payout")
    axes[1].tick_params(axis="x", rotation=90)
    _format_number(axes[1], "y")

    fig.tight_layout()
    _save(fig, "08_policies_and_claims_over_time.png")
    return fig


# Q9 -----------------------------------------------------------------
def plot_claim_severity(df):
    settled = df.loc[df["IsSettled"]]
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.boxplot(
        data=settled,
        x="ClaimAmount",
        y="PolicyType",
        hue="PolicyType",
        legend=False,
        palette="mako",
        ax=ax,
    )
    ax.set_title("Paid Claim Amount Distribution by Policy Type")
    ax.set_xlabel("Claim amount")
    _format_number(ax)
    fig.tight_layout()
    _save(fig, "09_claim_severity_by_type.png")
    return fig


# Q10 ----------------------------------------------------------------
def plot_premium_coverage_relationship(df, corr: float):
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.regplot(
        data=df,
        x="PremiumAmount",
        y="CoverageAmount",
        scatter_kws={"alpha": 0.2, "s": 12},
        line_kws={"color": "red"},
        ax=ax,
    )
    ax.set_title(f"Premium vs. Coverage (r = {corr:.2f})")
    ax.set_xlabel("Premium")
    ax.set_ylabel("Coverage")
    _format_number(ax)
    _format_number(ax, "y")
    fig.tight_layout()
    _save(fig, "10_premium_coverage_relationship.png")
    return fig
