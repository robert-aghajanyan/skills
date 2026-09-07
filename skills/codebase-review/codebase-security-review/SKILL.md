---
name: codebase-security-review
description: Perform deep security reviews and threat modeling grounded in exploitability and actual code paths. Use when the user asks for a security review, threat model, exploitability check, auth/authz audit, secrets review, tenant isolation review, injection review, SSRF/path traversal review, dependency trust review, agent security review, or whether a change can be abused or bypassed.
---

# Security Review

Use this skill for adversarial security review of repositories, PRs, branches, modules, services, APIs, agents, CLIs, integrations, and deployment surfaces. Keep this separate from architecture review: report design or maintainability only when it creates a concrete exploit, bypass, privilege escalation, data exposure, or fail-open path.

## Workflow

1. Define the exact review target, trusted baseline, changed files, runtime surface, and deployment context. If this is a PR, verify the live head or exact diff before reviewing.
2. Build a security surface map: entrypoints, external inputs, auth/authz checks, tenant/user/workspace/project boundaries, secrets/config loading, outbound network calls, file/database writes, dependency/plugin boundaries, logs, reports, exports, and user-visible outputs.
3. Identify attacker-controlled data and every trust boundary it crosses. Trace concrete source-to-sink paths before writing findings.
4. Review with the checks in [references/threat-model.md](references/threat-model.md), [references/web-api.md](references/web-api.md), [references/secrets-config.md](references/secrets-config.md), [references/multitenancy.md](references/multitenancy.md), [references/dependencies.md](references/dependencies.md), and [references/llm-agent-security.md](references/llm-agent-security.md) as applicable.
5. For every finding, include the affected file and line, attack path, required attacker capability, impact, exploitability, recommended fix, and negative test or adversarial probe.
6. Do not report theoretical issues unless there is a plausible path through the actual code. If deployment policy or runtime config is missing, mark the finding as conditional and name the missing evidence.
7. Prefer small, verifiable fixes over broad rewrites. If asked to fix issues, patch the minimal vulnerable path and add focused regression coverage.
8. Run repo-native security checks, tests, or focused repros where practical. End with a fresh attacker-perspective calibration pass and remove weak, duplicate, or non-exploitable findings.

## Optional Helper

When it will reduce blind spots, run the deterministic inventory helper from the target repo root:

```bash
python "${CLAUDE_SKILL_DIR}/scripts/security_inventory.py" <repo-root>
```

Use the output as a starting map only; validate every claim by reading the actual code path.

## Output

Use [references/output-format.md](references/output-format.md). Findings must be ordered by severity: Blocker, High, Medium, Low, Nit.

## Validation

- Prefer repo-native commands from docs, manifests, Makefiles, CI, or package scripts.
- Add or run focused negative tests for exploit paths when practical.
- If a check is skipped, state why and what residual risk remains.
- Before finalizing, re-read each finding from an attacker perspective and delete anything that lacks a plausible exploit path.

## Gotchas

- Architecture smell is not a security finding unless it enables abuse.
- Missing auth is only a finding after confirming the route or operation is reachable by an attacker without another guard.
- Secret findings must not expose raw secret values in the report.
- LLM or agent findings must distinguish untrusted model text from actual tool permissions and data access.
