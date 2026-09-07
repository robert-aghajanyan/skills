# Secrets And Config Checks

Use this reference for environment loading, secret stores, CI/CD variables, deployment manifests, app config, logs, reports, and generated artifacts.

## Secret Inventory

- Identify sources: `.env` files, config files, secret managers, Kubernetes Secrets, Helm values, Terraform variables, CI variables, GitHub Actions secrets, deployment scripts, local keychains, mounted files, and generated credentials.
- Track precedence: defaults, checked-in config, environment overrides, CLI flags, runtime discovery, and fallback behavior.
- Identify consumers: SDK clients, database clients, HTTP clients, CLIs, workers, plugins, tests, reports, logs, and telemetry.

Do not paste raw secret values into the report. If a real credential appears committed, cite the file and line and describe the credential class, with a masked sample only when necessary.

## Review Checks

- Hardcoded credentials, private keys, tokens, passwords, webhook secrets, signing secrets, OAuth client secrets, cloud keys, and internal URLs.
- Fail-open defaults, such as empty signing keys, disabled TLS verification, permissive CORS, debug mode, mock auth, public buckets, or local-only credentials used in shared deployments.
- Config confusion, such as one env var overriding another unexpectedly, prod fallback to dev values, missing required config validation, or booleans parsed from strings incorrectly.
- Secret scope, rotation, and lifetime: overbroad cloud/IAM permissions, long-lived tokens, shared service accounts, and missing rotation assumptions.
- Sensitive logging: request/response bodies, headers, cookies, authorization values, credentials, PII, customer data, internal URLs, model prompts, tool outputs, reports, and exception messages.
- Export surfaces: CSV, HTML, JSON, logs, metrics, traces, dashboards, alerts, cache files, and build artifacts that can disclose sensitive data.
- CI/CD exposure: pull-request workflows with secrets, unpinned actions, artifact uploads, debug echo, shell tracing, and write tokens on untrusted code.

## Validation Ideas

- Run the inventory helper and repo-native secret scanners if available.
- Check config parsing with empty, missing, malformed, and conflicting values.
- Add tests that assert secrets are redacted from logs, errors, reports, and telemetry.
- For conditional deployment claims, name the exact missing policy evidence, such as IAM policy, Kubernetes NetworkPolicy, secret-manager ACL, or CI environment protection.
