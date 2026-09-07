# Data Consistency

## What to inspect

- Database transactions, migrations, file writes, object storage uploads, cache invalidation, output generation, and multi-system updates.
- Paths that write more than one record, table, file, or external system.
- Recovery behavior after partial failure, process kill, timeout, or retry exhaustion.

## Reliability checks

- Related database writes should be in a transaction unless partial state is explicitly valid and recoverable.
- External side effects should be ordered so the system can reconcile or resume after a crash.
- Caches should have invalidation or expiry behavior that matches consistency needs.
- Output files should avoid partially written visible artifacts; prefer temp file plus atomic rename when supported.
- Migrations and schema changes should be forward/backward compatible with rolling deploys when applicable.
- Compensation or cleanup should be explicit for operations that cannot be atomic.

## Finding patterns

- State is marked complete before all required side effects succeed.
- Multiple writes can leave orphaned records on failure.
- Cache update succeeds while database write fails, or the reverse, with no reconciliation.
- Report/output path is visible while still being written.
- Migration requires all instances to restart simultaneously.

## Validation ideas

- Inject failure after each write step and verify recovery or rollback.
- Kill the process mid-output and assert no corrupt final artifact is consumed.
- Test stale cache behavior after failed writes.
- Run migration compatibility checks against old and new application code when possible.
