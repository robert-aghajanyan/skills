# Timeouts and Retries

## What to inspect

- Outbound HTTP, RPC, SDK, database, cache, queue, object-storage, and filesystem calls.
- Long-running loops, polling, batch jobs, stream consumers, and background workers.
- Retry libraries, hand-written retry loops, SDK retry defaults, queue redelivery behavior, and cron reruns.
- Cancellation propagation: request context, process signals, job deadlines, and user aborts.

## Reliability checks

- Every remote dependency call should have a finite timeout or deadline that matches the caller's SLA.
- Retries should be bounded by attempt count, elapsed time, and caller cancellation.
- Retryable errors should be explicit. Do not retry validation errors, authorization failures, permanent not-found states, or non-idempotent writes without a dedupe boundary.
- Backoff should include jitter when many clients can fail together.
- Nested retries should not multiply into long tail latency or retry storms.
- Retry exhaustion should return or record an actionable error, not silently continue with partial output.
- Polling loops should include max duration, interval bounds, and cancellation.

## Finding patterns

- Missing timeout on a production network call.
- SDK default timeout or retry policy relied on without being documented or configured.
- Infinite loop or unbounded retry around a dependency outage.
- Retrying a create/update operation that can duplicate side effects.
- Catch-all exception handling that retries bugs or bad inputs.

## Validation ideas

- Unit test retryable vs non-retryable errors.
- Simulate a dependency that hangs longer than the configured timeout.
- Simulate retry exhaustion and assert user-facing error, logs, metrics, and cleanup.
- Verify total elapsed retry time stays within the job/request budget.
