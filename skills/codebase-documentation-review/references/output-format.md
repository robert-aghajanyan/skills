# Output Format

Use this structure for documentation review reports. Keep findings evidence-first and remove sections that are empty.

## Documentation Map

- List documentation surfaces reviewed: README files, docs directories, runbooks, setup guides, API docs, examples, diagrams, changelog or release docs, CI/deploy docs, env examples, and doc-like comments.
- For each surface, note the main audience: user, developer, operator, maintainer, API consumer, or release owner.
- Mention high-risk docs not reviewed and why.

## Accuracy Findings

For each confirmed issue:

```text
[Severity] Doc title or claim
- Doc: path/to/doc.md:line
- Contradicted by: path/to/source.ext:line or config/script path
- Impact: what a user, developer, API consumer, or operator would do wrong
- Recommended change: concrete doc correction
- Evidence: command output, static source evidence, or verification command
```

Use `Blocker` when docs can cause unsafe operations, failed deploys, broken production recovery, security exposure, data loss, or materially wrong API usage. Use `High` when docs block setup, integration, operation, or migration. Use `Medium` for misleading but recoverable docs. Use `Low` sparingly for minor stale references that still matter.

## Missing Documentation Gaps

- Missing behavior, setup, API, migration, ownership, operational, or validation information that users need to act correctly.
- Include the source evidence proving the behavior exists and why the gap matters.

## Stale Or Conflicting Instructions

- Duplicate docs that disagree.
- Old branch names, service names, scripts, env vars, screenshots, diagrams, dates, release surfaces, or deployment paths.
- Identify the likely current source of truth.

## Broken Commands, Paths, And Examples

- Commands that do not exist or use old flags.
- Referenced paths or scripts that are missing or generated without instructions.
- Examples that no longer compile, parse, or match schemas.
- Include the exact command used to verify when safe.

## Runbook And Operational Gaps

- Missing prerequisites, access, environment scope, rollback, recovery, troubleshooting, escalation, ownership, or post-action validation.
- Call out dangerous or ambiguous production steps clearly.

## Suggested Fixes

- Group fixes by file when practical.
- Keep suggestions concrete enough to implement without re-investigation.
- Separate quick doc-only edits from changes that require code, config, or generated-doc updates.

## Verification Commands

- List commands already run and their result.
- List commands not run because they are unsafe, expensive, privileged, or environment-specific.
- Provide focused commands a maintainer can run after applying doc fixes.
