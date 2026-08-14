---
name: codebase-consolidation-cleanup
description: Assess unused, duplicate, or overlapping implementation paths in large codebases without modifying files. Use when the user asks to assess cleanup opportunities, identify unused modules/functions/artifacts, evaluate duplicate implementations, map wrapper/runner/output sprawl, or understand what would break if stale code is removed.
---

# Codebase Consolidation Cleanup

Find cleanup opportunities in large, evolved codebases where features, wrappers, runners, outputs, and compatibility paths have accumulated over time. This skill is assessment-only: produce evidence-backed candidates, impact analysis, confidence scores, and validation plans. Do not modify, delete, move, stage, commit, or rewrite files.

## Default Workflow

1. Establish scope: this skill always runs assessment-only, even if the user mentions cleanup or deletion. Confirm repo root, branch, dirty state, and any local repository instructions.
2. Build the execution map: identify user-facing entrypoints, scripts, CLIs, APIs, jobs, tests, package commands, deployment hooks, plugin manifests, docs, and generated artifact paths.
3. Discover consolidation candidates using [candidate taxonomy](references/candidate-taxonomy.md): duplicate logic, overlapping wrappers, repeated pipeline paths, stale options, unused modules/functions, orphaned artifacts, and dependency islands.
4. Prove or disprove each candidate with [evidence and impact rules](references/evidence-and-impact.md). Static "no references found" is never enough for code that may be loaded dynamically, externally, or by convention.
5. Classify candidates as removal-ready, consolidate-ready, deprecate/migrate, needs human confirmation, or do-not-touch. Assign each candidate a 0-100 confidence score and list the evidence that would raise or lower that score.
6. If the user asks to proceed with changes, do not edit. Produce a handoff plan for a separate implementation step using [execution safety](references/execution-safety.md).
7. Validate with repo-native tests, lint, typecheck, build, smoke checks, or targeted runtime commands. For production or leadership-facing use, apply the [production readiness gate](references/production-readiness.md).
8. Report results with [output format](references/output-format.md), including what would happen if each candidate is removed and the follow-up plan needed before deletion.

## Rules

- Do not delete, rewrite, move, format, stage, commit, or otherwise modify files. This skill only assesses and plans.
- Do not recommend cleanup just because code looks unused, old, or duplicated.
- Treat wrappers, CLIs, public APIs, configs, migrations, generated clients, plugins, scheduled jobs, and deployment files as externally reachable until proven otherwise.
- Prefer one canonical implementation only when the replacement path is behaviorally equivalent or a deliberate behavior change has been approved.
- Preserve unrelated user changes by staying read-only.
- Separate "unused" from "duplicated": duplicate code may still be required until callers are migrated.
- When the safest answer is deprecation before deletion, recommend that instead of forcing immediate removal.

## Generic Example

For a codebase with several ways to run the same pipeline, map every runner and output path first: CLI commands, scripts, UI/API calls, cron jobs, tests, docs, plugin tools, and deployment entrypoints. Then identify the canonical execution path, list wrappers that can delegate to it, and mark any obsolete paths for deprecation or removal only after callers and validation coverage are known.

## Validation

Before calling the assessment complete, verify that each recommendation includes:

- exact path or symbol
- candidate type and classification
- evidence commands or files inspected
- dependency and caller impact
- proposed action and rollback/deprecation plan
- confidence score with evidence gaps
- follow-up evidence and validation plan before deletion
- validation already run or required before deletion

If the user wants implementation after the assessment, stop at a handoff: restate the approved candidates, risks, validation plan, and that a separate edit-capable workflow must perform the changes.

For repo-specific memory, changelog, migration, or docs requirements, follow the local instructions before finishing.

## Gotchas

- Dynamic imports, plugin discovery, environment-selected backends, glob-loaded scripts, and external callers can make live code appear unused.
- Multiple wrappers may be intentional compatibility surfaces even when their internal logic overlaps.
- Generated artifacts may be committed intentionally for offline use, reproducibility, or deployment packaging.
- Removing a duplicate before moving callers can break docs, CI, scheduled jobs, or users even when application tests pass.
- Consolidation can accidentally change output shape, logging, metrics, side effects, or error handling; compare behavior before and after.
