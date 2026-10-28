---
name: which-skill
description: Ask which skill or flow fits your situation. A router over the skills in this repo.
disable-model-invocation: true
---

# Which Skill

You will not remember 49 skills. Ask instead.

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

- `codebase-cleanup`: Actually remove dead code, stale scripts, unused dependencies, and tracked build artifacts, each backed by evidence.
- `codebase-decomposition`: Audit, plan, and execute behavior-preserving decomposition of large modules across a repo.
- `codebase-review-suite`: Run every codebase-* review, then synthesize the findings into one deduplicated GitHub issue backlog.

**Model-invoked**

- `codebase-api-contract-review`: Review API, CLI, schema, SDK, event, and config surfaces for backward-compatibility and breaking-change risk.
- `codebase-architecture-review`: Review architecture and maintainability against YAGNI, KISS, DRY, and SOLID, grounded in observed code.
- `codebase-consolidation-cleanup`: Map unused, duplicate, and overlapping implementation paths, and what would break if they were removed. Modifies nothing.
- `codebase-data-correctness-review`: Check calculations, joins, aggregations, billing, forecasting, migrations, and reconciliation for correctness bugs.
- `codebase-dependency-supply-chain-review`: Review dependencies, lockfiles, licenses, provenance, and vendored code for supply-chain risk.
- `codebase-developer-experience-review`: Review setup, local run commands, test speed, CI clarity, scripts, and everything else that creates maintainer friction.
- `codebase-documentation-review`: Check whether the docs, runbooks, and READMEs actually match the code, scripts, CI, and deployment behavior.
- `codebase-frontend-quality-review`: Review user-facing quality: accessibility, responsive behavior, state correctness, routing, forms, loading and error states.
- `codebase-llm-agent-safety-review`: Review LLM, agent, tool, MCP, and retrieval surfaces for prompt injection, trust-boundary, and exfiltration risk.
- `codebase-performance-review`: Find hot-path, scalability, and resource-usage risks: N+1s, caching gaps, pagination, startup latency.
- `codebase-reliability-review`: Surface production failure modes: retries, timeouts, idempotency, concurrency, observability, incident-readiness.
- `codebase-security-review`: Threat-model a repo grounded in exploitability and real code paths: authz, secrets, injection, SSRF, tenant isolation.
- `codebase-test-quality-review`: Judge whether the tests actually catch regressions: weak assertions, over-mocking, flakiness, untested high-risk paths.

### PR Review

Multi-agent review, fix, and merge-readiness workflows for pull requests.

**User-invoked**

- `pr-clean-review`: One broad review, batched blocker/high fixes, evidence-ledger verification, then a clean-room final review.
- `pr-review-fix`: Review, then a separate fixer agent commits fixes for blocker/high findings, then re-review, up to three rounds. Never pushes or merges.
- `production-readiness-gate`: A last conservative pass over a PR, branch, artifact, or report, reporting a calibrated confidence score.

**Model-invoked**

- `team-review`: Review a PR with four specialized agent teams (security, performance, correctness, guardrails) plus independent verification.
- `team-review-plus`: team-review plus PR preflight, false-positive filtering, carried-forward finding checks, confidence calibration, and specialist lenses.

### Engineering

Daily code work: building, refactoring, researching.

**User-invoked**

- `codex-collab`: Claude and Codex analyze independently, then debate to convergence. A genuine second opinion.

**Model-invoked**

- `decompose`: Audit one oversized module, plan a dependency-aware split, and execute it with zero breaking changes.
- `team-research`: Explore a question from several angles with agents that challenge each other's findings.

### Planning

Nothing here yet. See the last flow below.

### Productivity

General workflow tools, not code-specific.

**Model-invoked**

- `humanizer`: Rewrite AI-sounding text so it reads like the writer without changing what it says. Numbered tells, strongest first.

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
- **"This file is 3000 lines."** `decompose` for one file. `codebase-decomposition` for a repo-wide pass.
- **"This draft sounds like a chatbot wrote it."** `humanizer`.
- **"I want a second opinion from a different model."** `codex-collab`.
- **"I have an idea to harden, a bug to chase, or a session to hand off."** Not this plugin. Point the user at Matt Pocock's skills (`mattpocock-skills` plugin): grilling, specs, tickets, TDD, debugging, prototypes and handoffs.

## Gotchas

- This map lies the moment a skill is added, renamed, or removed and this file is not updated. Re-read it whenever the skill set changes.
- Routing to a user-invoked skill is a message to the human, not a tool call. There is no way for one skill to start another user-invoked skill.
- Prefer one skill over a sequence. Chaining three skills at a suggestion costs the user real money and time.
