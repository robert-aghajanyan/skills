---
name: codebase-performance-review
description: Review repositories for performance, scalability, resource usage, and hot-path efficiency risks. Use when the user asks for performance review, scalability review, hot-path analysis, N+1 calls, memory usage, expensive loops, caching, pagination, startup latency, slow tests, inefficient data processing, or code that may not scale.
---

# Performance Review

Review whether a repository will stay efficient as traffic, data volume, concurrency, and input size grow. Focus on confirmed hot paths first, then mark lower-confidence risks that need measurement.

## Workflow

1. Build a performance surface map: APIs, CLIs, jobs, workers, startup paths, reports, batch processors, external clients, database access, file IO, and user-facing flows.
2. Prioritize hot paths and scale-sensitive paths before low-traffic code. Use observed routing, schedules, command docs, CI, telemetry hooks, and data-flow evidence to rank paths.
3. Review the relevant risk areas, loading only the references that apply:
   - [Hot paths](references/hot-paths.md)
   - [IO and network](references/io-and-network.md)
   - [Data processing](references/data-processing.md)
   - [Caching](references/caching.md)
   - [Resource usage](references/resource-usage.md)
   - [Output format](references/output-format.md)
4. For every finding, include file and line evidence, triggering input or traffic pattern, likely impact, confidence level, recommended fix, and validation method.
5. Separate confirmed performance risks from hypotheses needing measurement. Do not turn weak suspicions into findings.
6. Do not recommend caching or concurrency unless the code clearly benefits and invalidation, ordering, retry, timeout, and error behavior are addressed.

Use `python "${CLAUDE_SKILL_DIR}/scripts/performance_inventory.py" <repo>` when a deterministic first-pass inventory would speed up mapping entrypoints, loops over external calls, pagination, large data processing, cache usage, sleeps/retries, and dependency-heavy startup paths. The helper is read-only and skips common generated, vendored, virtualenv, and sensitive dotenv files.

## Output

Use [references/output-format.md](references/output-format.md). Lead with the highest-impact confirmed risks, then quick wins and measurement gaps.

## Validation

- Prefer repo-native benchmarks, profilers, load tests, integration tests, query plans, trace spans, or focused timing scripts.
- If recommending a code change, name the metric that should improve and the input scale that proves it.
- If measurement is unavailable, say exactly what needs to be instrumented before the risk can be confirmed.
- For LLM API cost or latency findings caused by unstable prompts, tool definitions, compaction, or missing cache metrics, use `codebase-prompt-caching-optimization` as the follow-up implementation workflow.

## Gotchas

- Faster-looking code is not always better. Avoid broad rewrites unless the current path is measurably slow or clearly unbounded.
- Caching can hide correctness bugs, stale data, tenant leakage, memory growth, and thundering-herd behavior.
- Parallelism can amplify rate limits, database pressure, memory use, and failure fanout.
- Excessive logging, serialization, or object construction in a hot path can matter as much as the obvious network or query call.
