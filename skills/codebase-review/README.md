# Codebase Review

Dimension-specific deep reviews of an existing repository.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[codebase-cleanup](./codebase-cleanup/SKILL.md)**: Actually remove dead code, stale scripts, unused dependencies, and tracked build artifacts, each backed by evidence.
- **[codebase-decomposition](./codebase-decomposition/SKILL.md)**: Audit, plan, and execute behavior-preserving decomposition of large modules across a repo.
- **[codebase-review-suite](./codebase-review-suite/SKILL.md)**: Run every codebase-* review, then synthesize the findings into one deduplicated GitHub issue backlog.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[codebase-api-contract-review](./codebase-api-contract-review/SKILL.md)**: Review API, CLI, schema, SDK, event, and config surfaces for backward-compatibility and breaking-change risk.
- **[codebase-architecture-review](./codebase-architecture-review/SKILL.md)**: Review architecture and maintainability against YAGNI, KISS, DRY, and SOLID, grounded in observed code.
- **[codebase-consolidation-cleanup](./codebase-consolidation-cleanup/SKILL.md)**: Map unused, duplicate, and overlapping implementation paths, and what would break if they were removed. Modifies nothing.
- **[codebase-data-correctness-review](./codebase-data-correctness-review/SKILL.md)**: Check calculations, joins, aggregations, billing, forecasting, migrations, and reconciliation for correctness bugs.
- **[codebase-dependency-supply-chain-review](./codebase-dependency-supply-chain-review/SKILL.md)**: Review dependencies, lockfiles, licenses, provenance, and vendored code for supply-chain risk.
- **[codebase-developer-experience-review](./codebase-developer-experience-review/SKILL.md)**: Review setup, local run commands, test speed, CI clarity, scripts, and everything else that creates maintainer friction.
- **[codebase-documentation-review](./codebase-documentation-review/SKILL.md)**: Check whether the docs, runbooks, and READMEs actually match the code, scripts, CI, and deployment behavior.
- **[codebase-frontend-quality-review](./codebase-frontend-quality-review/SKILL.md)**: Review user-facing quality: accessibility, responsive behavior, state correctness, routing, forms, loading and error states.
- **[codebase-llm-agent-safety-review](./codebase-llm-agent-safety-review/SKILL.md)**: Review LLM, agent, tool, MCP, and retrieval surfaces for prompt injection, trust-boundary, and exfiltration risk.
- **[codebase-performance-review](./codebase-performance-review/SKILL.md)**: Find hot-path, scalability, and resource-usage risks: N+1s, caching gaps, pagination, startup latency.
- **[codebase-reliability-review](./codebase-reliability-review/SKILL.md)**: Surface production failure modes: retries, timeouts, idempotency, concurrency, observability, incident-readiness.
- **[codebase-security-review](./codebase-security-review/SKILL.md)**: Threat-model a repo grounded in exploitability and real code paths: authz, secrets, injection, SSRF, tenant isolation.
- **[codebase-test-quality-review](./codebase-test-quality-review/SKILL.md)**: Judge whether the tests actually catch regressions: weak assertions, over-mocking, flakiness, untested high-risk paths.
