# Output Format

Use this structure for security review reports. Keep it concise, evidence-heavy, and ordered by risk.

## Executive Summary

- State whether the reviewed target appears safe to merge/deploy/use, unsafe, or conditionally safe.
- Name the highest-risk confirmed issue and the main residual uncertainty.
- Separate code safety from external gates such as missing deployment policy, missing credentials, or required approvals.
- Include a confidence rating: High, Medium, or Low, with the main evidence behind it and the main validation gap holding it back.

## Security Surface Map

Include the observed:

- entrypoints;
- external inputs;
- auth/authz boundaries;
- tenant/user/workspace/project boundaries;
- secrets and config loading;
- outbound network calls;
- file/database writes;
- dependency and plugin boundaries;
- logs, reports, exports, and user-visible outputs.

## Threat Model

Summarize:

- attacker roles considered;
- trust boundaries crossed;
- sensitive assets;
- assumptions and conditional deployment dependencies.

## Findings

Order by severity: Blocker, High, Medium, Low, Nit. For each finding, use:

```text
Severity: Blocker|High|Medium|Low|Nit
Title: <short exploit-oriented title>
Location: <file:line>
Evidence: <observed code behavior>
Attack path: <attacker input -> trust boundary -> vulnerable sink>
Required attacker capability: <role/access needed>
Impact: <what can be read, changed, executed, bypassed, or leaked>
Exploitability: <why this is easy/moderate/hard, and prerequisites>
Recommended fix: <small verifiable fix>
Negative test or probe: <test that should fail before the fix and pass after>
Status: Confirmed|Conditional
```

Do not include a finding if the attack path is only theoretical. Put uncertain deployment-dependent concerns in Open Questions or mark them Conditional.

## Severity Calibration

- Blocker: confirmed or highly likely path to code execution, secret disclosure, cross-tenant data access, auth bypass, destructive action, deployment compromise, or irreversible privilege escalation.
- High: plausible and reachable path to significant unauthorized read/write, privilege escalation, sensitive data exposure, SSRF to sensitive internal resources, command execution with constrained blast radius, or agent/tool abuse with meaningful side effects.
- Medium: reachable boundary weakness with limited impact, meaningful defense bypass requiring additional preconditions, sensitive metadata leak, or exploitable validation gap without immediate critical asset access.
- Low: hard-to-exploit weakness, minor data exposure, incomplete hardening, or risky default with limited current reach.
- Nit: report hygiene, small hardening suggestion, or clarity issue that does not materially change exploitability.

## Adversarial Probes Or Negative Tests

List concrete tests or repros run, plus the ones still needed. Prefer boundary tests over broad happy-path tests.

## Fix Recommendations

Prioritize minimal changes that close the exploit path. Include sequencing when multiple fixes depend on each other.

## Residual Risk

Name what remains after fixes or after the review scope ends: missing runtime policy, unreviewed services, unavailable secret-manager/IAM config, skipped dynamic testing, or external dependency uncertainty.

## Open Questions

Ask only questions that affect exploitability, severity, or the recommended fix. Avoid generic discovery questions already answerable from the repo.
