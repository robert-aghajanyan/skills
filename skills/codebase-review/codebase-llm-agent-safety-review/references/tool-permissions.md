# Tool Permissions

Tools are the main safety boundary in agentic systems. Review the code that authorizes and constrains tool calls, not only the prompt that describes them.

## Review Checks

- Identify every tool that can read private data, write files, call APIs, browse, run shell commands, execute code, send messages, approve workflows, spend money, change infrastructure, or persist memory.
- Inspect schemas for overbroad strings such as arbitrary path, command, URL, SQL, recipient, workspace, tenant ID, or raw JSON arguments.
- Check that tool arguments are validated after model generation and before execution.
- Verify allowlists for file roots, URL domains, HTTP methods, commands, environment variables, external recipients, APIs, resource IDs, tenants, and plugin names.
- Confirm tools run with least privilege and fail closed when config, tenant scope, auth, or approval state is missing.
- Check whether tool results can steer later tool calls without validation.
- Inspect MCP and plugin configs for server command lines, environment variables, filesystem roots, network reachability, approval modes, and trusted marketplace assumptions.

## Confused Deputy Paths

- The agent uses service credentials to access a resource the user cannot access directly.
- A valid-looking user-supplied ID selects another tenant's object.
- A plugin or MCP server receives secrets or workspace files because the model chose it as a destination.
- Browser automation follows attacker-controlled links into authenticated pages and exports data.
- A model-generated command performs a broader action than the natural-language task requested.

## Guardrails

- Tool-specific authorization checks tied to the acting user and target resource.
- Narrow schemas with enums, typed IDs, validated paths, bounded lists, and structured action types.
- Read-only default modes, dry-run previews, and explicit escalation paths for side effects.
- Static allowlists for safe commands, domains, file roots, repositories, projects, tenants, and recipients.
- Runtime sandboxing for code execution and browser automation.
- Audit logs that capture requester, model decision, tool name, arguments, approval, result summary, and external destination without leaking secrets.

## Probes

- Try path traversal, absolute paths, symlinks, shell metacharacters, command chaining, and glob expansion.
- Try disallowed domains, redirects, non-HTTPS URLs, internal metadata endpoints, and webhook exfiltration.
- Try cross-tenant IDs, stale resource IDs, forged metadata, and mixed-tenant retrieval results.
- Try large or nested tool arguments that bypass shallow validation.
- Try invoking side-effecting tools without approval or with spoofed approval text.
