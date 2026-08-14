---
name: codebase-review-suite
description: Orchestrate the full codebase review suite across codebase-* skills and synthesize findings into a deduplicated GitHub issue backlog. Use when the user asks to run all codebase review skills, perform a full repository review suite, coordinate cleanup/security/test/reliability/performance/data/API/docs/frontend/LLM-agent reviews, or create GitHub issues from suite findings.
---

# Codebase Review Suite

Run the installed `codebase-*` review skills as a coordinated assessment. This skill is an orchestrator, not a replacement for the individual skills: keep each lens separate, preserve evidence, then deduplicate findings into a clear backlog.

## Ground Rules

- Default to assessment-only. Do not edit code, create branches, open PRs, or create GitHub issues unless the user explicitly asks.
- Start with repo state: current path, branch, `git status --short`, remote, and whether `gh` can access the repository if issue creation is requested.
- Preserve user changes. Never revert or include unrelated dirty files.
- Run child review lenses one at a time. Do not paste all checklists into one pass.
- Treat issue creation as a second phase after the user reviews the proposed backlog.

## Suite Order

Run applicable skills in this order:

1. `codebase-cleanup` in assessment-only mode.
2. `codebase-dependency-supply-chain-review`.
3. `codebase-security-review`.
4. `codebase-llm-agent-safety-review` when LLM, agent, tool, MCP, RAG, memory, or automation surfaces exist.
5. `codebase-api-contract-review`.
6. `codebase-data-correctness-review`.
7. `codebase-test-quality-review`.
8. `codebase-reliability-review`.
9. `codebase-performance-review`.
10. `codebase-frontend-quality-review` when frontend surfaces exist.
11. `codebase-documentation-review`.
12. `codebase-architecture-review`.
13. `codebase-developer-experience-review`.

For each skill, explicitly apply that skill's workflow. If the skill body is not already loaded, read its `SKILL.md` and only the references needed for that lens.

## Follow-Up Skills

Use these only after the assessment/backlog phase, when the user explicitly asks to implement or plan a specific finding:

- `codebase-decomposition`: plan or execute an accepted module-splitting/decomposition finding from `codebase-architecture-review`.
- `codebase-prompt-caching-optimization`: audit or implement accepted LLM prompt caching cost/latency findings from `codebase-performance-review` or LLM call-site investigations.

Do not run follow-up skills as default suite lenses. They are implementation workflows, not assessment lenses.

## Finding Ledger

Record findings in the normalized format from [finding-ledger.md](references/finding-ledger.md). Each finding must include source skill, severity, confidence, evidence, affected files, impact, recommendation, validation, and whether it is an issue candidate.

Do not carry weak findings forward just to fill the backlog. A finding needs concrete evidence or it should be marked as a question, not an issue.

## Deduplication

After all lenses run, merge findings that share a root cause, affected code path, or fix. Prefer one high-quality issue over multiple overlapping issues from different lenses. Preserve the source-skill list inside the issue body.

Use [github-issue-policy.md](references/github-issue-policy.md) before creating issues.

## Output

Return:

- suite status and skipped lenses with reasons.
- review coverage map.
- findings ledger summary.
- deduplicated proposed GitHub issue backlog.
- issue creation commands only when requested.
- open questions and human-confirmation items.

## Gotchas

- Do not let architecture findings overwrite security or contract findings; security and compatibility issues usually need narrower fixes.
- Do not create issues directly from low-confidence findings.
- Do not run destructive cleanup from this skill. Cleanup PRs are a later implementation phase.
- Do not turn an architecture decomposition finding into an implementation task unless the user explicitly asks to proceed with that specific target.
- Do not assume every repo has frontend, LLM, data, or API surfaces; mark those lenses not applicable when evidence is absent.
