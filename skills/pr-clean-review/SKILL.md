---
name: pr-clean-review
description: Clean a pull request with a fast-strict review/fix workflow: one broad PR review, batched blocker/high fixes, evidence-ledger verification, and a clean-room final review. Use when the user says "make this PR clean and mergeable", "review and fix this PR until clean", "use team review and pr review fix in a loop", or asks for parallel xhigh PR cleanup without merging.
---

# PR Clean Review

Use this skill for end-to-end PR cleanup when the user wants one workflow to
review, fix, verify, and report merge readiness without repeatedly restarting
full review sessions.

The default mode is **fast-strict**:

- run one broad discovery pass at team-review depth
- freeze blocker/high findings into an evidence ledger
- fix blocker/high findings in batches
- prove each risky surface with direct tests or probes
- run one context-isolated final clean-room review on the exact final head
- report code-clean separately from GitHub merge-box eligibility

This skill is the experimental single-entry workflow. Keep `pr-review-fix`
untouched unless the user explicitly asks to consolidate the skills.

## Severity Policy

Only blocker/high findings are part of the clean gate:

- `[CRITICAL]` is a blocker.
- Evidence-backed `[WARNING]` is high severity.
- `[SUGGESTION]` is non-blocking by default.

Do not fix suggestions unless the user explicitly asks for polish or low-severity
cleanup. Suggestions may be reported in the final output, but they do not prevent
the PR from being called code-clean.

## Review Engine

Before the first review pass, read the current installed review skills when
available:

```bash
/Users/rob/.claude/skills/team-review/SKILL.md
/Users/rob/.claude/skills/team-review-plus/SKILL.md
```

Use `team-review-plus` evidence controls when available, while preserving the
core `team-review` lenses:

- context packet first
- security, performance, correctness, and guardrail lenses
- PR base/head verification
- carried-forward review comment handling
- false-positive filtering and confidence calibration
- independent verification of important claims before accepting findings

When the user asks for parallel review, xhigh, or "XI" effort, use up to four
disjoint reviewers for the initial discovery pass. Keep review and fix roles
separate so the fixer is not the only reviewer of its own changes.

## Fast-Strict Workflow

1. Resolve the exact PR target.
   - Use `gh pr view` for PR number, base branch, head branch, head SHA,
     mergeability, status checks, and review state.
   - Use the PR's real base branch, not `main` by default.
   - If the current checkout is dirty or stale, use a clean worktree, temp
     clone, or archive snapshot.
2. Build the context packet.
   - Diff against the true base.
   - Changed files and line counts.
   - PR intent/description.
   - Existing unresolved review comments.
   - Prior findings from the conversation.
   - Risk surfaces changed by the diff.
3. Run one broad read-only discovery pass.
   - Use `team-review-plus` if present; otherwise use `team-review`.
   - Use security, performance, correctness, and guardrail lenses.
   - Use parallel xhigh reviewers only when the user explicitly asked for
     parallel, delegated, team, xhigh, or XI review.
   - Verify the strongest findings with source reads, targeted tests, grep, or
     direct probes before accepting them.
   - Downgrade plausible but unproven concerns to suggestions or questions.
4. Freeze the blocker/high ledger.
   - Convert every `[CRITICAL]` and evidence-backed `[WARNING]` into a required
     ledger item.
   - Include unresolved prior blocker/high review comments.
   - Keep each item open until it is fixed or disproven on the current PR head.
   - Keep suggestions outside the fix queue unless the user asked for them.
5. Batch the fixes.
   - Fix all related blocker/high findings together where safe.
   - Patch the smallest coherent behavior surface.
   - Add focused regression tests or direct probes when practical.
   - Do not merge.
   - Commit and push only when the user explicitly asked for push or for the
     remote PR to be cleaned.
6. Run focused post-fix verification.
   - Re-check every open ledger item on the new head.
   - Re-run focused tests for touched behavior.
   - Re-run risk-surface probes affected by the fix.
   - Verify public entrypoints, docs, schemas, launchers, and mirrored
     implementations still agree when the diff touches those contracts.
   - Run repo-standard static/format checks or state why they could not run.
