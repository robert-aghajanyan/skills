# Writing Guide — Patterns & Anti-Patterns

## Core Principles

### Skip the obvious
Claude knows how to code. Focus on information that pushes it out of its default behavior — project-specific conventions, non-obvious edge cases, the particular tools or APIs to use. Ask: "Would Claude get this wrong without this instruction?" If no, cut it.

### Explain the why
Instead of rigid ALWAYS/NEVER directives, explain reasoning so Claude can make context-dependent decisions. Today's LLMs are smart — they have good theory of mind and when given a good harness can go beyond rote instructions. If you find yourself writing heavy-handed all-caps directives, that's a yellow flag: reframe and explain the reasoning so the model understands *why* the thing matters. That's more powerful and effective than brute-force compliance.

### Don't railroad
Give Claude the information it needs but let it adapt. Avoid rigid step-by-step sequences for flexible tasks. Be prescriptive only when operations are fragile or a specific sequence must be followed.

**Too prescriptive:**
```
Step 1: Run git log to find the commit.
Step 2: Run git cherry-pick <hash>.
Step 3: If there are conflicts, run git status...
```

**Better:**
```
Cherry-pick the commit onto a clean branch. Resolve conflicts preserving intent. If it can't land cleanly, explain why.
```

### Match specificity to fragility
- **Flexible tasks** (code review, analysis): describe what to look for, not exact steps
- **Fragile tasks** (database migration, deploy): be prescriptive, specify exact commands

## Effective Patterns

### Gotchas section
The highest-value content. Start with at least one gotcha, add more as Claude hits new edge cases over time.
```markdown
## Gotchas
- The `users` table uses soft deletes. Always include `WHERE deleted_at IS NULL`.
- User ID is `user_id` in DB, `uid` in auth, `accountId` in billing. All the same value.
```

### Output templates
More reliable than describing format in prose. Claude pattern-matches against concrete structures.
````markdown
## Report structure
Use this template:
```markdown
# [Title]
## Executive summary
[One paragraph]
## Key findings
- Finding 1 with data
## Recommendations
1. Specific action
```
````

### Validation loops
Have Claude validate its own work before proceeding.
```markdown
1. Make edits
2. Run: `python scripts/validate.py output/`
3. If validation fails, fix and re-run
4. Only proceed when validation passes
```

### Plan-validate-execute
For batch or destructive operations:
1. Create an intermediate plan (structured format)
2. Validate plan against source of truth
3. Only then execute

### Config.json for setup
Store first-run answers in config.json. Use dynamic context injection to load it:
```markdown
## Config
!`cat ${CLAUDE_SKILL_DIR}/config.json 2>/dev/null || echo "NOT_CONFIGURED"`

If NOT_CONFIGURED, ask the user for required settings and save to `${CLAUDE_SKILL_DIR}/config.json`.
```

### Memory via log files
For skills that benefit from cross-session history:
```markdown
## Memory
After completing the task, append a summary to `${CLAUDE_SKILL_DIR}/history.log`.
On each run, read the log to see what changed since last time.
```

## Anti-Patterns

- **Explaining what Claude already knows** — "A database migration modifies the schema..." is wasted tokens
- **Presenting menus instead of defaults** — "You can use pypdf, pdfplumber, PyMuPDF, or pdf2image..." → pick one default, mention alternatives briefly
- **Declaring answers instead of teaching procedures** — "Join orders to customers on customer_id" → teach the method of finding the right tables and joins
- **Covering every edge case** — most are better handled by Claude's judgment. Focus on the non-obvious ones in Gotchas.
- **Putting everything in SKILL.md** — if it's over 500 lines, split into references/
