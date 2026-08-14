---
name: codebase-developer-experience-review
description: Review any repository for developer workflow quality: setup, local run commands, test speed, CI clarity, scripts, docs accuracy, environment handling, debugging ergonomics, and maintainer friction. Use when the user asks for developer experience review, repo onboarding, local setup issues, CI cleanup, Makefile/script quality, test speed, docs accuracy, confusing commands, environment setup, or maintainer ergonomics.
---

# Codebase Developer Experience Review

Review how effectively a repository lets developers install, configure, run, test, debug, and maintain it. Focus on friction that blocks or slows real development, not broad documentation rewriting or subjective style cleanup.

## Workflow

1. Build a developer workflow map: install, configure, run, test, lint, typecheck, build, debug, release, and deploy commands. When useful, start with:
   `python3 "${CLAUDE_SKILL_DIR}/scripts/dx_inventory.py" <repo-root>`
2. Compare documentation against actual repo entrypoints: manifests, lockfiles, Makefiles, package scripts, task runners, CI workflows, Docker/devcontainer files, env examples, config readers, and repo-native scripts.
3. Load only the focused references needed for the repo:
   - [local setup](references/local-setup.md)
   - [CI and scripts](references/ci-and-scripts.md)
   - [docs accuracy](references/docs-accuracy.md)
   - [test speed](references/test-speed.md)
   - [debuggability](references/debuggability.md)
   - [output format](references/output-format.md)
4. Review for broken setup steps, duplicate scripts, unclear env vars, slow default tests, missing focused test commands, CI/local mismatch, stale docs, hidden prerequisites, poor error messages, and hard-to-debug workflows.
5. For each finding, include evidence, affected developer workflow, recommended fix, risk, and a validation command.
6. Calibrate before finalizing: remove taste-only preferences, unsupported guesses, broad doc rewrites, and findings that do not materially affect onboarding or day-to-day maintenance.

## Output

Use [references/output-format.md](references/output-format.md): DX summary, workflow map, friction findings, quick wins, commands to standardize, docs to update, validation steps, and open questions.

## Validation

- Prefer non-destructive repo-native commands: setup dry runs, focused tests, lint/typecheck, build checks, CI config validation, and script help output.
- Do not run release, deploy, migration, destructive cleanup, or credential-dependent commands unless the user explicitly asks and approvals are handled.
- If timing test commands, record the exact command, scope, and environment; distinguish measured slowness from static risk.
- Treat the inventory helper as a map, not proof. Read the relevant files before reporting findings.

## Gotchas

- Do not demand one universal workflow when a monorepo legitimately has per-package entrypoints; flag only undocumented or contradictory paths.
- Do not turn the review into copyediting. Documentation wording matters when it causes wrong commands, missing prerequisites, or unsafe assumptions.
- Passing CI does not prove good local DX; compare what CI runs with what developers are told to run.
- Multiple setup paths are not automatically bad. They become findings when docs do not name the recommended path, commands diverge, or failures are hard to diagnose.
