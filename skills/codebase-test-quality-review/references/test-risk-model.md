# Test Risk Model

Use risk to decide which tests matter most. Missing coverage is important only when the uncovered behavior can create a meaningful regression.

## Highest-Risk Behavior

- Auth and permissions: identity propagation, role checks, tenant boundaries, privilege escalation, default-deny behavior.
- Money, cost, quota, or billing logic: rounding, aggregation, proration, currency or unit conversion, limits, discounts, overage, savings, recommendations.
- Data transformations: joins, filters, normalization, deduplication, date windows, schema changes, migrations, and report calculations.
- Persistence and state transitions: transactions, idempotency, retries, rollbacks, soft deletes, cache invalidation, and uniqueness.
- External clients and contracts: request shape, response parsing, pagination, rate limits, authentication, timeouts, and failure mapping.
- Async jobs and queues: ordering, duplicate delivery, backoff, poison messages, partial failure, resumability, and checkpointing.
- Concurrency: locks, optimistic writes, stale reads, races, and eventual consistency.
- Error handling: invalid inputs, missing config, provider failures, degraded modes, and actionable user-facing errors.
- Config and environment parsing: defaults, precedence, validation, secrets, feature flags, and unsafe fallbacks.
- CLI/API/user-visible contracts: status codes, response schema, stdout/stderr, exit codes, generated files, and UI-visible outputs.

## Risk Signals In Code

- Complex branching with only happy-path tests.
- New code in shared helpers, middleware, serializers, query builders, or platform clients.
- Code that changed recently but tests only cover old behavior.
- Logic that depends on dates, time zones, ordering, randomness, filesystem layout, network state, or environment variables.
- Production code that has many mocks in tests but few real contract checks.
- Defensive code with no tests proving the failure mode is handled.

## Severity Calibration

- Blocker: a plausible regression could ship unnoticed and cause security exposure, data loss, financial error, broken deploy, or broad outage.
- High: a plausible regression could break a core workflow, corrupt important output, hide failures, or invalidate a CI gate.
- Medium: the suite gives weak confidence for meaningful edge cases, but the blast radius is narrower or fallback behavior exists.
- Low: maintainability or confidence issue with limited current regression risk.

Prefer fewer, sharper findings over a long list of uncovered files.
