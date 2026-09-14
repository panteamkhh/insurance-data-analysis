# Power BI dashboard

An interactive Power BI report — **Prism Insurance PVT.LTD** — built on the same
source file as the Python pipeline:
[`../data/insurance_data.csv`](../data/insurance_data.csv).

| File | Description |
| --- | --- |
| `insurance-dashboard.pbix` | Power BI Desktop report |
| `screenshots/Prism Insurance PVT.LTD.PNG` | Exported overview page |

## Overview page

<p align="center"><img src="screenshots/Prism Insurance PVT.LTD.PNG" width="820"/></p>

The page includes:

- **KPI cards** — premium (5.98M), coverage (600.55M) and claim amount (16.91M).
- **Slicers** — filter the whole page by policy, claim or customer.
- **Premium by policy type** — Travel leads the book.
- **Active vs. inactive policies** — 74.9% / 25.1%.
- **Claims by status** — rejected / settled / pending funnel.
- **Claim amount by age group** (young adult, adult, elder).
- **Policy-type matrix** — pending, rejected and settled amounts.

## Notes

- The report reads the raw CSV, so its totals include the few duplicate rows the
  Python pipeline removes (e.g. premium 5.98M vs. 5.97M).
- The Python package (`python -m src.run_analysis`) remains the source of truth
  for the numbers; the dashboard is the presentation layer.
- The report is a work in progress; additional pages are planned.
