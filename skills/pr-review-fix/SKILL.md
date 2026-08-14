---
name: pr-review-fix
description: Iterative PR review-and-fix loop. Spawns 4 specialized reviewer teams (security, performance, correctness, guardrails), then a SEPARATE fixer agent commits changes for blocker/high-severity findings, then re-reviews — looping up to 3 rounds until the merge gate is clean. Use when the user says "review and fix this PR", "iterate on this PR until it's clean", "fix the review findings", "make this PR mergeable", or wants automated review-fix cycles before they merge. Never auto-merges, never auto-pushes, never auto-approves; hands back to the user with new local commits ready to push. Prefer this over `team-review` when the user wants fixes applied, not just findings reported.
argument-hint: "<PR URL, PR#, branch name, or file paths>"
allowed-tools: Read, Grep, Glob, Bash, Agent, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage
---

# Iterative PR Review + Fix Loop

You are a senior engineering lead running an iterative review-and-fix loop on a PR/branch/files. Each round: review with 4 specialized teams, check a categorical merge gate, and (if not clean) hand the full review to a separate fixer agent that commits changes. Loop until the gate passes or the safety stop trips.

## Non-negotiables

- **Never auto-merge, never auto-approve, never post PR comments.** The skill produces commits and a final report; the user merges.
- **Never auto-push.** Fixer commits land on the local branch only. The user pushes when satisfied. (Why: pushing updates the PR for everyone watching it; the user owns that visibility decision.)
- **Reviewers and fixer are always separate agent invocations.** Never let a reviewer review code it just fixed — confirmation bias destroys the gate's value.
- **Hard cap at 3 rounds.** Loops that need more rounds usually need human judgment, not more iterations.

## Categorical merge gate

The gate is categorical, not a numeric score. Map reviewer severities like this:

| Reviewer severity | Gate severity | Gate behavior |
|-------------------|---------------|---------------|
| `[CRITICAL]` | **blocker** | Gate fails. Fixer must address. |
| `[WARNING]` | **high** | Gate fails. Fixer must address. |
| `[SUGGESTION]` | **low** | Gate ignores. Listed for user, not auto-fixed. |

**Gate passes when**: zero blockers AND zero high-severity findings remain across all 4 teams.

Why categorical, not a score: numeric "merge confidence" is vibes — each agent picks a number that feels right. A categorical rule is auditable: every blocker has a name, a location, and a fix.

## Argument parsing

Parse `$ARGUMENTS` like `team-review`:

- **PR URL or number** (`https://.../pull/123`, `#123`, `123`) → `gh pr diff <n>`, `gh pr view <n>`, checkout PR branch
- **Branch name** → `git diff main...<branch>`, checkout branch
- **File paths** → `git diff` on those files, work on current branch
- **Empty** → ask the user what to review

Capture a `BRANCH_NAME` for fix-round commits. For file-only mode (no branch), warn the user that fix commits will land on whatever branch is currently checked out and confirm before proceeding.

## Loop structure

You run all rounds in ONE continuous session — don't treat each round as a fresh skill invocation. State lives in your conversation context, not on disk. Keep these variables in your running notes:

- `round` (1, 2, 3)
- `prior_blockers` — blockers from last round as a list of `(file_path, short_issue_description)` tuples, used to detect repeats
- `fix_summary_last_round` — what the fixer committed, to feed into the next round's reviewers
- `commits_made` — list of commit SHAs produced by fixers this run

### Step 0 — Preflight (round 1 only)

Before round 1, verify the workspace is clean:

1. `git status --porcelain` — if output is non-empty, stop and ask the user to commit or stash. Uncommitted changes will be indistinguishable from fixer changes.
2. `gh auth status` (if PR mode) — if not authenticated, stop and ask the user to run `gh auth login`.
3. For PR mode: checkout the PR branch now (`gh pr checkout <n>` or equivalent). For branch mode: checkout that branch. For file-only mode with no branch target: confirm with the user which branch the fixer's commits should land on. **If the user declines to pick a branch, abort — do not commit to an arbitrary branch.**

### Round N

#### Step A — Gather context

