# Data dictionary

The source file `data/insurance_data.csv` contains one row per policy, with an
embedded claim record. It is a **synthetic sample** used for demonstration.

## Source columns

| Column | Type | Meaning | Used for |
| --- | --- | --- | --- |
| `PolicyNumber` | text | Unique policy identifier | Counting the portfolio, de-duplication |
| `CustomerID` | text | Customer identifier | Counting unique customers |
| `Gender` | category | `Male` / `Female` | Gender segmentation |
| `Age` | integer | Customer age at policy start | Age-band segmentation |
| `PolicyType` | category | `Auto`, `Travel`, `Health`, `Life`, `Home` | Product-line analysis |
| `PolicyStartDate` | date | When cover begins (`DD-MM-YYYY`) | Time trends, claim lag |
| `PolicyEndDate` | date | When cover ends (`DD-MM-YYYY`) | Policy duration, validation |
| `PremiumAmount` | float | Premium paid by the customer | Revenue, loss ratio |
| `CoverageAmount` | float | Maximum amount the policy pays out | Exposure, pricing check |
| `ClaimNumber` | text | Unique claim identifier | Counting claims |
| `ClaimDate` | date | When the claim was filed (empty for rejected claims) | Claim lag, claim trends |
| `ClaimAmount` | float | Amount claimed (`0` for rejected claims) | Payouts, severity, loss ratio |
| `ClaimStatus` | category | `Settled`, `Pending` or `Rejected` | Claim outcomes, loss ratio |

## Derived columns

Added by `src/feature_engineering.py`:

| Column | Definition |
| --- | --- |
| `PolicyYear` / `PolicyMonth` / `PolicyQuarter` | Calendar parts of `PolicyStartDate` |
| `PolicyDurationDays` | `PolicyEndDate - PolicyStartDate` in days |
| `AgeBand` | `18-25`, `26-35`, `36-45`, `46-55`, `56-65`, `65+` |
| `IsSettled` / `IsPending` / `IsRejected` | Boolean claim-status flags |
| `HasValidClaim` | `True` when the claim is settled or pending (not rejected) |
| `CoverageToPremiumRatio` | `CoverageAmount / PremiumAmount` |
| `ClaimToPremiumRatio` | `ClaimAmount / PremiumAmount` |
| `ClaimToCoverageRatio` | `ClaimAmount / CoverageAmount` |
| `ClaimLagDays` | `ClaimDate - PolicyStartDate` in days |

## Business rules applied during cleaning

- Exact duplicate rows are dropped.
- Text fields are stripped of surrounding whitespace.
- Dates are parsed day-first; unparseable values become missing.
- Policies must start before they end.
- A dated claim must fall inside its policy window.
- Negative amounts are not allowed.

See `src/data_cleaning.py` for the implementation and `docs/original_column_notes.docx`
for the original (Persian) column notes.
