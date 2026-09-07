# Evidence Ledger Template

Use this table when the final gate needs to be auditable or leadership-facing.

```markdown
| Area | Evidence | Result | Notes |
|---|---|---|---|
| Source of truth | PR/head/artifact verified at ... | Pass/Fail | exact SHA, path, or URL |
| Review state | live PR checks/reviews/comments | Pass/Fail | mergeability and blockers |
| Tests | command and result | Pass/Fail | include scope and pass count when useful |
| Static checks | lint/typecheck/format/docs validation | Pass/Fail | repo-specific checks |
| Adversarial cases | negative or boundary probes | Pass/Fail | cases that prove robustness |
| Reusability | shared path or multiple fixture families | Pass/Fail | why it generalizes |
| Runtime | smoke/dependency check | Pass/Fail/Not run | lower runtime score if not run |
| Rollback/ops | flag, rollback, observability, runbook | Pass/Fail/Partial | operational caveats |
| Leadership summary | caveats included | Pass/Fail | no hidden risks |
```
