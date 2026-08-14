# Golden Transcripts

These examples are deterministic response contracts for smoke testing. They are not a transcript of a live model run; they define the minimum acceptable shape and caveats for future model-facing validation.

## no-target-clarifying-question

What exact target should I run the production-readiness gate against: PR, branch, commit, report/artifact path, or deployed environment?

## local-skill-verdict

**Verdict**: Ready With Caveats

**Confidence**
- Code/PR/artifact readiness: 92/100
- Runtime/deployment readiness: 86/100
- Leadership-share readiness: 90/100

**Evidence Verified**
| Check | Result |
|---|---|
| Source of truth | Local skill path, file inventory, manifest, and content checksum verified |
| Provenance | Manifest records source provenance when available; otherwise the response calls out checksum-only traceability |
| Validation | Generic skill validation and semantic smoke tests pass |

**Reusability Judgment**
The local skill is reusable when the manifest, fixtures, and smoke tests pass against the exact installed path.

**Residual Risks**
| Risk | Impact | Next action |
|---|---|---|
| No Git commit provenance | Cannot claim commit-level release history | Stamp the manifest from a real source commit or keep the checksum caveat |

**Room For Improvement**
| Suggestion | Why it helps | Priority |
|---|---|---|
| Add source tag provenance | Makes release audits easier | Medium |

**Leadership Summary**
The skill can be used locally with explicit provenance caveats, content checksum evidence, and validation results.

## pr-verdict

**Verdict**: Ready With Caveats

**Confidence**
- Code/PR/artifact readiness: 91/100
- Runtime/deployment readiness: 84/100
- Leadership-share readiness: 90/100

**Evidence Verified**
| Check | Result |
|---|---|
| Source of truth | live PR metadata, source/base/head, checks, comments, and mergeability verified |
| Tests | Targeted verification run and recorded with scope |

**Reusability Judgment**
The change is reusable only if the verified path is shared and not a one-off happy path.

**Residual Risks**
| Risk | Impact | Next action |
|---|---|---|
| No deployment smoke evidence | Mergeability does not prove runtime behavior | Run the deployment or dependency smoke check before claiming runtime readiness |

**Room For Improvement**
| Suggestion | Why it helps | Priority |
|---|---|---|
| Add post-merge smoke evidence | Raises runtime confidence | Medium |

**Leadership Summary**
The PR can be described as code-ready only when live PR checks and tests support it; runtime readiness remains separate until deployment evidence exists.

## future-checklist-near-miss

Here is a practical production-readiness checklist for a future project:

- Source of truth and ownership are clear.
- Tests cover the highest-risk paths.
- Runtime dependencies have smoke checks.
- Rollback and support paths are documented.
- Leadership caveats are explicit.

## concept-near-miss

production ready usually means the service has enough verified evidence to trust the code, deployment path, runtime dependencies, rollback plan, and support model for its intended use. It is a claim about tested behavior and operational readiness, not just a green local test run.
