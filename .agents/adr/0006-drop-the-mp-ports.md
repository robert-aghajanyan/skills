# Drop the mp-* ports

**Supersedes [ADR 0004](0004-mp-skills-are-ports-not-forks.md).**

## Context

ADR 0004 kept 22 `mp-` skills as byte-for-byte ports of [mattpocock/skills](https://github.com/mattpocock/skills). Matt Pocock's skills are now installable directly as the `mattpocock-skills` plugin from `claude-plugins-official`. With both installed, every ported skill appeared twice under 2 names, and the ports only ever trailed upstream.

## Decision

Remove all 22 `mp-` skills, the upstream sync checker and its CI job. Users who want them install `mattpocock-skills`. Released as 4.0.0, since installed users lose skills.

## Consequences

- `mp-resolving-merge-conflicts` has no counterpart in the upstream plugin, so it is gone.
- The `planning` bucket is empty but stays promoted, so a future own skill has a home.
- `humanizer` stays a port under its own sync checker; this ADR does not touch it.
