# Engineering

Daily code work: building, refactoring, researching.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[codex-collab](./codex-collab/SKILL.md)**: Claude and Codex analyze independently, then debate to convergence. A genuine second opinion.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[decompose](./decompose/SKILL.md)**: Audit one oversized module, plan a dependency-aware split, and execute it with zero breaking changes.
- **[mp-tdd](./mp-tdd/SKILL.md)**: Build features and fix bugs test-first, one vertical slice at a time.
- **[team-research](./team-research/SKILL.md)**: Explore a question from several angles with agents that challenge each other's findings.
