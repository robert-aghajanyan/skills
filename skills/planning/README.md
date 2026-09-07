# Planning

Stress-testing plans and turning them into specs, issues, and handoffs.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[mp-grill-me](./mp-grill-me/SKILL.md)**: Get relentlessly interviewed about a plan, one question at a time, until every branch of the design tree is resolved.
- **[mp-grill-with-docs](./mp-grill-with-docs/SKILL.md)**: Grilling that also challenges your plan against the domain model, sharpening terminology and updating CONTEXT.md and ADRs inline.
- **[mp-improve-codebase-architecture](./mp-improve-codebase-architecture/SKILL.md)**: Find deepening opportunities in a codebase, informed by CONTEXT.md and the decisions in docs/adr/.
- **[mp-to-prd](./mp-to-prd/SKILL.md)**: Turn the current conversation into a PRD and publish it to the project issue tracker.
- **[mp-to-issues](./mp-to-issues/SKILL.md)**: Break a plan, spec, or PRD into independently-grabbable issues as tracer-bullet vertical slices.
- **[mp-handoff](./mp-handoff/SKILL.md)**: Compact the current conversation into a handoff document, saved outside the workspace, so the next session can continue.