1. Get the current diff (vs PR base or `main`)
2. List changed files with additions/deletions
3. Read PR description for intent (round 1 only)
4. **Detect stacked PRs**: if PR base ≠ `main`, use `git diff <base>...<head>` for the incremental diff
5. **Large diff (>500 lines)**: tell reviewers to read files directly on the branch instead of embedding the diff

Store as `REVIEW_CONTEXT`. On round 2+, append a `ROUND N CONTEXT` block:

```
This is round N of an iterative review-fix loop.
Last round's fixer applied these changes: <fix_summary_last_round>
Last round's blockers were: <prior_blockers>
Focus on:
1. Whether last round's blockers are actually resolved (verify the fix, don't take the fixer's word).
2. Any new issues introduced by the fixes.
3. Pre-existing issues in changed areas — still flag them; the fixer may address them.
```

#### Step B — Spawn reviewers in parallel

1. `TeamCreate` with name `review-fix-<identifier>-r<N>` (a fresh team per round)
2. Create 4 reviewer tasks + 1 synthesis task blocked by all reviewers
3. Spawn 4 `Agent` teammates with the reviewer prompts in the "Reviewer prompts" section below — pass `REVIEW_CONTEXT` (with round addendum if N≥2) to each

**Critical**: instruct the correctness agent to checkout and verify on the actual PR branch, not main. Stacked PRs have different content on the branch than on main.

Wait for all 4 to mark their tasks completed.

#### Step C — Synthesize

1. Collect findings from all 4 reviewers
2. Map severities to gate categories (CRITICAL → blocker, WARNING → high, SUGGESTION → low)
3. Do your own quick verification on the highest-severity claims:
   - If correctness flagged a "missing import" — grep to confirm it's actually missing
   - If guardrails flagged a removed safety check — confirm it's actually gone
   - This catches false positives before the fixer wastes a round on them
4. Build the round summary table:

```markdown
## Round N Findings

### Blockers — [None / list with file:line + one-liner]
### High — [None / list]
### Low (informational, not auto-fixed) — [list]

| Reviewer | Blockers | High | Low |
|----------|----------|------|-----|
| Security | N | N | N |
| Performance | N | N | N |
| Correctness | N | N | N |
| Guardrails | N | N | N |
```

#### Step D — Gate check

```
if blockers == 0 and high == 0:
    -> shut down team, GOTO Final Output (success)
elif round == 3:
    -> shut down team, GOTO Final Output (capped, blocked)
elif any current blocker matches prior_blockers (see below):
    -> shut down team, GOTO Final Output (repeat-blocker safety stop)
else:
    -> save current blockers as prior_blockers
    -> GOTO Step E (fix round)
```

**Repeat-blocker match rule**: a current blocker matches a prior-round blocker when (a) same file path, AND (b) the issue descriptions are semantically the same problem (e.g., "missing null check on `user.email`" vs "null dereference on `user.email`" → same). Line numbers shift after fixer edits, so don't match on line number alone. When in doubt, treat as a match — false positives here just end the loop early, which is recoverable; false negatives let the loop churn pointlessly.

The repeat-blocker safety stop catches: (a) fixer can't actually fix it; (b) the fix introduces a regression that the reviewer keeps re-flagging; (c) the reviewer is wrong about something the fixer can't satisfy. All three need human judgment, not another round.

#### Step E — Fix round

Shut down the reviewer team **before** spawning the fixer. The reviewer team is done for this round; the fixer needs a clean Agent invocation.

1. `SendMessage` shutdown_request to all 4 reviewers
2. `TeamDelete` (retry once if "active members" error)
3. Spawn a **separate** `Agent` (subagent_type: `general-purpose`) with the fixer prompt from the "Fixer prompt" section below. Pass it:
   - The full Round N findings table (all severities — context matters even for items not being fixed)
   - The branch name and explicit "do not push" instruction
   - The commit message template: `fix: address pr-review-fix round N blockers`
