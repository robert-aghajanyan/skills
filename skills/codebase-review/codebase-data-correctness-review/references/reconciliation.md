# Reconciliation

Use this reference for tie-outs, report validation, ledger comparisons, dashboard parity, source-of-truth checks, and explaining differences.

## Review Focus

- Identify the source of truth for each total. If there are multiple sources, name the intended precedence.
- Reconcile at the lowest useful grain before reconciling final totals.
- Separate source data drift, filter differences, grouping differences, timing differences, currency/unit differences, and rendering differences.
- Require before-and-after totals for migrations, backfills, transformations, and report-generation changes.
- Check whether exclusions have an explicit reason ledger or audit trail.
- Check dashboard/report comparisons use the same time window, source snapshot, filters, dimensions, and rounding.
- Check whether tolerances are absolute, relative, or domain-specific. Money and billing tolerances should be very small and explicitly justified.
- Record unreconciled residuals instead of hiding them in "other" buckets without explanation.

## Common Failure Modes

- Comparing outputs generated at different times and calling the difference a bug.
- Reconciling only the grand total while individual groups are swapped, duplicated, or missing.
- Treating a dashboard filter as equivalent to a report filter without checking the exact predicate.
- Ignoring excluded rows, null groups, or orphan dimension records.
- Passing a tolerance that is large enough to hide a material bug.
- Reconciliation scripts use different logic from production and therefore validate the wrong thing.

## Evidence To Collect

- Source totals, transformed totals, final report totals, and residual differences.
- Query or script used for each number.
- Generated-at timestamp and upstream data freshness for every compared artifact.
- Group-level comparison, not only grand totals.
- Explanation ledger for excluded, adjusted, or manually corrected rows.

## Minimal Reconciliation Shape

Prefer a table with:

- source name
- window and filters
- row count
- subtotal by key dimension
- final total
- difference vs expected
- reason for difference
- command or query used to reproduce the value
