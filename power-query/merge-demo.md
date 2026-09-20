# Merging queries (join)

**Merge** combines the columns of two tables by matching rows on one or more key
columns. It is the Power Query equivalent of a SQL `JOIN`.

In this project merge is how the flat policy export in
`data/insurance_data.csv` is turned into a proper **star schema**: the fact table
joins to lookup tables for policy type, customer and claim status.

## Join kinds

| Join kind | M value | Keeps |
| --- | --- | --- |
| Left outer | `JoinKind.LeftOuter` | All rows from the first table |
| Right outer | `JoinKind.RightOuter` | All rows from the second table |
| Full outer | `JoinKind.FullOuter` | All rows from both tables |
| Inner | `JoinKind.Inner` | Only rows that match in both |
| Left anti | `JoinKind.LeftAnti` | First-table rows with **no** match |
| Right anti | `JoinKind.RightAnti` | Second-table rows with **no** match |

Power Query is case-sensitive by default. Pass `[Comparer = Comparer.OrdinalIgnoreCase]`
for case-insensitive matching.

## Scenario 1: enrich policies with a lookup (left outer)

A lookup table maps each policy type to a risk band and a base rate:

**PolicyTypeLookup**

| PolicyType | RiskBand | BaseRate |
| --- | --- | --- |
| Auto | High | 1.25 |
| Travel | Medium | 1.00 |
| Health | High | 1.20 |
| Life | Low | 0.90 |
| Home | Low | 0.95 |

Merge it onto the fact table so every policy keeps its row and gains the lookup
columns.

### UI steps

1. Select the `insurance_data` query.
2. **Home** > **Merge Queries**.
3. Pick `PolicyTypeLookup` and select the `PolicyType` column in both tables.
4. Join kind: **Left Outer**.
5. Expand the new column and keep `RiskBand` and `BaseRate`.

### M

```m
let
    Source = insurance_data,
    Lookup = PolicyTypeLookup,
    Merged = Table.NestedJoin(
        Source,
        {"PolicyType"},
        Lookup,
        {"PolicyType"},
        "TypeInfo",
        JoinKind.LeftOuter
    ),
    Expanded = Table.ExpandTableColumn(
        Merged,
        "TypeInfo",
        {"RiskBand", "BaseRate"},
        {"RiskBand", "BaseRate"}
    ),
    Typed = Table.TransformColumnTypes(Expanded, {{"BaseRate", type number}})
in
    Typed
```

### Before and after

**Before**

| PolicyNumber | PolicyType | PremiumAmount |
| --- | --- | --- |
| P1 | Auto | 240.64 |
| P2 | Travel | 1059.73 |

**After (left outer)**

| PolicyNumber | PolicyType | PremiumAmount | RiskBand | BaseRate |
| --- | --- | --- | --- | --- |
| P1 | Auto | 240.64 | High | 1.25 |
| P2 | Travel | 1059.73 | Medium | 1.00 |

## Scenario 2: keep only matching rows (inner)

Use an inner join when a row without a match is an error you want to surface -
for example, a claim that points at a policy number that does not exist.

```m
ValidClaims = Table.NestedJoin(
    Claims,
    {"PolicyNumber"},
    Policies,
    {"PolicyNumber"},
    "Policy",
    JoinKind.Inner
)
```

Because `JoinKind.Inner` drops unmatched rows, the row count is a quick
referential-integrity check: if it is smaller than `Table.RowCount(Claims)`,
some claims reference unknown policies.

## Scenario 3: find unmatched rows (anti join)

Anti joins are the clean way to answer "which policies have **no** settled
claim?". Filter the fact table to settled claims, then anti-join it back onto the
full table.

```m
let
    Policies = insurance_data,
    Settled = Table.SelectRows(insurance_data, each [ClaimStatus] = "Settled"),
    PoliciesWithoutSettlement = Table.NestedJoin(
        Policies,
        {"PolicyNumber"},
        Settled,
        {"PolicyNumber"},
        "SettledMatch",
        JoinKind.LeftAnti
    )
in
    PoliciesWithoutSettlement
```

The result is every policy that never produced a settled claim - useful for a
"clean book" or upsell analysis. Swap to `JoinKind.RightAnti` to find settled
claims whose policy is missing from the fact table.

## Scenario 4: fuzzy merge on customer names

`data/customer_feedback.csv` identifies customers by **name**
(`Customer Name`), while the policy data uses `CustomerID`. Names rarely match
exactly (`"John Smith"` vs `"John  smith"` vs `"J. Smith"`), so a fuzzy merge is
appropriate.

```m
let
    Feedback = customer_feedback,
    Customers = DimCustomer,
    Fuzzy = Table.FuzzyNestedJoin(
        Feedback,
        {"Customer Name"},
        Customers,
        {"Customer Name"},
        "CustomerMatch",
        JoinKind.LeftOuter,
        [IgnoreCase = true, IgnoreSpace = true, Threshold = 0.8]
    ),
    Expanded = Table.ExpandTableColumn(
        Fuzzy,
        "CustomerMatch",
        {"CustomerID", "City"},
        {"CustomerID", "City"}
    )
in
    Expanded
```

Notes on fuzzy merge:

- `Threshold` is `0`-`1`; `0.8` is a reasonable starting point.
- It is **slow** on large tables. Filter and remove unused columns first.
- Always review matches: fuzzy joins can pair different customers. Keep a
  similarity column for auditing:

```m
    Fuzzy = Table.FuzzyNestedJoin(
        Feedback, {"Customer Name"}, Customers, {"Customer Name"},
        "CustomerMatch", JoinKind.LeftOuter,
        [IgnoreCase = true, IgnoreSpace = true, Threshold = 0.8,
         TransformationTable = null, NumberOfMatches = 1]
    ),
```

## Performance tips

1. **Merge as late as possible.** Reduce rows with filters and remove unused
   columns before joining.
2. **Expand only the columns you need.** Expanding a wide table is expensive.
3. **Watch the join key type.** Merging a text key to a number key silently
   yields no matches. Align types first.
4. **Prefer `Table.Join`** when you want the columns flattened directly:

   ```m
   Joined = Table.Join(Policies, {"PolicyType"}, Lookup, {"PolicyType"}, JoinKind.LeftOuter)
   ```

5. **Disable query load** on intermediate queries (right-click > uncheck **Enable
   load**) so only the final table is materialised.

## Verify the merge

A left outer join must not change the number of rows. Check it explicitly:

```m
let
    Merged = /* ... */,
    Check = [Before = Table.RowCount(Source), After = Table.RowCount(Merged)]
in
    Check
```

If `After` is larger than `Before`, the right-hand table has duplicate keys.
Deduplicate the lookup (`Table.Distinct(Lookup, {"PolicyType"})`) before merging.

## See also

- [Append (union) demo](append-demo.md)
- [Common transformations](transformations.md)
- Microsoft docs: [`Table.NestedJoin`](https://learn.microsoft.com/powerquery-m/table-nestedjoin),
  [`Table.Join`](https://learn.microsoft.com/powerquery-m/table-join),
  [`Table.FuzzyNestedJoin`](https://learn.microsoft.com/powerquery-m/table-fuzzynestedjoin)
