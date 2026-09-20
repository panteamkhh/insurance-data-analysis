# Power Query recipes

Hands-on Power Query (M) recipes used to shape the data for this project's Power
BI model. Each guide pairs the **UI action** with the **M code** it produces and
uses the real columns from `data/insurance_data.csv` and
`data/customer_feedback.csv`.

| Guide | What it covers |
| --- | --- |
| [append-demo.md](append-demo.md) | Stacking monthly/yearly extracts and feedback batches (`Table.Combine`, folder combine) |
| [merge-demo.md](merge-demo.md) | Joins: left outer, inner, anti and fuzzy merges (`Table.NestedJoin`) |
| [transformations.md](transformations.md) | Types/locale, cleaning, split, unpivot/pivot, group by, custom and conditional columns |
| [query-folding.md](query-folding.md) | What folds to the source, what breaks folding, and how to check |
| [date-table.md](date-table.md) | Building and marking a proper date table for time intelligence |
| [parameters-and-functions.md](parameters-and-functions.md) | Reusable parameters and custom M functions |

## Suggested order for this dataset

1. **Get Data** the CSV and [fix the date types](transformations.md#types-and-locale)
   (they are `DD-MM-YYYY`).
2. [De-duplicate](transformations.md#remove-duplicates) on `PolicyNumber`.
3. Derive `AgeBand`, `PolicyYear` and `ClaimLagDays`
   ([custom columns](transformations.md#add-a-custom-column)).
4. Build a `PolicyTypeLookup` and [merge](merge-demo.md) it onto the fact table.
5. Build a [date table](date-table.md) and relate it to `PolicyStartDate` and
   `ClaimDate`.
6. Load the model and mark the date table as a date table.

> Power Query is for **shape and clean**. Aggregation and business logic that
> changes with filters belong in **DAX measures**. Keep the split clean.
