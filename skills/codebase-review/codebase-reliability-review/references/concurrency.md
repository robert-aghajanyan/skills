# Concurrency

## What to inspect

- Thread pools, async tasks, process pools, workers, queue consumers, cron overlap, web request handlers, and distributed agents.
- Shared mutable state, caches, temporary files, counters, leases, locks, and singleton resources.
- Read-modify-write operations and multi-step state transitions.

## Reliability checks

- Concurrent execution should not corrupt shared state, produce duplicate side effects, or lose updates.
- Locks should have clear scope, timeout, ownership, and release behavior on exceptions.
- Cron jobs and workers should prevent unsafe overlap or make overlap harmless.
- Async fan-out should bound concurrency and propagate cancellation/errors.
- Race-prone operations should use atomic database updates, unique constraints, compare-and-swap, leases, or transactional guards when needed.
- Temporary files and output paths should be run-scoped when jobs can overlap.

## Finding patterns

- Global mutable cache used by concurrent requests without synchronization.
- `Promise.all`, `asyncio.gather`, goroutines, or thread pools without bounded concurrency against a fragile dependency.
- Read-check-write sequence used for uniqueness without a database constraint.
- Lock acquired with no timeout or with release skipped on error.
- Scheduled job can overlap and publish duplicate results.

## Validation ideas

- Run concurrent requests/jobs against the same key and assert one final state.
- Add a stress test with many duplicate queue messages.
- Inject errors while a lock is held and assert release/lease expiry.
- Confirm concurrency limits with a fake dependency that records simultaneous calls.
