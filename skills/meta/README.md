# Meta

Skills for building skills and navigating this repo.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[skill-builder](./skill-builder/SKILL.md)**: Create a well-designed skill from scratch, with the frontmatter, structure, and validation this repo expects.
- **[which-skill](./which-skill/SKILL.md)**: Ask which skill or flow fits your situation. A router over every user-reachable skill in this repo.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[mp-writing-for-agents](./mp-writing-for-agents/SKILL.md)**: Writing documents for agents: skills, AGENTS.md and CLAUDE.md, and any doc an agent reaches by a pointer.
- **[optimize-prompt-caching](./optimize-prompt-caching/SKILL.md)**: Audit and optimize LLM prompt caching in any codebase: cache_control breakpoints, compaction, cost and latency wins.