7. Use bounded additional rounds.
   - Normal PRs get at most two fix rounds.
   - High-risk PRs get at most three fix rounds.
   - If the same blocker repeats after a fix, stop and report the design or
     implementation decision needed instead of continuing to churn.
8. Run one final clean-room calibration on the exact final head.
   - Default to a context-isolated subagent inside the same session.
   - Give the final reviewer only the PR target, base/head metadata, changed
     files, and a request for team-review/team-review-plus depth.
   - Do not give it the fix history, ledger conclusions, or expected answer.
   - Save the raw final review output to a stable artifact path.
   - Any `[CRITICAL]` or evidence-backed `[WARNING]` from this pass re-enters
     the fix queue if round limits allow it.
   - Use a truly new session only when the PR is high-risk, the final
     reviewer finds a blocker/high issue, or the user explicitly asks for it.
9. Stop only when the exit gate in `references/exit-gate.md` passes.

## Risk Surfaces

Maintain a risk-surface map whenever the diff touches:

- validation, normalization, parsing, coercion, or schema contracts
- auth, tokens, host allowlists, credentials, env loading, or endpoint routing
- shell launchers, hooks, CLIs, MCP servers, or public entrypoints
- mirrored implementations such as Python plus shell helpers
- generated docs, diagrams, README claims, or help text that describe live behavior
- concurrency, locking, retries, cleanup, timeouts, or resource limits

Every changed risky surface needs direct proof. Happy-path tests are not enough;
include negative probes that show unsafe inputs are rejected or dangerous paths
fail closed.

## Evidence Ledger

Keep a JSON ledger during the run. Use this shape:

```json
{
  "pr": 123,
  "mode": "fast-strict",
  "risk_level": "normal",
  "head_sha": "abc123",
  "github": {
    "headRefOid": "abc123",
    "baseRefName": "main",
    "headRefName": "feature/pr-branch",
    "mergeable": "MERGEABLE",
    "mergeStateStatus": "CLEAN"
  },
  "workspace": {
    "strategy": "temp-clone",
    "clean": true
  },
  "review_structure": {
    "source_skill": "team-review-plus",
    "source_skill_loaded": true,
    "team_review_skill_loaded": true,
    "parallel_agents_requested": true,
    "reasoning_effort": "xhigh",
    "reviewer_count": 4,
    "lenses": ["security", "performance", "correctness", "guardrails"],
    "initial_discovery_full": true,
    "post_fix_verification": "ledger-focused",
    "final_clean_room": true
  },
  "execution_policy": {
    "push_requested": true,
    "pushed": true,
    "remote_head_verified": true,
    "merged": false
  },
  "fix_scope": {
    "allowed_severities": ["CRITICAL", "WARNING"],
    "suggestions_blocking": false,
    "fixed_low_severity": false,
    "user_requested_low_severity_cleanup": false
  },
  "round_limits": {
    "max_fix_rounds": 2,
    "fix_rounds_used": 1,
    "stopped_for_repeat_blocker": false
  },
  "rounds": [
    {
      "round": 1,
      "head_sha": "abc123",
      "review_mode": "parallel-team-review-plus",
      "phase": "initial-discovery",
      "critical": 1,
      "warning": 2,
      "suggestion": 3,
      "summary": "Initial discovery"
    },
    {
      "round": 2,
      "head_sha": "abc123",
      "review_mode": "ledger-focused-verification",
      "phase": "post-fix-verification",
      "critical": 0,
      "warning": 0,
      "suggestion": 3,
      "summary": "Ledger items closed and risk surfaces probed"
    }
  ],
  "findings": [
    {
      "id": "F1",
      "finding": "URL guard accepted userinfo host variant",
      "severity": "WARNING",
      "status": "closed",
      "file": "src/example.py",
      "proof": "pytest tests/test_example.py -q",
      "fixed_by": "commit sha or disproven",
      "verified_by": "focused verification and final clean-room review"
    }
  ],
  "risk_surfaces": [
    {
      "surface": "URL allowlist",
      "status": "closed",
      "entrypoints": ["CLI", "MCP"],
      "negative_tests": ["userinfo host rejected", "trailing-dot host rejected"],
      "observed_behavior": "Unsafe variants fail closed"
    }
  ],
  "final_calibration": {
    "head_sha": "abc123",
    "review_mode": "clean-room-team-review-plus",
    "fresh": true,
    "independent": true,
    "context_isolated": true,
    "critical": 0,
    "warning": 0,
    "commands": ["pytest tests -q", "git diff --check"]
  },
  "clean_passes": [
    {
      "name": "final clean-room calibration",
      "head_sha": "abc123",
      "review_mode": "clean-room-team-review-plus",
      "fresh": true,
      "independent": true,
      "critical": 0,
      "warning": 0
    }
  ],
  "external_reviews": [
    {
      "source": "fresh-subagent-team-review",
      "head_sha": "abc123",
      "review_mode": "team-review-plus",
      "context_isolated": true,
      "team_review_skill_loaded": true,
      "critical": 0,
      "warning": 0,
      "proof": "fresh context-isolated subagent output",
      "artifact_path": "/absolute/path/to/final-clean-room-review.md",
      "reconciled": true
    }
  ]
}
```

