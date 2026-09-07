---
name: which-skill
description: Ask which skill or flow fits your situation. A router over the skills in this repo.
disable-model-invocation: true
---

# Which Skill

You will not remember 34 skills. Ask instead.

Read the user's situation, then point them at one skill, or at a short sequence of them. Name the skill and say why it fits in one line. If nothing fits, say so plainly rather than forcing a match.

## How to answer

1. If the situation is clear, name **one** skill and stop. Do not list alternatives the user did not ask for.
2. If the situation is a multi-step flow, give the sequence in order, one line each.
3. If the situation is ambiguous, ask **one** question that would settle it, then answer.

A skill marked user-invoked below can only be started by the human typing its name. Never try to call one with the Skill tool: tell the user to run it. Model-invoked skills you may call directly with the Skill tool, one skill per call.

## The map

### Codebase Review

Dimension-specific deep reviews of an existing repository.

**User-invoked**

- `codebase-review-suite`: Run every codebase-* review, then synthesize the findings into one deduplicated GitHub issue backlog.
- `codebase-cleanup`: Actually remove dead code, stale scripts, unused dependencies, and tracked build artifacts, each backed by evidence.
- `codebase-decomposition`: Audit, plan, and execute behavior-preserving decomposition of large modules across a repo.

**Model-invoked**

- `codebase-security-review`: Threat-model a repo grounded in exploitability and real code paths: authz, secrets, injection, SSRF, tenant isolation.
- `codebase-performance-review`: Find hot-path, scalability, and resource-usage risks: N+1s, caching gaps, pagination, startup latency.
- `codebase-architecture-review`: Review architecture and maintainability against YAGNI, KISS, DRY, and SOLID, grounded in observed code.
- `codebase-reliability-review`: Surface production failure modes: retries, timeouts, idempotency, concurrency, observability, incident-readiness.
- `codebase-data-correctness-review`: Check calculations, joins, aggregations, billing, forecasting, migrations, and reconciliation for correctness bugs.
- `codebase-dependency-supply-chain-review`: Review dependencies, lockfiles, licenses, provenance, and vendored code for supply-chain risk.
- `codebase-documentation-review`: Check whether the docs, runbooks, and READMEs actually match the code, scripts, CI, and deployment behavior.
- `codebase-frontend-quality-review`: Review user-facing quality: accessibility, responsive behavior, state correctness, routing, forms, loading and error states.
- `codebase-llm-agent-safety-review`: Review LLM, agent, tool, MCP, and retrieval surfaces for prompt injection, trust-boundary, and exfiltration risk.
- `codebase-developer-experience-review`: Review setup, local run commands, test speed, CI clarity, scripts, and everything else that creates maintainer friction.
- `codebase-api-contract-review`: Review API, CLI, schema, SDK, event, and config surfaces for backward-compatibility and breaking-change risk.
- `codebase-test-quality-review`: Judge whether the tests actually catch regressions: weak assertions, over-mocking, flakiness, untested high-risk paths.
- `codebase-consolidation-cleanup`: Map unused, duplicate, and overlapping implementation paths, and what would break if they were removed. Modifies nothing.

### PR Review

Multi-agent review, fix, and merge-readiness workflows for pull requests.

**User-invoked**

- `team-review-plus`: team-review plus PR preflight, false-positive filtering, carried-forward finding checks, confidence calibration, and specialist lenses.
- `pr-clean-review`: One broad review, batched blocker/high fixes, evidence-ledger verification, then a clean-room final review.
- `pr-review-fix`: Review, then a separate fixer agent commits fixes for blocker/high findings, then re-review, up to three rounds. Never pushes or merges.
- `production-readiness-gate`: A last conservative pass over a PR, branch, artifact, or report, reporting a calibrated confidence score.

**Model-invoked**

- `team-review`: Review a PR with four specialized agent teams (security, performance, correctness, guardrails) plus independent verification.

### Engineering

Daily code work: building, refactoring, researching.

**User-invoked**

- `codex-collab`: Claude and Codex analyze independently, then debate to convergence. A genuine second opinion.

**Model-invoked**

- `decompose`: Audit one oversized module, plan a dependency-aware split, and execute it with zero breaking changes.
- `mp-tdd`: Build features and fix bugs test-first, one vertical slice at a time.
- `team-research`: Explore a question from several angles with agents that challenge each other's findings.

### Planning

Stress-testing plans and turning them into specs, issues, and handoffs.

**User-invoked**

- `mp-grill-me`: Get relentlessly interviewed about a plan, one question at a time, until every branch of the design tree is resolved.
- `mp-grill-with-docs`: Grilling that also challenges your plan against the domain model, sharpening terminology and updating CONTEXT.md and ADRs inline.
- `mp-improve-codebase-architecture`: Find deepening opportunities in a codebase, informed by CONTEXT.md and the decisions in docs/adr/.
- `mp-to-prd`: Turn the current conversation into a PRD and publish it to the project issue tracker.
- `mp-to-issues`: Break a plan, spec, or PRD into independently-grabbable issues as tracer-bullet vertical slices.
- `mp-handoff`: Compact the current conversation into a handoff document, saved outside the workspace, so the next session can continue.

### Meta

Skills for building skills and navigating this repo.

**User-invoked**

- `skill-builder`: Create a well-designed skill from scratch, with the frontmatter, structure, and validation this repo expects.

**Model-invoked**

- `optimize-prompt-caching`: Audit and optimize LLM prompt caching in any codebase: cache_control breakpoints, compaction, cost and latency wins.

## Common flows

- **"I inherited this repo and don't trust it."** `codebase-review-suite`, which fans out to the whole `codebase-review` bucket and files one deduplicated backlog.
- **"One dimension only."** Call the single `codebase-*-review` skill for it. Cheaper and sharper than the suite.
- **"I have a PR and want findings."** `team-review`. Want the findings fixed too? `pr-review-fix`. Want it fixed and re-reviewed until clean? `pr-clean-review`.
- **"I'm about to ship and I'm nervous."** `production-readiness-gate`, last.
- **"I have an idea, not a plan."** `mp-grill-me` to harden it, then `mp-to-prd`, then `mp-to-issues`.
- **"This file is 3000 lines."** `decompose` for one file. `codebase-decomposition` for a repo-wide pass.
- **"I'm running out of context."** `mp-handoff`.
- **"I want a second opinion from a different model."** `codex-collab`.

## Gotchas

- This map lies the moment a skill is added, renamed, or removed and this file is not updated. Re-read it whenever the skill set changes.
- Routing to a user-invoked skill is a message to the human, not a tool call. There is no way for one skill to start another user-invoked skill.
- Prefer one skill over a sequence. Chaining three skills at a suggestion costs the user real money and time.
