# Joins And Aggregation

Use this reference for SQL joins, pandas merges, ORM relationships, Spark/DataFrame joins, grouping, rollups, pivots, deduplication, and report totals.

## Review Focus

- Identify every join key and whether it is unique on the left side, right side, both sides, or neither.
- Confirm join type matches the business requirement: inner, left, right, full outer, semi, anti, as-of, or cross join.
- Check whether filters run before or after joins and aggregations. Moving a filter can drop rows, duplicate rows, or change denominators.
- Check one-to-many and many-to-many joins for row multiplication. Reconcile row counts before and after the join.
- Verify grouping keys match the requested grain. Extra keys split totals; missing keys collapse unrelated rows.
- Verify distinct counts and deduplication rules have a deterministic tie-breaker.
- Confirm null keys and blank keys are handled deliberately. Many systems do not join nulls the same way.
- Check slowly changing dimensions, effective dates, and latest-record joins.
- Check aggregation order: aggregate-before-join and join-before-aggregate can produce different answers.

## Common Failure Modes

- Inner join drops valid fact rows with missing dimension records.
- Left join followed by a `WHERE` clause on right-table fields behaves like an inner join.
- Duplicate dimension records multiply cost, usage, revenue, or count.
- Joining on names or labels instead of stable IDs causes collisions.
- Joining monthly facts to daily dimensions without effective-date logic.
- Deduplicating by arbitrary first row instead of a deterministic ordering.
- Grouping by formatted labels instead of canonical IDs.
- Double-counting subtotal rows together with detail rows.
- Applying `DISTINCT` to hide duplicates without fixing the join grain.

## Evidence To Collect

- Join key definitions, uniqueness expectations, and schema constraints if present.
- Row counts before and after each join.
- Duplicate-key queries for both sides of the join.
- Grouping grain and output grain.
- A failing fixture that shows a duplicate, dropped row, or collapsed group.

## Minimal Checks

Use the repo-native language, SQL engine, or DataFrame library to verify:

- duplicate keys on each join side
- unmatched left-side and right-side rows
- row-count changes after joins
- total changes after joins
- null-key behavior
- output rows at the expected grain
