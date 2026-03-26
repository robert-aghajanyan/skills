---
name: skill-builder
description: Create well-designed Claude Code skills from scratch. Use when user says "create a skill", "build a skill", "new skill", "make a command", "turn this into a skill", or wants to package a workflow as a reusable slash command.
argument-hint: "[skill description or name]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, AskUserQuestion
---

# Skill Builder

Create well-designed Claude Code skills following Anthropic's official best practices.

## Workflow

### 1. Understand the intent

**If the conversation already contains a workflow** the user wants to capture ("turn this into a skill"), extract from the conversation history: tools used, sequence of steps, corrections the user made, input/output formats. Confirm with the user before proceeding.

**If the user provided a description** (`$ARGUMENTS`), use it.

**Otherwise**, ask:
- What should this skill do?
- When should it trigger? (user invokes manually, Claude invokes automatically, or both?)
- What's the expected output?

### 2. Classify the skill

Determine which category fits. Read [references/categories.md](references/categories.md) for the 9 categories. Skills that fit cleanly into one category work best.

### 3. Make key decisions

Ask the user (use AskUserQuestion) about any unclear points:
- **Scope**: Personal (`~/.claude/skills/`) or project (`.claude/skills/`)?
- **Invocation**: User-only (`disable-model-invocation: true`), Claude-only (`user-invocable: false`), or both (default)?
- **Isolation**: Run inline (default) or in a subagent (`context: fork`)? Fork runs in isolation without conversation history — only for skills with a concrete task, not reference/guidelines.

For the full list of frontmatter fields, substitutions, and hooks, see [references/frontmatter-reference.md](references/frontmatter-reference.md).

### 4. Write the description

The description is the most important field — it's how Claude decides when to load the skill. Follow this structure:

```
[What it does]. Use when [trigger phrases the user would say].
```

Include 2-3 natural trigger phrases. Be specific. **Make it slightly pushy** — Claude tends to undertrigger skills, so err on the side of including more trigger contexts rather than fewer.

Read [references/description-guide.md](references/description-guide.md) for good/bad examples and rules.

### 5. Draft the skill

Create the skill directory and SKILL.md. Use the template in [assets/skill-template.md](assets/skill-template.md) as a starting point. Apply these rules:

- **Under 500 lines** for SKILL.md — move detail to `references/`
- **Skip the obvious** — focus on what pushes Claude out of its default behavior
- **Explain the why** — instead of rigid ALWAYS/NEVER directives, explain reasoning so Claude can make context-dependent decisions. Heavy-handed directives are a yellow flag; reframe with rationale.
- **Include a Gotchas section** — even one item. This is the highest-signal content and grows over time as Claude hits new edge cases.
- **Provide defaults, not menus** — pick one approach, mention alternatives briefly

Read [references/writing-guide.md](references/writing-guide.md) for patterns like validation loops, templates, and checklists.

### 6. Add supporting files (if needed)

Consider whether the skill needs:
- `references/*.md` — detailed docs loaded only when relevant
- `scripts/*.py` — deterministic operations Claude runs instead of reconstructing
- `assets/*` — templates, examples for Claude to copy and adapt
- `config.json` pattern — for first-run setup that persists

Reference supporting files from SKILL.md so Claude knows what they contain and when to load them.

**Look for repeated work**: if you expect every invocation to independently produce similar helper code (a data-fetching script, a formatter, a validator), write it once, put it in `scripts/`, and tell the skill to use it. This saves every future run from reinventing the wheel.

### 7. Validate

Run the validation script to check for common issues:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/validate-skill.py <skill-directory>
```

### 8. Test

Suggest the user test with 2-3 realistic prompts:
1. **Direct invocation**: `/skill-name [args]` — does it produce the right output?
2. **Auto-trigger** (if enabled): rephrase the request naturally — does Claude load the skill?
3. **Baseline comparison**: try the same prompt WITHOUT the skill. Is the skill version meaningfully better? If not, the skill may not be adding enough value.

For skills with objectively verifiable outputs, consider writing simple assertions to check automatically. For subjective outputs (writing style, design), rely on human review.

After testing, iterate: fix what's broken, rerun, repeat until satisfied. Don't overfit to test examples — the skill needs to generalize to prompts you haven't tested.

## Gotchas

- **Name must be kebab-case** — `my-skill` not `my_skill` or `MySkill`. Max 64 chars. No "claude" or "anthropic" in the name.
- **Description max 1024 chars** — no XML tags allowed in description or name. Write in third person ("Processes files..." not "I help you...").
- **Claude undertriggers by default** — descriptions should be slightly pushy. Include more trigger contexts than feels necessary. "Even if they don't explicitly ask for X" is a valid addition.
- **Don't put `__init__.py` in the skill directory** — it's not a Python package.
- **`$ARGUMENTS` vs appended args** — if you don't include `$ARGUMENTS` in the content, Claude Code appends them as `ARGUMENTS: <value>`. Include it explicitly if you want control over placement.
- **`context: fork` needs a task** — a forked skill with only guidelines and no actionable prompt returns nothing useful.
- **Hooks in skills are session-scoped** — they activate when the skill is called and last for the session. Use for guardrails you only want sometimes.
- **Don't generalize from one failure** — if a test fails, understand why before changing the skill. The fix should improve the general case, not just patch the specific example.
