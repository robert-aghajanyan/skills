---
name: mp-handoff
description: Create a concise handoff document for a future Claude Code session and save it outside the workspace. Use when the user says "handoff", "write a handoff doc", "summarize this for the next agent", or asks to compact the current conversation into a continuation note.
---

# Handoff

Use this skill to create a handoff document that a fresh agent can use to continue the work without replaying the whole conversation.

## Instructions

Parse the current user request directly. If the user includes text after the handoff request, treat it as the intended focus for the next session and tailor the document to that focus.

Write one Markdown file outside the current workspace or repository — use the session's scratchpad directory if one is available, otherwise the OS temporary directory. Resolve the temp directory at runtime, for example:

```bash
python3 -c 'import tempfile; print(tempfile.gettempdir())'
```

Use a descriptive filename such as `claude-handoff-YYYYMMDD-HHMMSS.md`.

## Document Shape

Include only sections that carry useful continuation context:

- **Purpose**: what the next session is for, including the user's stated focus when provided.
- **Current State**: what has already been done or decided in this conversation.
- **Artifacts To Reference**: paths, URLs, branch names, PRs, commits, issues, docs, generated files, or logs that already contain detail. Do not duplicate their contents.
- **Open Work**: concrete next steps, blockers, risks, and verification still needed.
- **Suggested Skills**: skill names the next agent should invoke and why.
- **Sensitive Data Notes**: confirm that secrets and personal data were redacted, or note that none were encountered.

## Redaction

Before saving, scan the draft for sensitive material and remove or mask it:

- API keys, tokens, cookies, passwords, private keys, credentials, database URLs, and bearer strings.
- Personal data that is not needed for continuation.
- Raw `.env` values or copied command output that may contain secrets.

Prefer references to sensitive sources by path only, such as "repo `.env` exists", without copying values.

## Artifact Discipline

Do not duplicate content already captured in source artifacts such as PRDs, plans, ADRs, GitHub issues, commits, pull requests, diffs, generated reports, or saved logs. Link or cite the exact path, URL, branch, commit, or command instead.

Keep the handoff practical and short enough for a future agent to skim quickly. Include exact commands only when they are not already captured elsewhere and are needed to resume safely.

## Validation

After writing the file:

1. Confirm it exists in the OS temp directory.
2. Re-open or print the first lines to verify the document was written correctly.
3. Run a quick sensitive-string sanity check when credentials may have appeared in the conversation.
4. Final response should include the absolute handoff file path and a one-line summary of what it covers.

## Gotchas

- Do not save the handoff in the current workspace unless the user explicitly overrides the temp-directory requirement.
- Do not depend on `argument-hint` or other frontmatter placeholder variables being populated; infer the focus from the actual user message.
- Do not claim the handoff is complete if major current-state facts are uncertain. Label uncertain items as needing verification.
