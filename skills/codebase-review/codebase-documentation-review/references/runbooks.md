# Runbooks

Use this reference when reviewing on-call docs, incident guides, troubleshooting docs, rollback instructions, recovery procedures, maintenance docs, and operational checklists.

## Evidence To Compare

- Deployment manifests, CI/CD workflows, infrastructure config, service entrypoints, observability config, alert definitions, dashboards referenced by path or URL, logging code, scripts, and production configuration.
- Current service names, namespaces, queues, jobs, cron schedules, regions, accounts, clusters, feature flags, and ownership files.

## Checks

- The runbook states when to use it, the expected symptoms, and the affected service or environment.
- Commands, scripts, dashboards, log queries, alert names, and paths are current.
- Prerequisites and access requirements are explicit enough for an operator who is not the original author.
- Mitigation, rollback, recovery, and validation steps are distinct and ordered safely.
- Destructive, irreversible, or customer-impacting actions include scope checks, backups, dry-run options, or approval expectations.
- The runbook includes escalation or ownership for cases where the procedure does not resolve the issue.
- Post-action validation proves the service recovered and that no queued, delayed, or downstream work remains broken.
- Incident guidance avoids stale dates, old branch names, old deploy surfaces, and obsolete dashboards.

## Common Findings

- A rollback doc references a deployment job or namespace that no longer exists.
- Troubleshooting stops at "check logs" without exact service, query, timeframe, or failure signal.
- A recovery step restarts a worker but omits backlog validation.
- The doc identifies symptoms but not when to escalate or who owns the service.
- A command is dangerous in production but the doc does not require environment or account confirmation.

## Calibration

Do not require production-specific secrets or private URLs to be fully spelled out in public docs. Do require the doc to identify where authorized operators can find them and how to verify they are using the right environment.
