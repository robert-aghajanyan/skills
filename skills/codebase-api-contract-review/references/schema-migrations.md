# Schema Migrations

Review schemas as contracts for stored data, wire data, generated code, analytics, and downstream validation. Include database schemas, migrations, ORM models, JSON Schema, OpenAPI components, GraphQL schemas, protobuf, Avro, AsyncAPI payloads, CSV layouts, warehouse tables, and exported report formats.

## Map

Capture:

- Current and changed schema files, migration files, generated models, validators, serializers, and deserializers.
- Required fields, defaults, nullability, enums, constraints, indexes, unique keys, foreign keys, type widths, precision, and timestamp formats.
- Data producers and consumers, including background jobs, reports, dashboards, importers, backfills, rollbacks, and older deployed versions.
- Whether migrations are expand/migrate/contract, online/offline, reversible, idempotent, and safe for rolling deployments.

## Red Flags

- Removing or renaming columns, fields, enum values, message fields, GraphQL fields, or JSON keys without a compatibility window.
- Making optional data required before all writers and stored rows can satisfy it.
- Tightening validation, type ranges, string formats, uniqueness, nullability, or referential constraints without a cleanup/backfill path.
- Reusing numeric protobuf tags, changing Avro defaults incompatibly, changing CSV column order, or changing report JSON shape without a version bump.
- Migrations that are irreversible, non-idempotent, table-locking, or unsafe while old and new application versions run together.
- Generated clients, snapshots, fixtures, or schema registries not updated alongside schema changes.

## Compatibility Strategies

- Prefer expand/migrate/contract: add nullable/new fields first, deploy dual read/write or backfill, verify consumer readiness, then remove old fields later.
- Keep tolerant readers and conservative writers during mixed-version deployments.
- Preserve old field names as aliases or derived fields until consumers migrate.
- Version files, endpoints, event subjects, or exported reports when shape changes are intentionally breaking.
- Add contract tests that parse old payloads and validate new payloads against the promised schema.

## Evidence

Tie findings to the changed schema, the migration, and at least one producer or consumer path when possible. If only the producer side is visible, state that consumer impact is conditional and name the unknowns.
