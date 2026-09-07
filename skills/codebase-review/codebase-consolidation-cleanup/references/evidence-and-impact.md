# Evidence And Impact Rules

Every recommendation needs both usage evidence and impact analysis. Absence of evidence is only a lead.

## Baseline Evidence

Collect the cheapest high-signal facts first:

- `git status --short --branch`
- repository instructions such as `AGENTS.md`, `README`, contribution docs, and architecture notes
- manifests: package files, lockfiles, build files, task runners, Docker, CI, deployment, plugin, and hook configs
- repo-native test, lint, typecheck, build, and smoke commands
- source searches with `rg` for file names, symbols, command names, import paths, config keys, env vars, output names, and docs references
- language-aware graph tools already present in the repo

Do not introduce heavy new tools or network-dependent analyzers unless the user approves or the repo already depends on them.

## Reachability Questions

For each candidate, answer:

- Who or what can call it: source imports, CLI, API route, UI action, CI job, scheduled job, deployment hook, plugin, framework convention, config, docs, external user, or test?
- Is the call static, dynamic, convention-based, generated, or external?
- Is there telemetry, log output, artifact naming, or documentation that indicates operational use?
- Is there a canonical replacement path?
- Does the replacement path preserve inputs, outputs, side effects, exit codes, logging, metrics, retries, auth, caching, and error behavior?

## Impact Analysis

For each proposed removal or consolidation, state what happens if it is done:

- behavior that disappears
- commands, imports, endpoints, jobs, docs, or artifacts affected
- dependencies that become removable or simpler
- tests that need to change
- users or downstream systems that need migration
- rollback path if the cleanup is wrong
- whether deprecation is safer than immediate deletion

## Per-Candidate Confidence

Assign every candidate a 0-100 confidence score. The score is not a vote on whether cleanup is desirable; it is a measure of how strong the current evidence is for the specific recommendation.

- **90-100 high confidence**: known callers are mapped, dynamic/config/docs/CI surfaces are checked, replacement behavior is compared when relevant, and validation is clear.
- **75-89 medium-high confidence**: evidence is strong, but one realistic usage surface or parity check still needs confirmation before deletion.
- **60-74 medium confidence**: the candidate is plausible, but static evidence dominates or ownership/external usage is still uncertain.
- **40-59 low confidence**: only weak leads exist; recommend investigation, not cleanup.
- **below 40 very low confidence**: do not treat as a cleanup candidate yet.

For each score, explain the top two reasons it is not higher. If a candidate is removal-ready or consolidate-ready below 90, state why that lower confidence is still acceptable or downgrade the classification.

## Follow-Up Evidence Plan

For every candidate that is not do-not-touch, include a short plan to improve confidence before deletion:

- searches still needed, including symbols, filenames, commands, env vars, output names, docs, and config keys
- runtime or smoke checks needed to prove reachability or non-use
- parity checks needed between duplicate and canonical paths
- owner or downstream confirmation needed for external/public surfaces
- tests that should be added or updated before removal
- dependency-manager or artifact-regeneration checks needed

The plan should be concrete enough that another agent can execute it without rediscovering the candidate from scratch.

## Strong Evidence

Strong evidence can include:

- every known caller already routes through the canonical implementation
- tests cover behavior parity between duplicate paths
- docs, CI, package scripts, deployment configs, and manifests do not reference the stale path
- runtime entrypoint inventory confirms the path is not launched
- generated artifact can be reproduced from a documented command
- package-manager metadata shows a dependency is only needed by code being removed

## Weak Evidence

Do not recommend deletion based only on:

- no direct `rg` hits
- no recent commits
- naming that looks temporary or legacy
- duplicate-looking code without behavior comparison
- missing tests
- local-only intuition about how the app is run
- generated-looking files without proving regeneration

## Risk Classification

- **removal-ready**: non-use or reproducibility is strongly proven; future removal has clear validation and rollback.
- **consolidate-ready**: duplicate path has a known canonical replacement and caller migration is clear.
- **deprecate/migrate**: likely obsolete, but external callers or compatibility risk make staged removal safer.
- **needs human confirmation**: static evidence is insufficient because usage may be external, dynamic, or ownership-dependent.
- **do-not-touch**: active, public, migration-related, security-sensitive, or too risky for cleanup scope.
