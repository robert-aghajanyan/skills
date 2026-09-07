# Writing Effective Descriptions

The description is the most important field. Claude scans descriptions at startup to decide "is there a skill for this request?" It's a trigger, not a summary.

## Structure

```
[What it does]. Use when [trigger condition with natural phrases].
```

## Good examples

```yaml
# Specific + actionable + trigger phrases
description: Monitors a PR until it merges. Trigger on 'babysit', 'watch CI', 'make sure this lands'.

# Clear what + when
description: Post your daily standup. Triggers on "standup", "daily".

# Includes file types
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.

# Task-specific with triggers
description: Audit and decompose large modules into smaller units. Use when user mentions "split", "decompose", "monolith", "god class", "too big".
```

## Bad examples

```yaml
# Too vague — when does this trigger?
description: Helps with projects.

# Missing triggers — describes capability but not when to activate
description: Creates sophisticated multi-page documentation systems.

# Too technical, no user triggers
description: Implements the Project entity model with hierarchical relationships.

# Summary, not a trigger
description: A comprehensive tool for monitoring pull request status across the development lifecycle.
```

## Rules

- Max 1024 characters
- No XML tags (`<` or `>`)
- **Write in third person** — "Processes Excel files..." not "I can help you..." or "You can use this to...". The description is injected into the system prompt; inconsistent point-of-view causes discovery problems.
- Include 2-3 natural phrases a user would say
- Include relevant file types or domain terms if applicable
- **Make it slightly pushy** — Claude tends to undertrigger skills. Err on the side of including more trigger contexts. Adding "even if they don't explicitly ask for X" is valid. Example: instead of "Builds dashboards", write "Builds dashboards. Use when user mentions dashboards, data visualization, internal metrics, or wants to display any kind of data, even if they don't explicitly ask for a 'dashboard'."
- Test: "If a user said X, would this description match?" — if not, add X

## Testing your description

After writing a description, create 10-15 test queries to verify it triggers correctly:

**Should-trigger queries (6-8)**: Realistic prompts a user would actually type. Different phrasings of the same intent — some formal, some casual. Include cases where the user doesn't name the skill but clearly needs it. Make them concrete with details (file paths, column names, context), not abstract ("format this data").

**Should-not-trigger queries (4-6)**: Near-misses that share keywords but need something different. These are the most valuable — they test precision. Avoid obviously irrelevant queries ("write a fibonacci function" for a PDF skill tests nothing).

Test each query by asking yourself: "Would Claude correctly decide to load this skill?" If your should-trigger queries don't feel like they'd match, make the description pushier. If your should-not-trigger queries feel like they'd match, make the description more specific.
