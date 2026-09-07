# Hot Paths

Use this reference to identify where review effort should go first.

## Surface Map Signals

- Request handlers, routes, controllers, RPC methods, middleware, GraphQL resolvers, and public API clients.
- CLIs, scheduled jobs, report generators, workers, queue consumers, migrations, import/export jobs, startup hooks, and app bootstrap.
- User-facing flows with repeated interactions: search, list, dashboard, checkout, upload, sync, recommendation, analytics, and admin bulk actions.
- Loops over users, tenants, accounts, services, regions, files, rows, records, pages, issues, commits, objects, or external resources.
- Paths named by docs, CI, Makefiles, package scripts, cron config, deployment manifests, command registries, route tables, or telemetry.

## Prioritization

Rank paths by:

- Frequency: request volume, worker throughput, cron cadence, CLI/report usage, or repeated test execution.
- Scale variable: rows, files, tenants, accounts, regions, API pages, payload size, graph depth, or concurrent users.
- Cost per unit: database query, network call, filesystem scan, serialization, compression, model call, cloud API, or CPU-heavy transformation.
- User or business impact: latency, timeout, spend, backlog, memory pressure, failed report, slow deploy, blocked CI, or degraded interactive flow.

## Review Checks

- Nested loops where the inner operation is nontrivial or external.
- Repeated work that could be computed once per request, job, file, tenant, or batch.
- Expensive setup repeated per item instead of per process or per batch.
- Per-record serialization, JSON parsing, schema validation, regex compilation, sorting, grouping, or logging inside large loops.
- Algorithms that become quadratic or worse as input grows.
- Sync work in a request path that could safely move outside the latency-sensitive boundary.
- Test setup or fixtures that repeatedly rebuild heavy state and make CI slow.

## Evidence To Collect

- File and line for the hot path and the expensive operation.
- The scale variable and realistic bounds.
- Whether the path is latency-sensitive, throughput-sensitive, cost-sensitive, memory-sensitive, or startup-sensitive.
- Existing limits, batching, pagination, streaming, query plan, cache, or timeout behavior.
- Any telemetry, benchmark, production metric, CI timing, or report runtime that supports the impact.

## Calibration

Treat low-traffic admin code differently from customer-facing APIs, scheduled bulk jobs, and shared library code. Do not spend finding budget on tiny inefficiencies unless they are inside a proven hot path or create severe memory, cost, or timeout risk.
