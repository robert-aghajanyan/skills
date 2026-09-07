# Idempotency

## What to inspect

- Operations triggered by queues, webhooks, cron, CLIs, agents, retries, and user refreshes.
- Writes that create orders, tickets, jobs, reports, files, notifications, deployments, or billing records.
- External side effects: emails, Slack messages, payment calls, GitHub comments, cloud API mutations, and downstream job starts.

## Reliability checks

- Retried or replayed operations should have an idempotency key, dedupe key, natural unique constraint, or already-completed check.
- Deduplication should cover the same boundary as the side effect. A local in-memory flag is not enough for multi-process workers.
- Idempotency records should be written atomically with the state transition when practical.
- Partial success should be detectable and resumable without duplicating external effects.
- "At least once" inputs from queues, webhooks, and scheduled jobs should be assumed even if happy-path code sees each event once.
- CLI reruns should either be safe by default or require an explicit destructive flag.

## Finding patterns

- Queue consumer sends an external notification before recording processed state.
- Cron job appends or publishes every run without checking whether the period was already processed.
- Retry loop wraps a create call with no unique key.
- File/report generation overwrites shared paths without run-scoped names.
- API endpoint can double-submit because client retry and server dedupe are missing.

## Validation ideas

- Run the same event/job/request twice and assert one durable side effect.
- Force a crash between the local write and external call, then rerun.
- Test duplicate delivery from the queue or webhook handler.
- Add database uniqueness tests for dedupe keys and conflict handling.
