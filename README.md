# Agent Skills

34 agent skills for Claude Code, shipped as one installable plugin. Deep codebase review across thirteen dimensions, multi-agent PR review and fix loops, plan stress-testing, and the tooling to write more skills.

Skills are self-contained folders of instructions, scripts, and reference docs that Claude loads on demand, either because you typed the name or because what you asked for matched the skill's triggers.

## Install

```bash
claude plugin marketplace add robert-aghajanyan/skills
claude plugin install robert-aghajanyan-skills@robert-aghajanyan
```

Or, from inside a session:

```
/plugin marketplace add robert-aghajanyan/skills
/plugin install robert-aghajanyan-skills@robert-aghajanyan
```

One plugin ships the whole promoted set. Update it with `claude plugin marketplace update robert-aghajanyan`.

**Try it without installing:**

```bash
git clone https://github.com/robert-aghajanyan/skills
claude --plugin-dir ./skills
```

## Start here

Not sure which one you want? Run `/which-skill` and describe your situation. It routes over every skill below.

## Invocation

Every skill is one of two kinds, and the distinction matters:

- **User-invoked** (15 of 34): reachable only when **you type the name**. Everything that deletes, rewrites, commits, publishes, or spends a lot of tokens is user-invoked, so Claude cannot start it on a hunch.
- **Model-invoked** (19 of 34): Claude can reach for these on its own when what you asked for matches. All of them are read-and-report.

See [.agents/invocation.md](.agents/invocation.md) for the rules, and [ADR 0002](.agents/adr/0002-bucket-folders-and-the-promoted-set.md) for why the repo is laid out in buckets.

## Skills

### Codebase Review

