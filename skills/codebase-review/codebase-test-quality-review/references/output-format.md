# Output Format

Use this structure for test quality reviews. Keep it concise, evidence-backed, and ordered by regression risk.

```markdown
**Executive Summary**
[One short paragraph on whether the suite gives meaningful confidence and the top risk.]

**Test Map**
- Languages/frameworks:
- Test commands:
- CI test jobs:
- Coverage tools/config:
- Source areas:
- Test areas:
- Fixtures/snapshots/mocks:
- Integration setup:

**Risk Coverage**
| Risk area | Current evidence | Confidence | Gap |
| --- | --- | --- | --- |
| [Auth/cost/data/etc.] | [tests/files read] | High/Medium/Low | [specific missing behavior] |

**Findings**
- [Severity] [Title] - [production file] / [test file if available]
  Behavior at risk:
  Why current tests miss it:
  Recommended test shape:
  Test type:
  Minimal cases:

**Recommended Tests**
1. [Highest-value test first, including the regression it catches.]
2. [Next.]

**Flaky Or Brittle Risks**
- [Only include concrete risks, not generic possibilities.]

**Valuable Existing Tests**
- [Tests that should be preserved because they prove important behavior.]

**Validation Commands Run**
- `[command]` - [result]

**Human Confirmation Needed**
- [External systems, product intent, credentials, or CI-only behavior that could not be verified locally.]
```

## Rules

- Findings come before broad suggestions.
- Every recommendation must name the regression it would catch.
- Include affected production and test files whenever available.
- Do not use "add more tests" as a recommendation.
- If no high-risk gaps are found, say so and list residual risks or commands not run.
