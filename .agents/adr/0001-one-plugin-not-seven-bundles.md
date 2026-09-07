# Ship one plugin, not seven marketplace bundles

## Context

Until v2.0.0 this repo had no `.claude-plugin/plugin.json` at all. Distribution was seven entries in `marketplace.json` (`code-quality-skills`, `team-skills`, `meta-skills`, `codebase-review-skills`, `pr-workflow-skills`, `planning-skills`, `collab-skills`), each with `"source": "./"` and a different subset of skill paths.

Three problems with that:

1. **Overlap duplicated skills.** `team-review` appeared in three bundles and `optimize-prompt-caching` in two. Installing two bundles installed those skills twice.
2. **No whole-set install.** A user had to know a bundle name. There was no "give me everything" path.
3. **Ineligible for the official marketplace.** Anthropic's `claude-plugins-official` listing reads a repo's `plugin.json` directly. With no `plugin.json`, this repo could never be listed.

The README also documented `claude install-skill <url>`, which is not a command. It silently fell through to the CLI's help text, so the documented install path did nothing.

## Decision

Ship **one** plugin, declared in `.claude-plugin/plugin.json` with an explicit array of skill directory paths. It was named `robert-aghajanyan-skills` here; [0005](./0005-the-plugin-is-named-rob.md) renamed it to `rob` in 3.0.0. The count of plugins, not the name, is what this record decides.

`marketplace.json` keeps exactly one plugin entry, making the repo its own single-plugin marketplace. That is the install route today, since this repo is not in the official marketplace.

Grouping now happens through **bucket folders** under `skills/` (see [0002](./0002-bucket-folders-and-the-promoted-set.md)) and through the `which-skill` router, not through bundles. Buckets are for humans reading the repo; the plugin ships a flat set either way.

## Consequences

- Every promoted skill needs an entry in `plugin.json`'s `skills` array. `scripts/check-consistency.py` enforces it.
- Bundle names are gone. Anyone who installed one has to reinstall, which is why this is a major version.
- The version in `plugin.json` is what Claude Code compares to decide an installed user sees an update. Bump it on every release.
