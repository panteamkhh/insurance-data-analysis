# Building a date table

Time intelligence in Power BI (`SAMEPERIODLASTYEAR`, `YTD`, `DATESINPERIOD`, ...)
requires a **date table**: one row per day, with no gaps, marked as a date table
and related to the fact tables.

This dataset has two date columns - `PolicyStartDate` and `ClaimDate` - so a
single shared date table lets you slice policies and claims by the same calendar.

## Generate the table in Power Query

```m
let
    StartDate = #date(2023, 1, 1),
    EndDate = #date(2025, 12, 31),
    DayCount = Duration.Days(EndDate - StartDate) + 1,
    Dates = List.Dates(StartDate, DayCount, #duration(1, 0, 0, 0)),
    ToTable = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(ToTable, {{"Date", type date}}),
    AddYear = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    AddQuarter = Table.AddColumn(AddYear, "Quarter",
        each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddMonthNumber = Table.AddColumn(AddQuarter, "MonthNumber",
        each Date.Month([Date]), Int64.Type),
    AddMonthName = Table.AddColumn(AddMonthNumber, "Month",
        each Date.ToText([Date], "MMM"), type text),
    AddMonthKey = Table.AddColumn(AddMonthName, "MonthKey",
        each Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    AddDay = Table.AddColumn(AddMonthKey, "Day",
        each Date.Day([Date]), Int64.Type),
    AddWeekday = Table.AddColumn(AddDay, "DayOfWeek",
        each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    AddWeekdayName = Table.AddColumn(AddWeekday, "Weekday",
        each Date.ToText([Date], "dddd"), type text),
    AddIsWeekend = Table.AddColumn(AddWeekdayName, "IsWeekend",
        each Date.DayOfWeek([Date], Day.Monday) >= 5, type logical)
in
    AddIsWeekend
```

Rather than hard-coding the range, derive it from the fact table so it always
covers the data:

```m
    StartDate = Date.StartOfYear(List.Min(insurance_data[PolicyStartDate])),
    EndDate = Date.EndOfYear(List.Max(insurance_data[PolicyStartDate])),
```

Add a couple of extra years at each end if you want year-over-year comparisons
to line up cleanly.

## Mark as a date table

1. Load the query as `DimDate`.
2. In **Model view**, select `DimDate`, then **Mark as date table** and choose
   the `Date` column.
3. Create the relationships:
   - `DimDate[Date]` → `FactPolicies[PolicyStartDate]` (active)
   - `DimDate[Date]` → `FactPolicies[ClaimDate]` (inactive, activate in DAX with
     `USERELATIONSHIP`)

## Fiscal calendar

If the business year starts in April, add fiscal columns:

```m
    AddFiscalYear = Table.AddColumn(AddIsWeekend, "FiscalYear",
        each if Date.Month([Date]) >= 4 then Date.Year([Date]) + 1 else Date.Year([Date]),
        Int64.Type),
    AddFiscalMonth = Table.AddColumn(AddFiscalYear, "FiscalMonth",
        each Date.Month(Date.AddMonths([Date], -3)), Int64.Type),
    AddFiscalQuarter = Table.AddColumn(AddFiscalMonth, "FiscalQuarter",
        each "FQ" & Text.From(Date.QuarterOfYear(Date.AddMonths([Date], -3))), type text)
```

## Common mistakes

- **Gaps or duplicate dates.** Build from `List.Dates`, never from the fact
  table's distinct dates.
- **Not marked as a date table.** Time-intelligence functions may silently
  return wrong results.
- **Multiple date columns, one relationship.** Only one relationship can be
  active; use `USERELATIONSHIP` in measures for the others.
- **A date column typed as text.** The model then treats it as a category, not a
  hierarchy.

## See also

- [Common transformations](transformations.md)
- Microsoft docs: [Create a date table](https://learn.microsoft.com/power-bi/transform-model/desktop-date-tables)
