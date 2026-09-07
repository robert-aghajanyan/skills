# Deployment and Runtime

## What to inspect

- Dockerfiles, compose files, Kubernetes manifests, Helm charts, Terraform, CI/CD workflows, process managers, systemd units, scheduler config, and environment defaults.
- Startup, readiness, liveness, shutdown, signal handling, secrets, resource limits, and rollout strategy.

## Reliability checks

- Startup should fail fast on missing required config and invalid credentials, while optional features should degrade explicitly.
- Default config should be safe for production or visibly non-production.
- Readiness should wait until the process can actually serve its critical path.
- Shutdown should stop accepting work, drain in-flight work where possible, honor deadlines, and release locks/leases.
- Resource requests/limits, worker concurrency, queue prefetch, connection pools, and timeouts should be mutually consistent.
- Rollouts should avoid downtime for schema/config changes and should have rollback paths.
- Scheduled tasks should have clear timezone, overlap, catch-up, and missed-run behavior.

## Finding patterns

- Environment variable default silently points to dev, local, or an unsafe production target.
- Container has no health/readiness checks for a long-running service.
- Worker exits on SIGTERM without acknowledging or requeueing in-flight work.
- Concurrency default exceeds database connection pool or downstream rate limit.
- Cron schedule can double-run across replicas or miss intended windows.

## Validation ideas

- Start with missing/invalid required config and assert fail-fast behavior.
- Send SIGTERM during active work and assert graceful shutdown or safe requeue.
- Validate manifests/charts with repo-native tools.
- Run a rolling-deploy compatibility check for config and schema changes.
