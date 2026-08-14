---
name: codebase-documentation-review
description: Review repository documentation for accuracy, completeness, staleness, operational usefulness, and alignment with actual code, scripts, CI, configuration, APIs, and deployment behavior. Use when the user asks for documentation review, docs accuracy, stale docs, runbook review, README review, setup docs, operational docs, API docs, examples, command verification, or whether documentation matches the codebase.
---

# Codebase Documentation Review

Review documentation as executable and verifiable claims about the repository. Focus on incorrect, stale, missing, conflicting, or misleading docs, not style-only prose edits.

## Workflow

1. Build a documentation map: README files, docs directories, runbooks, architecture docs, setup guides, API docs, examples, diagrams, changelog/release docs, CI/deploy docs, env examples, and comments that serve as docs. When useful, run:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/docs_inventory.py" <repo-root>`
2. Extract concrete documentation claims: commands, scripts, paths, env vars, config keys, API routes, schemas, CLI flags, deployment steps, diagrams, ownership, prerequisites, and validation steps.
3. Verify claims against repository evidence: source code, handlers, schemas, manifests, package scripts, Makefiles, CI workflows, Docker files, deployment manifests, env examples, tests, and repo-native tooling.
4. Review operational usefulness: troubleshooting, rollback, recovery, ownership, escalation, prerequisites, environment scope, validation commands, and ambiguous run/deploy instructions.
5. Review user and developer usefulness: onboarding gaps, outdated examples, duplicate or conflicting instructions, undocumented behavior, migration notes, and missing "how to verify" steps.
6. Report each finding with the doc file and line, contradicted or missing source evidence, user impact, recommended doc change, and verification command or evidence.
7. Calibrate before finalizing: remove style-only comments, weak guesses, duplicate findings, and claims not backed by repository evidence.

## References

- Setup and onboarding docs: [references/setup-docs.md](references/setup-docs.md)
- API docs and schemas: [references/api-docs.md](references/api-docs.md)
- Runbooks and incident docs: [references/runbooks.md](references/runbooks.md)
- Examples and snippets: [references/examples.md](references/examples.md)
- Operational, CI, deploy, and architecture docs: [references/operational-docs.md](references/operational-docs.md)
- Report shape: [references/output-format.md](references/output-format.md)

## Validation

- Prefer repo-native commands from docs, manifests, Makefiles, package scripts, CI, or deployment tooling.
- If a documented command is destructive, privileged, expensive, or environment-specific, validate statically and state what was not executed.
- Treat the inventory script as a starting point only; read the relevant docs and code before making findings.

## Gotchas

- Do not rewrite docs for tone, grammar, or style unless the wording creates a real operational or technical misunderstanding.
- Do not assume docs are wrong because they use a different path or command; verify aliases, wrappers, generated files, and deployment-specific entrypoints first.
- Do not demand exhaustive documentation for every implementation detail; focus on behavior users, developers, and operators need to act safely.
