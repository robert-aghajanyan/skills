# Reliability Baseline

Include reliability observations when architecture choices make failures hard to reason about, test, or recover from.

## Baseline Checks

Review high-risk runtime surfaces:

- external clients without timeouts, retries, backoff, circuit breaking, or clear failure contracts
- retry logic mixed with non-idempotent writes or side effects
- queues, scheduled jobs, agents, and workflows without deduplication, checkpointing, or compensation paths
- persistence code with unclear transaction boundaries, partial-write handling, or migration assumptions
- configuration defaults that silently select production resources or unsafe modes
- region/provider/client fallback behavior that is implicit, duplicated, or untested
- concurrency, caching, global state, or async code that hides ordering assumptions
- observability that cannot connect a request/job/agent step to decisions and downstream calls
- generated reports or artifacts where freshness, provenance, or input identity is not captured

## Reporting Rules

- Cite exact files and line references where reliability behavior is defined or missing.
- Explain the failure mode and the change that would trigger it.
- Distinguish confirmed missing handling from unknown behavior that needs a targeted test.
- Do not require enterprise-grade reliability for simple scripts unless the repo treats them as production paths.

## Useful Recommendations

Prefer changes that make failure behavior explicit:

- define small client contracts for timeout, retry, and error classification
- isolate idempotency keys, checkpoints, and side-effect ordering in workflow code
- centralize config parsing and fail closed on ambiguous production settings
- add focused tests for partial failures, duplicate events, stale inputs, and provider/region fallback
- preserve provenance in generated artifacts and reports when decisions depend on time-windowed inputs
