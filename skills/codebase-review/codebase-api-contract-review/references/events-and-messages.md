# Events And Messages

Events and messages are contracts between producers, consumers, replay jobs, warehouses, alerting, dashboards, and older service versions. Review payload shape plus delivery semantics.

## Map

Capture:

- Topics, queues, subjects, routing keys, event names, message versions, schema files, registry entries, producers, consumers, DLQs, replay/backfill paths, and retention windows.
- Payload fields, required/optional status, defaults, enum values, timestamp formats, identifiers, idempotency keys, correlation IDs, and metadata headers.
- Delivery assumptions: ordering, at-least-once behavior, deduplication, retries, backoff, batching, compression, partitioning, and poison-message handling.

## Red Flags

- Removing or renaming event names, topics, fields, enum values, headers, or routing keys.
- Making optional fields required or changing a field's meaning without a new event version.
- Changing timestamp, ID, amount, currency, locale, or unit formats.
- Repartitioning or changing keys in ways that break ordering, deduplication, or consumer scaling.
- Dropping compatibility for replayed old messages.
- Producer-only tests with no consumer contract test or schema-registry validation.

## Compatibility Strategies

- Add fields instead of mutating existing ones; keep consumers tolerant of unknown fields.
- Version event names, subjects, or schema versions when semantics change.
- Run dual-publish or adapter periods for renamed events and fields.
- Keep replay compatibility tests with old fixture payloads.
- Coordinate producer and consumer rollout order and rollback behavior.

## Evidence

Use schema definitions, producer code, consumer code, topic configuration, replay jobs, fixtures, contract tests, and dashboards. When consumer repos are not available, mark the risk conditional and list the likely consumers to verify.
