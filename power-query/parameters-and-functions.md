# Parameters and custom functions

Two Power Query features that keep a model maintainable: **parameters** hold a
value you want to change in one place, and **custom functions** let you reuse
logic instead of copy-pasting steps.

## Parameters

Create with **Home** > **Manage Parameters** > **New Parameter**. Always set a
**type** and, where useful, an allowed-values list.

### File path parameter

Hard-coded paths break the moment the file moves. Use a parameter instead.

```m
// Parameter: DataFolder (type text)
let
    Source = Folder.Files(DataFolder),
    OnlyCsv = Table.SelectRows(Source, each [Extension] = ".csv"),
    AddData = Table.AddColumn(OnlyCsv, "Data", each
        Table.PromoteHeaders(
            Csv.Document([Content], [Delimiter = ",", Encoding = 65001]),
            [PromoteAllScalars = true]
        )
    ),
    Combined = Table.Combine(AddData[Data])
in
    Combined
```

### Threshold parameter

The sentiment label thresholds used by `src/sentiment.py` (0.80 and 0.50) are a
natural fit for parameters, so they live in one place:

```m
// Parameters: ExcellentThreshold (decimal, 0.80), GoodThreshold (decimal, 0.50)
= Table.AddColumn(Source, "SentimentLabel", each
    if [sentiment_score] >= ExcellentThreshold then "Excellent"
    else if [sentiment_score] > GoodThreshold then "Good"
    else "Needs Improvement",
    type text)
```

### Date-range parameter

```m
// Parameter: MinPolicyDate (date, 2024-01-01)
= Table.SelectRows(Source, each [PolicyStartDate] >= MinPolicyDate)
```

### Invoke a parameter

In the UI, use **Invoke Parameter** to turn the current value into a step, which
makes it easy to switch the model between environments:

```m
= DataFolder
```

## Custom functions

A custom function is just a query whose `let` expression starts with a
**parameter list**:

```m
(input) => let
    ...
in
    ...
```

### Example: clean feedback text

Reusable text cleaning, mirroring `src/text_preprocessing.py`:

```m
// Query name: fnCleanText
(text as nullable text) as nullable text =>
let
    Lowered = if text = null then null else Text.Lower(text),
    Cleaned = if Lowered = null then null else Text.Clean(Lowered),
    Trimmed = if Cleaned = null then null else Text.Trim(Cleaned),
    NoPunctuation = if Trimmed = null then null
        else Text.Select(Trimmed, {"a".."z", " "}),
    Collapsed = if NoPunctuation = null then null
        else Text.Combine(List.Select(Text.Split(NoPunctuation, " "), each _ <> " "), " ")
in
    Collapsed
```

Use it on a column with **Add Column** > **Invoke Custom Function**, or inline:

```m
= Table.TransformColumns(Source, {{"Feedback", fnCleanText, type text}})
```

### Example: label a sentiment score

```m
// Query name: fnSentimentLabel
(score as nullable number) as text =>
if score = null then "Needs Improvement"
else if score >= 0.80 then "Excellent"
else if score > 0.50 then "Good"
else "Needs Improvement"
```

```m
= Table.AddColumn(Source, "SentimentLabel",
    each fnSentimentLabel([sentiment_score]), type text)
```

### Example: add an age band

```m
// Query name: fnAgeBand
(age as nullable number) as text =>
if age = null then "Unknown"
else if age <= 25 then "18-25"
else if age <= 35 then "26-35"
else if age <= 45 then "36-45"
else if age <= 55 then "46-55"
else if age <= 65 then "56-65"
else "65+"
```

### Functions that take a table

Declare the parameter as a table to write a reusable whole-table transformation:

```m
// Query name: fnDeDuplicate
(source as table, key as text) as table =>
let
    Distinct = Table.Distinct(source, {key})
in
    Distinct
```

```m
= fnDeDuplicate(insurance_data, "PolicyNumber")
```

## Organisation tips

- Prefix function queries with `fn` (`fnCleanText`) so they sort together and are
  easy to spot.
- **Disable load** on function queries and helper queries (right-click > uncheck
  **Enable load**) - they should not appear as tables in the model.
- Group related queries in folders (right-click > **Move to Group**), for example
  `Functions`, `Staging`, `Model`.
- Document each function with a short comment above the signature.

## See also

- [Common transformations](transformations.md)
- [Building a date table](date-table.md)
- Microsoft docs: [Custom functions](https://learn.microsoft.com/power-query/custom-function)