Dimension-specific deep reviews of an existing repository. ([bucket README](skills/codebase-review/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`codebase-cleanup`](skills/codebase-review/codebase-cleanup/SKILL.md) | user | Actually remove dead code, stale scripts, unused dependencies, and tracked build artifacts, each backed by evidence. |
| [`codebase-decomposition`](skills/codebase-review/codebase-decomposition/SKILL.md) | user | Audit, plan, and execute behavior-preserving decomposition of large modules across a repo. |
| [`codebase-review-suite`](skills/codebase-review/codebase-review-suite/SKILL.md) | user | Run every codebase-* review, then synthesize the findings into one deduplicated GitHub issue backlog. |
| [`codebase-api-contract-review`](skills/codebase-review/codebase-api-contract-review/SKILL.md) | model | Review API, CLI, schema, SDK, event, and config surfaces for backward-compatibility and breaking-change risk. |
| [`codebase-architecture-review`](skills/codebase-review/codebase-architecture-review/SKILL.md) | model | Review architecture and maintainability against YAGNI, KISS, DRY, and SOLID, grounded in observed code. |
| [`codebase-consolidation-cleanup`](skills/codebase-review/codebase-consolidation-cleanup/SKILL.md) | model | Map unused, duplicate, and overlapping implementation paths, and what would break if they were removed. Modifies nothing. |
| [`codebase-data-correctness-review`](skills/codebase-review/codebase-data-correctness-review/SKILL.md) | model | Check calculations, joins, aggregations, billing, forecasting, migrations, and reconciliation for correctness bugs. |
| [`codebase-dependency-supply-chain-review`](skills/codebase-review/codebase-dependency-supply-chain-review/SKILL.md) | model | Review dependencies, lockfiles, licenses, provenance, and vendored code for supply-chain risk. |
| [`codebase-developer-experience-review`](skills/codebase-review/codebase-developer-experience-review/SKILL.md) | model | Review setup, local run commands, test speed, CI clarity, scripts, and everything else that creates maintainer friction. |
| [`codebase-documentation-review`](skills/codebase-review/codebase-documentation-review/SKILL.md) | model | Check whether the docs, runbooks, and READMEs actually match the code, scripts, CI, and deployment behavior. |
| [`codebase-frontend-quality-review`](skills/codebase-review/codebase-frontend-quality-review/SKILL.md) | model | Review user-facing quality: accessibility, responsive behavior, state correctness, routing, forms, loading and error states. |
| [`codebase-llm-agent-safety-review`](skills/codebase-review/codebase-llm-agent-safety-review/SKILL.md) | model | Review LLM, agent, tool, MCP, and retrieval surfaces for prompt injection, trust-boundary, and exfiltration risk. |
| [`codebase-performance-review`](skills/codebase-review/codebase-performance-review/SKILL.md) | model | Find hot-path, scalability, and resource-usage risks: N+1s, caching gaps, pagination, startup latency. |
| [`codebase-reliability-review`](skills/codebase-review/codebase-reliability-review/SKILL.md) | model | Surface production failure modes: retries, timeouts, idempotency, concurrency, observability, incident-readiness. |
| [`codebase-security-review`](skills/codebase-review/codebase-security-review/SKILL.md) | model | Threat-model a repo grounded in exploitability and real code paths: authz, secrets, injection, SSRF, tenant isolation. |
| [`codebase-test-quality-review`](skills/codebase-review/codebase-test-quality-review/SKILL.md) | model | Judge whether the tests actually catch regressions: weak assertions, over-mocking, flakiness, untested high-risk paths. |

### PR Review

Multi-agent review, fix, and merge-readiness workflows for pull requests. ([bucket README](skills/pr-review/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`pr-clean-review`](skills/pr-review/pr-clean-review/SKILL.md) | user | One broad review, batched blocker/high fixes, evidence-ledger verification, then a clean-room final review. |
| [`pr-review-fix`](skills/pr-review/pr-review-fix/SKILL.md) | user | Review, then a separate fixer agent commits fixes for blocker/high findings, then re-review, up to three rounds. Never pushes or merges. |
| [`production-readiness-gate`](skills/pr-review/production-readiness-gate/SKILL.md) | user | A last conservative pass over a PR, branch, artifact, or report, reporting a calibrated confidence score. |
| [`team-review`](skills/pr-review/team-review/SKILL.md) | model | Review a PR with four specialized agent teams (security, performance, correctness, guardrails) plus independent verification. |
| [`team-review-plus`](skills/pr-review/team-review-plus/SKILL.md) | model | team-review plus PR preflight, false-positive filtering, carried-forward finding checks, confidence calibration, and specialist lenses. |

### Engineering

Daily code work: building, refactoring, researching. ([bucket README](skills/engineering/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`codex-collab`](skills/engineering/codex-collab/SKILL.md) | user | Claude and Codex analyze independently, then debate to convergence. A genuine second opinion. |
| [`decompose`](skills/engineering/decompose/SKILL.md) | model | Audit one oversized module, plan a dependency-aware split, and execute it with zero breaking changes. |
| [`mp-tdd`](skills/engineering/mp-tdd/SKILL.md) | model | Build features and fix bugs test-first, one vertical slice at a time. |
| [`team-research`](skills/engineering/team-research/SKILL.md) | model | Explore a question from several angles with agents that challenge each other's findings. |

### Planning

Stress-testing plans and turning them into specs, issues, and handoffs. ([bucket README](skills/planning/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`mp-grill-me`](skills/planning/mp-grill-me/SKILL.md) | user | Get relentlessly interviewed about a plan, one question at a time, until every branch of the design tree is resolved. |
| [`mp-grill-with-docs`](skills/planning/mp-grill-with-docs/SKILL.md) | user | Grilling that also challenges your plan against the domain model, sharpening terminology and updating CONTEXT.md and ADRs inline. |
| [`mp-handoff`](skills/planning/mp-handoff/SKILL.md) | user | Compact the current conversation into a handoff document, saved outside the workspace, so the next session can continue. |
| [`mp-improve-codebase-architecture`](skills/planning/mp-improve-codebase-architecture/SKILL.md) | user | Find deepening opportunities in a codebase, informed by CONTEXT.md and the decisions in docs/adr/. |
| [`mp-to-issues`](skills/planning/mp-to-issues/SKILL.md) | user | Break a plan, spec, or PRD into independently-grabbable issues as tracer-bullet vertical slices. |
| [`mp-to-prd`](skills/planning/mp-to-prd/SKILL.md) | user | Turn the current conversation into a PRD and publish it to the project issue tracker. |

### Meta

Skills for building skills and navigating this repo. ([bucket README](skills/meta/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`skill-builder`](skills/meta/skill-builder/SKILL.md) | user | Create a well-designed skill from scratch, with the frontmatter, structure, and validation this repo expects. |
| [`which-skill`](skills/meta/which-skill/SKILL.md) | user | Ask which skill or flow fits your situation. A router over every user-reachable skill in this repo. |
| [`optimize-prompt-caching`](skills/meta/optimize-prompt-caching/SKILL.md) | model | Audit and optimize LLM prompt caching in any codebase: cache_control breakpoints, compaction, cost and latency wins. |

## Repository layout

```
skills/<bucket>/<skill>/
  SKILL.md            required: frontmatter + instructions
  LICENSE.txt         required
  agents/openai.yaml  required: Codex display metadata and invocation policy
  references/         optional: detail linked from SKILL.md
  scripts/            optional: deterministic helpers
  assets/             optional: templates and examples
```

Buckets `codebase-review/`, `pr-review/`, `engineering/`, `planning/`, and `meta/` are **promoted**: the plugin ships exactly those. `in-progress/` and `deprecated/` are public but not shipped.

- [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) is the plugin manifest, and the version in it is what tells installed users an update exists.
- [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) makes this repo its own single-plugin marketplace.
- [`spec/agent-skills-spec.md`](spec/agent-skills-spec.md) is a local copy of the Agent Skills specification.
- [`template/SKILL.md`](template/SKILL.md) is the minimal starter for a new skill.

## Contributing

Read [CLAUDE.md](CLAUDE.md), then:

```bash
python3 skills/meta/skill-builder/scripts/validate-skill.py skills/<bucket>/<name>/
python3 scripts/check-consistency.py
claude plugin validate . --strict
```

All three run in CI on every push and pull request.

## License

MIT. Each skill also carries its own `LICENSE.txt`.
