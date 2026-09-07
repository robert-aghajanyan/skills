# Setup Docs

Use this reference when reviewing README setup sections, install guides, local development docs, environment setup, Docker Compose instructions, dependency setup, and first-run workflows.

## Evidence To Compare

- Package and runtime manifests: `package.json`, `pyproject.toml`, `requirements*.txt`, `go.mod`, `Cargo.toml`, `Gemfile`, lockfiles, version files, Dockerfiles, devcontainers, and tool config.
- Script surfaces: Makefile targets, package manager scripts, `scripts/`, `bin/`, task runners, CI setup jobs, bootstrap scripts, and checked-in env templates.
- Runtime prerequisites: databases, queues, caches, cloud credentials, local services, ports, secrets, migrations, seed data, feature flags, and required accounts.

## Checks

- Commands in docs exist and use current names, flags, package managers, working directories, and prerequisites.
- Required versions match manifests, CI, Docker images, or runtime constraints.
- Referenced paths exist or are intentionally generated, and docs explain generation when needed.
- Env vars and config keys match code reads, env examples, deployment manifests, and CI secrets.
- Setup steps include validation commands that prove the app, CLI, test suite, or service actually works.
- Docker, Compose, devcontainer, and local service instructions match checked-in manifests and current ports.
- Database, migration, seed, cache, and queue instructions match repo-native tools.
- Platform-specific assumptions are called out when commands only work on one shell, OS, architecture, or package manager.

## Common Findings

- A README points to an old script after scripts were renamed or moved.
- Docs say to set an env var that code no longer reads, or omit one that is required at startup.
- Setup instructions skip a migration, seed, or service dependency that fails later.
- Docs use a package manager command inconsistent with the lockfile and CI.
- A quickstart succeeds only because of local state not described in the docs.

## Calibration

Do not flag a missing setup detail if it is intentionally handled by a single repo-native bootstrap command and that command is documented. Do flag it when the bootstrap command is undocumented, stale, or fails without hidden prerequisites.
