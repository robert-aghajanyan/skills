---
name: team-review-plus
description: Enhanced evidence-calibrated PR review using team-review's core lenses plus PR preflight, false-positive filtering, carried-forward finding checks, confidence calibration, and optional specialist lenses. Use when the user explicitly invokes team-review-plus, asks for an enhanced/deep PR review, wants a false-positive-calibrated review, or wants specialist review lenses before merging.
---

# Team Review Plus

Run the standard `team-review` workflow with additional PR-specific evidence controls. This skill exists so the default `team-review` behavior can stay stable while deeper review is opt-in.

Use this when the user wants a more conservative, evidence-calibrated PR review than the default team review.

## Phase 1: Gather Review Context

### Step 1: Parse the Request

Use the current user request to determine what to review:

- **PR URL or number**: use `gh pr view` and `gh pr diff` if available
- **Branch name**: use `git diff <base>...<branch>`
- **File paths**: diff or read only those files
- **Existing patch or discussion**: use that as the source of truth

If the target is ambiguous, clarify before reviewing.

### Step 2: Build the Context Packet

Collect:

1. The relevant diff
2. Changed files with additions and deletions
3. The PR description or intent, if available
4. Whether the change is stacked on another branch instead of `main`
5. Whether the diff is large enough that reviewers should read files directly instead of relying on an embedded patch
6. Whether the change is documentation-only
7. Whether the current worktree is dirty
8. For PR reviews, the exact base, head SHA, live PR state, and unresolved review comments or carried-forward findings

Never reset or overwrite the user's current checkout just to perform a review.

Use [references/review-evidence-lenses.md](references/review-evidence-lenses.md) for PR preflight checks, false-positive filtering, confidence calibration, carried-forward comment handling, and specialist lenses such as tests, error handling, comments, type/schema invariants, and maintainability.

## Phase 2: Apply Review Lenses

### Step 3: Choose Review Mode

Use sub-agents only when the user explicitly asked for multi-agent or parallel review.

- If delegation is explicit, spawn up to four reviewers with disjoint core lenses, and apply specialist lenses locally or with clearly scoped additional reviewers when requested.
- Otherwise, apply the core and applicable specialist lenses yourself in sequence.

If you use sub-agents, close them after capturing their findings.

### Step 4: Review Through Core Lenses

Every finding should include:

- Severity: `[CRITICAL]`, `[WARNING]`, or `[SUGGESTION]`
- Confidence: `High`, `Medium`, or `Low`
- Location: `file:line`
- Issue: one-line description
- Detail: why it matters and under what conditions
- Fix: a concrete remediation

Treat `[CRITICAL]` and `[WARNING]` findings as high-confidence by default. If a concern is plausible but not proven, frame it as a `[SUGGESTION]` or an open question instead of a blocker.

Use these core lenses:

#### Security

Only flag:

- injection risks
- authentication or authorization flaws
- data exposure
- insecure deserialization
- cryptography mistakes
- missing validation at trust boundaries
- insecure defaults

#### Performance

Only flag:

- algorithmic regressions
- unnecessary allocations in hot paths
- repeated work that should be cached
- resource leaks
- N+1 patterns
- blocking work in async paths
- unbounded payload handling

#### Correctness

Only flag:

- regressions in existing behavior
- edge cases and boundary mistakes
- broken assumptions
- missing or invalid tests
- race conditions
- contract violations

#### Guardrails

Only flag:

- removed or weakened safety checks
- missing limits or validation
- unsafe config changes
- missing integration error handling
- rollback or kill-switch gaps

For documentation-only changes, skip the performance lens unless the docs make performance claims that need verification.

## Phase 3: Independent Verification

### Step 5: Verify Important Claims

After the lens review, verify the strongest claims directly.

- confirm suspected bugs against the actual diff or branch content
- re-check unresolved prior review comments and carried-forward blocker/high findings on the current head
- run targeted tests when the repo supports them
- grep for removed symbols, imports, or safety checks
- use `git diff`, `git show`, or a temporary `git worktree` instead of switching the user's current branch when the worktree is dirty

For stacked PRs, verify against the actual base and head branches, not blindly against `main`.

## Phase 4: Synthesize

### Step 6: Present Findings

Summarize the result as:

```markdown
## Team Review Plus Summary

**Target**: ...
**Files**: N | **Lines**: +X / -Y

### Critical Issues
...

### Warnings
...

### Suggestions And Questions
...

### Review Breakdown
| Lens | Criticals | Warnings | Suggestions / Questions |
|------|-----------|----------|-------------------------|
| Security | N | N | N |
| Performance | N | N | N |
| Correctness | N | N | N |
| Guardrails | N | N | N |
| Specialist | N | N | N |

### Independent Verification
| Check | Result |
|-------|--------|
| Tests | ... |
| Diff verification | ... |
| Compatibility checks | ... |
| Carry-forward findings | ... |
```

After the summary, answer:

- What problem the change solves
- Whether it is safe to merge
- Any merge-order dependencies
- Your confidence level and why, separating evidence-backed risks from lower-confidence questions

Stop there and let the user decide what feedback to send.

## Gotchas

- **This is opt-in**: use normal `team-review` for the user's default workflow unless they invoke this skill or ask for enhanced review.
- **Stacked PRs create false positives**: verify against the actual base and head branches, not just `main`.
- **Large diffs need file-level reading**: do not rely on a truncated pasted diff for a complex review.
- **Documentation-only changes need a different mix of checks**: skip or soften performance review unless the docs make performance claims.
- **A dirty worktree changes the git strategy**: prefer non-destructive inspection or a temporary worktree over branch switching.
- **Sub-agent use is opt-in**: if the user did not ask for delegated or parallel review, do the work yourself.
- **Confidence must be earned**: do not report speculative issues as blockers.
