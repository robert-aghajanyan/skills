---
name: codebase-cleanup
description: Perform careful, evidence-backed codebase cleanup for existing repositories. Use when the user asks to clean up a repo, remove dead code, prune unused files, tidy stale scripts, remove unused dependencies, clean tracked generated artifacts, improve repo hygiene, or prepare a codebase for maintainable future work.
---

# Codebase Cleanup

Clean the existing codebase without changing intended behavior. This is not an architecture review or security review: focus on making the repository smaller, clearer, easier to navigate, and safer to maintain.

## Default Workflow

1. Establish scope: confirm whether the user wants assessment-only or edits, find the repo root, inspect branch and dirty state, and preserve unrelated user changes.
2. Read repo-native context: docs, manifests, CI config, package files, Makefiles, test commands, deployment/runtime files, and ignored-file rules.
3. Build an inventory of languages, package managers, source directories, tests, scripts, configs, generated artifacts, dependency manifests, entrypoints, runtime files, and docs.
4. Classify cleanup candidates as safe, likely, risky, or do-not-touch using [cleanup categories](references/cleanup-categories.md).
5. Gather evidence before every recommendation using [evidence rules](references/evidence-rules.md). If usage may be dynamic, reflective, plugin-loaded, config-driven, or external, mark it as needing human confirmation.
6. If edits are requested, apply the smallest safe cleanup batch first and follow [safe deletion](references/safe-deletion.md) and [dependency cleanup](references/dependency-cleanup.md).
7. Validate with relevant repo-native tests, lint, typecheck, build, or targeted checks when practical.
8. Report results using [output format](references/output-format.md).

## Helper Script

When a repo needs a first-pass inventory, run the read-only helper:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/cleanup_inventory.py" <repo-root>
```

Use its output as leads only. It does not prove a file or dependency is unused.

## Core Rules

- Never delete or rewrite code just because it looks unused.
- Every cleanup recommendation needs concrete evidence.
- Preserve user changes; do not revert unrelated edits.
- Prefer small, reviewable cleanup batches.
- Do not change behavior unless the user explicitly asks for a behavioral fix.
- Treat public APIs, migrations, fixtures, generated clients, deployment config, plugin metadata, and compatibility shims as high-risk until proven safe.
- Leave lockfiles alone unless dependency cleanup requires them.

## Gotchas

- Static reference checks miss dynamic imports, config-driven loading, CLIs, plugins, migrations, and externally consumed APIs.
- Generated files may be intentionally committed for reproducible builds, offline use, vendoring, or generated-client distribution.
- Dependency manifests can contain transitive tools, build-time packages, optional extras, or scripts that are not visible in source imports.
