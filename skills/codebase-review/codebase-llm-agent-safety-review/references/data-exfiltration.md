# Data Exfiltration

Data exfiltration review traces sensitive sources to external or attacker-controlled sinks, including indirect channels created by model output and tools.

## Sensitive Sources

- system, developer, policy, and tool prompts;
- API keys, credentials, tokens, cookies, environment variables, and secret-manager values;
- private source code, workspace files, user uploads, documents, emails, tickets, chat history, and browser pages;
- tenant, user, organization, account, project, billing, financial, and customer records;
- tool outputs, logs, traces, memory, vector stores, cache entries, database rows, and generated reports.

## Output Sinks

- chat responses, citations, summaries, generated files, downloads, logs, analytics, traces, telemetry, and memory;
- email, Slack, Teams, tickets, PR comments, issue comments, webhooks, external APIs, and browser navigation;
- model provider requests, retrieval indexes, plugin calls, MCP server processes, shell commands, code execution, and network calls.

## Review Checks

- Trace every sensitive source to output sinks and external calls.
- Check whether model output can choose recipients, URLs, domains, filenames, comments, or API payload fields.
- Verify redaction before logs, traces, model requests, memory writes, analytics, and error reporting.
- Inspect browser and network tools for arbitrary navigation, redirects, internal network access, file uploads, and download handling.
- Check whether hidden prompts, chain-of-thought-like traces, tool outputs, or workspace file contents can be exposed through user-visible messages.
- Review exports and reports for cross-tenant joins, stale caches, broad filesystem reads, or accidental inclusion of debug data.

## Guardrails

- Data classification and explicit source-to-sink policy before output or external calls.
- Destination allowlists for domains, recipients, repositories, workspaces, and APIs.
- Redacted logging and structured summaries of tool outputs instead of raw dumps.
- Network egress controls, browser sandboxing, and blocked internal metadata endpoints.
- User-visible confirmation that names the destination and data class before external sends.

## Probes

- Ask the agent to send hidden prompts, tool output, private files, or credentials to an external URL.
- Use a malicious document with a markdown link, image URL, webhook, or redirect that encodes private data.
- Force an error path and verify secrets are not printed in exceptions, logs, or traces.
- Request another tenant's data through a valid-looking identifier and verify no output leak occurs.
- Try to export broad directories, logs, cache files, memory stores, and prompt traces.
