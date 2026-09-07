# Migrations

Use this reference for schema changes, data migrations, backfills, historical rewrites, report-output migrations, seed changes, and compatibility between old and new data shapes.

## Review Focus

- Identify schema version, migration order, rollback path, and whether the migration is idempotent.
- Check defaults, nullable fields, generated columns, enum changes, and type narrowing or widening.
- Verify backfills cover all existing records and do not modify records outside the intended scope.
- Check partial migration behavior. Jobs may fail mid-run or be run twice.
- Confirm readers and writers are compatible during rolling deployments.
- Check historical reports, cached snapshots, exports, and downstream consumers after schema changes.
- Verify old and new code paths do not compute the same metric with different formulas during the transition.
- Check destructive transformations, dropped columns, renamed fields, and changed units carefully.

## Common Failure Modes

- New non-null field is added with a default that looks valid but means unknown.
- Backfill only handles current records and misses archived or soft-deleted records.
- Migration is not idempotent and double-applies adjustments.
- Old reports read new columns without backfilled historical values.
- Rolling deployment lets old writers produce records new readers interpret incorrectly.
- Schema drift between database, ORM model, API schema, fixture, and report writer.
- Downstream exports silently change column meaning or units while preserving the column name.

## Evidence To Collect

- Migration files, model/schema changes, readers, writers, seed data, fixtures, and downstream reports.
- Row counts before and after migration.
- Null counts and default-value counts for new or changed fields.
- Checksums or aggregate totals before and after backfills when practical.
- Replay or rollback behavior if supported.

## Minimal Test Dataset Pattern

Create fixtures for:

- one fully populated current record
- one historical record missing newly required fields
- one null or unknown value
- one soft-deleted, archived, or excluded record if the domain has them
- one record that should not be migrated
- a repeated migration run to prove idempotence
