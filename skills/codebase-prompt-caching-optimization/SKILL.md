---
name: codebase-prompt-caching-optimization
description: Audit and optimize LLM prompt caching in codebases. Use when user wants to reduce LLM API cost or latency, add cache breakpoints, compact long conversations safely, improve cache hit rate, or optimize Anthropic, OpenAI, or similar integrations.
---

# Codebase Prompt Caching Optimization

Audit request construction so stable prefix tokens are reused instead of rebuilt every turn. The core rule is prefix stability: any change near the start of the request invalidates everything after it.

## Modes

Infer the mode from the user's request:

- **Audit** when they ask for findings, recommendations, or diagnosis.
- **Implement** when they ask for fixes. Present the audit and plan first, then wait for confirmation before editing.

## Step 1: Discover LLM API Usage

Search the codebase for LLM API call sites. Check for:

```text
anthropic
client.messages.create
client.messages.stream
cache_control

openai
client.responses.create
client.chat.completions.create

system prompt
instructions
tools
messages
conversation history
response.usage
```

For each call site, record:

- file path and line number
- SDK/provider
- how system instructions are passed
- how tools are passed
- how messages/history are built
- whether explicit cache breakpoints already exist
- whether cache metrics are captured

## Step 2: Audit Against the 7 Rules

### Rule 1: Static Content First, Dynamic Content Last

The reusable prefix should generally look like:

1. Static system instructions
2. Stable project context such as repo policies or shared guidance
3. Tool definitions
4. Session history
5. Current user input

Flag:

- timestamps, dates, or per-user data embedded in system instructions
- f-strings or string concatenation in the system prompt
- tool definitions that vary per request
- request construction that reorders stable sections between calls

Fix:

Move dynamic context into later messages or structured inputs. Keep the system prompt and tools as stable as possible.

### Rule 2: Use Messages for Updates, Not System Prompt Mutations

If information changes between turns, it usually belongs in a new message or tool result, not in a rewritten system prompt.

Flag:

- mode changes that rewrite the system prompt
- per-turn context appended to system instructions
- current date or transient state embedded in the prefix

Fix:

Keep the system prompt stable. Inject updates as new conversation content.

### Rule 3: Avoid Mid-Session Model Switching When the Provider Scopes Cache by Model

Some providers scope prompt caches to the exact model. A mid-session model switch can discard the cached prefix and erase the intended savings.

Flag:

- conditional model routing inside one user session
- "cheap model for simple turns, expensive model for hard turns" logic on the same conversation
- summarization or compaction calls that swap models while expecting cache reuse

Fix:

Choose the model once per session when cache reuse matters. If a side task must use a different model, treat it as a separate session.

### Rule 4: Keep Tool Definitions Stable

Tool schemas are part of the cacheable prefix in many tool-using integrations.

Flag:

- tools added or removed per request
- tool lists gated by conversation state
- dynamic tool generation

Fix:

Keep the tool inventory stable across turns. Represent mode changes in messages or dedicated tool results, not by swapping the tool list.

### Rule 5: Design Features Around Cache Reuse

Features such as plan mode, review mode, or compaction should preserve the reusable prefix instead of rebuilding it.

Flag:

- feature flags that alter early prompt sections
- separate side calls that rebuild system instructions from scratch
- prompt assembly code that duplicates almost-identical prefixes in multiple places

Fix:

Centralize prompt assembly and keep the stable prefix identical across related requests.

### Rule 6: Measure Cache Hit Rate

Capture usage metrics so regressions are visible.

Flag:

- no logging of cache-related usage fields
- no hit-rate or saved-token reporting
- no alerting or dashboards for sudden cache misses

Fix:

Extract the provider's cache metrics from the response usage object and log them. Report low hit rates or sudden drops.

### Rule 7: Compact Long Conversations Without Breaking the Prefix

When you summarize or compact history, preserve the same prefix and append the compaction instruction at the end of the existing conversation.

Flag:

- compaction that uses a different system prompt
- compaction that drops or rewrites tools
- summarization jobs that rebuild the request from scratch and lose cache reuse

Fix:

Reuse the exact same system instructions and tool definitions. Append the compaction request as a later message.

## Step 3: Check Explicit Breakpoints Where the Provider Supports Them

Some providers expose explicit cache breakpoints, such as Anthropic's `cache_control`. When they do, place them at stable boundaries:

| Breakpoint | Location | Typical Scope |
|------------|----------|---------------|
| 1 | End of stable system instructions | Cross-session |
| 2 | End of stable tool definitions | Cross-session |
| 3 | Last stable message before the newest user input | Per session |

For Anthropic-style explicit caching:

- pass `system` as a block array instead of a plain string
- place `cache_control` on the last stable tool definition
- place the conversation breakpoint on the stable message immediately before the latest user input

```python
system = [
    {
        "type": "text",
        "text": "Stable system instructions...",
        "cache_control": {"type": "ephemeral"},
    }
]
```

```python
tools = copy.deepcopy(TOOLS)
tools[-1]["cache_control"] = {"type": "ephemeral"}
```

If the provider has automatic caching instead of explicit breakpoints, keep the request prefix byte-for-byte stable and skip provider-specific fields.

## Step 4: Check for Safe Compaction

For long conversations:

- reuse the exact same stable prefix
- keep tool definitions unchanged
- append a compaction request as a new message
- leave enough room for the summary output

```python
compact_messages = existing_messages + [
    {"role": "user", "content": "Summarize the conversation so far for continued work."}
]
```

## Step 5: Check SDK and API Support

Verify that the installed SDK and API version support the caching features the code expects. If the implementation relies on provider-specific fields, cite the relevant official docs in the audit report and flag outdated SDKs or mismatched APIs.

## Step 6: Generate the Report

Present findings as a table:

```markdown
## Prompt Caching Audit Report

### Call Sites Found
| # | File:Line | Provider | System Prefix | Tools | Messages | Explicit Breakpoints |
|---|-----------|----------|---------------|-------|----------|----------------------|
| 1 | chat.py:340 | anthropic | static block | stable list | growing history | partial |

### Violations
| Rule | Location | Issue | Fix |
|------|----------|-------|-----|
| R1 | chat.py:71 | Dynamic timestamp embedded in system prompt | Move it into the current user message |
| R6 | chat.py:28 | Cache metrics are not logged | Extract usage fields and log hit rate |

### Estimated Impact
- Stable system instructions: ~X tokens reusable across requests
- Stable tools: ~X tokens reusable across requests
- Session history: ~X tokens reusable within a session
```

## Step 7: Implement

If the user asked for implementation:

1. Present the audit report and proposed edits.
2. Wait for confirmation before editing.
3. Apply changes in this order:
   a. Upgrade or align the SDK/API usage if needed.
   b. Stabilize system instructions.
   c. Stabilize tool definitions.
   d. Add explicit breakpoints where supported.
   e. Add cache metrics logging.
   f. Add compaction logic if conversations can grow long.
   g. Fix remaining Rule 1-7 violations.
4. Run existing tests.
5. Summarize the behavior and cost impact.

## Gotchas

- **Prefix matching is absolute**: even a small change near the start of the request can invalidate everything after it.
- **Explicit breakpoints belong at stable boundaries**: placing them too early or on unstable content limits reuse.
- **String system prompts may block provider-specific caching features**: some APIs require structured blocks instead.
- **Ephemeral caches usually expire quickly**: frequent cache misses may be a TTL or traffic-pattern problem, not just a code bug.
- **Metric fields differ by SDK**: read the actual response usage shape before wiring dashboards or alerts.
