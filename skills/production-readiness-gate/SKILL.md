---
name: production-readiness-gate
description: Final conservative production-readiness gate for PRs, branches, artifacts, reports, or completed fixes. Use when the user invokes this skill directly, asks for "one more round of verification", "production ready", "confidence score", "leadership-ready", "robust reliable reusable", or says "I do not want to fail".
---

# Production Readiness Gate

Run the final fail-closed verification pass after a solution appears complete. This skill does not replace a normal code review or `pr-review-fix`; it decides whether the current target is ready to trust, reuse, explain to leadership, and move toward production.

Default intent when this skill is triggered:

> Run one more round of verification. I need production readiness, leadership-safe confidence scores, and clear residual risks.

The user should not have to restate that full sentence every time. Once this skill is invoked, assume that default intent unless the user narrows or changes the request.

## Instructions

Parse the current request and identify the exact target. The target may appear in the same prompt, recent conversation context, or a follow-up answer:

- PR number or URL
- branch and base branch
- commit SHA
- report, document, or generated artifact path
- local skill directory, reusable workflow package, or file/directory artifact
- deployed environment or runtime surface

If the target is clear, proceed with the gate. If the target is not clear from the request or recent context, ask one concise question before judging readiness:

```text
What exact target should I run the production-readiness gate against: PR, branch, commit, report/artifact path, or deployed environment?
```

Treat high-stakes language such as "I do not want to fail" as a request for conservative verification, not reassurance. Do not call a solution production-ready until the evidence supports that claim.

## Review Evidence Lenses

For PR or code targets, include these lenses when they apply. Treat them as evidence inputs for the gate, not as the final verdict:

- project-guideline or repository-memory compliance
- obvious bug and regression scan
- git history, blame, or prior-PR context for changed files
- unresolved review comments or carried-forward feedback
- code-comment and documentation accuracy
- test coverage quality, especially negative and boundary cases
- silent failure, error handling, fallback, retry, and logging behavior
- type, schema, or invariant strength
- simplification and maintainability opportunities

Only report high-confidence issues as readiness risks. Lower-confidence or non-blocking ideas belong in Room For Improvement.

## Verification Flow

1. Establish source of truth:
   - exact target, base, head, SHA, artifact path, or deployment URL
   - current local worktree state
   - whether changes are committed and pushed when a PR is involved
   - live PR mergeability, checks, review state, and comments when GitHub is the source of truth
   - for local skill or artifact directories, absolute path, file inventory, modification times, provenance manifest when present, and a content checksum or explicit caveat when no versioned source exists
2. Reconstruct the claim:
   - what was fixed or built
   - what future cases it should cover
   - what user-facing, operational, or leadership promise it is making
3. Build a risk-surface map. Use [references/risk-surface-checklist.md](references/risk-surface-checklist.md) when the changed surface is broad or high-risk.
4. Create an evidence plan:
   - required tests and checks
   - adversarial or negative cases
   - runtime or smoke checks
   - docs, memory, or wiki checks if the workflow requires them
5. Run the strongest practical verification bundle:
   - diff and changed-file inspection
   - targeted tests for touched behavior
   - full test suite when blast radius justifies it
   - lint, typecheck, formatting, and repo-specific validation
   - live PR/check-state verification when applicable
   - real runtime or dependency smoke checks when credentials and environment exist
6. Judge reusability:
   - identify whether the fix is shared-path or service-specific
   - prove it covers more than the exact happy-path case
   - state what future cases are still not covered
7. Separate residual risks from room-for-improvement ideas:
   - residual risks are readiness-relevant caveats, blockers, or follow-up actions that can affect confidence
   - room-for-improvement items are useful hardening, polish, coverage, observability, or process improvements that are not required for the current readiness verdict
8. Score readiness using [references/readiness-rubric.md](references/readiness-rubric.md).
9. Produce a leadership-safe final answer using the output shape below.

## Output Shape

Use this structure for the final response:

```markdown
**Verdict**: Ready / Ready With Caveats / Not Ready

**Confidence**
- Code/PR/artifact readiness: N/100
- Runtime/deployment readiness: N/100
- Leadership-share readiness: N/100

**Evidence Verified**
| Check | Result |
|---|---|

**Reusability Judgment**
...

**Residual Risks**
| Risk | Impact | Next action |
|---|---|---|

**Room For Improvement**
| Suggestion | Why it helps | Priority |
|---|---|---|

**Leadership Summary**
...
```