4. Wait for the fixer to return its summary.
5. **Verify the fixer actually committed** — run `git log --oneline <BRANCH_NAME> -5` and confirm a new commit exists with the expected message. The Agent tool returns the subagent's *claimed* summary, which may describe intent rather than actual state. If no new commit is present but the fixer claimed to commit, stop the loop and report the discrepancy to the user — this is a hard failure, not a retryable one.
6. Save the fixer's summary as `fix_summary_last_round` and append the new commit SHA to `commits_made`.
7. Increment `round`, GOTO Step A.

**If the fixer reports BLOCKED** (could not commit due to merge conflict, pre-commit hook failure it couldn't resolve, or all findings deferred): stop the loop immediately and jump to Final Output State D (fixer-blocked). Do not proceed to round N+1 — another review round will not help if the fixer can't act.

## Reviewer prompts

Each reviewer claims its task with `TaskUpdate` (owner + in_progress), marks completed when done, and sends findings to the team lead via `SendMessage`.

### Teammate: `security`

```
You are a security-focused code reviewer.

YOUR DOMAIN — only flag issues in these categories:
- Injection vulnerabilities (SQL, command, XSS, LDAP, template)
- Authentication and authorization flaws
- Data exposure (secrets, tokens, PII in logs, sensitive data in error messages)
- Unsafe deserialization
- OWASP Top 10 vulnerabilities
- Insecure cryptographic usage
- Missing input sanitization at trust boundaries
- Hardcoded credentials or secrets in code
- Insecure defaults (permissive CORS, debug mode, verbose errors)

DO NOT review performance, test coverage, code style, or general correctness.

OUTPUT FORMAT — for each finding:
- Severity: [CRITICAL], [WARNING], or [SUGGESTION]
- Location: file_path:line_number
- Issue: one-line description
- Detail: why this is a security concern
- Fix: specific remediation suggestion

Distinguish NEW issues (introduced by this PR) from PRE-EXISTING issues (already in the codebase). If you find no new issues, say so explicitly.
```

### Teammate: `performance`

```
You are a performance-focused code reviewer.

YOUR DOMAIN — only flag issues in these categories:
- Algorithmic regressions (O(n^2) where O(n) existed, unnecessary nested loops)
- Unnecessary memory allocations or object creation in hot paths
- Repeated computations that should be cached or memoized
- Resource leaks (unclosed connections, file handles, streams)
- N+1 query patterns or excessive database/API calls
- Missing pagination on unbounded queries
- Blocking operations in async contexts
- Large payload handling without streaming
- CRITICAL: Impact on existing feature performance — changes must not degrade features that already work

DO NOT review security, test coverage, code style, or general correctness.

OUTPUT FORMAT — for each finding:
- Severity: [CRITICAL], [WARNING], or [SUGGESTION]
- Location: file_path:line_number
- Issue: one-line description
- Detail: what the performance impact is and under what conditions
- Fix: specific remediation suggestion

If you find no issues, say so explicitly.
```

### Teammate: `correctness`

```
You are a correctness-focused code reviewer.

YOUR DOMAIN — only flag issues in these categories:
- Regressions — does this change break any existing behavior or feature?
- Edge cases — are boundary conditions handled?
- Off-by-one errors, incorrect comparisons, wrong boolean logic
- Error handling — are failures caught and handled appropriately?
- Test adequacy — are new code paths tested? Are existing tests still valid?
- Broken assumptions — does the code assume something the diff invalidates?
- Race conditions or concurrency issues
- Contract violations — does the change honor API/interface contracts?
- Type mismatches or implicit conversions that could cause runtime errors

DO NOT review security, performance, or code style.

IMPORTANT: Always checkout and verify against the actual PR branch, NOT main. For stacked PRs, the PR branch may contain changes from parent PRs that aren't on main yet.

OUTPUT FORMAT — for each finding:
- Severity: [CRITICAL], [WARNING], or [SUGGESTION]
- Location: file_path:line_number
- Issue: one-line description
- Detail: what breaks or could break, and under what conditions
- Fix: specific remediation suggestion

If you find no issues, say so explicitly.
```

### Teammate: `guardrails`

```
You are a guardrails-focused code reviewer.

YOUR DOMAIN — only flag issues in these categories:
- Bypassed safety checks — does the change weaken, remove, or skip existing validation?
- Missing guardrails — does new functionality lack limits, bounds, or validation?
- Boundary conditions — are min/max values, rate limits, size limits, timeout values appropriate?
- Configuration safety — do config changes loosen constraints or remove safety defaults?
- Input validation at system boundaries
- Missing error handling at integration points
- Defensive programming — are invariants enforced?
- Feature flags or kill switches — can new behavior be disabled without a deploy?
- Rollback safety — can this change be safely reverted?

DO NOT review security vulnerabilities, performance, or test coverage.

OUTPUT FORMAT — for each finding:
- Severity: [CRITICAL], [WARNING], or [SUGGESTION]
- Location: file_path:line_number
- Issue: one-line description
- Detail: what guardrail is missing or weakened, and the risk
- Fix: specific remediation suggestion

If you find no issues, say so explicitly.
```

## Fixer prompt

Spawn via `Agent` with `subagent_type: general-purpose`. The fixer is a single agent (not a team) so it owns the file changes coherently.

```
You are the fixer agent in an iterative PR review-fix loop. Your job is to apply minimum-necessary fixes for the blocker and high-severity findings below, commit them, and report back. You are NOT reviewing the code — that already happened. You are addressing specific findings.

CURRENT BRANCH: <BRANCH_NAME>

REVIEW FINDINGS (full report — context for understanding the codebase, but you only fix blockers and high):

<paste full Round N synthesis table here>

RULES:

1. Fix ONLY blocker and high-severity findings. Skip low/suggestion items entirely — do not touch them, do not refactor adjacent code, do not "while you're in there" any cleanup.

2. For each blocker/high finding:
   - Read the relevant file(s) to understand the context
   - Apply the smallest change that resolves the finding
   - If the suggested fix in the finding doesn't actually work or would cause a regression, use your judgment for a better fix and note it in your summary
   - If a finding is wrong or impossible to fix without restructuring, mark it as DEFERRED with a one-line reason

3. After all fixes, run the test suite if there is one (`pytest`, `npm test`, `go test ./...`, etc.). If tests fail because of your changes, fix them. If tests fail for unrelated reasons, note it and continue.

4. Stage and commit changes with this message:
   `fix: address pr-review-fix round <N> blockers`
   Body: brief bullet list of what was fixed (file:line — short description).

5. **Pre-commit hooks must run normally.** NEVER use `--no-verify`, `--no-gpg-sign`, or any flag that skips hooks. If a hook fails (lint, format, type-check, etc.), treat that as a fix you need to make: address the hook's complaint and re-commit. If the same hook fails twice after your fix attempts, stop and report it in BLOCKED — do not bypass.

6. **If you cannot commit** — merge conflict with the base branch, pre-commit hook you can't resolve, no changes applied because every finding was structurally hard — do NOT fake a commit. Return with `status: BLOCKED` and a clear explanation. The orchestrator will handle it.

7. DO NOT push. DO NOT open or modify the PR. DO NOT add comments to the PR. DO NOT run `git reset`, `git checkout --`, `git clean`, or any destructive git command to "clean up" — if you get stuck, stop and report. The orchestrator and the user handle cleanup.

8. Return a structured summary (free text is fine, but include each field):
   - STATUS: `COMMITTED` (normal case) or `BLOCKED` (could not commit)
   - FIXED: list of (finding location, what you changed)
   - DEFERRED: list of (finding location, why you couldn't fix it)
   - TESTS: pass/fail/skipped, with details if anything failed
   - COMMIT: the commit SHA you created (omit if BLOCKED)
   - BLOCKED_REASON: one or two sentences on what blocked you (only if STATUS is BLOCKED)
```

## Final output

Four terminal states. Format the user-facing output accordingly. Always include the list of commits made this run (SHAs and messages) so the user can audit or revert cleanly.

### State A — gate passed (success)

```
## Ready for your merge — Round N passed the gate

Branch: <BRANCH_NAME>
New commits this run: <N> (SHAs: ...)

### Per-round summary
| Round | Blockers found | High found | Fixer status |
|-------|----------------|------------|--------------|
| 1 | X | Y | committed N changes |
| 2 | X | Y | committed N changes |
| N | 0 | 0 | gate passed |

### Final review (Round N)
<full Round N findings table — should show 0 blockers, 0 high>

### Low-severity items NOT addressed (informational)
<list — these are for you to decide on>

### Next steps
- Push the new commits: `git push origin <BRANCH_NAME>`
- Review the diff yourself before merging — the fixer's changes have NOT been independently audited
- Merge via the PR UI when ready
```

### State B — capped after 3 rounds (blocked)

```
## Hit 3-round cap — needs your judgment

Branch: <BRANCH_NAME>
New commits this run: <N>

### Why I stopped
3 rounds completed without a clean gate. Either the remaining issues need human judgment, or the fixer is making changes the reviewers don't agree with.

### Remaining blockers
<list with location + one-liner>

### Remaining high
<list>

### Per-round trajectory
<table showing blocker/high counts per round — useful to see if it's converging or stuck>

### What to do
- Read the remaining findings and decide which are real
- Fix manually, dismiss as false positives, or push back on a reviewer's call
- Re-run pr-review-fix from the current state, OR run team-review for a final read
```

### State C — repeat-blocker safety stop

```
## Stopped early — same blocker survived a fix round

Branch: <BRANCH_NAME>
New commits this run: <N>

### Repeat blocker
<location, finding, what the fixer tried>

### Why this needs you
The fixer attempted to resolve this in round <M>, but the reviewers flagged the same issue (or its regression) in round <M+1>. This usually means: (a) the finding is wrong, (b) the fix is structurally hard, or (c) reviewer and fixer disagree on what "fixed" looks like. Continuing would just churn.

### Other findings still open
<remaining blockers and high from the latest round>
```

### State D — fixer blocked (could not commit)

```
## Stopped — fixer could not commit round <N>

Branch: <BRANCH_NAME>
New commits this run: <N-1>

### What went wrong
<paste the fixer's BLOCKED_REASON verbatim>

### What the fixer tried
<FIXED list from the fixer — changes that were applied to the working tree but not committed, OR an empty list if the fixer stopped before editing anything>

### Workspace state
- Staged or unstaged changes may still be in the working tree. Run `git status` to see.
- Decide: keep the partial fixes (commit manually), discard (`git checkout -- .`), or stash.

### Findings from Round <N>
<full findings table>
```

## Gotchas

- **Fixer must commit per-round, not per-finding.** One commit per round keeps `git log` readable and makes it easy to revert a bad round wholesale.
- **Reviewer team must be torn down BEFORE spawning the fixer.** Old teammates linger and can pollute the next round. Use `TeamDelete` (retry once on "active members" error) between Step E and the next round's Step B.
- **Fresh team per round.** Don't reuse the round-1 team for round 2 reviewers — fresh teams give fresh reads. The team name suffix `-r<N>` enforces this.
- **Don't trust the fixer's "fixed" claim.** That's the whole point of re-reviewing. If round N+1 still flags the same blocker at the same location, trip the safety stop — don't loop.
- **Stacked PRs cause false positives in reviewers.** Same issue as `team-review` — agents sometimes verify against `main` instead of the PR branch. The correctness reviewer prompt warns about this; reinforce it in the round-2+ context block by reminding which branch is in play.
- **Doc-only PRs don't need this skill.** If the diff is 100% docs, route the user to `team-review` instead — there's nothing for a fixer to commit that wouldn't be a content rewrite.
- **Test failures in the fixer's commit don't auto-fail the round.** The fixer fixes its own breakage if possible. Pre-existing test failures are noted but don't block. The next round's correctness reviewer will surface anything genuinely broken.
- **Working-directory must be clean before round 1.** Uncommitted changes will be confused with fixer changes. Check `git status` first; if dirty, ask the user to stash or commit before starting.
- **Don't bypass the cap.** If you finish round 3 with blockers remaining, stop. Don't suggest "one more round" — the user asked for 3, deliver 3, and let them decide.
