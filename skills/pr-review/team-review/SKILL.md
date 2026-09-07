---
name: team-review
description: Thorough PR review with 4 specialized agent teams (security, performance, correctness, guardrails) plus independent verification. Use when user says "review this PR", "team review", "check this PR", or wants a multi-perspective code review before merging.
argument-hint: "<PR URL, PR#, branch name, or file paths>"
allowed-tools: Read, Grep, Glob, Bash, Agent, TeamCreate, TeamDelete, TaskCreate, TaskUpdate, TaskList, TaskGet, SendMessage
---

# Thorough PR Review — Team + Independent Verification

You are a senior engineering lead coordinating a thorough PR review. The process has 3 phases:
1. **Phase 1**: Spawn 4 specialized agent reviewers in parallel
2. **Phase 2**: Independent hands-on verification (checkout branch, run tests, grep for issues)
3. **Phase 3**: Merge safety analysis and findings presentation

**IMPORTANT**: Do NOT post any comments or approve/reject the PR. Present all findings to the user for discussion. The user decides what feedback to provide.

## Phase 1: Agent Team Review

### Step 1: Parse Arguments

Parse `$ARGUMENTS` to determine what to review:

- **PR URL or number** (e.g., `https://github.com/.../pull/123` or `#123` or `123`) — extract PR number, use `gh pr diff <number>` and `gh pr view <number>`
- **Branch name** (e.g., `feature-auth`) — use `git diff main...<branch>`
- **File paths** (e.g., `src/auth.py src/models.py`) — use `git diff` on those files
- **Empty** — ask the user what they want reviewed

### Step 2: Gather Context

Before spawning agents, collect the full review context:

1. Get the complete diff
2. List all changed files with additions/deletions per file
3. Read PR description/body for intent
4. **Detect stacked PRs**: Check if the PR's base branch is NOT `main`. If it targets another feature branch, get the **incremental diff** (`git diff <base-branch>...<head-branch>`) instead of the full diff vs main. Tell the agents about the stacked context.
5. **For large diffs (>500 lines)**: Instead of embedding the full diff in agent prompts, instruct agents to read files directly from the PR branch. Provide file paths and key areas to focus on.
6. **For documentation-only PRs** (no code changes): Skip the performance reviewer. Replace it with a fact-checking agent that verifies claims against the actual codebase.

Store this as `REVIEW_CONTEXT`.

### Step 3: Create Team and Tasks

1. Use `TeamCreate` with name `review-<identifier>`
2. Create tasks for each reviewer + a synthesis task blocked by all reviewers
3. Spawn 4 Agent teammates (see reviewer prompts below)

**CRITICAL for correctness reviewer**: Always instruct the correctness agent to **checkout the actual PR branch** before verifying claims. Stacked PRs have different content on their branch vs what `main` shows. The correctness agent must grep/read files ON THE PR BRANCH, not on main.

### Step 4: Reviewer Prompts

Each reviewer gets the `REVIEW_CONTEXT` plus domain-specific instructions. All reviewers must:
- Claim their task with TaskUpdate (owner + in_progress)
- Mark task completed when done
- Send findings to "team-lead" via SendMessage

#### Teammate: `security`

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

#### Teammate: `performance`

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

#### Teammate: `correctness`

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

#### Teammate: `guardrails`

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

### Step 5: Wait for Completion

Wait until all reviewer tasks are marked completed. Do not begin Phase 2 until all teammates have finished.

## Phase 2: Independent Hands-On Verification

After the team reports in, do your OWN verification. This catches false positives/negatives from the agents.

### Step 6: Checkout and Test

1. `git fetch origin <branch> && git checkout --detach origin/<branch>`
2. `source .venv/bin/activate && python -m pytest tests/ -q` — run full test suite
3. Verify key claims from the team review:
   - If correctness flagged missing imports/methods: grep to confirm
   - If correctness flagged a critical bug: verify it actually exists on the PR branch (agents sometimes check against main for stacked PRs — this is a known false positive pattern)
   - If guardrails flagged a removed safety check: verify it's actually gone
4. Check backward compatibility:
   - Grep for removed symbols still referenced elsewhere
   - Verify public API imports still work
5. `git checkout main` when done

### Step 7: Synthesize and Clean Up

1. Shut down all teammates via SendMessage (shutdown_request)
2. TeamDelete to clean up
3. Produce the **Team Review Summary** table:

```markdown
## Team Review Summary

**PR**: [title] | **Files**: N | **Lines**: +X / -Y

### Critical Issues — [None / list]
### Warnings — [None / list]
### Suggestions — [list]

### Review Breakdown
| Reviewer | Criticals | Warnings | Suggestions |
|----------|-----------|----------|-------------|
| Security | N | N | N |
| Performance | N | N | N |
| Correctness | N | N | N |
| Guardrails | N | N | N |
```

## Phase 3: Merge Safety Analysis

### Step 8: Present Findings

After the team summary, provide YOUR OWN independent analysis answering these questions:

#### My Hands-On Verification
Table of checks performed and results (tests, imports, grep verifications, etc.)

#### How is this PR useful?
- What problem does it solve?
- What value does it add to the codebase?
- Is it a prerequisite for other work?

#### Will we have any issues merging?
- Will it break any existing functionality or features?
- Are there backward compatibility concerns?
- Are there merge order dependencies?
- Confidence score (0-100) with reasoning

### Step 9: Wait for User Decision

**STOP HERE.** Do not post comments, approve, or reject. Present all findings and wait for the user to decide:
- What feedback to provide
- Whether to approve, request changes, or discuss further
- What inline comments to post

Only act on the PR when the user explicitly instructs you to do so.

## Gotchas

- **Stacked PRs cause false positives** — correctness agents sometimes check against `main` instead of the PR branch. For PRs that depend on other unmerged PRs, the branch has parent changes that `main` doesn't. Always instruct agents to checkout and verify on the actual PR branch.
- **Large diffs (>500 lines) overflow agent context** — don't embed the full diff in agent prompts. Instead, instruct agents to read files directly on the PR branch. Provide file paths and areas to focus on.
- **Doc-only PRs don't need performance review** — skip the performance agent for PRs with zero code changes. Replace it with a fact-checking agent that verifies doc claims against the actual codebase.
- **Always use inline comments, never general PR comments** — inline comments on specific files are more actionable. Use `gh api .../pulls/N/comments` with `path` and `line` or `subject_type: "file"` when the target line isn't in the diff.
- **Agent shutdown race** — `TeamDelete` may fail if agents haven't acknowledged shutdown yet. Retry once if you get "active members" error.
