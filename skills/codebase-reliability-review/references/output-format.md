# Output Format

Use this structure for reliability reviews. Keep it concise, evidence-backed, and ordered by operational risk.

```markdown
## Executive Summary
[One paragraph: overall reliability posture, highest-risk failure modes, and whether the system is ready for production use.]

## Runtime Map
| Area | Evidence | Reliability notes |
| --- | --- | --- |
| Services | `path:line` | ... |
| Workers/jobs | `path:line` | ... |
| APIs/CLIs | `path:line` | ... |
| Queues/databases | `path:line` | ... |
| External dependencies | `path:line` | ... |
| Deployment/runtime config | `path:line` | ... |

## Failure-Mode Table
| Boundary | Scenario | Current behavior | Impact | Coverage |
| --- | --- | --- | --- | --- |
| Network call | Dependency hangs | ... | ... | Test/log/metric or gap |

## Findings
### [Severity] Title
- Affected file/line: `path:line`
- Failure scenario: ...
- User/business impact: ...
- Recommended fix: ...
- Validation test: ...

## Quick Wins
- ...

## Deeper Reliability Investments
- ...

## Tests and Validation Commands
- `command`

## Open Questions
- ...
```

## Severity guide

- **Blocker**: likely data loss, duplicate customer-visible side effects, outage, unsafe deploy, or unrecoverable incident path.
- **High**: plausible production failure with material customer/business impact and no reliable mitigation.
- **Medium**: reliability weakness with bounded impact, manual recovery, or lower likelihood.
- **Low**: hardening, clarity, or observability improvement with limited immediate risk.

## Reporting rules

- Findings need concrete file and line evidence.
- Separate "quick wins" from "deeper investments" so small fixes are not buried under architecture work.
- If recommending a bigger mechanism, name the simpler alternative considered and why it is insufficient.
- Do not claim production readiness from static review alone; state what was and was not validated.
