# Query folding

**Query folding** is Power Query's ability to translate your transformation
steps into a single query that runs against the source system (SQL, OData,
SharePoint, ...), instead of pulling all the raw data into Power Query first.

When folding works, filtering, grouping and joining happen on the server. When
it breaks, Power Query has to download everything and finish the work locally -
which is the usual cause of a slow refresh.

> **Note for this project.** The sources are CSV files. File sources do **not**
> fold, so folding does not apply here. This guide matters as soon as you point
> the same model at a database, data warehouse or OData feed.

## Why it matters

| | Folded | Not folded |
| --- | --- | --- |
| Work happens | On the source | On your machine |
| Data transferred | Only what is needed | Everything |
| Refresh speed | Fast, scales | Slow, memory-bound |
| Typical sources | SQL Server, PostgreSQL, Oracle, OData, SharePoint | CSV, Excel, PDF, web pages |

## How to check

In Power Query Editor, select a step and look at **View** > **View Native
Query**:

- **Enabled** - the step folds; click it to see the generated SQL.
- **Greyed out** - folding has stopped at (or before) this step.

The first non-folding step is where folding breaks; every step after it runs
locally.

## Steps that usually fold

- Filtering rows (`Table.SelectRows`)
- Selecting / removing / renaming columns
- Changing data types
- Sorting and **Keep Top N**
- Group by (`Table.Group`)
- Joins between foldable sources (`Table.NestedJoin`, `Table.Join`)
- Appends (`Table.Combine`)
- Simple column arithmetic and date functions

## Steps that usually break folding

- **Index columns** (`Table.AddIndexColumn`)
- **Pivot / unpivot** on some sources
- **Custom columns** whose logic the source cannot express
- **Custom functions** applied per row
- Merging with a **non-foldable** source (for example a CSV)
- `Table.Buffer`, `Table.AddRankColumn`
- Changing the **type of the whole table** in one step in some connectors
- Any step added after a previous break (once broken, it stays broken)

## Keeping folding alive

**Filter and remove early.** Reduce rows and columns before any expensive step.

```m
let
    Source = Sql.Database("server", "InsuranceDB"),
    Policies = Source{[Schema = "dbo", Item = "Policies"]}[Data],
    Recent = Table.SelectRows(Policies, each [PolicyStartDate] >= #date(2024, 1, 1)),
    Slim = Table.SelectColumns(Recent, {"PolicyNumber", "PolicyType", "PremiumAmount"}),
    Grouped = Table.Group(Slim, {"PolicyType"},
        {{"TotalPremium", each List.Sum([PremiumAmount]), type number}})
in
    Grouped
```

Every step above folds into a single SQL query.

**Replace fragile custom columns** with foldable equivalents. Instead of a
custom `Text` function that the source cannot translate, prefer native column
operations when possible.

**Stop folding on purpose** when a later step must run locally, so the break
happens at a known place:

```m
    Buffered = Table.Buffer(Slim)  // folding stops here, deliberately
```

**Use native SQL** when you need full control and folding is not enough:

```m
    Native = Value.NativeQuery(
        Source,
        "SELECT PolicyType, SUM(PremiumAmount) AS TotalPremium
         FROM dbo.Policies GROUP BY PolicyType"
    )
```

## Diagnosing a slow refresh

1. Look for the **last folding step** with **View Native Query**.
2. Move filters and column removals **before** that step.
3. Re-check that joins reference foldable sources.
4. If needed, split the query: one foldable part, then `Table.Buffer`, then the
   local part.

## See also

- [Common transformations](transformations.md)
- [Merge (join) demo](merge-demo.md)
- Microsoft docs: [Query folding guidance](https://learn.microsoft.com/power-query/query-folding-basics)
