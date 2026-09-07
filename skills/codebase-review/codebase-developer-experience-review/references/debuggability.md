# Debuggability

Use this reference for local debugging, failure messages, observability during development, and troubleshooting ergonomics.

## Evidence To Collect

- CLI and script error handling, logging config, debug flags, verbose modes, stack traces, exception handling, and validation errors.
- Local service tooling: Docker Compose, devcontainers, seed data, migrations, health checks, ports, admin UIs, and teardown commands.
- Troubleshooting docs, known-issues docs, runbooks, CI failure summaries, and scripts that print reproduction commands.
- Generated artifacts, cache directories, temp paths, report outputs, and instructions for cleaning or regenerating them.

## Checks

- Common setup and test failures point to the missing prerequisite or validation step.
- Scripts print the command or context needed to reproduce failures locally.
- Debug or verbose modes are discoverable and safe for local use.
- Logs avoid hiding root causes behind broad exception wrappers, swallowed output, or generic "failed" messages.
- Local services expose health checks, ports, and teardown instructions.
- Generated files and caches have clear regeneration and cleanup commands.
- CI output tells developers which local command should reproduce the failure.

## Common Findings

- A setup script catches every exception and prints only "bootstrap failed".
- A local run command fails after several minutes because a missing env var is first used deep in startup.
- Tests require generated data but the generator command is not documented.
- CI uploads artifacts but docs do not tell developers where to inspect equivalent local outputs.
- Debug logging exists behind an undocumented env var or flag.

## Calibration

Do not require production-grade observability for every local tool. Focus on failure paths that developers are likely to hit while setting up, testing, debugging, or maintaining the repo.
