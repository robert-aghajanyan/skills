# Output Format

Use this structure for API contract review reports. Keep it evidence-first and separate confirmed breakage from conditional external-consumer risk.

## Scope And Validation

- Repository, branch, PR, diff, or files reviewed.
- Contract inventory method: manual map, helper script, repo-native docs, generated specs, tests, or consumer call-site search.
- Validation commands run and results.
- Known gaps such as unavailable consumer repos, credentials, generated clients, schema registry, or deployment history.

## Contract Map

Summarize observed contracts:

| Surface | Files / Evidence | Consumers | Compatibility Promise | Notes |
| --- | --- | --- | --- | --- |
| API / CLI / Schema / Event / Config / SDK / Plugin | `path:line` | confirmed or likely users | explicit, inferred, or unknown | relevant versions, docs, tests |

## Compatibility Risk Table

| Surface | Old Behavior | New Behavior | Affected Consumers | Severity | Confidence | Strategy |
| --- | --- | --- | --- | --- | --- | --- |
| `route`, `flag`, `field`, `topic`, `key`, `export` | what worked before | what changes now | confirmed or conditional | Blocker/High/Medium/Low | Confirmed/Conditional | alias, version, migrate, test, document |

## Findings

Order findings by severity. Use this shape:

```markdown
### [Severity] [Finding Title]

- Status: Confirmed or Conditional
- Surface: API, CLI, Schema, Event, Config, SDK, Plugin, or Data Contract
- Old behavior: exact behavior or accepted shape before the change
- New behavior: exact behavior or accepted shape after the change
- Affected consumers: confirmed consumers, likely consumers, or unknown external consumers
- Evidence: `path/file.ext:line` plus concise observation
- Impact: how the consumer breaks or why rollout/rollback is unsafe
- Compatibility strategy: alias, tolerant reader, version bump, deprecation period, expand/migrate/contract, dual publish, adapter, docs, or migration tool
- Tests to add: focused contract, regression, snapshot, schema, CLI, SDK, migration, replay, or consumer fixture tests
```

Severity guide:

- Blocker: likely breaks existing consumers, stored data, deployments, or automation with no safe migration path.
- High: credible compatibility risk with known or likely consumers and incomplete migration/deprecation coverage.
- Medium: contained contract drift or missing tests/docs that could break consumers under common usage.
- Low: minor compatibility hygiene, documentation drift, or conditional risk that needs confirmation.

## Migration And Deprecation Recommendations

Include:

- Immediate compatibility changes.
- Deprecation messaging and removal timeline.
- Required docs, changelog, versioning, generated client, or schema registry updates.
- Rollout and rollback order.
- Consumer communication or migration guide needs.

## Tests To Add

List concrete tests:

- old request/payload/config still accepted
- new behavior produced only when opted in or versioned
- CLI stdout/stderr/exit-code snapshots
- schema compatibility fixtures
- migration idempotency and mixed-version deployment tests
- event replay fixtures and consumer contract tests

## Open Questions

Ask only questions that change severity or strategy, such as consumer ownership, compatibility promises, rollout constraints, schema-registry policy, generated-client release flow, or deprecation timeline.

## Final Calibration

Before delivering:

- remove generic "best practice" concerns
- cite exact evidence for every confirmed finding
- mark uncertain external-consumer impact as conditional
- avoid calling intentional versioned breaking changes bugs when the migration path is complete
- separate contract safety from unrelated architecture, security, or performance concerns
