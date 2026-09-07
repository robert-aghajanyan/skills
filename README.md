# Agent Skills

49 agent skills for Claude Code, shipped as one installable plugin. Deep codebase review across thirteen dimensions, multi-agent PR review and fix loops, TDD and implementation flows, plan stress-testing, and the tooling to write more skills.

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

Working in a repo for the first time? Run `/mp-setup` once. It configures the issue tracker, triage labels, and domain doc layout that `mp-to-spec`, `mp-to-tickets`, `mp-triage`, and `mp-wayfinder` assume.

## Invocation

Every skill is one of two kinds, and the distinction matters:

- **User-invoked** (22 of 49): reachable only when **you type the name**. Everything that deletes, rewrites, commits, publishes, or spends a lot of tokens is user-invoked, so Claude cannot start it on a hunch.
- **Model-invoked** (27 of 49): Claude can reach for these on its own when what you asked for matches.

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
| [`mp-implement`](skills/engineering/mp-implement/SKILL.md) | user | Build the work described by a spec or set of tickets, driving TDD at pre-agreed seams and closing out with a review before committing. |
| [`decompose`](skills/engineering/decompose/SKILL.md) | model | Audit one oversized module, plan a dependency-aware split, and execute it with zero breaking changes. |
| [`mp-codebase-design`](skills/engineering/mp-codebase-design/SKILL.md) | model | Shared discipline and vocabulary for designing deep modules: small interfaces, clean seams, testable through the interface. |
| [`mp-diagnosing-bugs`](skills/engineering/mp-diagnosing-bugs/SKILL.md) | model | Disciplined loop for hard bugs and performance regressions: build a feedback loop that goes red, minimise, hypothesise, instrument, fix, regression-test. |
| [`mp-prototype`](skills/engineering/mp-prototype/SKILL.md) | model | Build a throwaway prototype to answer a design question: a shareable HTML file for state and logic, or several toggleable UI variations. |
| [`mp-resolving-merge-conflicts`](skills/engineering/mp-resolving-merge-conflicts/SKILL.md) | model | Work an in-progress merge or rebase hunk by hunk, resolving by intent traced to each side primary source, then finish. Never --abort. |
| [`mp-tdd`](skills/engineering/mp-tdd/SKILL.md) | model | Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time. |
| [`mp-wizard`](skills/engineering/mp-wizard/SKILL.md) | model | Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning, credentials, dashboards, one-off migrations. |
| [`team-research`](skills/engineering/team-research/SKILL.md) | model | Explore a question from several angles with agents that challenge each other's findings. |

### Planning

Stress-testing plans and turning them into specs, issues, and handoffs. ([bucket README](skills/planning/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`mp-grill-me`](skills/planning/mp-grill-me/SKILL.md) | user | Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved. |
| [`mp-grill-with-docs`](skills/planning/mp-grill-with-docs/SKILL.md) | user | Grilling that also builds the domain model, sharpening terminology and updating CONTEXT.md and ADRs inline. |
| [`mp-improve-codebase-architecture`](skills/planning/mp-improve-codebase-architecture/SKILL.md) | user | Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick. |
| [`mp-setup`](skills/planning/mp-setup/SKILL.md) | user | Scaffold the per-repo configuration the other skills assume: issue tracker, triage label vocabulary, and domain doc layout. Run once per repo. |
| [`mp-to-spec`](skills/planning/mp-to-spec/SKILL.md) | user | Turn the current conversation into a spec and publish it to the project issue tracker. |
| [`mp-to-tickets`](skills/planning/mp-to-tickets/SKILL.md) | user | Break any plan, spec, or conversation into tracer-bullet tickets, each declaring its blocking edges. |
| [`mp-triage`](skills/planning/mp-triage/SKILL.md) | user | Move issues and external PRs through a state machine of triage roles: categorise, verify, grill if needed, and write agent-ready briefs. |
| [`mp-wayfinder`](skills/planning/mp-wayfinder/SKILL.md) | user | Plan a chunk of work larger than one agent session as a map of decision tickets on the tracker, resolved one at a time until the way is clear. |
| [`mp-domain-modeling`](skills/planning/mp-domain-modeling/SKILL.md) | model | Actively build and sharpen the project domain model by challenging terms, stress-testing with scenarios, and updating CONTEXT.md and ADRs inline. |
| [`mp-grilling`](skills/planning/mp-grilling/SKILL.md) | model | Interview the user in rounds, asking the whole settled frontier of the design tree at once, each question with a recommended answer. |

### Productivity

General workflow tools, not code-specific. ([bucket README](skills/productivity/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`humanizer`](skills/productivity/humanizer/SKILL.md) | user | Rewrite AI-sounding text so it reads like the writer without changing what it says. 25 tells from Wikipedia's "Signs of AI writing", graded by strength. |
| [`mp-handoff`](skills/productivity/mp-handoff/SKILL.md) | user | Compact the current conversation into a handoff document so another agent can continue the work. |
| [`mp-teach`](skills/productivity/mp-teach/SKILL.md) | user | Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace. |
| [`mp-to-questionnaire`](skills/productivity/mp-to-questionnaire/SKILL.md) | user | Turn a decision you cannot answer alone into a Markdown questionnaire for the one person who can, filled in async or worked through together. |
| [`mp-wait-what`](skills/productivity/mp-wait-what/SKILL.md) | user | Fire this the moment a message does not land. The agent re-pitches it with the context you are missing, in plain English. |

### Meta

Skills for building skills and navigating this repo. ([bucket README](skills/meta/README.md))

| Skill | Invocation | What it does |
|---|---|---|
| [`skill-builder`](skills/meta/skill-builder/SKILL.md) | user | Create a well-designed skill from scratch, with the frontmatter, structure, and validation this repo expects. |
| [`which-skill`](skills/meta/which-skill/SKILL.md) | user | Ask which skill or flow fits your situation. A router over every user-reachable skill in this repo. |
| [`mp-writing-for-agents`](skills/meta/mp-writing-for-agents/SKILL.md) | model | Writing documents for agents: skills, AGENTS.md and CLAUDE.md, and any doc an agent reaches by a pointer. |
| [`optimize-prompt-caching`](skills/meta/optimize-prompt-caching/SKILL.md) | model | Audit and optimize LLM prompt caching in any codebase: cache_control breakpoints, compaction, cost and latency wins. |

## Credits

The 22 skills prefixed `mp-` are ported from [mattpocock/skills](https://github.com/mattpocock/skills) (MIT), kept in sync with upstream and renamed into this repo's namespace so both plugins can be installed side by side. Each carries its own `LICENSE.txt` with the original copyright notice. Everything else is this repo's own work.

Upstream skills deliberately not ported, because this repo already covers them: `ask-matt` (see `which-skill`), `code-review` (see `team-review`), `research` (see `team-research`).

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

Buckets `codebase-review/`, `pr-review/`, `engineering/`, `planning/`, `productivity/`, and `meta/` are **promoted**: the plugin ships exactly those. `in-progress/` and `deprecated/` are public but not shipped.

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

MIT for the `mp-` skills (see each one's `LICENSE.txt`), Apache-2.0 for the rest.
