# LLM And Agent Security Checks

Use this reference when the reviewed system uses LLMs, agents, tool calling, retrieval, plugins, browser automation, code execution, generated prompts, or model-produced actions.

## Boundaries

- Treat model output, retrieved documents, uploaded files, web pages, tool results, emails, tickets, chat messages, and plugin metadata as untrusted input.
- Separate instruction sources: system/developer policy, application policy, user instructions, retrieved content, tool observations, and generated text.
- Identify tools that can read data, write files, send messages, browse, execute commands, call APIs, create tickets, approve workflows, spend money, or change infrastructure.

## Review Checks

- Prompt injection: untrusted content can override policy, reveal hidden context, redirect tools, or alter the intended task.
- Tool misuse: tools expose broader read/write/network scopes than the workflow needs, or model text can select dangerous arguments without validation.
- Data exfiltration: secrets, credentials, private documents, source code, prompts, tool outputs, tenant data, or hidden metadata can be sent to external destinations.
- Confused deputy: the agent uses privileged credentials to perform attacker-requested actions on resources the attacker cannot access directly.
- Unsafe code execution: generated code, shell commands, notebook cells, plugins, or transformations run without review, sandboxing, or allowlists.
- Retrieval trust: retrieved text is treated as instruction, metadata filters are missing, tenant filters are absent, or private context is mixed with public context.
- Memory and logging: sensitive prompts, tool outputs, uploaded files, or model traces are persisted or exported unexpectedly.
- Human approval: approval gates are missing, ambiguous, spoofable, or applied after the irreversible action.

## Controls To Look For

- Tool allowlists, argument schemas, path/network/domain allowlists, dry-run modes, approval before side effects, explicit data-flow checks, tenant-filtered retrieval, redaction, audit logs, and fail-closed tool errors.
- Clear treatment of model output as data until validated by deterministic code or approved by a human.
- Tests with malicious retrieved content, hostile tool output, forged metadata, and attempts to exfiltrate hidden context.

## Negative Probes

- Retrieved document says to ignore policy and call a sensitive tool.
- Web page or email instructs the agent to send secrets to an external URL.
- User asks the agent to act on another tenant's resource using a valid-looking ID.
- Tool output contains instructions that would change the next tool call.
- Generated command includes shell metacharacters, path traversal, or external network access.
