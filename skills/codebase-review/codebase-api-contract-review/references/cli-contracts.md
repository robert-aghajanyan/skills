# CLI Contracts

CLIs are contracts for humans, scripts, CI jobs, cron tasks, release automation, documentation, and generated examples. Treat command names, flags, defaults, output, exit codes, prompts, config lookup, and environment behavior as compatibility surfaces.

## Map

Capture:

- Commands, subcommands, aliases, flags, environment variables, config files, defaults, positional arguments, stdin behavior, prompts, and interactive/non-interactive modes.
- Output formats: stdout, stderr, JSON fields, table columns, line ordering, logs, progress output, file outputs, and generated artifact paths.
- Exit codes, retry behavior, timeout behavior, dry-run semantics, confirmation prompts, destructive operations, and idempotency.
- Packaging surfaces: `bin` entries, shell completions, Docker entrypoints, Make targets, npm scripts, setup entry points, and documented examples.

## Red Flags

- Removing or renaming commands, flags, aliases, env vars, output fields, columns, or artifact paths.
- Changing defaults, config precedence, current working directory assumptions, glob expansion, prompt behavior, or dry-run semantics.
- Making parsing stricter in ways that break existing scripts.
- Moving information from stdout to stderr or changing machine-readable output without a versioned mode.
- New interactive prompts in paths used by automation.
- Changed exit codes or success/failure classification.

## Compatibility Strategies

- Keep old flags and aliases with deprecation warnings.
- Preserve machine-readable output or add a new versioned output mode.
- Keep non-interactive behavior stable; gate prompts behind explicit interactive modes.
- Support old config locations and env vars during migration.
- Add CLI snapshot tests and script-level tests for common invocation patterns.

## Evidence

Use parser definitions, command registration, help output, docs, scripts, CI workflows, Makefiles, package manifests, and tests. If possible, run old and new commands or compare snapshots.
