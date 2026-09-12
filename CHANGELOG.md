# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-09-12

### Added

- Reusable `src/` package: `config`, `data_loader`, `data_cleaning`,
  `feature_engineering`, `analysis`, `visualization` and `run_analysis`.
- Ten business questions answered end-to-end: portfolio overview, premium and
  coverage by policy type, claim outcomes, loss ratios, status mix, gender and
  age analysis, time trends, claim severity and premium/coverage pricing.
- Ten chart exports written to `screenshots/`.
- Executed Jupyter notebook: `notebooks/Insurance_Data_Analysis.ipynb`.
- pytest suite covering loading, cleaning, validation, feature engineering and
  every analysis function (27 tests).
- Project tooling: `pyproject.toml`, pinned requirements, ruff/black config,
  pre-commit hooks and a GitHub Actions CI workflow.
- Documentation: README, data dictionary and contributing guide.
