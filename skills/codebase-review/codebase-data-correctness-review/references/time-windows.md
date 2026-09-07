# Time Windows

Use this reference for date filters, timezones, fiscal calendars, reporting periods, rolling windows, snapshots, forecasts, and freshness logic.

## Review Focus

- Write down each window as `[start, end)` or another explicit convention. Avoid vague "last month" or "previous 30 days" wording.
- Confirm timezone for inputs, storage, calculations, dashboards, and rendered reports.
- Check inclusive vs exclusive boundaries for SQL `BETWEEN`, pandas filters, ORM predicates, and API query params.
- Verify fiscal calendars, calendar months, ISO weeks, retail weeks, and custom business periods are not mixed.
- Check partial periods. Current month, current day, and in-flight billing windows often need explicit exclusion or labeling.
- Verify snapshot freshness and generated-at timestamps. A fresh report can still contain stale upstream data.
- Check daylight saving transitions, leap days, month-end, quarter-end, year-end, and fiscal-year boundaries.
- Check forecast windows separately from historical actuals. Forecast generation should not rewrite actuals unless that is the explicit process.
- Check cache keys and materialized views include the window, timezone, filters, and source version.

## Common Failure Modes

- Off-by-one end dates include the first row of the next period or exclude the last row of the target period.
- Local timezone conversion shifts UTC rows into the wrong day or month.
- `now()` makes tests non-deterministic and reports non-reproducible.
- Rolling windows include partial current periods without labeling them as partial.
- Dashboard and report use the same period label but different cutoffs.
- Backfills update source rows but not derived snapshots or cached report data.
- Forecast code compares actuals through one month with forecasts through another.

## Evidence To Collect

- The exact timestamp fields used for filtering.
- Window construction code, timezone conversion code, and scheduler configuration.
- Report labels, dashboard filters, generated-at values, and upstream source freshness.
- Boundary fixtures at the start and end of the period.
- The command or query that recomputes the period.

## Minimal Test Dataset Pattern

Create rows at:

- one instant before the start boundary
- exactly at the start boundary
- one instant before the end boundary
- exactly at the end boundary
- one row in another timezone when timezone conversion matters
- one row in a partial current period when partial windows are possible
