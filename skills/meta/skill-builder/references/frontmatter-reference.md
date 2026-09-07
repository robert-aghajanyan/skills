# Frontmatter Reference

All YAML frontmatter fields for SKILL.md. Only `description` is recommended; everything else is optional.

## Fields

| Field | Description | Default |
|-------|-------------|---------|
| `name` | Kebab-case, max 64 chars, no "claude"/"anthropic". Uses directory name if omitted. | directory name |
| `description` | What the skill does + when to trigger. Max 1024 chars, no XML tags. | first paragraph |
| `argument-hint` | Shown during autocomplete. E.g., `"[issue-number]"` | none |
| `disable-model-invocation` | `true` = only user can invoke (for dangerous/side-effect skills) | `false` |
| `user-invocable` | `false` = only Claude can invoke (for background knowledge) | `true` |
| `allowed-tools` | Tools Claude can use without permission when skill is active. E.g., `Read, Grep, Bash` | none |
| `model` | Override model for this skill. E.g., `claude-sonnet-4-6` | session model |
| `effort` | Override effort level. Options: `low`, `medium`, `high`, `max` (max is Opus only) | session effort |
| `context` | `fork` runs in isolated subagent (no conversation history) | inline |
| `agent` | Subagent type when `context: fork`. Options: `Explore`, `Plan`, `general-purpose`, or custom | `general-purpose` |
| `hooks` | On-demand hooks activated when skill is called, lasting for the session | none |

## Variable Substitutions

| Variable | Description |
|----------|-------------|
| `$ARGUMENTS` | All arguments passed after the skill name |
| `$ARGUMENTS[N]` or `$N` | Specific argument by 0-based index |
| `${CLAUDE_SKILL_DIR}` | Directory containing this SKILL.md |
| `${CLAUDE_SESSION_ID}` | Current session ID (for logging, session-specific files) |

## Dynamic Context Injection

The `` !`command` `` syntax runs a shell command before Claude sees the content:

```markdown
## Config
!`cat ${CLAUDE_SKILL_DIR}/config.json 2>/dev/null || echo "NOT_CONFIGURED"`
```

The command output replaces the placeholder. Claude only sees the result.

## Invocation Matrix

| Frontmatter | User can invoke | Claude can invoke |
|-------------|-----------------|-------------------|
| (default) | Yes | Yes |
| `disable-model-invocation: true` | Yes | No |
| `user-invocable: false` | No | Yes |

## Hooks Example

```yaml
---
name: careful-mode
description: Enable safety guardrails for production work
hooks:
  PreToolUse:
    - matcher: Bash
      hook: |
        if echo "$INPUT" | grep -qE 'rm -rf|DROP TABLE|force-push|kubectl delete'; then
          echo "BLOCKED: Dangerous command detected"
          exit 1
        fi
---
```
