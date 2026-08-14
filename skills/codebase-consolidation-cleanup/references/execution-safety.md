# Assessment Safety And Handoff

This skill is assessment-only. It must not edit, delete, move, format, stage, commit, or otherwise modify repository files. If the user asks to proceed with cleanup, produce a handoff plan for a separate implementation workflow instead of making changes.

## Read-Only Boundaries

- Allowed: read files, inspect git status, run read-only searches, inspect manifests, run non-mutating validation commands, and summarize evidence.
- Avoid: commands that rewrite files, regenerate artifacts in place, update lockfiles, apply patches, delete files, move files, stage changes, commit, or push.
- If a validation command may write caches, generated files, snapshots, reports, or lockfiles, either use a disposable location or mark the validation as pending for the implementation phase.

## Handoff Strategy

When the assessment identifies a cleanup candidate, provide a handoff that an edit-capable workflow can execute later:

- exact files, symbols, commands, artifacts, or dependencies involved
- classification and per-candidate confidence score
- evidence already gathered
- evidence gaps and owner confirmations still needed
- expected caller migration or deprecation sequence
- tests and smoke checks to run before and after removal
- rollback strategy if the cleanup proves wrong

## Validation Strategy

Use repo-native checks first, but keep them read-only in this skill:

- import or module collection checks
- tests that do not mutate tracked files
- CLI/script dry runs or help output
- lint/typecheck/build commands only when their write behavior is understood
- artifact regeneration or report comparison only in a disposable output directory

If full validation is too expensive, destructive, credential-dependent, or likely to mutate the worktree, do not run it. Add it to the follow-up validation plan and state the residual risk.

## Deprecation Guidance

Prefer deprecation over deletion when callers are unknown. Because this skill does not edit files, describe the deprecation option without implementing it. A good follow-up deprecation step may document the canonical replacement, keep import compatibility while delegating internally, add tests proving wrapper behavior matches the canonical path, and schedule actual deletion for a later cleanup batch.
