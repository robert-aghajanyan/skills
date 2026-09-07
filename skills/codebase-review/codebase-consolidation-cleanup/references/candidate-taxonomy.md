# Candidate Taxonomy

Use this taxonomy to create cleanup leads. A lead is not a recommendation until evidence and impact analysis support it.

## Duplicate Or Overlapping Logic

- two or more functions/classes implement the same algorithm or normalization
- parallel clients/adapters call the same external system with overlapping behavior
- repeated report, serialization, validation, caching, or fallback logic
- copy-pasted tests or fixtures that assert the same behavior through different paths

Recommended next step: compare inputs, outputs, side effects, error handling, performance assumptions, and caller expectations before proposing a canonical implementation.

## Wrapper And Runner Sprawl

- several scripts, CLIs, jobs, tools, notebooks, or UI/API actions launch the same workflow
- old and new runners both remain after a migration
- shell wrappers, Python entrypoints, package scripts, and plugin tools disagree on environment setup or defaults
- documentation points to one path while CI or deployment uses another

Recommended next step: build a runner matrix with command, caller, environment, output location, ownership, and observed usage.

## Stale Options And Feature Paths

- flags, modes, config keys, or code branches no longer reachable from current entrypoints
- compatibility branches for removed providers, old schemas, or retired behavior
- fallback paths that were added during incidents but no longer have a clear owner
- TODO-style alternate paths that tests never exercise

Recommended next step: search code, docs, configs, environment examples, telemetry names, tests, issue history, and release notes before declaring them stale.

## Unused Modules, Functions, And Classes

- source files or symbols with no static imports or direct references
- helpers only referenced by removed tests or legacy scripts
- modules outside the package graph but still tracked
- dead exception types, constants, model fields, or dataclasses

Recommended next step: treat public symbols, dynamic imports, framework hooks, and convention-based files as risky unless the framework's loading behavior is understood.

## Orphaned Artifacts

- tracked generated reports, build outputs, caches, snapshots, temporary files, and stale local exports
- docs or examples that point to deleted commands
- archived scripts that are not clearly marked as historical
- fixture data that no test or documented workflow consumes

Recommended next step: prove regeneration or non-use, check ignore rules, and separate intentionally committed artifacts from accidental residue.

## Dependency Islands

- packages or internal modules only used by a candidate stale path
- optional extras that are not wired into any supported runner
- build-time tools that remain after the build system changed
- transitive dependency pinning that only supports retired functionality

Recommended next step: use package-manager metadata and lockfile context; do not remove lockfile entries directly unless the package manager updates them.
