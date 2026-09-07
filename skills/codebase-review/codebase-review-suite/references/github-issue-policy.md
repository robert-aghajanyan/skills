# GitHub Issue Policy

Create GitHub issues only after the user explicitly approves the proposed backlog.

Before issue creation:

1. Confirm repository remote and default branch.
2. Confirm `gh auth status` for the relevant host.
3. Present a dry-run backlog grouped by severity and area.
4. Deduplicate overlapping findings.
5. Exclude low-confidence findings unless the user wants tracking issues.

Issue granularity:

- One issue should represent one independently fixable unit of work.
- Merge findings that require the same code change.
- Split issues when fixes require different owners, risk levels, or validation paths.
- Do not create one issue per file unless each file has an independent defect.

Issue body template:

```markdown
## Summary
<what is wrong and why it matters>

## Evidence
- Source skill(s): <skill names>
- Severity: <severity>
- Confidence: <confidence>
- Affected files: <files/lines>
- Evidence: <code/config/test/doc evidence>

## Impact
<user, production, security, correctness, compatibility, developer, or cost impact>

## Suggested Fix
<smallest useful fix, not a broad rewrite>

## Validation
<tests, commands, repro, screenshots, or manual checks>

## Notes
<open questions, assumptions, or related findings>
```

Suggested labels:

- `codebase-review`
- `severity:blocker`, `severity:high`, `severity:medium`, `severity:low`
- `area:security`, `area:reliability`, `area:performance`, `area:tests`, `area:docs`, `area:api-contract`, `area:data-correctness`, `area:frontend`, `area:dependency`, `area:llm-agent`, `area:architecture`, `area:developer-experience`, `area:cleanup`

If labels do not exist, either omit labels or ask before creating them.
