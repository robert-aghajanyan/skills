---
name: codebase-llm-agent-safety-review
description: Review repositories that use LLMs, agents, tools, MCP servers, plugins, retrieval, memory, file access, browser access, code execution, or automation for safety, trust-boundary, and abuse risks. Use when the user asks for LLM safety review, agent safety, prompt injection review, tool permission review, MCP/plugin safety, RAG safety, memory safety, data exfiltration review, model guardrails, or whether an agentic system can be abused.
---

# LLM Agent Safety Review

Review agentic and LLM-backed systems for concrete abuse paths across prompts, tools, retrieval, memory, autonomy, permissions, and output trust.

## Workflow

1. Define the exact review target: repo, PR, branch, files, runtime mode, deployed surface, and user or tenant roles in scope.
2. Build an agent surface map covering models, prompts, tools, tool permissions, MCP servers, plugins, retrieval sources, memory, user-uploaded content, file access, network access, shell or code execution, browser automation, external APIs, and output destinations. Use [references/trust-boundaries.md](references/trust-boundaries.md) and run `python "${CLAUDE_SKILL_DIR}/scripts/agent_surface_inventory.py" .` as a first pass when useful.
3. Identify trust boundaries: user input, retrieved content, third-party content, tool outputs, logs, memory, secrets, credentials, workspace files, tenant data, and privileged actions.
4. Review the applicable risk areas:
   - [Prompt injection](references/prompt-injection.md)
   - [Tool permissions](references/tool-permissions.md)
   - [RAG and memory](references/rag-and-memory.md)
   - [Data exfiltration](references/data-exfiltration.md)
   - [Human approval](references/human-approval.md)
5. For each finding, include code or config evidence, attack path, attacker capability, impacted data or action, severity, recommended guardrail, and adversarial probe or negative test.
6. Separate confirmed risks from speculative model-behavior concerns. If a concern depends on unavailable deployment policy, credentials, or runtime config, mark it conditional and state the missing evidence.
7. Prefer enforceable controls over prompt-only mitigations: permission checks, scoped tools, allowlists, typed schemas, redaction, tenant filters, audit logs, dry-run modes, and human approval for high-impact actions.
8. Run repo-native tests and add focused adversarial tests when practical. Re-check findings from the attacker perspective before finalizing.

## Optional Helper

From the target repo root, run:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/agent_surface_inventory.py" .
```

Treat the inventory as a blind-spot reducer, not proof. Validate each claim by reading the actual code path.

## Output

Use [references/output-format.md](references/output-format.md). Required sections are:

- Agent surface map
- Trust-boundary map
- Findings ordered by severity
- Adversarial probes
- Guardrail recommendations
- Required tests
- Residual risk
- Open questions

## Validation

- Tie findings to concrete files, lines, configs, or runtime behavior.
- Prefer negative tests that prove the guardrail rejects hostile prompt content, forged tool output, cross-tenant retrieval, unsafe tool arguments, memory leakage, or unapproved side effects.
- If validation is skipped, state why and name the remaining risk.

## Gotchas

- Generic prompt wording is not sufficient mitigation for privileged tools or sensitive data.
- Model output, retrieved text, tool output, logs, browser content, and plugin metadata are untrusted until validated by deterministic code or explicit approval.
- A tool schema that exposes broad paths, domains, commands, recipients, or resource IDs is a permission boundary, not just a developer convenience.
- Do not report a prompt-injection concern as confirmed unless it can influence a reachable sink such as a tool call, retrieved context, memory write, external API, generated code, or user-visible decision.
- Prompt caching and compaction changes can accidentally move, drop, or mutate safety instructions and tool boundaries. If cost optimization is requested, use `codebase-prompt-caching-optimization` and rerun the relevant safety probes afterward.
