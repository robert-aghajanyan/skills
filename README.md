# Agent Skills

Public repository for Agent Skills — reusable skill packages for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

Skills are folders of instructions, scripts, and resources that Claude loads dynamically for specialized tasks. They extend Claude's capabilities without modifying its core behavior.

## Available Skills

33 skills across 7 categories.

### Code Quality & Review

| Skill | Description |
|-------|-------------|
| [decompose](skills/decompose/) | Audit and decompose large modules into smaller, maintainable units |
| [optimize-prompt-caching](skills/optimize-prompt-caching/) | Audit and optimize LLM prompt caching in any codebase |

### Codebase Review Suite

Deep, dimension-specific repository reviews, plus an orchestrator that runs them all and files a deduplicated issue backlog.

| Skill | Description |
|-------|-------------|
| [codebase-review-suite](skills/codebase-review-suite/) | Orchestrate the full codebase review suite and synthesize findings into a deduplicated GitHub issue backlog |
| [codebase-security-review](skills/codebase-security-review/) | Deep security reviews and threat modeling grounded in exploitability and actual code paths |
| [codebase-performance-review](skills/codebase-performance-review/) | Performance, scalability, resource usage, and hot-path efficiency risks |
| [codebase-architecture-review](skills/codebase-architecture-review/) | Architecture and maintainability reviews — YAGNI, KISS, DRY, SOLID, decomposition opportunities |
| [codebase-reliability-review](skills/codebase-reliability-review/) | Production reliability risks — retries, timeouts, idempotency, concurrency, observability |
| [codebase-data-correctness-review](skills/codebase-data-correctness-review/) | Correctness risks in calculations, aggregations, reporting, forecasting, and reconciliation logic |
| [codebase-dependency-supply-chain-review](skills/codebase-dependency-supply-chain-review/) | Dependency, lockfile, license, provenance, and supply-chain risk |
| [codebase-documentation-review](skills/codebase-documentation-review/) | Documentation accuracy, staleness, and alignment with actual code and behavior |
| [codebase-frontend-quality-review](skills/codebase-frontend-quality-review/) | Frontend UX quality — accessibility, responsive behavior, state correctness, visual regressions |
| [codebase-llm-agent-safety-review](skills/codebase-llm-agent-safety-review/) | Safety review for repos using LLMs, agents, tools, MCP servers, or automation |
| [codebase-developer-experience-review](skills/codebase-developer-experience-review/) | Developer workflow quality — setup, CI clarity, scripts, docs accuracy, debugging ergonomics |
| [codebase-api-contract-review](skills/codebase-api-contract-review/) | API, CLI, schema, SDK, event, and config compatibility risk |
| [codebase-test-quality-review](skills/codebase-test-quality-review/) | Test suite quality — regression-catching value, flaky behavior, weak assertions, over-mocking |
| [codebase-cleanup](skills/codebase-cleanup/) | Evidence-backed cleanup — dead code, unused files, stale scripts, unused dependencies |
| [codebase-consolidation-cleanup](skills/codebase-consolidation-cleanup/) | Assess unused/duplicate/overlapping implementation paths without modifying files |
| [codebase-decomposition](skills/codebase-decomposition/) | Audit, plan, and execute behavior-preserving decomposition of large modules |

### PR Workflow

| Skill | Description |
|-------|-------------|
| [team-review](skills/team-review/) | Thorough PR review with 4 specialized agent teams plus independent verification |
| [team-review-plus](skills/team-review-plus/) | Enhanced evidence-calibrated review — false-positive filtering, confidence calibration |
| [pr-clean-review](skills/pr-clean-review/) | Fast-strict PR review/fix workflow with evidence-ledger verification and a clean-room final pass |
| [pr-review-fix](skills/pr-review-fix/) | Iterative review-and-fix loop — 4 reviewer teams, a separate fixer agent, up to 3 rounds |
| [production-readiness-gate](skills/production-readiness-gate/) | Final conservative production-readiness gate with leadership-safe confidence scores |

### Planning

