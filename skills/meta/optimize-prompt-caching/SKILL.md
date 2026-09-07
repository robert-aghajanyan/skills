---
name: optimize-prompt-caching
description: Audit and optimize LLM prompt caching in any codebase. Use when you want to reduce LLM API costs, improve latency, add cache_control breakpoints, implement compaction, or apply prompt caching best practices from the Claude Code team's article.
argument-hint: "[audit|implement]"
allowed-tools: Read, Grep, Glob, Edit, Write, Bash, Agent
---

# Prompt Caching Optimizer

Based on the lessons from the Claude Code team's article: "Prompt Caching Is Everything."

Prompt caching works by **prefix matching** — the API caches everything from the start of the request up to each `cache_control` breakpoint. Any change anywhere in the prefix invalidates everything after it. The entire system must be designed around this constraint.

## Mode

- If `$ARGUMENTS` is `audit` (or empty/omitted): **Audit only** — scan the codebase, report findings and recommendations, do NOT modify files.
- If `$ARGUMENTS` is `implement`: **Implement** — scan, then apply all fixes. Confirm the plan with the user before editing.

---

## Step 1: Discover LLM API Usage

Search the codebase for all files that call LLM APIs. Check for:

```
# Anthropic SDK
anthropic
client.messages.create
client.messages.stream
client.beta.prompt_caching

# OpenAI SDK
openai
client.chat.completions.create
client.responses.create

# Common patterns
system_prompt
system=
tools=
messages=
cache_control
```

For each call site found, record:
- File path and line number
- Which SDK (anthropic, openai, other)
- How the system prompt is passed (string vs block array)
- How tools are passed (static list vs dynamic)
- How messages/conversation history is built
- Whether `cache_control` is already present

## Step 2: Audit Against the 7 Rules

For each call site, check every rule below. A violation means a caching opportunity is being missed.

### Rule 1: Static Content First, Dynamic Content Last

The prompt prefix order MUST be:
1. Static system prompt (globally cached across all sessions)
2. Project/user context like CLAUDE.md (cached within a project)
3. Tool definitions (globally cached — same tools for everyone)
4. Session context / conversation history (cached within a session)
5. Current user message (never cached — changes every turn)

**Violations to flag:**
- Timestamps, dates, or user-specific info embedded in the system prompt string
- Dynamic values interpolated into the system prompt (f-strings, `.format()`, string concatenation with variables)
- Tool definitions that change between calls
- System prompt constructed differently per-request

**Fix:** Move all dynamic content into messages (via `<system-reminder>` tags in user messages). Keep the system prompt pure static.

### Rule 2: Use Messages for Updates, Not System Prompt Changes

If any information changes between turns (current date, user state, mode changes, file contents), it should be injected as a message — NOT by modifying the system prompt.

**Violations to flag:**
- System prompt modified between API calls (e.g., appending context, changing instructions)
- State transitions that alter the system prompt (plan mode, debug mode, etc.)
- Date/time embedded in system prompt

**Fix:** Keep system prompt identical across all calls. Pass updates as `<system-reminder>` content in the next user message or tool result.

### Rule 3: Never Change Models Mid-Session

Prompt caches are per-model. Switching from Opus to Haiku mid-conversation rebuilds the entire cache — the "cheaper" model actually costs MORE because you lose the cached prefix.

**Violations to flag:**
- Model parameter that changes based on conditions (e.g., "use haiku for simple questions")
- Model switching logic mid-conversation
- Different models for different turn types in the same session

**Fix:** Set the model once at session start. If you need a different model for subtasks, use subagents (fork a new conversation with a focused handoff message).

### Rule 4: Never Add or Remove Tools Mid-Session

Tools are part of the cached prefix. Changing the tool set invalidates the cache for the ENTIRE conversation history.

**Violations to flag:**
- Tool list that varies by request (conditional tool inclusion)
- Tools added/removed based on user permissions or conversation state
- Dynamic tool generation

**Fix:** Keep all tools in every request. Use tool stubs with `defer_loading: true` for rarely-used tools. Model state transitions (like plan mode) as tools themselves, not as tool set changes.

### Rule 5: Design Features Around the Cache

State transitions (plan mode, review mode, etc.) should be modeled as tool calls and messages, not as changes to the system prompt or tool set.

**Violations to flag:**
- Mode changes that swap the system prompt
- Feature flags that alter tool definitions
- Conditional system prompt sections

**Fix:** Use dedicated tools for mode transitions (e.g., `EnterPlanMode` tool). Send mode instructions as messages, not system prompt modifications.

### Rule 6: Monitor Cache Hit Rate

Track `cache_creation_input_tokens` and `cache_read_input_tokens` from API responses. Alert when hit rate drops.

**Violations to flag:**
- No cache token tracking in the codebase
- No logging of cache metrics
- No alerting on low cache hit rates

**Fix:** Extract cache metrics from `response.usage`, log them, compute hit rate: `cache_read / (input + cache_creation + cache_read)`. Warn below 30%.

### Rule 7: Cache-Safe Forking (Compaction / Summarization)

