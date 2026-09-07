# Trust Boundaries

Use this reference to build the agent surface map and boundary map before writing findings.

## Agent Surface Map

Capture observed evidence for:

- model providers, model names, client libraries, API routes, SDK wrappers, and streaming paths;
- system, developer, policy, task, and tool prompts, including generated prompt templates;
- tool definitions, tool schemas, tool routers, tool permission checks, and tool result handling;
- MCP server configs, plugin manifests, connector settings, marketplace metadata, and local install paths;
- retrieval sources, indexes, vector stores, metadata filters, document loaders, web search, crawlers, and upload paths;
- memory stores, chat history, checkpoints, caches, traces, logs, analytics, and summarizers;
- file access, workspace access, network access, shell/code execution, browser automation, external APIs, and output destinations.

If a surface is not present, say it was not observed rather than assuming it is safe.

## Boundary Map

Mark where untrusted data crosses into privileged context:

- user input into prompts, tool arguments, generated code, SQL, shell commands, URLs, file paths, or external messages;
- retrieved or third-party content into model instructions, summaries, memory, or tool calls;
- tool output back into prompts, state machines, follow-up tool selection, logs, or user-visible outputs;
- tenant, user, project, workspace, account, or organization IDs across retrieval, APIs, files, caches, and memory;
- secrets, credentials, tokens, private source code, private documents, or hidden prompts into model context or external sinks;
- model output into trusted data structures, commands, policies, approvals, database writes, or workflow state.

## Evidence To Collect

- File and line for each prompt constructor, model call, tool schema, permission check, retrieval filter, memory write, and side-effecting action.
- Runtime config that changes permissions: environment variables, MCP manifests, plugin config, feature flags, workflow permissions, IAM roles, and deployment values.
- Output sinks: chat responses, email, Slack, tickets, PR comments, browser navigation, downloads, reports, logs, telemetry, databases, files, queues, and webhooks.

## Boundary Questions

- Who controls the input at this point?
- What privileged data or action becomes reachable after this boundary?
- Is the next step deterministic validation, model interpretation, or a tool call?
- Does the code fail closed when metadata, tenant scope, approval state, or policy config is missing?
- Can an attacker influence where data is sent, what file is read, what command is run, or what resource ID is used?
