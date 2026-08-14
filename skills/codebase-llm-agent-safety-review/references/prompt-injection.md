# Prompt Injection

Prompt injection is a confirmed finding only when hostile text can reach a decision point that changes data access, tool use, memory, generated code, external output, or a user-visible decision.

## Review Checks

- Separate instruction sources: system/developer policy, application rules, user task, retrieved text, tool output, browser content, file content, memory, and generated summaries.
- Inspect prompt assembly for untrusted content placed near privileged instructions without delimiting, labeling, or downstream enforcement.
- Look for model-visible secrets, hidden prompts, credentials, internal URLs, private file paths, tenant data, or tool outputs that hostile content can ask the model to reveal.
- Check whether retrieved documents, web pages, emails, tickets, uploaded files, or tool results can instruct the model to ignore policy, call tools, alter arguments, or write memory.
- Confirm whether the model can choose tools, recipients, domains, paths, resource IDs, commands, or approval text based on untrusted instructions.
- Check multi-turn persistence: hostile content stored in memory, summaries, scratchpads, vector indexes, logs, or task state can trigger later.

## Mitigations That Count

- Deterministic policy checks after model output and before side effects.
- Tool allowlists and typed schemas that reject unauthorized resources, paths, recipients, domains, commands, and actions.
- Tenant-scoped retrieval and memory filters enforced outside the model.
- Explicit labeling of untrusted content plus code-level refusal to treat it as instruction.
- Redaction before prompt construction, logging, memory writes, and external outputs.
- Human approval before irreversible, external, costly, privileged, or destructive actions.

Prompt wording alone is useful context, but it is not sufficient mitigation for privileged tools, sensitive data, or external side effects.

## Attack Patterns

- A retrieved document says to reveal system prompts or secrets.
- A web page tells the agent to send local files to a URL.
- A tool result contains instructions for the next tool call.
- A user upload says to approve, merge, email, delete, or execute something outside the intended task.
- A memory entry silently changes future policy or tool selection.
- A generated plan smuggles an unsafe command, path traversal, or external recipient.

## Probes

- Add hostile text to a retrieved document and assert it is treated as data, not instruction.
- Return hostile text from a mocked tool and assert no unauthorized follow-up tool call occurs.
- Attempt to exfiltrate hidden prompts, credentials, private files, and cross-tenant records.
- Attempt to store malicious memory and verify future sessions do not execute it as instruction.
- Attempt to smuggle disallowed tool arguments through natural language, JSON strings, markdown links, filenames, and redirect URLs.
