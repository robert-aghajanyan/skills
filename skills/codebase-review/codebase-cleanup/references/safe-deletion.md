# Safe Deletion

Deletion is the highest-risk cleanup action. Prefer a small, reversible patch with clear evidence.

## Before Deleting

1. Check `git status --short --branch` and avoid unrelated dirty files.
2. Confirm the candidate is inside the agreed cleanup scope.
3. Search for references by file path, basename, symbol names, package names, command names, and generated output names.
4. Check CI, package scripts, Makefiles, task runners, Docker files, release scripts, deployment config, and docs.
5. Identify whether the file can be loaded dynamically or externally.
6. Decide whether the evidence supports deletion or only a human-confirmation note.

## Editing Rules

- Make the smallest safe batch first.
- Group deletions by reason, not by broad directory sweeps.
- Do not combine cleanup with behavior changes.
- Do not run broad formatters unless formatting is the cleanup target.
- Update docs, manifests, configs, or tests only when directly tied to the cleanup.
- If deleting tracked generated artifacts, update ignore rules only when the repo should continue ignoring regenerated output.
- If replacing duplicate utilities, keep behavior covered by tests before removing the duplicate.

## High-Risk Files

Require explicit confirmation or unusually strong repo evidence for:

- migrations and schema history
- fixtures, snapshots, golden files, sample payloads, and benchmark data
- generated clients, API schemas, protobufs, OpenAPI files, and GraphQL schemas
- compatibility shims, public exports, plugin metadata, and extension hooks
- deployment, release, runtime, observability, and infrastructure config
- files with names referenced by convention rather than imports

## Validation

After edits, run the narrowest meaningful checks first:

- targeted tests around touched modules
- package-manager validation for dependency or manifest changes
- lint/typecheck/build when cleanup affects shared source, exports, package metadata, or configs
- doc or script smoke tests when cleanup touches developer workflow

If validation is skipped, say why and identify the residual risk.
