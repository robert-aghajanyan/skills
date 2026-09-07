# PR Review

Multi-agent review, fix, and merge-readiness workflows for pull requests.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[pr-clean-review](./pr-clean-review/SKILL.md)**: One broad review, batched blocker/high fixes, evidence-ledger verification, then a clean-room final review.
- **[pr-review-fix](./pr-review-fix/SKILL.md)**: Review, then a separate fixer agent commits fixes for blocker/high findings, then re-review, up to three rounds. Never pushes or merges.
- **[production-readiness-gate](./production-readiness-gate/SKILL.md)**: A last conservative pass over a PR, branch, artifact, or report, reporting a calibrated confidence score.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[team-review](./team-review/SKILL.md)**: Review a PR with four specialized agent teams (security, performance, correctness, guardrails) plus independent verification.
- **[team-review-plus](./team-review-plus/SKILL.md)**: team-review plus PR preflight, false-positive filtering, carried-forward finding checks, confidence calibration, and specialist lenses.
