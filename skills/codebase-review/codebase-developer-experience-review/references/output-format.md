# Output Format

Use this report shape for developer experience reviews. Remove empty sections and keep findings evidence-first.

## DX Summary

- State the overall developer workflow risk: clean, some friction, high friction, or blocked onboarding.
- Name the top 2-4 bottlenecks and the workflows they affect.
- Mention important surfaces reviewed and any high-risk areas not verified.

## Workflow Map

Use a compact table or list covering:

- Install
- Configure/env
- Local run
- Test: focused and full
- Lint
- Typecheck
- Build
- Debug/troubleshoot
- Release
- Deploy

For each workflow, include the apparent canonical command, alternate commands, source files, and whether docs match the repo.

## Friction Findings

For each confirmed issue:

```text
[Severity] Finding title
- Evidence: file:line, command output, config, or CI/doc source
- Affected workflow: install, configure, run, test, lint, typecheck, build, debug, release, or deploy
- Risk: what a developer or maintainer will waste time on or get wrong
- Recommended fix: concrete repo change, script change, docs correction, or command standardization
- Validation command: focused command to prove the fix
```

Use `Blocker` when a fresh checkout cannot be set up, tested, or run using documented steps. Use `High` when common development or CI reproduction is unreliable or misleading. Use `Medium` for recurring friction with clear workaround. Use `Low` sparingly for small but real workflow cleanup.

## Quick Wins

- List low-risk changes that remove friction immediately: command aliases, doc corrections, missing help text, env example updates, or focused test wrappers.
- Keep quick wins tied to observed evidence.

## Commands To Standardize

- Name the recommended canonical commands for install, run, test, lint, typecheck, build, debug, release, and deploy.
- Identify duplicate or contradictory commands to remove, rename, or document as scoped alternatives.

## Docs To Update

- List exact docs and sections that need updates.
- Keep this to workflow-impacting docs, not broad prose rewrites.

## Validation Steps

- List commands already run and outcomes.
- List commands intentionally not run because they are destructive, privileged, expensive, or environment-specific.
- Provide the minimal post-fix validation sequence maintainers should run.

## Open Questions

- Include only questions that block confident recommendations, such as undocumented deployment ownership, missing credentials model, or unknown intended package manager.
