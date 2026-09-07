# Output Format

Use a concise, evidence-first report. For small cleanup patches, keep it short; for assessment-only work, include the full candidate table.

## Required Sections

```markdown
**Scope**
Repo, assessment-only vs edits, and explicit boundaries.

**Worktree Safety**
Branch, dirty files, ignored/tracked artifact notes, and how user changes were preserved.

**Inventory**
- Languages/package managers:
- Source:
- Tests:
- Scripts:
- Config/runtime:
- Generated/artifacts:
- Docs:

**Cleanup Candidates**
| Category | Candidate | Evidence | Risk | Recommendation |
| --- | --- | --- | --- | --- |
| Safe | ... | ... | Low | Delete/update in this batch |
| Likely | ... | ... | Medium | Confirm with tests/tooling first |
| Risky | ... | ... | High | Needs human confirmation |

**Changes Made**
Files changed, or "None; assessment only".

**Left Untouched**
Important candidates intentionally skipped and why.

**Validation**
Commands run and results, or why validation was skipped.

**Follow-Up**
Cleanup candidates needing human confirmation or broader validation.
```

## Recommendation Language

Use precise action verbs:

- `delete`
- `ignore going forward`
- `remove dependency`
- `merge duplicate utility`
- `update stale docs`
- `keep`
- `needs human confirmation`

Avoid unsupported phrasing such as "probably unused" without evidence.

## Final Answer After Edits

Lead with what changed and what was validated. Mention residual risk only when it matters. Include exact file paths for touched files and exact commands for validation.
