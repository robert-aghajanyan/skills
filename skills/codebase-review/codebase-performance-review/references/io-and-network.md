# IO And Network

Review external work for unbounded fanout, missing pagination, repeated calls, and request-path latency.

## Database And Query Risks

- N+1 reads or writes from resolvers, serializers, template rendering, mappers, or per-row enrichment.
- Queries inside loops where batch fetch, join, prefetch, select-related, eager load, or aggregation would preserve behavior.
- Missing indexes or query predicates on high-cardinality tables.
- Full-table scans, broad `SELECT *`, unbounded `ORDER BY`, unbounded `GROUP BY`, or offset pagination at high page depths.
- Per-row inserts or updates when bulk operations or transactions are available and safe.
- Repeated connection/client construction in hot code.
- Inefficient migrations or backfills without batching, progress tracking, or resume behavior.

## Network And Cloud API Risks

- Per-item HTTP, RPC, SDK, object-storage, model, or SaaS API calls.
- Redundant calls with identical parameters in one request, job, or batch.
- Missing pagination or page limits for list/search APIs.
- Sequential remote calls that dominate latency and could be safely batched, coalesced, or moved out of the request path.
- Retry loops that multiply cost or latency without timeout, budget, jitter, or idempotency.
- Excessive payload transfer, repeated downloads, repeated uploads, or unnecessary full-object reads.
- Logging or tracing every item in a large remote-response loop.

## Pagination

Confirm:

- The code follows `next`, `cursor`, `page_token`, `Link`, `offset`, continuation token, or SDK paginator semantics correctly.
- There is a clear upper bound, caller-visible limit, checkpoint, or streaming behavior for large result sets.
- The loop cannot silently drop the last page, repeat the same page, or run forever.
- Errors include enough context to resume or retry safely.

## File IO

- Repeated whole-directory scans in request paths or tests.
- Whole-file reads for large files where streaming or chunking is practical.
- Repeated parsing of static config, schemas, templates, notebooks, models, or reports.
- Temporary files that accumulate, duplicate large payloads, or force unnecessary copy/compress/decompress cycles.
- Synchronous filesystem work in latency-sensitive handlers.

## Findings

A strong IO finding names the external operation, the loop or call path that multiplies it, the triggering cardinality, and a fix that preserves correctness under errors and partial results.
