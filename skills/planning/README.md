# Planning

Stress-testing plans and turning them into specs, issues, and handoffs.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[mp-grill-me](./mp-grill-me/SKILL.md)**: Get relentlessly interviewed about a plan or design until every branch of the design tree is resolved.
- **[mp-grill-with-docs](./mp-grill-with-docs/SKILL.md)**: Grilling that also builds the domain model, sharpening terminology and updating CONTEXT.md and ADRs inline.
- **[mp-improve-codebase-architecture](./mp-improve-codebase-architecture/SKILL.md)**: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- **[mp-setup](./mp-setup/SKILL.md)**: Scaffold the per-repo configuration the other skills assume: issue tracker, triage label vocabulary, and domain doc layout. Run once per repo.
- **[mp-to-spec](./mp-to-spec/SKILL.md)**: Turn the current conversation into a spec and publish it to the project issue tracker.
- **[mp-to-tickets](./mp-to-tickets/SKILL.md)**: Break any plan, spec, or conversation into tracer-bullet tickets, each declaring its blocking edges.
- **[mp-triage](./mp-triage/SKILL.md)**: Move issues and external PRs through a state machine of triage roles: categorise, verify, grill if needed, and write agent-ready briefs.
- **[mp-wayfinder](./mp-wayfinder/SKILL.md)**: Plan a chunk of work larger than one agent session as a map of decision tickets on the tracker, resolved one at a time until the way is clear.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[mp-domain-modeling](./mp-domain-modeling/SKILL.md)**: Actively build and sharpen the project domain model by challenging terms, stress-testing with scenarios, and updating CONTEXT.md and ADRs inline.
- **[mp-grilling](./mp-grilling/SKILL.md)**: Interview the user in rounds, asking the whole settled frontier of the design tree at once, each question with a recommended answer.
