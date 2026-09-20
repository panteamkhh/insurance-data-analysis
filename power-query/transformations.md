# Common transformations

A reference for the Power Query (M) transformations used to prepare this
project's data in Power BI. Each section pairs the **UI action** with the
**M code** it generates, and uses the columns from
`data/insurance_data.csv` and `data/customer_feedback.csv`.

Power Query records every action as a step in a `let ... in` expression. The
steps are just function calls applied in order, so anything done in the UI can
be read - and edited - as code.

```m
let
    Source = Csv.Document(File.Contents("data\insurance_data.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"PremiumAmount", type number}})
in
    Typed
```

## Types and locale

The dates in this dataset are `DD-MM-YYYY`. Converting them with the default
(US) culture can swap day and month or produce errors. Always convert with the
matching culture.

```m
let
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"PolicyStartDate", type date},
            {"PolicyEndDate", type date},
            {"ClaimDate", type date},
            {"PremiumAmount", type number},
            {"CoverageAmount", type number},
            {"ClaimAmount", type number},
            {"Age", Int64.Type}
        },
        "en-GB"
    )
in
    Typed
```

To convert a single text column when the type transform is not enough:

```m
= Table.TransformColumns(Source, {{"PolicyStartDate",
    each Date.FromText(_, [Format = "dd-MM-yyyy", Culture = "en-GB"]), type date}})
```

> Set types **after** appending and **before** merging, so join keys line up.

## Clean text columns

`Text.Trim` removes leading/trailing spaces; `Text.Clean` removes non-printable
characters. Both prevent phantom categories such as `"Auto "` next to `"Auto"`.

```m
= Table.TransformColumns(Source, {
    {"Customer Name", Text.Trim, type text},
    {"Feedback", each Text.Clean(Text.Trim(_)), type text}
})
```

## Remove duplicates

The raw export repeats a few policies, so de-duplicate on the key:

```m
= Table.Distinct(Source, {"PolicyNumber"})
```

With no second argument, `Table.Distinct` removes rows that are identical in
**every** column.

## Filter rows

```m
= Table.SelectRows(Source, each [ClaimStatus] = "Settled")
```

Multiple conditions:

```m
= Table.SelectRows(Source, each
    [ClaimStatus] = "Settled" and [ClaimAmount] > 0)
```

Filter on a list of values:

```m
= Table.SelectRows(Source, each List.Contains({"Auto", "Travel"}, [PolicyType]))
```

## Replace values

Cleaning sentinel values such as `NULL`, `N/A` or `-` to real `null`:

```m
= Table.ReplaceValue(Source, "N/A", null, Replacer.ReplaceValue, {"ClaimDate"})
```

Replace a whole word rather than a substring:

```m
= Table.ReplaceValue(Source, "PVT.LTD", "Private Limited",
    Replacer.ReplaceText, {"Customer Name"})
```

## Split a column

Splitting a full name into first and last:

```m
= Table.SplitColumn(
    Source,
    "Customer Name",
    Splitter.SplitTextByDelimiter(" ", QuoteStyle.Csv),
    {"FirstName", "LastName"}
)
```

Split by a fixed number of characters:

```m
= Table.SplitColumn(Source, "PolicyNumber",
    Splitter.SplitTextByPositions({0, 1}), {"Prefix", "Number"})
```

## Unpivot columns

Unpivot turns wide "one column per period" data into a tidy long format. Given a
table with one column per year:

| PolicyNumber | Premium_2023 | Premium_2024 |
| --- | --- | --- |
| P1 | 240.64 | 260.10 |

```m
= Table.UnpivotOtherColumns(Source, {"PolicyNumber"}, "Year", "Premium")
```

Result:

| PolicyNumber | Year | Premium |
| --- | --- | --- |
| P1 | Premium_2023 | 240.64 |
| P1 | Premium_2024 | 260.10 |

Unpivot is almost always the right move before loading into a Power BI model.

## Pivot columns

The reverse: turn distinct row values into columns. Counting claims by status
per policy type:

```m
= Table.Pivot(
    Source,
    List.Distinct(Source[ClaimStatus]),
    "ClaimStatus",
    "ClaimNumber",
    List.Count
)
```

## Group by (aggregate)

Aggregate premium and policy count per policy type - the Power Query equivalent
of the Python `premium_and_coverage_by_policy_type` function:

