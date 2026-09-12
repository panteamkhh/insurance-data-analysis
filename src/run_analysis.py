"""End-to-end runner: load -> clean -> validate -> derive -> analyze -> plot -> export.

Usage::

    python -m src.run_analysis
    python -m src.run_analysis --input data/insurance_data.csv --output-dir output
"""

import argparse
from pathlib import Path

import pandas as pd

from . import analysis, visualization
from .config import DATA_FILE, OUTPUT_DIR
from .data_cleaning import clean_data, validate_data
from .data_loader import load_data
from .feature_engineering import compute_derived_columns


def build_analysis_table(filepath=DATA_FILE) -> pd.DataFrame:
    """Run the full load/clean/validate/derive pipeline."""
    raw = load_data(filepath)
    cleaned = clean_data(raw)
    validated = validate_data(cleaned)
    return compute_derived_columns(validated)


def run(filepath=DATA_FILE, output_dir=OUTPUT_DIR, export: bool = True) -> pd.DataFrame:
    """Execute every analysis question and render all charts."""
    df = build_analysis_table(filepath)

    by_type = analysis.premium_and_coverage_by_policy_type(df)
    visualization.plot_policies_and_premium(by_type)
    visualization.plot_premium_and_coverage(by_type)

    outcomes = analysis.claim_outcomes_by_policy_type(df)
    visualization.plot_claim_outcomes(outcomes)

    loss_ratio = analysis.loss_ratio_by_policy_type(df)
    visualization.plot_loss_ratio(loss_ratio)

    visualization.plot_claim_status_distribution(analysis.claim_status_distribution(df))
    visualization.plot_claims_by_gender(analysis.claims_by_gender(df))
    visualization.plot_age_bands(analysis.age_band_analysis(df))

    policies = analysis.policies_over_time(df)
    claims = analysis.claims_over_time(df)
    visualization.plot_policies_over_time(policies, claims)

    visualization.plot_claim_severity(df)
    corr = analysis.premium_coverage_correlation(df)
    visualization.plot_premium_coverage_relationship(df, corr)

    if export:
        export_dir = Path(output_dir)
        export_dir.mkdir(parents=True, exist_ok=True)
        df.to_csv(export_dir / "master_insurance_data.csv", index=False)
        analysis.portfolio_summary(df).to_csv(export_dir / "portfolio_summary.csv")
        by_type.to_csv(export_dir / "premium_by_policy_type.csv")
        loss_ratio.to_csv(export_dir / "loss_ratio_by_policy_type.csv")

    summary = analysis.portfolio_summary(df)
    print(f"Policies: {summary['Policies']:,}")
    print(f"Total premium: {summary['Total Premium']:,.0f}")
    print(f"Loss ratio: {summary['Loss Ratio %']}%")
    print(f"Premium vs. coverage correlation (r): {corr:.3f}")
    print(f"Charts written to: {visualization.SCREENSHOTS_DIR}")
    return df


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run the insurance analysis end-to-end.")
    parser.add_argument("--input", default=str(DATA_FILE), help="Path to the source insurance CSV")
    parser.add_argument(
        "--output-dir", default=str(OUTPUT_DIR), help="Where to write the CSV exports"
    )
    parser.add_argument("--no-export", action="store_true", help="Skip writing CSV exports")
    args = parser.parse_args(argv)

    run(filepath=args.input, output_dir=args.output_dir, export=not args.no_export)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
