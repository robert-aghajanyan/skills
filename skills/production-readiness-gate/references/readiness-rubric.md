# Readiness Rubric

Use three scores. Do not collapse code confidence and runtime confidence into one number.

## Code/PR/Artifact Readiness

- `95-100`: exact head verified, review clean, strong targeted and broad tests pass, adversarial cases covered, no unresolved high-risk comments
- `90-94`: code is strong and checks pass, but proof is missing for a minor edge or final external gate
- `80-89`: likely correct, but coverage, review state, or blast-radius proof is incomplete
- `<80`: unresolved blocker, weak proof, stale source of truth, or risky unverified behavior

For local skills and file artifacts, this score covers package integrity, validation, smoke coverage, and checksum/source-of-truth quality. It does not imply PR mergeability or commit-level provenance unless those were verified separately.

## Runtime/Deployment Readiness

- `95-100`: deployed or deployable state verified, dependency smoke checks pass, rollback path understood
- `90-94`: deployment path is clear, but final live smoke or external dependency proof remains
- `80-89`: code is probably deployable, but environment, credentials, egress, data, or runtime state is not fully verified
- `<80`: deployment unknowns can plausibly break the result

## Leadership-Share Readiness

- `95-100`: summary is evidence-backed, caveats are explicit, and confidence is easy to defend
- `90-94`: safe to share with clear caveats
- `80-89`: share only as a status update, not a production-ready claim
- `<80`: not leadership-ready

## Scoring Rules

- Lower a score when evidence is stale, inferred, or not tied to the exact target.
- Lower runtime confidence if no live runtime or dependency check was run.
- Lower leadership-share confidence if residual risks are vague or hidden.
- Never use a high confidence score to compensate for an unverified critical surface.
