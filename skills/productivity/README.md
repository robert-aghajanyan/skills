# Productivity

General workflow tools, not code-specific.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[mp-handoff](./mp-handoff/SKILL.md)**: Compact the current conversation into a handoff document so another agent can continue the work.
- **[mp-teach](./mp-teach/SKILL.md)**: Teach the user a new skill or concept over multiple sessions, using the current directory as a stateful teaching workspace.
- **[mp-to-questionnaire](./mp-to-questionnaire/SKILL.md)**: Turn a decision you cannot answer alone into a Markdown questionnaire for the one person who can, filled in async or worked through together.
- **[mp-wait-what](./mp-wait-what/SKILL.md)**: Fire this the moment a message does not land. The agent re-pitches it with the context you are missing, in plain English.
