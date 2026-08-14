# Multitenancy And Isolation Checks

Use this reference when code has tenants, orgs, users, accounts, workspaces, projects, environments, regions, customers, providers, or delegated access.

## Boundary Inventory

- Name the isolation unit: tenant, org, user, workspace, project, account, region, environment, provider, or customer.
- Identify how the boundary is represented: token claims, session fields, request headers, route params, database columns, cache keys, object names, storage prefixes, queue topics, and service-account scopes.
- Trace who can set each boundary value and where it is revalidated.

## Common Failure Modes

- IDOR: object fetched by ID without also scoping by owner, tenant, project, or workspace.
- Query scope loss: helper functions, repository methods, background jobs, exports, counts, search, autocomplete, or joins omit tenant filters.
- Cache bleed: cache keys lack tenant/user/project dimensions or use unstable display names instead of canonical IDs.
- Storage bleed: object storage prefixes, local paths, report names, temp files, or archive names omit the isolation key.
- Queue and worker confusion: messages trust tenant IDs from payloads without verifying against the actor or source.
- Admin confusion: admin endpoints reuse user paths, impersonation lacks explicit scope/audit, or support tools can act across tenants without guardrails.
- Cross-region or cross-environment leakage: prod/dev, region, provider, or account boundaries are inferred from names instead of policy.
- Error and timing leaks: existence checks reveal objects across tenants through status codes, messages, counts, or timing.

## Review Pattern

For each sensitive operation, verify:

1. The actor identity is authenticated.
2. The operation-level permission is checked.
3. The target resource is scoped to the actor's tenant or delegated scope.
4. All reads, writes, exports, logs, caches, and async side effects preserve that scope.
5. Deny behavior is closed and audited where appropriate.

## Negative Tests

- Tenant A cannot fetch, update, delete, export, search, count, or infer Tenant B records.
- A valid ID from another tenant is denied even when the actor has the same role in their own tenant.
- Cached or generated artifacts created by Tenant A are not visible to Tenant B.
- Background jobs reject forged tenant IDs or resource IDs not tied to the job owner.
