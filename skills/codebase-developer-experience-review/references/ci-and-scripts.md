# CI And Scripts

Use this reference for Makefiles, package scripts, shell helpers, task runners, CI jobs, and release/deploy entrypoints.

## Evidence To Collect

- Script surfaces: `package.json` scripts, `Makefile`, `Justfile`, `Taskfile`, `tox.ini`, `noxfile.py`, `scripts/`, `bin/`, repo CLIs, Gradle/Maven tasks, Cargo aliases, and checked-in workflow helpers.
- CI surfaces: `.github/workflows/*`, `.gitlab-ci.yml`, CircleCI, Buildkite, Jenkins, Azure Pipelines, Docker build workflows, deploy workflows, and release automation.
- Execution details: working directories, environment variables, caches, service containers, matrix versions, artifacts, required secrets, job names, and failure-summary output.

## Checks

- Local commands cover the same critical checks CI runs, or docs explain why they differ.
- Canonical commands are easy to find: install, run, test, lint, typecheck, build, format, debug, release, and deploy.
- Duplicate commands do not drift across README, Makefile, package scripts, and CI.
- Script names describe scope and risk, especially for destructive, deploy, cleanup, or production-affecting actions.
- Scripts use predictable exit codes and fail on errors instead of hiding failures.
- CI job names and logs tell developers what failed and what local command reproduces it.
- Release/deploy commands separate dry-run, staging, and production behavior clearly.

## Common Findings

- CI runs `npm run test:ci` but docs only mention `npm test`, and the two commands exercise different suites.
- Make targets and package scripts wrap the same tools with different flags, causing local/CI disagreements.
- A deploy script also builds, migrates, and pushes without a dry-run or confirmation boundary.
- CI failures require opening multiple logs because job names are generic and scripts suppress the failing command.
- A helper script assumes the repo root but docs invoke it from a subdirectory.

## Calibration

Do not require a Makefile or task runner if package scripts or repo-native tooling already make workflows clear. Recommend consolidation only when it removes real duplicate or contradictory entrypoints.
