# Engineering

Daily code work: building, refactoring, researching.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[codex-collab](./codex-collab/SKILL.md)**: Claude and Codex analyze independently, then debate to convergence. A genuine second opinion.
- **[mp-implement](./mp-implement/SKILL.md)**: Build the work described by a spec or set of tickets, driving TDD at pre-agreed seams and closing out with a review before committing.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[decompose](./decompose/SKILL.md)**: Audit one oversized module, plan a dependency-aware split, and execute it with zero breaking changes.
- **[mp-codebase-design](./mp-codebase-design/SKILL.md)**: Shared discipline and vocabulary for designing deep modules: small interfaces, clean seams, testable through the interface.
- **[mp-diagnosing-bugs](./mp-diagnosing-bugs/SKILL.md)**: Disciplined loop for hard bugs and performance regressions: build a feedback loop that goes red, minimise, hypothesise, instrument, fix, regression-test.
- **[mp-prototype](./mp-prototype/SKILL.md)**: Build a throwaway prototype to answer a design question: a shareable HTML file for state and logic, or several toggleable UI variations.
- **[mp-resolving-merge-conflicts](./mp-resolving-merge-conflicts/SKILL.md)**: Work an in-progress merge or rebase hunk by hunk, resolving by intent traced to each side primary source, then finish. Never --abort.
- **[mp-tdd](./mp-tdd/SKILL.md)**: Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- **[mp-wizard](./mp-wizard/SKILL.md)**: Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning, credentials, dashboards, one-off migrations.
- **[team-research](./team-research/SKILL.md)**: Explore a question from several angles with agents that challenge each other's findings.
