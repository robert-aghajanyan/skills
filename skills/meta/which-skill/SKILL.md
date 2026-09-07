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
- `mp-implement`: Build the work described by a spec or set of tickets, driving TDD at pre-agreed seams and closing out with a review before committing.

**Model-invoked**

- `decompose`: Audit one oversized module, plan a dependency-aware split, and execute it with zero breaking changes.
- `mp-codebase-design`: Shared discipline and vocabulary for designing deep modules: small interfaces, clean seams, testable through the interface.
- `mp-diagnosing-bugs`: Disciplined loop for hard bugs and performance regressions: build a feedback loop that goes red, minimise, hypothesise, instrument, fix, regression-test.
- `mp-prototype`: Build a throwaway prototype to answer a design question: a shareable HTML file for state and logic, or several toggleable UI variations.
- `mp-resolving-merge-conflicts`: Work an in-progress merge or rebase hunk by hunk, resolving by intent traced to each side primary source, then finish. Never --abort.
- `mp-tdd`: Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- `mp-wizard`: Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning, credentials, dashboards, one-off migrations.
- `team-research`: Explore a question from several angles with agents that challenge each other's findings.

### Planning

Stress-testing plans and turning them into specs, issues, and handoffs.

**User-invoked**

- `mp-grill-me`: Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved.
- `mp-grill-with-docs`: Grilling that also builds the domain model, sharpening terminology and updating CONTEXT.md and ADRs inline.
- `mp-improve-codebase-architecture`: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- `mp-setup`: Scaffold the per-repo configuration the other skills assume: issue tracker, triage label vocabulary, and domain doc layout. Run once per repo.
- `mp-to-spec`: Turn the current conversation into a spec and publish it to the project issue tracker.
- `mp-to-tickets`: Break any plan, spec, or conversation into tracer-bullet tickets, each declaring its blocking edges.
- `mp-triage`: Move issues and external PRs through a state machine of triage roles: categorise, verify, grill if needed, and write agent-ready briefs.
- `mp-wayfinder`: Plan a chunk of work larger than one agent session as a map of decision tickets on the tracker, resolved one at a time until the way is clear.

**Model-invoked**

- `mp-domain-modeling`: Actively build and sharpen the project domain model by challenging terms, stress-testing with scenarios, and updating CONTEXT.md and ADRs inline.
- `mp-grilling`: Interview the user in rounds, asking the whole settled frontier of the design tree at once, each question with a recommended answer.

### Productivity

General workflow tools, not code-specific.

**User-invoked**

- `mp-handoff`: Compact the current conversation into a handoff document so another agent can continue the work.
- `mp-teach`: Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace.
- `mp-to-questionnaire`: Turn a decision you cannot answer alone into a Markdown questionnaire for the one person who can, filled in async or worked through together.
- `mp-wait-what`: Fire this the moment a message does not land. The agent re-pitches it with the context you are missing, in plain English.

### Meta

Skills for building skills and navigating this repo.

**User-invoked**

- `skill-builder`: Create a well-designed skill from scratch, with the frontmatter, structure, and validation this repo expects.

**Model-invoked**

- `mp-writing-for-agents`: Writing documents for agents: skills, AGENTS.md and CLAUDE.md, and any doc an agent reaches by a pointer.
- `optimize-prompt-caching`: Audit and optimize LLM prompt caching in any codebase: cache_control breakpoints, compaction, cost and latency wins.

## Common flows

- **"I inherited this repo and don't trust it."** `codebase-review-suite`, which fans out to the whole `codebase-review` bucket and files one deduplicated backlog.
- **"One dimension only."** Call the single `codebase-*-review` skill for it. Cheaper and sharper than the suite.
- **"I have a PR and want findings."** `team-review`. Want the findings fixed too? `pr-review-fix`. Want it fixed and re-reviewed until clean? `pr-clean-review`.
- **"I'm about to ship and I'm nervous."** `production-readiness-gate`, last.
- **"I have an idea, not a plan."** `mp-grill-me` to harden it, then `mp-to-spec`, then `mp-to-tickets`, then `mp-implement`.
- **"The work is bigger than one session."** `mp-wayfinder` first: it maps the decisions before anyone writes tickets.
- **"Something is broken and I don't know why."** `mp-diagnosing-bugs`. Do not reach for a review skill; reviews find risks, not this bug.
- **"I'm mid-merge and it's a mess."** `mp-resolving-merge-conflicts`.
- **"I don't know what this module should look like."** `mp-codebase-design` for the vocabulary, `mp-prototype` to answer it empirically.
- **"This file is 3000 lines."** `decompose` for one file. `codebase-decomposition` for a repo-wide pass.
- **"I'm running out of context."** `mp-handoff`.
- **"I did not understand what you just said."** `mp-wait-what`.
- **"I want a second opinion from a different model."** `codex-collab`.

## First run in a repo

`mp-setup` configures the issue tracker, triage labels, and domain doc layout that `mp-to-spec`, `mp-to-tickets`, `mp-triage`, and `mp-wayfinder` all assume. Tell the user to run `/mp-setup` once per repo before those four.

## Gotchas

- This map lies the moment a skill is added, renamed, or removed and this file is not updated. Re-read it whenever the skill set changes.
- Routing to a user-invoked skill is a message to the human, not a tool call. There is no way for one skill to start another user-invoked skill.
- Prefer one skill over a sequence. Chaining three skills at a suggestion costs the user real money and time.
- The `mp-` skills are ported from github.com/mattpocock/skills and follow that repo's conventions. The rest are this repo's own.
