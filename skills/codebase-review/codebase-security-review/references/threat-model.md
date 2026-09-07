# Threat Model

Use this reference to keep the review adversarial and evidence-based.

## Evidence Standard

Every finding needs a plausible source-to-sink path:

1. Attacker capability: anonymous internet user, authenticated user, low-privileged tenant member, malicious admin, compromised dependency, CI contributor, prompt injector, or local user.
2. Entry point: request route, CLI argument, file upload, webhook, queue message, config field, database record, model output, plugin boundary, or deployment variable.
3. Trust boundary crossed: auth, authorization, tenant, workspace, project, process, network, filesystem, secret, model/tool, or deployment boundary.
4. Vulnerable behavior: missing check, weak validation, type coercion, unsafe default, dangerous sink, overly broad permission, confused deputy, or fail-open branch.
5. Impact: data exposure, privilege escalation, account takeover, code execution, SSRF, write/delete, cross-tenant access, secret leakage, policy bypass, or audit/log tampering.

Classify evidence:

- Confirmed: the code path, attacker input, missing guard, and sink are all observed.
- Conditional: the path is plausible but depends on runtime policy, deployment config, external IAM, network policy, or data shape not present in the repo.
- Not a finding: no reachable attacker path, guard is enforced earlier, sink is unreachable, or impact is only speculative.

## Surface Map Checklist

- Entrypoints: HTTP routes, RPC handlers, webhooks, CLIs, background workers, scheduled jobs, message consumers, plugin hooks, migration scripts, admin tools, deployment scripts, and generated artifacts.
- External inputs: path/query/body fields, headers, cookies, file names, uploaded bytes, archives, URLs, IDs, config, environment variables, database rows, queue payloads, LLM outputs, and third-party API responses.
- Identity and policy: authentication, session handling, service accounts, impersonation, delegated tokens, role checks, object ownership checks, tenancy scope, and admin bypasses.
- Sensitive resources: secrets, tokens, private keys, customer data, financial data, source code, logs, exports, reports, audit trails, model context, and internal URLs.
- Sinks: SQL/NoSQL queries, shell commands, template rendering, dynamic imports, deserialization, HTTP clients, file reads/writes, archive extraction, redirects, logs, metrics, reports, and notifications.

## Attacker Perspective Pass

For each candidate issue, ask:

- Can the attacker reach this code with the stated capability?
- Can the attacker control the value that reaches the sink?
- Does another middleware, schema, policy, query scope, or deployment control stop it?
- What exact data or action becomes available if the attack works?
- What is the smallest negative test that would prove the issue?

Drop findings that cannot answer those questions concretely.
