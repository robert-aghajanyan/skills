---
name: codebase-api-contract-review
description: Review repositories for API, CLI, schema, SDK, event, config, plugin, and data-contract compatibility risks. Use when the user asks for API compatibility, contract review, backward compatibility, schema changes, CLI compatibility, SDK behavior, event/message contracts, config migration, public interfaces, or breaking-change analysis.
---

# Codebase API Contract Review

Use this skill to find consumer-visible compatibility risks in APIs, CLIs, schemas, SDKs, events, config, plugins, and data contracts. Treat internal correctness as necessary but not sufficient; the review is about whether existing consumers can keep working.

## Workflow

1. Build a contract map covering public APIs, routes, request/response shapes, CLI commands and flags, config files and env vars, schemas, migrations, events, plugin hooks, SDK exports, generated clients, documented examples, and stored data. When useful, run `python "${CLAUDE_SKILL_DIR}/scripts/contract_inventory.py" <repo-root>`.
2. Identify likely consumers: external users, internal services, CI jobs, scripts, dashboards, configs, stored records, generated clients, deployment automation, and backward-compatible rollout flows.
3. Compare old and new behavior for renamed fields, removed defaults, changed response shapes, stricter parsing, incompatible migrations, CLI semantic changes, silent behavior changes, versioning gaps, missing deprecation paths, and rollout hazards.
4. Use the focused references for each surface: [public interfaces](references/public-interfaces.md), [schema migrations](references/schema-migrations.md), [CLI contracts](references/cli-contracts.md), [events and messages](references/events-and-messages.md), and [config compatibility](references/config-compatibility.md).
5. For every finding, include old behavior, new behavior, affected consumers, evidence, severity, recommended compatibility strategy, and regression or contract tests.
6. Calibrate at the end: keep confirmed risks separate from conditional external-consumer risks, and remove findings that cannot be tied to a concrete contract or plausible consumer.

## Output

Use the report structure in [references/output-format.md](references/output-format.md): contract map, breaking-change findings, compatibility risk table, migration/deprecation recommendations, tests to add, and open questions.

## Validation

- Prefer repo-native contract, integration, snapshot, schema, SDK, and CLI tests before inventing new commands.
- If reviewing a diff or PR, inspect both sides of the changed contract and cite exact files and lines.
- Run the inventory helper when it will reduce blind spots:
  `python "${CLAUDE_SKILL_DIR}/scripts/contract_inventory.py" <repo-root>`
- If validation depends on unavailable external consumers, mark the risk conditional and name the missing evidence.

## Gotchas

- A passing build does not prove backward compatibility.
- Optional fields, defaults, exit codes, stdout shape, config precedence, and undocumented examples can be real contracts.
- Do not overclaim external impact when consumers are unknown; label it conditional and explain the plausible break path.
- Data migrations and event schema changes need rollout and rollback thinking, not only final-state correctness.