When you need a side computation (summarization, compaction, skill execution), use the EXACT same system prompt, tools, and conversation prefix so the cached data is reused.

**Violations to flag:**
- Compaction/summarization that uses a different system prompt
- Side computations with different tool sets
- Separate API calls that don't share the parent's prefix

**Fix:** For compaction, append the compaction instruction as a new user message at the end of the existing conversation. Use identical `system=` and `tools=` parameters. This reuses the parent's cache.

## Step 3: Check `cache_control` Breakpoint Placement

The API supports up to 4 `cache_control` breakpoints. Optimal placement:

| Breakpoint | Location | Scope |
|------------|----------|-------|
| 1 | End of system prompt | Global (all sessions) |
| 2 | Last tool definition | Global (all sessions) |
| 3 | Last message before current user input | Session (grows each turn) |
| 4 | Reserved for compaction or special use | As needed |

**For system prompt** — must be passed as a block array, not a string:
```python
# WRONG — no caching
system="You are a helpful assistant..."

# RIGHT — cacheable
system=[
    {
        "type": "text",
        "text": "You are a helpful assistant...",
        "cache_control": {"type": "ephemeral"}
    }
]
```

**For tools** — add `cache_control` to the last tool:
```python
tools = copy.deepcopy(TOOLS)
tools[-1]["cache_control"] = {"type": "ephemeral"}
```

**For messages** — add breakpoint to the message right before the latest user input:
```python
# Find the last user message, put cache_control on the message before it
# Convert string content to block format if needed
messages[target_idx]["content"] = [
    {"type": "text", "text": content, "cache_control": {"type": "ephemeral"}}
]
```

## Step 4: Check for Compaction

Long conversations should be compacted when approaching context limits. The compaction MUST be cache-safe:

- Use the EXACT same `system=` and `tools=` as the parent conversation
- Prepend the parent's full message history
- Append the compaction instruction as a new user message
- This reuses the parent's cached prefix — no extra cache-miss cost
- Leave a "compaction buffer" so there's room for the summary output

```python
# Cache-safe compaction pattern
compact_messages = existing_messages + [
    {"role": "user", "content": "Summarize our conversation so far..."}
]
response = client.messages.create(
    system=same_cached_system,   # SAME prefix
    tools=same_cached_tools,     # SAME prefix
    messages=compact_messages,
)
```

## Step 5: Check SDK Version

Prompt caching requires:
- `anthropic >= 1.0.0` (Python) or `@anthropic-ai/sdk >= 0.27.0` (JS/TS)
- OpenAI SDK doesn't have equivalent `cache_control` — but you can structure prompts for their automatic caching

Flag if the SDK version is too old.

## Step 6: Generate Report

Present findings as a table:

```
## Prompt Caching Audit Report

### Call Sites Found
| # | File:Line | SDK | System Prompt | Tools | Messages | cache_control |
|---|-----------|-----|---------------|-------|----------|---------------|
| 1 | chat.py:340 | anthropic | static string (NO cache) | static list (NO cache) | growing history (NO cache) | MISSING |

### Violations
| Rule | Location | Issue | Fix |
|------|----------|-------|-----|
| R1 | chat.py:71 | System prompt is a raw string, not block array | Wrap in list with cache_control |
| R6 | chat.py:28 | No cache token tracking | Add cache_creation/cache_read fields |

### Estimated Impact
- System prompt: ~X tokens cached globally (saves on every request)
- Tools: ~X tokens cached globally
- Conversation: ~X tokens cached per session per turn
```

## Step 7: Implement (if mode is `implement`)

If the user requested implementation:

1. Present the audit report and proposed changes
2. Wait for user confirmation before editing
3. Apply changes in this order:
   a. Update SDK version in requirements/package.json
   b. Add `cache_control` to system prompt (convert string → block array)
   c. Add `cache_control` to last tool definition
   d. Add conversation message cache breakpoints
   e. Add cache token tracking fields to session/message models
   f. Add cache metrics logging
   g. Add compaction logic if conversations can grow long
   h. Fix any Rule 1-7 violations found
4. Run existing tests to verify nothing breaks
5. Summarize all changes made

## Gotchas

- **Prefix matching is absolute** — any change anywhere in the cached prefix invalidates everything after it. System prompt, tools, and early conversation turns must be completely static for caching to work.
- **`cache_control` on tools goes on the LAST tool** — placing it on an earlier tool means tools added later break the cache prefix. Always put the breakpoint on the final tool definition.
- **String system prompts don't support cache_control** — you must convert `system: "text"` to the block array format `system: [{type: "text", text: "...", cache_control: {...}}]` before caching works.
- **Cache TTL is 5 minutes by default** — ephemeral caching expires quickly. For long-running sessions, ensure requests happen frequently enough to keep the cache warm.
- **Compaction must preserve the cache prefix** — when truncating conversation history to fit context, never modify the system prompt or tool definitions. Only compact conversation messages.
- **Token tracking fields vary by SDK** — Anthropic SDK returns `cache_creation_input_tokens` and `cache_read_input_tokens` in the usage object. Other SDKs may not expose these. Check your SDK version.
