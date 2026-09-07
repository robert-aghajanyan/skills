# Calculations

Use this reference for formulas, metrics, billing, cost, forecasting, financial math, rates, percentages, and derived fields.

## Review Focus

- Trace the formula from raw input fields to final output fields. Name every transformation step and every unit or currency conversion.
- Verify numerator, denominator, filters, and grouping keys against the business meaning of the metric.
- Check whether the code mixes absolute values, deltas, rates, percentages, basis points, and ratios.
- Check currency handling: source currency, converted currency, exchange-rate date, precision, and whether totals mix currencies.
- Check unit handling: bytes vs GiB, cores vs millicores, seconds vs milliseconds, daily vs monthly, fiscal vs calendar periods.
- Check rounding and precision at the right boundary. Intermediate rounding can change totals; presentation rounding should not feed downstream calculations unless explicitly required.
- Check sign conventions for credits, refunds, discounts, reversals, negative usage, overages, underprovisioned increases, and contra entries.
- Check default behavior for missing values. A zero default is often wrong when the real meaning is unknown or not applicable.
- Check forecast cutovers: actuals should not be overwritten by forecasts, and future forecasts should not leak into historical comparisons.

## Common Failure Modes

- Division by the wrong denominator, especially after filters or joins.
- Averaging averages instead of weighting by volume, cost, duration, or count.
- Summing percentages, rates, utilization values, or already-aggregated rows.
- Applying rounding before grouping or reconciliation.
- Converting units in one branch but not another.
- Treating null, missing, zero, and empty string as equivalent.
- Reusing a formula name after changing its meaning.
- Comparing fiscal and calendar periods as if they are the same.
- Using local machine time or current date in a reproducibility-sensitive calculation.

## Evidence To Collect

- Formula code and any matching documentation, dashboard, spreadsheet, SQL, or notebook.
- Minimal input rows that show both normal behavior and the failing edge case.
- Expected output calculated independently.
- Reconciliation against source totals or an authoritative external total.
- The exact command that recomputes the output.

## Minimal Test Dataset Pattern

Create a small fixture with:

- two normal rows that should aggregate cleanly
- one null or missing value
- one zero value that should stay distinct from null
- one negative, refund, credit, or reversal row if the domain allows it
- one row in a different unit, currency, or period boundary when applicable
- one row that would expose incorrect rounding or weighting
