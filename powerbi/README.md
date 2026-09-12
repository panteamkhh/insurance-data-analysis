# Power BI dashboard (work in progress)

This folder holds the interactive Power BI report that complements the Python
analysis in [`../src`](../src).

| File | Description |
| --- | --- |
| `insurance-dashboard.pbix` | Power BI Desktop report (in progress) |
| `screenshots/` | Exported pages of the report, once complete |

The report is built on the same source file used by the Python pipeline:
[`../data/insurance_data.csv`](../data/insurance_data.csv).

Planned pages:

- **Portfolio overview** — total policies, premium, coverage, settled payout and loss ratio.
- **Claims** — outcome mix (settled / pending / rejected), severity and lag.
- **Products & segments** — premium, coverage and loss ratio by policy type, gender and age band.
- **Trends** — policies written and settled payout over time.

> The Python package (`python -m src.run_analysis`) is the source of truth for
> the numbers; the dashboard is a presentation layer on top of it.
