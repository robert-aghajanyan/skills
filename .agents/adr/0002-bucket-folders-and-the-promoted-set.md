# Bucket folders under skills/, and a promoted set

## Context

Thirty-four skills sat as thirty-four sibling directories under `skills/`. Two consequences: the directory listing was unreadable, and there was no way to publish a skill for feedback without shipping it in the plugin. Everything in `skills/` was shipped, by construction.

## Decision

Skills live in bucket folders under `skills/`:

| bucket | promoted | what it is |
| --- | --- | --- |
| `codebase-review/` | yes | dimension-specific deep reviews of an existing repo |
| `pr-review/` | yes | review, fix, and merge-readiness workflows for PRs |
| `engineering/` | yes | daily code work |
| `planning/` | yes | stress-testing plans and turning them into specs and issues |
| `meta/` | yes | building skills, and navigating this repo |
| `in-progress/` | **no** | beta, public on purpose, feedback wanted |
| `deprecated/` | **no** | retired, kept for reference |

The plugin ships exactly the promoted set. `plugin.json` lists explicit paths, so a non-promoted bucket is excluded with zero ambiguity.

This works because Claude Code's `plugin.json` accepts `skills` as an **array of paths**. Codex's `.codex-plugin/plugin.json` accepts only a single path string and discovers `SKILL.md` recursively beneath it, so it cannot express "these two buckets but not those two". A native Codex plugin is therefore deferred; the per-skill `agents/openai.yaml` files still make each skill usable in Codex when copied in individually.

## Consequences

- Skill paths changed. Anything pinning `skills/<name>/` breaks; the bucket is now in the path.
- Adding a skill means picking a bucket, and a promoted skill needs entries in `plugin.json`, its bucket `README.md`, the top-level `README.md`, and the `which-skill` map.
- `scripts/check-consistency.py` fails the build when a promoted skill is missing from any of those, and when a non-promoted skill appears in `plugin.json`.
