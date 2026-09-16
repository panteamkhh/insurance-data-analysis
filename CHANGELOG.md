# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Customer feedback sentiment analysis.** Score and label the 97 customer
  reviews with a machine-learning pipeline:
  - `src/text_preprocessing.py` - offline tokenising and stop-word removal.
  - `src/sentiment.py` - three interchangeable scorers (distilled sklearn model,
    pretrained transformer, VADER lexicon) and the score-to-label mapping.
  - `src/train_sentiment.py` - teacher labelling, cross-validated model
    selection and persistence.
  - `src/word_analysis.py` - word frequencies and dark-theme word clouds.
  - `src/feedback_visualization.py` and `src/run_feedback_analysis.py` -
    sentiment charts and an end-to-end CLI.
- `data/customer_feedback.csv`, `models/sentiment_model.joblib` and
  `models/sentiment_metrics.json` (90% accuracy, 0.86 macro F1 on 5-fold CV).
- Executed notebook `notebooks/Customer_Feedback_Sentiment.ipynb` and
  `docs/sentiment_methodology.md`.
- Shared dark chart theme in `src/theme.py`, reused by every chart.

### Changed

- All charts now use the dark theme that matches the Power BI dashboard.

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
