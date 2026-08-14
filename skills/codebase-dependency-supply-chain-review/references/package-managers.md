# Package Managers

Use this file while building the dependency map and deciding which repo-native commands to trust.

## Ecosystem Signals

| Ecosystem | Manifests | Lockfiles | Common install commands |
| --- | --- | --- | --- |
| Node.js npm | `package.json` | `package-lock.json`, `npm-shrinkwrap.json` | `npm ci`, `npm install` |
| Node.js Yarn | `package.json`, `.yarnrc.yml` | `yarn.lock` | `yarn install --immutable`, `yarn install --frozen-lockfile` |
| Node.js pnpm | `package.json`, `pnpm-workspace.yaml` | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` |
| Node.js Bun | `package.json` | `bun.lock`, `bun.lockb` | `bun install --frozen-lockfile` |
| Python pip | `requirements*.txt`, `setup.py`, `setup.cfg`, `pyproject.toml` | `requirements*.lock` | `pip install -r ...` |
| Python Poetry | `pyproject.toml` | `poetry.lock` | `poetry install --no-root` |
| Python uv | `pyproject.toml`, `requirements*.txt` | `uv.lock` | `uv sync --frozen` |
| Python Pipenv | `Pipfile` | `Pipfile.lock` | `pipenv sync --dev` |
| Go | `go.mod` | `go.sum` | `go mod download`, `go test ./...` |
| Rust | `Cargo.toml` | `Cargo.lock` | `cargo fetch`, `cargo test` |
| Java Maven | `pom.xml` | usually no lockfile | `mvn dependency:tree`, `mvn test` |
| Java Gradle | `build.gradle`, `build.gradle.kts`, `settings.gradle` | `gradle.lockfile`, dependency locks | `gradle dependencies`, `gradle test` |
| Ruby | `Gemfile`, gemspecs | `Gemfile.lock` | `bundle install`, `bundle exec ...` |
| PHP Composer | `composer.json` | `composer.lock` | `composer install` |
| .NET | `*.csproj`, `packages.config`, `Directory.Packages.props` | `packages.lock.json` | `dotnet restore --locked-mode` |
| Swift | `Package.swift` | `Package.resolved` | `swift package resolve` |
| Containers | `Dockerfile`, Compose files, Helm/K8s YAML | image digests if pinned | `docker build`, `helm template` |
| GitHub Actions | `.github/workflows/*.yml` | action refs in workflow files | workflow `uses:` and `run:` steps |

## Review Checks

- Identify which package manager is authoritative. Multiple managers for one ecosystem are a risk unless the repo documents why.
- Separate runtime, development, optional, peer, test, and build dependencies. Flag dev-only packages that are imported at runtime or runtime packages placed only in dev sections.
- Check whether install commands in CI match the lockfile strategy. A repo with `package-lock.json` but CI running `npm install` may update the lockfile implicitly.
- Record registry configuration from `.npmrc`, `.yarnrc.yml`, `pip.conf`, `pyproject.toml` sources, `.pypirc`, `.cargo/config*`, `settings.xml`, `gradle.properties`, `nuget.config`, and Composer config.
- Treat generated clients and build plugins as dependency surfaces. OpenAPI generators, protobuf plugins, Gradle plugins, Maven plugins, Vite plugins, webpack loaders, Terraform providers, Helm charts, and GitHub Actions can execute code during build or CI.
- Look for dependency source changes in PRs, not only dependency names. Registry URL, scope mapping, authentication config, and install command changes can be more important than version changes.

## Version Range Hints

- Exact pins usually look like `1.2.3`, `==1.2.3`, `=1.2.3`, image digests, or commit SHAs.
- Broad or mutable ranges include `*`, `latest`, `x`, `^`, `~`, `>=`, branch names, untagged Docker images, floating GitHub Action refs, and Git URLs without a commit SHA.
- A broad range is lower risk when an enforced lockfile is committed and CI installs with a frozen mode. It is higher risk when no lockfile exists, install scripts run, or production builds resolve dependencies live.
