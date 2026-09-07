# The plugin is named `rob`

## Context

Claude Code prefixes every plugin skill with the plugin's own name, so `plugin.json`'s `name` is what a user types: `<plugin>:<skill>`. The plugin was called `robert-aghajanyan-skills`, which made the router entry for a handoff read

```
/robert-aghajanyan-skills:mp-handoff
```

Forty-two characters before the skill name, in a menu where the skill name is the part being scanned. The length came from an assumption that the prefix had to match the GitHub owner and repo. It does not: `plugin.json`'s `name` and `marketplace.json`'s `name` are two independent strings, neither derived from the remote.

## Decision

Name the plugin `rob`. The install id becomes `rob@robert-aghajanyan` and skills read `/rob:humanizer`.

The **marketplace** stays `robert-aghajanyan`. It appears only in the install and update commands, where the longer, more specific name is worth having, and a marketplace named `rob` says nothing about whose it is.

`rob` over a bare `skills`: a marketplace could plausibly host two plugins that both want the generic word, and a prefix that collides is worse than a prefix that is long.

## Consequences

- The install identity changed, so `robert-aghajanyan-skills@robert-aghajanyan` no longer resolves. Existing installs cannot update across the rename; they must uninstall and install `rob@robert-aghajanyan`. This is why the release is a major bump to 3.0.0 rather than 2.3.0.
- `plugin.json`'s `name` and `marketplace.json`'s `plugins[0].name` must stay equal. They are two literals in two files with nothing enforcing the match.
- The name is a user-facing surface now, typed on every invocation. Treat a future rename as another breaking release, not a tidy-up.
- Wording lives in [`.agents/install-block.md`](../install-block.md) and is copied verbatim into `README.md`. Change it there first.
