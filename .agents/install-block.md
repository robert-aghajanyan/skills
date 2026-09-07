# The canonical install block

One install story, one wording. `README.md` and any docs must say **this** and nothing else. Change it here first, then propagate.

This repo is its own single-plugin marketplace. It is **not** in Claude Code's official marketplace, so the marketplace has to be added before the plugin can be installed. Do not write install instructions that skip that step, and do not invent CLI commands: `claude install-skill` does not exist.

<canonical-block name="claude-code">

```bash
claude plugin marketplace add robert-aghajanyan/skills
claude plugin install rob@robert-aghajanyan
```

Or, from inside a session:

```
/plugin marketplace add robert-aghajanyan/skills
/plugin install rob@robert-aghajanyan
```

One plugin ships the whole promoted set. Update with `claude plugin marketplace update robert-aghajanyan`.

</canonical-block>

## Trying it without installing

<canonical-block name="try-it">

```bash
git clone https://github.com/robert-aghajanyan/skills
claude --plugin-dir ./skills
```

Loads the plugin for that session only.

</canonical-block>

## Working on the skills

`scripts/link-skills.sh` symlinks every promoted and in-progress skill into `~/.claude/skills` and `~/.agents/skills`, so a `git pull` keeps them current. That is a maintainer workflow, not an install route: do not document it to users, and never run it alongside the plugin, or every skill appears twice.
