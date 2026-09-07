# Local Setup

Use this reference for onboarding, installation, environment setup, first run, and local services.

## Evidence To Collect

- Runtime and package manifests: `package.json`, `pyproject.toml`, `requirements*.txt`, `uv.lock`, `poetry.lock`, `Pipfile`, `go.mod`, `Cargo.toml`, `Gemfile`, `pom.xml`, `build.gradle`, lockfiles, and version files.
- Toolchain selectors: `.tool-versions`, `.nvmrc`, `.node-version`, `.python-version`, `.ruby-version`, `.java-version`, `mise.toml`, `asdf` config, Docker images, and devcontainer config.
- Setup entrypoints: README quickstarts, `Makefile`, `Justfile`, `Taskfile`, package scripts, `scripts/bootstrap*`, `scripts/setup*`, Docker Compose, and CI setup jobs.
- Runtime prerequisites: databases, queues, caches, cloud credentials, local ports, migrations, seed data, feature flags, certificates, and required accounts.
- Env surfaces: `.env.example`, `.env.sample`, config templates, CI secrets, deployment manifests, and code paths that read env vars.

## Checks

- A new developer can identify the recommended setup path without choosing among stale alternatives.
- Required runtime versions match manifests, lockfiles, CI images, containers, and docs.
- Install commands match the lockfile and package manager the repo actually uses.
- Bootstrap commands fail early with clear missing-prerequisite messages.
- Env examples include required keys without checked-in secrets or misleading placeholder values.
- Local services, ports, migrations, and seed steps are documented where the app or tests require them.
- First-run validation proves the repo is usable, such as a smoke test, health check, focused test, or local CLI command.

## Common Findings

- Docs say `npm install` while the repo uses `pnpm-lock.yaml` and CI uses `pnpm install --frozen-lockfile`.
- Setup succeeds only on machines with unstated global tools, shell aliases, credentials, databases, or cached generated files.
- `.env.example` omits a startup-required variable or documents a variable the code no longer reads.
- Docker Compose starts dependencies but docs never explain migrations, seed data, ports, or teardown.
- A bootstrap script hides failures behind broad `|| true`, swallowed output, or missing `set -e` behavior.

## Calibration

Do not flag missing low-level setup details when a documented bootstrap command truly handles them and has a validation step. Do flag hidden assumptions when a fresh checkout would fail before a developer reaches a useful error.
