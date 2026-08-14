# Config Compatibility

Configuration is a contract for deployments, local development, CI, scripts, dashboards, plugins, and customer installations. Include file names, env vars, defaults, precedence, validation, and migration paths.

## Map

Capture:

- Config files, sample configs, env vars, secrets names, feature flags, plugin manifests, Helm/Kubernetes values, Terraform variables, Docker Compose files, CI variables, and command-line overrides.
- Defaults, required/optional status, validation rules, precedence order, path resolution, casing, naming, units, and allowed values.
- Runtime consumers: app startup, workers, CLIs, tests, jobs, deployments, dashboards, generated docs, and onboarding instructions.

## Red Flags

- Renaming or removing keys, env vars, secret names, feature flags, plugin manifest fields, or default file paths.
- Changing default values, units, boolean interpretation, precedence, requiredness, or validation strictness.
- Failing closed at startup without migration messaging or aliases for old keys.
- New config needed for rolling deploys but no backward-compatible default.
- Documentation and example configs not updated.
- Values accepted by old versions rejected by new versions during mixed deployments.

## Compatibility Strategies

- Accept old and new key names with warnings; document the replacement and removal window.
- Preserve defaults or require explicit opt-in for changed behavior.
- Add config migration checks that produce actionable errors.
- Keep old deployment flows working until all environments are updated.
- Add tests for config precedence, env var aliases, sample configs, and startup with legacy config.

## Evidence

Use config loaders, validators, manifests, deployment files, sample configs, docs, CI workflows, and startup tests. Separate confirmed deployment use from plausible but unverified external installs.
