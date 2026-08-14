# Dependency Cleanup

Removing dependencies can change behavior at build, test, packaging, or runtime. Treat dependency cleanup as a manifest change plus a lockfile and validation change.

## Inventory

Identify all manifests and package managers before editing:

- JavaScript/TypeScript: `package.json`, lockfiles, workspace files, `npm`, `pnpm`, `yarn`
- Python: `pyproject.toml`, `requirements*.txt`, `setup.py`, `setup.cfg`, lockfiles, `pip`, `poetry`, `uv`
- Go: `go.mod`, `go.sum`
- Rust: `Cargo.toml`, `Cargo.lock`
- Ruby: `Gemfile`, `Gemfile.lock`
- Java/Kotlin/Scala: `pom.xml`, `build.gradle`, `gradle.lockfile`, `build.sbt`
- .NET: `.csproj`, `.fsproj`, `.sln`, `packages.lock.json`

## Evidence Before Removal

Check for:

- source imports and require statements
- CLI usage in scripts, docs, CI, Docker, Makefiles, task runners, and release automation
- framework config usage, plugins, presets, loaders, type packages, test environment packages, and build tooling
- optional extras, peer dependencies, dev dependencies, package exports, and generated-code requirements
- transitive dependency explanations from package-manager metadata

Do not remove a dependency just because application source does not import it.

## Lockfiles

- Keep lockfiles unless the manifest changes require lockfile updates.
- Use the repo's package manager to update lockfiles.
- Avoid hand-editing lockfiles.
- If lockfile updates are not possible because dependencies cannot be installed or network is unavailable, leave the dependency change unmade or clearly mark validation as blocked.

## Validation

After dependency edits, run practical repo-native checks:

- install or lockfile check when available
- tests touching the affected package or app
- lint, typecheck, build, or packaging commands
- command smoke tests for removed CLIs or scripts

Report the exact commands and results.
