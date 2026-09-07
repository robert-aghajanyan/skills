# Production Readiness Gate

Use this gate when the user needs the cleanup assessment or cleanup batch to be reusable, leadership-ready, or safe enough to guide production repository work.

## Required Checks

Before calling the skill output production-ready, verify:

- packaging: the skill validates with the local skill validator and has no audit warnings
- trigger clarity: the description distinguishes consolidation cleanup from generic cleanup, architecture review, and code review
- portability: instructions do not depend on one repository, one company, absolute local paths, credentials, or time-sensitive facts
- assessment safety: the skill is strictly read-only and must hand off implementation instead of editing, deleting, staging, committing, or pushing
- evidence quality: every recommendation requires reachability evidence, impact analysis, per-finding confidence, evidence gaps, validation, and rollback or deprecation guidance
- dynamic usage safety: external callers, plugin loading, framework conventions, generated code, and config-driven behavior are treated as risky until proven safe
- output repeatability: the expected output includes a candidate ledger, classification, evidence, impact, recommendation, per-finding confidence, evidence gaps, follow-up evidence plan, and pre-deletion validation
- repo-native fit: the workflow tells the agent to use existing tests, scripts, docs, manifests, and architecture-memory requirements before inventing new checks

## Confidence Rubric

Use a 0-100 score and a plain-language label:

- **90-100 high**: packaging checks pass, trigger is clear, behavior is strictly assessment-only, output format is complete, and only minor wording risk remains.
- **75-89 medium-high**: usable now, but one meaningful gap remains, such as missing dry-run evidence, weak trigger distinction, or incomplete confidence reporting.
- **60-74 medium**: promising but not production-ready; it needs clearer workflow, stronger safety rules, or better output structure.
- **below 60 low**: do not rely on it for large-codebase cleanup until structural issues are fixed.

Do not give 100 unless the skill has also been exercised on multiple representative repositories and the outputs were reviewed against real cleanup decisions.

## Reuse Test Prompts

Use these prompts as lightweight smoke tests:

1. "Assess this repo for duplicate runners, stale wrappers, and unused implementation paths. Assessment only; do not edit files."
2. "Use codebase-consolidation-cleanup to map overlapping pipeline entrypoints and tell me what would break if we removed each stale path."
3. "Clean up generated artifacts in this small repo."

Expected behavior:

- prompts 1 and 2 should trigger this skill and produce an assessment-first candidate ledger
- prompt 3 should usually prefer a generic cleanup skill unless duplicate implementation or consolidation risk is explicitly present; if this skill is used, it must still assess only and not clean up anything

## Leadership-Ready Summary

For leadership-facing reporting, include:

- what was verified
- what the skill prevents
- what remains outside its guarantee
- confidence score
- clear next step, such as "ready for reuse" or "needs another validation pass on a second repo"
