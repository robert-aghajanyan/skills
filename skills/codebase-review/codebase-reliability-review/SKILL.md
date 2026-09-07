---
name: codebase-reliability-review
description: Reviews production reliability risks across repositories, services, pipelines, CLIs, agents, workers, APIs, and distributed systems. Use when the user asks for production-readiness, reliability, resilience, failure-mode analysis, retries, timeouts, idempotency, concurrency, observability, operational risk, or incident-readiness review.
---

# Reliability Review

Review whether a system behaves predictably under failures, retries, concurrency, partial outages, bad inputs, slow dependencies, and operational incidents.

## Workflow

1. Build a runtime map from observed evidence: services, workers, jobs, CLIs, APIs, queues, databases, external dependencies, scheduled tasks, and deployment/runtime config.
2. Identify failure boundaries: network calls, database writes, file writes, long-running jobs, retries, caches, locks, concurrency, and background processing.
3. Review the relevant risk areas, loading only the references that apply:
   - [Timeouts and retries](references/timeouts-retries.md)
   - [Idempotency](references/idempotency.md)
   - [Concurrency](references/concurrency.md)
   - [Data consistency](references/data-consistency.md)
   - [Observability](references/observability.md)
   - [Deployment and runtime](references/deployment-runtime.md)
   - [Output format](references/output-format.md)
4. For every finding, include the affected file and line, failure scenario, user or business impact, recommended fix, and validation test.
5. Avoid speculative architecture. If evidence is missing, list it as an open question instead of filling gaps with assumptions.

Use `python "${CLAUDE_SKILL_DIR}/scripts/reliability_inventory.py" <repo>` when a deterministic first-pass inventory of calls, retries, timeouts, workers, logging, config defaults, and health checks would speed up the review. The helper skips sensitive dotenv files and redacts secret-like assignments in output.

## Validation

- Tie findings to concrete files and lines before reporting them.
- Prefer repo-native tests, linters, deployment validators, or smoke checks for validation commands.
- When recommending new tests, make them exercise the failure mode directly: timeout, retry exhaustion, duplicate delivery, partial write, concurrent execution, bad input, dependency outage, or shutdown.
- If no high-risk issues are found, still report residual risk and the evidence reviewed.

## Gotchas

- Do not recommend queues, sagas, distributed locks, or service mesh features unless the code clearly needs that machinery.
- A retry without a timeout, idempotency boundary, or retry budget is usually a reliability risk, not a resilience feature.
- Missing observability is a finding only when it would materially slow detection, triage, rollback, or customer-impact assessment.
