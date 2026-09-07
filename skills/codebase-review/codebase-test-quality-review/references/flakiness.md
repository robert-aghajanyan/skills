# Flakiness

Flaky tests reduce CI confidence even when they usually pass. Review both existing flakes and patterns likely to become flakes.

## Common Sources

- Real time, sleeps, timeouts, polling, or assumptions about scheduler speed.
- Random data without deterministic seeds or bounded uniqueness.
- Test ordering dependence from global state, shared databases, caches, environment variables, temp paths, or monkeypatches.
- Parallel test interference through ports, files, queues, buckets, tables, snapshots, or external accounts.
- Network, filesystem, or service dependencies that are not isolated or explicitly marked as integration tests.
- Async jobs where tests assert before work is complete or rely on arbitrary delays.
- Locale, timezone, platform path, line-ending, or case-sensitivity differences.

## Evidence To Look For

- Retries in CI config around tests.
- Quarantined, skipped, xfailed, focused, or order-dependent tests.
- Test helpers that sleep, use wall-clock time, or call live services.
- Random fixture generation without stable seeds.
- Shared fixture mutation or module-level state.

## Recommendations

- Freeze or inject clocks.
- Seed randomness and assert deterministic examples.
- Use temp directories, isolated databases, unique queues, and cleanup hooks.
- Await explicit completion signals instead of sleeping.
- Separate true integration tests from unit suites and make external dependencies explicit.
- Add regression tests for previously observed flakes only when the test can be made deterministic.