For deeper verification records, use [references/evidence-ledger-template.md](references/evidence-ledger-template.md).

For local skill package audits, include [references/release-notes.md](references/release-notes.md) when reporting version or provenance, and use [references/golden-transcripts.md](references/golden-transcripts.md) as deterministic examples of the expected response contract.

## Validation

Before calling the gate complete:

- confirm the target and head state are current
- confirm every readiness score has a reason
- separate code/PR confidence from runtime/deployment confidence
- downgrade runtime confidence when runtime smoke checks were not run
- list any residual risk that leadership should know about
- include room-for-improvement suggestions when useful, but do not mix optional improvements with readiness-blocking risks
- avoid "production-ready" language if evidence is incomplete

After meaningful edits, refresh the manifest checksums first:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/update_manifest.py" "/Users/rob/.claude/skills/production-readiness-gate"
```

If the installed copy is backed by a source repository, pass `--source-repo`, `--source-commit`, and optionally `--source-tag` so the manifest can record commit-level provenance. Do not invent a source commit for a local-only install.

Then validate this skill with:

```bash
python3 "/Users/rob/.claude/skills/skill-builder/scripts/validate-skill.py" "/Users/rob/.claude/skills/production-readiness-gate"
```

Run the semantic smoke tests after meaningful edits:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/smoke_production_readiness_gate.py" "/Users/rob/.claude/skills/production-readiness-gate"
```

The smoke test verifies durable contract markers, `manifest.json`, trigger fixtures in [references/trigger-fixtures.json](references/trigger-fixtures.json), model-response contract fixtures in [references/response-contract-fixtures.json](references/response-contract-fixtures.json), golden transcript examples in [references/golden-transcripts.md](references/golden-transcripts.md), release/provenance notes in [references/release-notes.md](references/release-notes.md), and a temporary clean-install copy. After changing trigger examples, source-of-truth guidance, or support files, update the fixture file, golden transcripts, release notes, and manifest checksums in the same change.

Useful trigger tests:

1. `$production-readiness-gate`
   Expected outcome: asks for the exact target before judging readiness.
2. `$production-readiness-gate Run one more round of verification. I need production readiness, leadership-safe confidence scores, and clear residual risks.`
   Expected outcome: asks for the exact target unless recent context already identifies one.
3. `Run the production-readiness gate for PR 123 and give me confidence scores.`
   Expected outcome: verifies live PR state, checks, comments, source/base/head, tests, and mergeability before scoring.
4. `Let's do one more round of verification. I need this to be robust, reliable, reusable, and leadership-ready.`
   Expected outcome: reconstructs the claim, maps risk surfaces, proves reusability, and separates residual risks from optional improvements.
5. `Use production-readiness-gate to evaluate /path/to/a/local/skill`
   Expected outcome: treats the local path as the target, verifies the file inventory and validation commands, records checksum/version caveats, and avoids claiming commit-level traceability unless it exists.
6. `Is this production ready? I do not want to fail.`
   Expected outcome: applies conservative verification and returns Ready, Ready With Caveats, or Not Ready with caveats and confidence scores.
7. Near-miss: `Brainstorm production-readiness ideas for a future proposal.`
   Expected outcome: does not run the gate unless the user asks for a readiness verdict on a concrete target.
8. Near-miss: `Help me draft a production-readiness checklist for a future project.`
   Expected outcome: provides planning help without scoring readiness or using the gate output shape.
9. Near-miss: `What does production ready usually mean for services like this?`
   Expected outcome: explains the concept without judging a concrete target.

## Gotchas

- A green test run is not the same as production readiness.
- Mergeable is not the same as deployed and smoke-tested.
- Reusability must be proved with shared-path behavior or multiple cases, not assumed from one example.
- Leadership-ready summaries must include caveats without burying them.
- Room-for-improvement items should not dilute the verdict. If an item is required for readiness, classify it as a residual risk instead.
- If runtime access, credentials, or deployment state cannot be verified, say so and lower runtime confidence.