```m
= Table.Group(
    Source,
    {"PolicyType"},
    {
        {"Policies", each Table.RowCount(_), Int64.Type},
        {"TotalPremium", each List.Sum([PremiumAmount]), type number},
        {"AvgPremium", each List.Average([PremiumAmount]), type number}
    }
)
```

Add `GroupKind.Local` and a sorted table if you only want to collapse adjacent
rows.

## Add a custom column

Derive `AgeBand` from `Age`, mirroring `src/feature_engineering.py`:

```m
= Table.AddColumn(Source, "AgeBand", each
    if [Age] <= 25 then "18-25"
    else if [Age] <= 35 then "26-35"
    else if [Age] <= 45 then "36-45"
    else if [Age] <= 55 then "46-55"
    else if [Age] <= 65 then "56-65"
    else "65+",
    type text)
```

## Conditional column

The UI's **Add Column** > **Conditional Column** produces the same `if` chain.
Labelling a sentiment score, matching `src/sentiment.py`:

```m
= Table.AddColumn(Source, "SentimentLabel", each
    if [sentiment_score] >= 0.80 then "Excellent"
    else if [sentiment_score] > 0.50 then "Good"
    else "Needs Improvement",
    type text)
```

## Date transformations

```m
let
    WithYear = Table.AddColumn(Source, "PolicyYear",
        each Date.Year([PolicyStartDate]), Int64.Type),
    WithMonth = Table.AddColumn(WithYear, "PolicyMonth",
        each Date.ToText([PolicyStartDate], "yyyy-MM"), type text),
    WithLag = Table.AddColumn(WithMonth, "ClaimLagDays",
        each if [ClaimDate] = null then null
             else Duration.Days([ClaimDate] - [PolicyStartDate]), Int64.Type)
in
    WithLag
```

A proper date table (one row per day) is still recommended for time intelligence
in the model; generate one with `List.Dates`:

```m
let
    Start = #date(2023, 1, 1),
    End = #date(2025, 12, 31),
    Dates = List.Dates(Start, Duration.Days(End - Start) + 1, #duration(1, 0, 0, 0)),
    Table_ = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(Table_, {{"Date", type date}}),
    WithYear = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    WithMonth = Table.AddColumn(WithYear, "Month", each Date.Month([Date]), Int64.Type)
in
    WithMonth
```

## Column from examples

**Add Column** > **Column from Examples** lets you type a few example outputs and
Power Query infers the transformation. It is ideal for one-off parsing, but
review the generated M and replace brittle string logic with explicit functions
where possible.

## Rename, reorder and remove

```m
= Table.RenameColumns(Source, {{"Customer Name", "CustomerName"}})
= Table.ReorderColumns(Source, {"PolicyNumber", "CustomerID", "PolicyType"})
= Table.RemoveColumns(Source, {"ClaimNumber", "ClaimDate"})
```

Remove columns you do not need **before** merging or expanding - it is the
single biggest performance win in most queries.

## Reusable expressions

Define helper values once at the top of the query with `let`:

```m
let
    Source = insurance_data,
    ExcellentThreshold = 0.80,
    GoodThreshold = 0.50,
    Labeled = Table.AddColumn(Source, "SentimentLabel", each
        if [sentiment_score] >= ExcellentThreshold then "Excellent"
        else if [sentiment_score] > GoodThreshold then "Good"
        else "Needs Improvement",
        type text)
in
    Labeled
```

## Cheat sheet

| Task | Function |
| --- | --- |
| Stack rows | `Table.Combine` |
| Join columns | `Table.NestedJoin`, `Table.Join` |
| Remove duplicate rows | `Table.Distinct` |
| Filter rows | `Table.SelectRows` |
| Remove columns | `Table.SelectColumns`, `Table.RemoveColumns` |
| Rename columns | `Table.RenameColumns` |
| Change types | `Table.TransformColumnTypes` |
| Replace values | `Table.ReplaceValue` |
| Split a column | `Table.SplitColumn` |
| Merge columns | `Table.CombineColumns` |
| Wide to long | `Table.UnpivotOtherColumns` |
| Long to wide | `Table.Pivot` |
| Aggregate | `Table.Group` |
| Add a column | `Table.AddColumn` |
| Handle errors | `try ... otherwise ...`, `Table.RemoveRowsWithErrors` |
| Replace errors | `Table.ReplaceErrorValues` |

## See also

- [Append (union) demo](append-demo.md)
- [Merge (join) demo](merge-demo.md)
- Microsoft docs: [Power Query M reference](https://learn.microsoft.com/powerquery-m/)
