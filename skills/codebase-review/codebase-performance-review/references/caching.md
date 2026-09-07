# Caching

Caching is a performance tool only when the code has repeated expensive work and clear correctness boundaries.

## When Caching Is Worth Considering

- The same expensive computation or remote call repeats within one request, job, process, or deployment.
- Inputs are stable enough that reuse is correct.
- The cache key can include tenant, user, region, environment, auth scope, version, locale, and other correctness dimensions.
- Staleness is acceptable or explicit invalidation exists.
- Memory growth is bounded by size, TTL, LRU, lifecycle, or process scope.
- Failures and partial values are not cached accidentally.

## Cache Risks

- Tenant, user, workspace, project, region, or permission leakage through incomplete keys.
- Stale authorization, pricing, feature flags, resource inventory, or external state.
- Unbounded in-memory dictionaries, global singletons, memoization, or module-level caches.
- Cache stampedes when many workers miss at once.
- Negative caching that masks transient dependency recovery.
- Caches that are bypassed in one path and used in another, creating inconsistent behavior.
- Test-only caches that make tests order-dependent.

## Alternatives Before Caching

- Remove duplicated work.
- Batch or prefetch external calls.
- Push filtering or aggregation into the database.
- Stream or chunk data.
- Move nonessential work out of a request path.
- Persist a computed artifact only if ownership and invalidation are clear.

## Review Guidance

Do not recommend caching as a generic fix. A cache recommendation must include:

- The repeated expensive operation.
- The cache scope and key.
- The invalidation or TTL strategy.
- Memory bound.
- Error behavior.
- Validation for stale data, isolation, and hit-rate impact.
