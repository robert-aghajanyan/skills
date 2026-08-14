# Output Format

Use this structure for data correctness reviews. Keep the report evidence-first and remove findings that do not cite concrete code, formulas, queries, files, or reproducible data.

## Data-Flow Map

Include:

- inputs and source-of-truth systems
- outputs, reports, exports, dashboards, and downstream consumers
- transformations and formulas
- joins, filters, grouping keys, and output grain
- date windows, timezone, and freshness assumptions
- currency, unit, precision, rounding, and null/default handling
- migrations, backfills, snapshots, and cache/materialization points
- validation commands already available in the repo

## Correctness Findings

Order findings by impact: Blocker, High, Medium, Low, Nit.

For each finding include:

- title with severity
- affected file, line, formula, query, or report path
- exact evidence from code or data flow
- incorrect scenario with minimal rows or values
- expected behavior
- likely user, business, financial, compliance, or operational impact
- recommended fix
- minimal test dataset
- validation command

## Reconciliation Gaps

List missing or weak tie-outs separately from confirmed bugs. For each gap include:

- total or metric that needs reconciliation
- authoritative source
- current comparison, if any
- missing grain, filter, window, or freshness proof
- recommended reconciliation check

## Edge-Case Test Plan

Prioritize tests that exercise:

- period boundaries and timezone conversion
- null vs zero vs missing values
- duplicate and unmatched join keys
- one-to-many and many-to-many joins
- unit, currency, and rounding boundaries
- negative values, credits, refunds, or reversals
- partial periods and stale snapshots
- migration reruns and partial migration recovery

## Fixture Recommendations

Recommend the smallest fixture that proves the behavior. Include expected totals in the fixture or a sidecar file so tests fail for the right reason.

## Validation Commands

Prefer existing repo commands. If a command was not run, state why and what risk remains. Include exact commands for focused tests, reconciliation scripts, report regeneration, snapshot rebuilds, or migration dry runs.
