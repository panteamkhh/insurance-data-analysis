# Appending queries (union)

**Append** stacks the rows of two or more tables into one, as long as the tables
have compatible columns. It is the Power Query equivalent of SQL `UNION ALL`.

In this project append is the tool for **monthly or yearly extracts** of the
policy fact table, and for **batches of customer feedback**, that all need to
become a single query before the data model is built.

## When to use append

| Situation | Use append |
| --- | --- |
| One file per month / year / region | Yes |
| The same table exported from two systems | Yes |
| Adding columns from another table | No - use [merge](merge-demo.md) |
| Combining tables with different granularity | No |

## Scenario: three monthly policy extracts

Assume the source folder contains one CSV per month with the same columns as
`data/insurance_data.csv`:

```
policies_2024_01.csv
policies_2024_02.csv
policies_2024_03.csv
```

Each file has the columns `PolicyNumber, CustomerID, Gender, Age, PolicyType,
PolicyStartDate, PolicyEndDate, PremiumAmount, CoverageAmount, ClaimNumber,
ClaimDate, ClaimAmount, ClaimStatus`.

### Step by step (Power BI Desktop)

1. **Get Data** > **Text/CSV** and load `policies_2024_01.csv`.
2. In Power Query, set the column types (especially the dates, which are
   `DD-MM-YYYY`; see [transformations](transformations.md#types-and-locale)).
3. Rename the query to `Policies_2024_01`.
4. Repeat for the other two files.
5. Select `Policies_2024_01`, then **Home** > **Append Queries** >
   **Append Queries as New**, and add the other two tables.
6. Rename the new query `FactPolicies`.

### The generated M

```m
let
    Policies2024_01 = /* previous step */,
    Policies2024_02 = /* previous step */,
    Policies2024_03 = /* previous step */,
    Combined = Table.Combine({Policies2024_01, Policies2024_02, Policies2024_03})
in
    Combined
```

`Table.Combine` is exactly what the UI builds. To append in place instead of
creating a new query, use `Table.Combine({Source, OtherQuery})` as a step inside
the target query.

### Mismatched columns

If a table is missing a column the others have, `Table.Combine` fails by
default. Pass the optional second argument to fill the gaps with `null`:

```m
Combined = Table.Combine(
    {Policies2024_01, Policies2024_02, Policies2024_03},
    MissingField.UseNull
)
```

Column **order** does not matter - Power Query matches by name - but column
**names and types** must line up. Standardise them before appending.

## Scenario: combine every file in a folder

Rather than adding one query per file, point at the folder and let Power Query
read every CSV. This scales to hundreds of files.

```m
let
    Source = Folder.Files("C:\insurance\policies"),
    OnlyCsv = Table.SelectRows(Source, each [Extension] = ".csv"),
    AddData = Table.AddColumn(OnlyCsv, "Data", each
        Table.PromoteHeaders(
            Csv.Document([Content], [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
            [PromoteAllScalars = true]
        )
    ),
    Combined = Table.Combine(AddData[Data])
in
    Combined
```

To keep the source file name for auditing, add it before combining:

```m
    AddData = Table.AddColumn(OnlyCsv, "Data", each
        Table.AddColumn(
            Table.PromoteHeaders(
                Csv.Document([Content], [Delimiter = ",", Encoding = 65001]),
                [PromoteAllScalars = true]
            ),
            "SourceFile",
            each [Name],
            type text
        )
    ),
```

## Scenario: appending feedback batches

The same pattern applies to `data/customer_feedback.csv` if reviews arrive in
separate files (`feedback_2024_q1.csv`, `feedback_2024_q2.csv`, ...):

```m
let
    Q1 = Csv.Document(File.Contents("C:\insurance\feedback_2024_q1.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Q1Headers = Table.PromoteHeaders(Q1, [PromoteAllScalars = true]),
    Q2 = Csv.Document(File.Contents("C:\insurance\feedback_2024_q2.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Q2Headers = Table.PromoteHeaders(Q2, [PromoteAllScalars = true]),
    AllFeedback = Table.Combine({Q1Headers, Q2Headers})
in
    AllFeedback
```

Add a `Batch` column before combining if you need to trace each row back to its
source:

```m
    Tagged = Table.AddColumn(Q1Headers, "Batch", each "2024-Q1", type text),
    Tagged2 = Table.AddColumn(Q2Headers, "Batch", each "2024-Q2", type text),
    AllFeedback = Table.Combine({Tagged, Tagged2})
```

## Before and after

**Policies2024_01**

| PolicyNumber | CustomerID | PolicyType | PremiumAmount |
| --- | --- | --- | --- |
| P1 | C1 | Auto | 240.64 |
| P2 | C2 | Travel | 1059.73 |

**Policies2024_02**

| PolicyNumber | CustomerID | PolicyType | PremiumAmount |
| --- | --- | --- | --- |
| P3 | C3 | Travel | 1019.59 |
| P4 | C4 | Travel | 549.70 |

**Combined**

| PolicyNumber | CustomerID | PolicyType | PremiumAmount |
| --- | --- | --- | --- |
| P1 | C1 | Auto | 240.64 |
| P2 | C2 | Travel | 1059.73 |
| P3 | C3 | Travel | 1019.59 |
| P4 | C4 | Travel | 549.70 |

## Gotchas

- **Duplicate rows.** Appending does not remove duplicates. If a row appears in
  two extracts, it appears twice. Follow the append with **Remove Rows** >
  **Remove Duplicates** on the key (`PolicyNumber`) when the sources can
  overlap.
- **Type drift.** If one file stores `PremiumAmount` as text and another as a
  number, the combined column becomes text. Set types **after** combining, or
  fix them in each source query.
- **Header rows repeated.** Some exports include the header as a data row;
  filter it out (`Table.SelectRows(..., each [PolicyNumber] <> "PolicyNumber")`)
  before appending.
- **Column name casing.** `PolicyNumber` and `policynumber` are different
  columns to Power Query. Normalise casing first.

## Verify the append

After combining, check the row count and that no key is unexpectedly repeated:

```m
let
    Combined = /* ... */,
    RowCount = Table.RowCount(Combined),
    DistinctPolicies = List.Count(List.Distinct(Combined[PolicyNumber]))
in
    [Rows = RowCount, DistinctPolicies = DistinctPolicies]
```

If `Rows` is larger than `DistinctPolicies` for a table that should be unique by
policy, you have overlapping extracts.

## See also

- [Merge (join) demo](merge-demo.md)
- [Common transformations](transformations.md)
- Microsoft docs: [`Table.Combine`](https://learn.microsoft.com/powerquery-m/table-combine),
  [`MissingField.UseNull`](https://learn.microsoft.com/powerquery-m/missingfield-typenullable)
