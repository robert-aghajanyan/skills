# Exit Gate

Use this reference before saying a PR is code-clean, safe to merge, or
mergeable.

## Required Evidence

The PR can be called code-clean only when all of these are true:

1. The reviewed head SHA matches the current GitHub PR head.
2. The initial discovery pass was broad, fresh, and run at team-review or
   team-review-plus depth.
3. Every `[CRITICAL]` and evidence-backed `[WARNING]` finding from every round
   is either fixed or disproven on the current head.
4. `[SUGGESTION]` findings are not part of the clean gate unless the user
   explicitly requested low-severity cleanup.
5. Every changed risky surface has direct probe evidence.
6. Mirrored implementations, public entrypoints, docs, schemas, and launchers
   agree when the diff touches those contracts.
7. Focused tests or direct probes cover each fixed blocker/high issue when
   practical.
8. Formatting/static checks relevant to the repo have run or the reason they
   could not run is stated.
9. The final calibration pass is a fresh context-isolated clean-room review on
   the exact current PR head, not only a regression check.
10. The final clean-room review has zero critical findings and zero warnings.
11. The round limit has not been exceeded, and the run did not stop because of a
    repeat blocker.

The PR can be called mergeable only when the code-clean gate passes and GitHub
also reports a merge-eligible state, normally:

- `mergeable: MERGEABLE`
- `mergeStateStatus: CLEAN`

If GitHub reports `BLOCKED`, `DIRTY`, `UNKNOWN`, missing checks, unresolved
threads, or stale mergeability, report that directly. It may still be
code-clean, but do not call it mergeable.

## Fast-Strict Default

Fast-strict mode is the default. It uses one broad discovery pass, batched
blocker/high fixes, focused post-fix verification, and one final clean-room
review.

The final clean-room review should usually be a context-isolated subagent inside
the same session. Use a fully new session only when:

- the PR is high-risk enough to need an extra independent pass
- the final clean-room reviewer finds a blocker/high issue
- the user explicitly asks for a new session

## Two-Clean-Pass Option

For high-risk PRs or especially sensitive changes, require two consecutive clean
independent reviews on the same current PR head:

1. A post-fix full review with zero critical/warning findings.
2. A final clean-room calibration pass from exact remote head, preferably with
   fresh reviewer context.

Use this when the user is seeing repeated "clean" claims followed by new
findings in a new session. Record both passes in `clean_passes`, and mark each
pass with `fresh: true`, `independent: true`, `critical: 0`, and `warning: 0`.
The validator enforces this automatically when `risk_level` is `high`, or when
called with `--require-two-clean-passes`.

## Stop Conditions

Stop and report instead of continuing silently when:

- the same blocker repeats after a fix round
- a normal PR has used two fix rounds without a clean calibration pass
- a high-risk PR has used three fix rounds without a clean calibration pass
- the remaining issue requires a product/design decision
- tests cannot run and no direct probe can replace the missing evidence
- the branch cannot be pushed or the GitHub head cannot be verified

## Minimum Final Checks

Adapt this list to the repo, but do not skip the categories:

- exact GitHub head: `gh pr view <N> --json headRefOid,baseRefName,headRefName,mergeable,mergeStateStatus,statusCheckRollup`
- local head matches remote PR head
- isolated patch/review surface, recorded as `workspace.strategy` plus
  `workspace.clean: true`
- current review structure recorded as `review_structure`; when parallel xhigh
  review was requested, it must show `parallel_agents_requested: true`,
  `reasoning_effort: xhigh`, all four core lenses, `initial_discovery_full:
  true`, and `final_clean_room: true`
- final clean-room review recorded as `external_reviews`; at least one entry
  must be context-isolated, loaded from `team-review` or `team-review-plus`, on
  the current head, and show `critical: 0`, `warning: 0`, `proof`, a non-empty
  `artifact_path`, and `reconciled: true`
- push and merge policy recorded as `execution_policy`; pushed PRs require
  `push_requested: true` and `remote_head_verified: true`, and `merged` must be
  false
- fix scope recorded as `fix_scope`; only critical/warning findings should be
  in scope unless the user explicitly requested low-severity cleanup, and
  `suggestions_blocking` must be false by default
- round limits recorded as `round_limits`
- current diff against true PR base
- focused tests for touched behavior
- repo-standard static/format checks
- `git diff --check`
- final review pass results
- ledger validation with `scripts/validate_clean_gate.py`
