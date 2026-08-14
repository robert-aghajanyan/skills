# Observability

## What to inspect

- Logs, metrics, traces, audit events, health checks, readiness checks, job status, exit codes, dashboards, and alerts.
- Error boundaries, retry exhaustion paths, partial failures, background task failures, and startup/shutdown events.

## Reliability checks

- Logs should include stable identifiers: request ID, job ID, tenant/account, resource key, dependency name, attempt number, and final outcome where relevant.
- Expected operational failures should be visible at the right severity and should not be swallowed.
- Retry exhaustion, dead-lettering, skipped work, degraded mode, and partial output should emit metrics or structured events.
- Health checks should distinguish process-alive from ready-to-serve when dependencies or warmup matter.
- CLIs and pipelines should use meaningful exit codes and machine-readable output when automation depends on them.
- Sensitive data should not be logged while adding reliability context.

## Finding patterns

- Background worker catches and logs an exception but reports success.
- Retry loop logs every attempt but not the final exhausted failure.
- Health endpoint returns healthy before required dependencies/config are ready.
- Incident triage would require reading raw artifacts because no summary metric/status exists.
- CLI prints an error but exits zero.

## Validation ideas

- Force dependency outage and assert logs, metrics, status, and exit code.
- Test health/readiness transitions during startup, degraded dependency state, and shutdown.
- Verify structured log fields are present in failure paths.
- Confirm alertable metrics for queue lag, job failure, retry exhaustion, and stale scheduled work where applicable.