The validator intentionally fails closed on the evidence contract:

- `mode` must be `fast-strict`.
- `final_calibration.head_sha` must be present and match `head_sha`.
- Every run must record the four core team-review lenses: security,
  performance, correctness, and guardrails.
- Parallel xhigh runs must also record `parallel_agents_requested: true`,
  `reasoning_effort: xhigh`, and at least four reviewers.

Validate the ledger before claiming success:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_clean_gate.py" path/to/ledger.json
```

After editing this skill or validator, refresh the manifest and run the bundled
regression test:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/update_manifest.py" "/Users/rob/.claude/skills/pr-clean-review"
```

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/test_validate_clean_gate.py"
```

The regression suite uses `references/golden-ledgers.json` for the canonical
valid ledger and includes CLI smoke checks plus negative tests for stale final
heads, missing lenses, merge-box blockage, unauthorized pushes, and suggestion
scope drift.

For a PR that needs the stricter two-pass gate, require two clean independent
passes explicitly:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_clean_gate.py" path/to/ledger.json --require-two-clean-passes
```

If GitHub policy is blocked but the code/test gate is otherwise clean, use:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/validate_clean_gate.py" path/to/ledger.json --code-clean-only
```

In that case, report "code-clean but GitHub merge box blocked"; do not say the
PR is mergeable.

## Output

Final output should be short and evidence-first:

```markdown
PR <N> is code-clean on head `<sha>`.

GitHub merge state: `<mergeStateStatus>` / `<mergeable>`.
Mode: fast-strict.
Fix rounds: <count>/<limit>.
Fix commits: <sha list>.
Final verification: <key commands and results>.
Final clean-room review: <artifact path or subagent id>.
Suggestions: <count, non-blocking unless requested>.
Residual risk: <specific remaining risk or "none known from this pass">.
```

If the exit gate fails, lead with the blocker:

```markdown
I cannot call PR <N> clean yet.

Blocking reason: <finding or missing proof>.
Current head: `<sha>`.
Fix rounds used: <count>/<limit>.
Next action: <specific patch/probe/review step>.
```

## Gotchas

- A clean old-finding checklist is not a clean PR. The final calibration must
  still be a fresh context-isolated review of the exact current head.
- Do not let suggestions keep the loop open unless the user explicitly asked
  for low-severity cleanup.
- Do not conflate `mergeable: MERGEABLE` with GitHub UI eligibility. If
  `mergeStateStatus` is `BLOCKED`, report the policy/check state separately.
- Stacked PRs create false positives when reviewed against the wrong base.
- Dirty local checkouts can mix unrelated edits into the branch. Prefer an
  isolated patch surface and verify the remote head after push.
- More looping is not better. If the same blocker repeats after a fix, stop and
  explain the design decision needed.
