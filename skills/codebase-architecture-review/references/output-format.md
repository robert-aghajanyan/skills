# Output Format

Use this structure for the final report. Keep it concise enough to be useful, but include enough evidence that another engineer can verify every claim.

## Executive Summary

One short section covering:

- the repository scope reviewed and validation performed
- the top architecture risks
- the highest-leverage next steps
- what is confirmed versus hypothetical

## Repository Map

Summarize observed structure:

- languages, manifests, build/test commands, deployment files, and runtime config
- main entrypoints and workflows
- major modules/packages/services
- clients, regions, providers, tenants, agents, adapters, or generated-code boundaries
- test coverage shape and notable gaps

## Risk Map

Use a compact table:

| Area | Evidence | Risk | Severity | Confidence |
| --- | --- | --- | --- | --- |
| `path/or/unit` | files, lines, metrics, tests | why it matters | High/Medium/Low | Confirmed/Hypothesis |

## Findings

Order findings by severity. Use this shape:

```markdown
### [Severity] [Finding Title]

- Status: Confirmed or Hypothesis
- Evidence: `path/file.ext:line` plus brief observed behavior
- Principle: YAGNI/KISS/DRY/SOLID/Decomposition/Testability/Security/Reliability
- Impact: concrete maintenance or evolution risk
- Recommendation: specific change or investigation
- Validation: tests, builds, static checks, or code paths used to confirm
```

Severity guide:

- High: likely to cause recurring defects, unsafe changes, cross-client drift, or blocks important evolution.
- Medium: real maintainability cost with a clear but contained blast radius.
- Low: opportunistic cleanup with low risk and obvious local benefit.

Avoid "best practice" findings with no observed impact.

## Decomposition Candidates

Use the template from [decomposition.md](decomposition.md). Include only candidates where the boundary, migration steps, tests, and tradeoffs are concrete.

## Quick Wins

List small improvements that reduce review risk without broad rewrites:

- delete dead code with no callers
- collapse pass-through wrappers
- centralize duplicated rules behind an existing module
- add focused tests around config precedence or branching
- move direct IO behind small injectable functions where policy code is otherwise hard to test

## Do-Not-Change List

Explain complexity or duplication that should stay:

- evidence that it is cohesive or intentionally local
- why abstraction would make the code harder, riskier, or slower
- when to revisit the decision

## Test And Validation Plan

Include:

- repo-native commands run and their result
- focused checks still recommended
- behavior-preservation tests for proposed decompositions
- validation gaps caused by time, credentials, environment, or expensive integration dependencies

## Open Questions

Ask only questions that change the recommendation, such as ownership boundaries, near-term clients/providers, compatibility promises, or migration constraints.

## Final Calibration

Before delivering:

- remove findings without exact code evidence
- merge duplicate findings
- downgrade hypotheses that lack enough proof
- verify recommendations do not over-abstract simple code
- ensure confirmed issues and hypotheses are clearly separated
