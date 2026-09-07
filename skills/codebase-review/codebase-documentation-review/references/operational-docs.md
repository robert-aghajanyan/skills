# Operational Docs

Use this reference when reviewing architecture docs, deployment docs, CI/CD docs, environment docs, configuration docs, observability docs, release notes, changelogs, diagrams, and ownership docs.

## Evidence To Compare

- CI workflow files, deployment pipelines, Dockerfiles, Kubernetes manifests, Terraform or cloud config, Helm charts, runtime config, service discovery, scheduler config, monitoring config, alert rules, logging setup, and ownership metadata.
- Source entrypoints, background jobs, queues, databases, caches, external clients, feature flags, migrations, and release tooling.

## Checks

- Architecture diagrams match current services, jobs, data stores, queues, external systems, and direction of data flow.
- CI docs match actual workflow names, triggers, required checks, artifacts, cache behavior, and release gates.
- Deployment docs match current environments, branches, tags, image names, config maps, secrets, namespaces, regions, and rollback paths.
- Configuration docs match code reads, defaults, env examples, manifests, and feature flag behavior.
- Observability docs match log fields, metrics, traces, dashboards, alerts, and known failure modes.
- Changelog and migration docs identify required operator or developer action, not only code changes.
- Ownership docs identify current maintainers or escalation paths when the repo has that metadata.

## Common Findings

- A diagram shows a service, queue, database, or dependency that the repo no longer deploys or calls.
- CI docs name jobs that have been renamed, removed, or made optional.
- Deploy instructions omit a new required secret, migration, feature flag, or release gate.
- Config docs describe defaults that no longer match code.
- Release notes mention behavior changes without migration or verification steps.

## Calibration

Do not treat every architecture simplification as wrong. Flag it when the simplification would cause a developer or operator to configure, deploy, debug, integrate, or assess risk incorrectly.
