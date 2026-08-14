# Review Evidence Lenses

Use this reference to sharpen PR reviews without turning every review into a broad codebase audit. These checks are optional inputs to the review, not a replacement for the core security, performance, correctness, and guardrail lenses in `SKILL.md`.

## PR Preflight

For GitHub PR targets, establish:

- exact base branch, head branch, and head SHA
- whether the PR is draft, closed, stale, stacked, or already superseded
- changed files and whether the patch is too large for patch-only review
- current review comments, unresolved threads, and prior automated review output
- whether earlier blocker/high findings are still present on the current head

If a PR is draft, closed, trivial, or already reviewed, do not silently skip when the user explicitly asked for a review. Instead, state the condition and continue or stop based on the user's request.

## False-Positive Filter

Before reporting a finding, check whether it is:

- pre-existing and not made worse by the diff
- outside modified lines and not caused by the PR
- a nitpick that does not affect behavior, safety, maintainability, or an explicit repo rule
- a typecheck, formatting, import, or lint issue that normal CI will catch unless it points to a deeper workflow problem
- a change in behavior that appears intentional and matches the PR goal
- a guideline concern that is not actually required by repo instructions
- a low-confidence concern that should be framed as a question instead of a defect

Prefer fewer, stronger findings. A review that reports only proven issues is more useful than one that lists every possible concern.

## Confidence Calibration

Use this scale internally:

- **High**: directly verified against code, diff, tests, reproduction, docs contract, or current PR state; safe to present as a blocker or warning.
- **Medium**: likely real but not fully proven; present as a suggestion or clearly marked question unless impact is severe.
- **Low**: plausible but speculative; do not list as a finding. Mention only as an open question if it materially affects merge safety.

`[CRITICAL]` and `[WARNING]` should normally require high confidence. Do not inflate severity to make a weak concern sound more important.

## Optional Specialist Lenses

Apply these only when the diff touches the relevant surface:

| Lens | Use When | Look For |
|---|---|---|
| Tests | New behavior, validation, parsing, finance/reporting logic, async/concurrency, bug fixes | missing behavioral, negative, boundary, integration, or regression coverage |
| Error handling | `try`/`catch`, retries, fallbacks, optional integrations, background jobs, dependency calls | silent failures, swallowed exceptions, misleading success states, missing context/logging |
| Comments/docs | comments, docstrings, README/runbook/wiki updates, generated docs | comment rot, inaccurate claims, missing caveats, docs contradicting code |
| Type/schema invariants | data models, schemas, config, public contracts, generated JSON, typed APIs | invalid states, weak validation, inconsistent enforcement, backward-incompatible shape drift |
| History/context | risky files, surprising changes, regressions, unclear intent | prior PR comments, blame context, reverted patterns, old bug fixes being undone |
| Maintainability | complex fixes, broad branching, duplicated logic, new abstractions | unnecessary complexity, hard-to-debug structure, one-off logic that should be shared |

## Carry-Forward Handling

When the conversation, PR comments, or previous review output contains existing findings:

1. Build a carried-forward checklist of blocker/high items.
2. Re-check each item against the current head, not stale local state.
3. Mark each as fixed, still present, no longer applicable, or unverified.
4. Do not call a PR clean while a carried-forward blocker/high item is unverified.

## Gotchas

- Do not assume agent names, model names, or tool availability beyond what this skill declares; verify against the current runtime instead of hardcoding assumptions.
- Do not let a specialist lens distract from the actual PR intent.
- Do not use confidence scoring to hide a severe unverified risk; verify it or state the uncertainty directly.
