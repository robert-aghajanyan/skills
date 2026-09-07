---
name: codebase-data-correctness-review
description: Review repositories for correctness risks in calculations, data transformations, joins, aggregations, reporting, forecasting, billing, cost, metrics, migrations, and reconciliation logic. Use when the user asks for data correctness, calculation review, reporting accuracy, aggregation review, financial/cost/math logic, forecast logic, ETL validation, reconciliation, rounding, joins, migrations, or metric correctness.
---

# Data Correctness Review

Review whether code computes, transforms, aggregates, migrates, and reports data correctly. Treat money, cost, billing, forecasting, compliance, dashboards, and customer-visible metrics as the highest-risk areas.

## Workflow

1. Build a data-flow map: inputs, outputs, transformations, joins, filters, grouping keys, date windows, currency/unit handling, null handling, migrations, reports, and downstream consumers. When useful, run `python3 "${CLAUDE_SKILL_DIR}/scripts/data_flow_inventory.py" <repo-root>`.
2. Prioritize money, cost, billing, forecasting, compliance, dashboard, and customer-visible calculations before lower-impact internal transforms.
3. Review formulas and transforms using [references/calculations.md](references/calculations.md), [references/joins-and-aggregation.md](references/joins-and-aggregation.md), [references/time-windows.md](references/time-windows.md), [references/reconciliation.md](references/reconciliation.md), and [references/migrations.md](references/migrations.md) as applicable.
4. Look specifically for off-by-one windows, timezone drift, incorrect joins, duplicate rows, dropped rows, null/default mistakes, rounding errors, unit mismatches, stale snapshots, schema drift, partial migrations, and unreconciled totals.
5. For each finding, include exact formula/path evidence, incorrect scenario, expected behavior, likely impact, recommended fix, and a minimal test dataset.
6. Prefer reproducible examples over abstract concerns. If the risk cannot be reproduced or tied to a concrete code path, mark it as a hypothesis or remove it.
7. Prefer repo-native validation commands from docs, manifests, Makefiles, CI, notebooks, or scripts. Add focused fixture tests when asked to fix issues.

## Optional Helper

Use the read-only inventory helper when the repository is unfamiliar or has many data paths:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/data_flow_inventory.py" <repo-root>
```

The helper summarizes likely data inputs, outputs, transformations, SQL files, migrations, report writers, aggregation code, date/window logic, and fixture/example datasets. Treat the output as a starting map, not proof.

## Output

Use [references/output-format.md](references/output-format.md). Include a data-flow map, correctness findings, reconciliation gaps, edge-case test plan, fixture recommendations, and validation commands.

## Gotchas

- Do not report generic "could be wrong" concerns without a concrete data path, formula, join, or window.
- Do not trust dashboard/report parity unless the source window, filters, grouping keys, and freshness match.
- Do not treat snapshot tests as correctness proof unless the fixture totals are independently reconciled.
- Do not silently accept tolerances for money, billing, compliance, or customer-visible metrics; justify the tolerance and show its effect.