| Skill | Description |
|-------|-------------|
| [mp-grill-me](skills/mp-grill-me/) | Stress-test a plan through a relentless one-question-at-a-time interview |
| [mp-grill-with-docs](skills/mp-grill-with-docs/) | Grilling session that also updates CONTEXT.md/ADRs inline as decisions crystallise |
| [mp-improve-codebase-architecture](skills/mp-improve-codebase-architecture/) | Find deepening opportunities in a codebase, informed by domain language and ADRs |
| [mp-tdd](skills/mp-tdd/) | Test-driven development with a red-green-refactor loop |
| [mp-to-prd](skills/mp-to-prd/) | Turn the current conversation context into a PRD and publish it |
| [mp-to-issues](skills/mp-to-issues/) | Break a plan/spec/PRD into independently-grabbable issues via tracer-bullet vertical slices |
| [mp-handoff](skills/mp-handoff/) | Create a concise handoff document for a future session, saved outside the workspace |

### Meta

| Skill | Description |
|-------|-------------|
| [skill-builder](skills/skill-builder/) | Create well-designed Claude Code skills from scratch |

### Collaboration

| Skill | Description |
|-------|-------------|
| [codex-collab](skills/codex-collab/) | Claude + Codex parallel critique loop — both analyze independently, then debate to convergence |

### Business Process & Automation

| Skill | Description |
|-------|-------------|
| [team-research](skills/team-research/) | Research and investigation swarm with adversarial debate |

## Installation

### Install all skills

```bash
claude install-skill https://github.com/robert-aghajanyan/skills
```

### Install a specific skill

```bash
claude install-skill https://github.com/robert-aghajanyan/skills/tree/main/skills/decompose
```

### Install a plugin bundle

The marketplace groups related skills into plugin bundles (see [.claude-plugin/marketplace.json](.claude-plugin/marketplace.json)): `code-quality-skills`, `team-skills`, `meta-skills`, `codebase-review-skills`, `pr-workflow-skills`, `planning-skills`, `collab-skills`. Add this repo as a marketplace source in Claude Code, then install a bundle by name.

## Usage

Once installed, skills are available as slash commands:

```
/decompose <file path>              # Decompose a large module
/optimize-prompt-caching            # Audit prompt caching
/skill-builder                      # Create a new skill
/team-research <topic>              # Multi-agent research swarm
/team-review <PR>                   # Multi-agent PR review
/codebase-review-suite              # Run the full codebase-* review suite
/codebase-security-review           # Deep security review of a repo
/pr-review-fix <PR>                 # Iterative PR review-and-fix loop
/production-readiness-gate <target> # Final readiness gate with confidence scores
/mp-grill-me <plan>                 # Stress-test a plan via interview
/mp-tdd                             # Red-green-refactor TDD loop
/codex-collab <task>                # Claude + Codex cross-model debate
```

Claude also auto-triggers skills based on natural language — for example, saying "this file is too big, split it up" will activate the decompose skill, and "review this repo for security issues" will activate codebase-security-review.

## Skill Structure

Each skill is a self-contained directory under `skills/`:

```
skills/my-skill/
  SKILL.md           # Required: frontmatter + instructions
  LICENSE.txt        # License file
  references/        # Optional: detailed docs loaded on demand
  scripts/           # Optional: deterministic helper scripts
  assets/            # Optional: templates, examples
```

The core file is `SKILL.md` with YAML frontmatter:

```yaml
---
name: my-skill
description: What it does. Use when user says "trigger phrase".
---

# Instructions here
```

See the [template](template/) directory for a minimal starter, or use `/skill-builder` to create one interactively.

## Specification

For the full Agent Skills specification, see [agentskills.io](https://agentskills.io/specification).

## Contributing

1. Fork this repository
2. Create your skill directory under `skills/`
3. Include a `SKILL.md` with valid frontmatter and a `LICENSE.txt`
4. Validate with: `python skills/skill-builder/scripts/validate-skill.py skills/your-skill/`
5. Submit a pull request

## License

Individual skills are licensed under the Apache License 2.0 unless otherwise noted. See each skill's `LICENSE.txt` for details.
