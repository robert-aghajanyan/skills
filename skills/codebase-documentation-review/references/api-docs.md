# API Docs

Use this reference when reviewing REST, GraphQL, RPC, OpenAPI, protobuf, SDK, webhook, event, or public contract documentation.

## Evidence To Compare

- Route registrations, controllers, handlers, routers, serializers, validators, schemas, generated clients, OpenAPI or GraphQL definitions, protobuf files, event definitions, SDK methods, and contract tests.
- Auth, permissions, rate limiting, pagination, filtering, sorting, versioning, deprecation, and error handling code.
- Example requests and responses in docs, tests, fixtures, API collections, and generated documentation.

## Checks

- Documented paths, methods, RPC names, operation names, SDK methods, and event names exist.
- Request fields, response fields, types, defaults, required or nullable status, enum values, and nested objects match handlers and schemas.
- Auth requirements, permissions, scopes, headers, tokens, tenancy boundaries, and rate limits match implementation.
- Status codes, error payloads, retry behavior, idempotency keys, and pagination semantics match code and tests.
- API examples are syntactically valid and use current field names, URLs, headers, and payload shapes.
- Versioning and deprecation notes match routing, schema, compatibility code, and release docs.
- Generated docs are traced back to the source that produces them; stale generated artifacts are called out separately from source docs.

## Common Findings

- Docs list an endpoint or field that was removed from the handler.
- OpenAPI examples omit a required auth header or required request field.
- Error documentation says one status code while the handler returns another.
- Pagination, filtering, or sorting behavior is implemented but undocumented.
- SDK examples use old method names or old response shapes.

## Calibration

When implementation and generated spec disagree, identify the source of truth used by users. If the generated spec is published, stale generation can be a user-facing documentation bug even when source schemas are correct.
