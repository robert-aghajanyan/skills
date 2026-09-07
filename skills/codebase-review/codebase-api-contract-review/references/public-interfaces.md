# Public Interfaces

Public interfaces are any behavior another person, service, package, plugin, script, generated client, or documented example can depend on. Include intentionally public surfaces and "semi-public" internal surfaces that are used across repos, CI, dashboards, deployments, or automation.

## Map

Capture:

- HTTP/RPC routes, methods, auth expectations, status codes, headers, pagination, filtering, error shapes, idempotency, rate limits, and request/response fields.
- SDK/package exports, module paths, class/function names, argument defaults, return types, thrown errors, async behavior, and side effects.
- Plugin hooks, extension points, manifest fields, lifecycle callbacks, capability names, and host/plugin version constraints.
- Generated clients and examples that users copy into scripts, docs, notebooks, dashboards, runbooks, or CI jobs.
- Public files: OpenAPI, GraphQL, protobuf, AsyncAPI, JSON Schema, README examples, changelogs, sample configs, and generated docs.

## Red Flags

- Renamed or removed fields, routes, exports, hooks, enum values, status codes, headers, or error codes.
- New required request fields, stricter validation, narrower accepted formats, shorter limits, or removed coercion.
- Changed defaults, pagination order, nullability, timestamp format, sorting, filtering, auth scope, timeout, retry, or idempotency behavior.
- Same endpoint or export name with changed semantics.
- Public docs or examples that still show the old behavior.
- Version number, changelog, OpenAPI spec, generated SDK, or migration guide not updated with the behavior change.

## Compatibility Strategies

- Add new fields or endpoints while keeping old ones, then deprecate with a documented timeline.
- Accept old and new input shapes during migration; emit the canonical new shape only when consumers are ready.
- Keep aliases for renamed exports, CLI flags, config keys, routes, enum values, and plugin hooks.
- Version the contract when compatibility cannot be preserved, and make routing or negotiation explicit.
- Update generated clients, docs, examples, and contract tests in the same change as the behavior change.

## Evidence

Use exact files and lines from route definitions, exported modules, schemas, docs, tests, generated clients, changelogs, and consumer call sites. When a consumer is inferred from naming or documentation rather than confirmed usage, mark the risk conditional.
