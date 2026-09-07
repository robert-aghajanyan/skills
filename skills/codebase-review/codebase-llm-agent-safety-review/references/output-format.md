# Output Format

Use this structure for LLM and agent safety reviews. Keep it evidence-heavy and separate confirmed risks from speculative model-behavior concerns.

## Agent Surface Map

List observed:

- models and model-call wrappers;
- system, developer, policy, task, and generated prompts;
- tools, tool schemas, tool routers, and permission checks;
- MCP servers, plugins, connectors, browser automation, shell/code execution, and external APIs;
- retrieval sources, upload paths, indexes, memory stores, logs, traces, caches, and summaries;
- sensitive sources and output destinations.

## Trust-Boundary Map

For each boundary, include:

```text
Boundary: <source -> sink>
Controller: <who controls the source data>
Privileged context reached: <data/action/model/tool/memory/output>
Existing guardrail: <code/config evidence or none observed>
Residual concern: <confirmed risk, conditional gap, or none observed>
```

## Findings

Order by severity: Blocker, High, Medium, Low, Nit. For each finding, use:

```text
Severity: Blocker|High|Medium|Low|Nit
Title: <short abuse-oriented title>
Status: Confirmed|Conditional
Location: <file:line or config path>
Evidence: <observed code/config behavior>
Attack path: <attacker input -> trust boundary -> model/tool/memory/output sink>
Attacker capability: <role/access/content control needed>
Impacted data/action: <what can be read, changed, executed, leaked, persisted, or sent>
Recommended guardrail: <enforceable control, not just prompt wording>
Adversarial probe or negative test: <test that fails before the fix and passes after>
```

Do not include a finding when the only evidence is generic model unpredictability. Put unresolved deployment or policy gaps in Open Questions unless they create a reachable fail-open path.

## Adversarial Probes

List probes run and probes still required, grouped by prompt injection, tool permissions, retrieval, memory, exfiltration, approval, and output trust.

## Guardrail Recommendations

Prioritize enforceable controls:

- typed schemas, allowlists, scoped credentials, tenant filters, path/domain/command restrictions;
- deterministic validators between model output and tools;
- redaction before prompts, logs, memory, traces, and external outputs;
- dry-run previews and human approval for high-impact actions;
- audit logs and fail-closed defaults.

## Required Tests

Name the exact regression tests needed for confirmed findings and high-risk boundaries. Prefer hostile-content tests, cross-tenant tests, forged-tool-output tests, approval-bypass tests, unsafe-argument tests, and exfiltration tests.

## Residual Risk

State what remains after the review or after fixes: unavailable runtime config, unreviewed MCP servers, unverified plugin permissions, skipped dynamic tests, missing IAM policy, opaque model-provider behavior, or deployment-only controls.

## Open Questions

Ask only questions that affect exploitability, severity, guardrail design, or merge/deployment safety.
