---
name: codebase-architecture-review
description: Perform deep repository architecture and maintainability reviews grounded in observed code. Use when the user asks to review a repo or codebase for architecture quality, YAGNI, KISS, DRY, SOLID, maintainability, decomposition opportunities, over-complex modules, duplicated logic, unclear boundaries, or client/region/provider/tenant/agent-specific branching.
---

# Codebase Architecture Review

Use this skill to review a repository's architecture and long-term maintainability. Findings must be grounded in observed code, exact files, and preferably line references; remove generic principle-only comments during the final calibration pass.

## Workflow

1. Build a repository map from manifests, CI config, docs, Makefiles, repository scripts, package files, source layout, tests, deployment files, and runtime config. When useful, run `python "${CLAUDE_SKILL_DIR}/scripts/repo_inventory.py" <repo-root>`.
2. Identify review units: modules, packages, services, clients, regions, providers, tenants, agents, adapters, workflows, shared libraries, generated code, and deployment surfaces.
3. Prioritize high-risk areas first: shared libraries, orchestration, policy/business logic, persistence, external clients, generated-code boundaries, runtime configuration, and code with many conditionals.
4. Review each unit using the lenses in [references/maintainability.md](references/maintainability.md), [references/decomposition.md](references/decomposition.md), [references/security-baseline.md](references/security-baseline.md), and [references/reliability-baseline.md](references/reliability-baseline.md).
5. For every decomposition recommendation, include the current problem, proposed boundary, suggested file/module layout, incremental migration steps, behavior-preservation tests, risk of doing it now, and risk of not doing it.
6. Run repo-native tests/builds where practical. If full validation is too expensive or unsafe, run focused static checks and explain the gap.
7. End with a calibration pass: remove weak, generic, duplicate, or principle-only findings; clearly separate confirmed issues from hypotheses.

## Output

Use the report structure in [references/output-format.md](references/output-format.md). Include a do-not-change section for complexity or duplication that is justified by local clarity, compatibility, generated code, performance, or domain constraints.

## Validation

- Validate claims by reading the concrete code paths involved and citing exact files and line references where possible.
- Prefer repo-native commands from manifests, Makefiles, CI, or docs before inventing validation steps.
- Run the inventory helper when it will reduce blind spots:
  `python "${CLAUDE_SKILL_DIR}/scripts/repo_inventory.py" <repo-root>`

## Gotchas

- Do not turn SOLID, DRY, or YAGNI into a checklist detached from the code. A finding without evidence is not a finding.
- Do not flag harmless local repetition that makes code easier to read.
- Do not recommend decomposition unless the proposed boundary, migration path, tests, and tradeoffs are concrete.
- Keep security and reliability observations baseline-level unless the user's primary request is security-focused; then suggest a dedicated security review.
