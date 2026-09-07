# The version lives only in plugin.json

## Context

Claude Code compares `plugin.json`'s `version` against what a user has installed to decide whether to offer an update. That number has to be right, and it has to move on release.

The obvious pattern, copied from repos that publish to npm, is `package.json` as the source of truth plus a script that copies its version into `plugin.json`, wired into a changesets release workflow. That is the right shape when something is actually published to a registry and needs a generated `CHANGELOG.md`.

## Decision

This repo publishes nothing to npm and has no other reason to hold a `package.json`. So there is one version number, in `.claude-plugin/plugin.json`, and `marketplace.json`'s `metadata.version` mirrors it.

No `package.json`, no changesets, no version-sync script. `scripts/check-consistency.py` fails if the two versions disagree, which is the only failure mode the sync script existed to prevent.

## Consequences

- Releasing is: edit `version` in both manifests, commit, tag.
- No generated `CHANGELOG.md`. Git history is the changelog.
- If this repo ever gains npm-published tooling, revisit: at that point a single source of truth outside the plugin manifest starts to earn its keep.
