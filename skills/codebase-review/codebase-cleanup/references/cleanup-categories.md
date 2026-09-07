# Cleanup Categories

Use these categories to sort findings before recommending or editing anything.

## Safe Cleanup

Usually safe when supported by direct evidence:

- tracked cache, build, coverage, temp, or editor artifacts that match ignored patterns or repo conventions
- duplicate generated reports or output files with newer canonical equivalents
- broken symlinks that no command, test, package manifest, or documentation references
- local-only helper scripts with no references, no CI usage, no package script usage, and clear replacement paths
- stale empty directories represented only by placeholder files when the repo no longer needs the placeholder

Evidence threshold: show exact file paths, why they are artifacts or duplicates, and the reference checks that found no live use.

## Likely Cleanup

Reasonable candidates, but they need stronger checks or smaller batches:

- unused dependencies after import search plus package-manager metadata checks
- unused exports, orphaned modules, obsolete wrappers, or stale feature flags
- outdated docs that contradict current commands, file names, APIs, or config
- duplicate utilities with one clear canonical implementation
- old scripts replaced by package scripts, Make targets, task runners, or CI jobs
- stale compatibility layers when supported versions no longer need them

Evidence threshold: show static references, manifest references, tests or type checks, and why the current behavior remains unchanged.

## Risky Cleanup

Do not delete in an automated pass unless the user explicitly confirms and evidence is very strong:

- public APIs, CLI commands, exported packages, plugin hooks, compatibility shims, and extension points
- migrations, fixtures, seed data, data snapshots, golden files, generated clients, schemas, and protocol definitions
- deployment, runtime, infrastructure, feature-flag, observability, or release config
- files loaded dynamically, reflectively, by naming convention, by glob, through entrypoints, or by external systems
- branch-specific, customer-specific, region-specific, or environment-specific files

Recommendation should usually be "needs human confirmation" with the concrete reason.

## Do Not Touch

Leave these alone unless the user explicitly includes them in scope:

- unrelated dirty changes in the worktree
- secrets, local env files, credentials, private keys, and machine-local config
- vendor directories, vendored lock snapshots, and third-party generated bundles
- lockfiles when no dependency changes are being made
- live infrastructure or deployment config
- historical release notes, compliance records, audit artifacts, or migration history
