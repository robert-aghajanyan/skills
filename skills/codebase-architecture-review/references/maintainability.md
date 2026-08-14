# Maintainability Review Checks

Apply these checks per review unit and keep only issues backed by observed code.

## Repository Map Evidence

Capture the facts that shape maintainability:

- languages, frameworks, build tools, package managers, deployment targets, and generated-code directories
- main entrypoints, background jobs, CLIs, scripts, scheduled tasks, and event handlers
- shared libraries, adapters, clients, providers, tenants, regions, agents, workflow engines, and plugin points
- test layout and which production units have no direct tests
- runtime configuration and environment-specific branching

## YAGNI

Look for premature generality that already creates cost:

- interfaces with one implementation and no near-term variability in the repo
- config knobs or plugin registries that are not exercised by tests, docs, or production entrypoints
- inheritance or strategy layers that only forward calls
- optional execution paths that are untested, undocumented, or impossible to select
- dead code, unused adapters, stale clients, and compatibility layers with no current caller

Do not flag simple extension points when they protect a real public API, stable domain boundary, or known provider split.

## KISS

Prefer simpler control flow when complexity is not buying resilience:

- deeply nested orchestration that mixes policy, IO, persistence, formatting, and retries
- excessive indirection where call chains obscure the real behavior
- configuration precedence that requires reading many files to predict runtime behavior
- "framework inside the app" patterns where plain functions or small modules would be enough
- dynamic imports, reflection, metaprogramming, or generic dispatch that hides dependencies without clear payoff

Show the shorter path and why it preserves behavior.

## DRY

Flag duplication only when it can diverge into bugs:

- repeated business rules, validation rules, authorization checks, cost formulas, feature flags, retry policies, or serialization rules
- copied client, provider, tenant, region, or agent branches that differ in small, risky ways
- duplicated test fixtures that encode conflicting assumptions
- parallel implementations for CLI, API, batch, and UI paths that should share a core policy module

Do not flag nearby repetition that keeps local code readable or avoids an awkward abstraction.

## SOLID And Boundaries

Use SOLID as evidence language, not as doctrine:

- mixed responsibilities: transport, persistence, policy, orchestration, rendering, and observability in one unit
- dependency direction problems: domain logic importing concrete clients, UI, storage, or deployment code
- oversized interfaces or base classes that force implementations to accept unused behavior
- substitutability risks where implementations violate shared contracts or require caller-specific knowledge
- hidden dependencies through globals, singletons, environment reads, implicit working directories, or module import side effects

Tie each claim to the maintenance risk it creates.

## Coupling, Cohesion, And Evolution Risk

Prioritize code that will make the next change expensive:

- one change requiring edits across many clients, providers, regions, agents, or packages
- shared modules that know too much about downstream product variants
- client or region conditionals embedded deep inside common workflows
- tests that can only exercise small changes through full integration flows
- import cycles, broad public modules, or utility packages that attract unrelated responsibilities

## Testability

Call out testability issues when they block reliable evolution:

- direct network, filesystem, clock, random, environment, or subprocess calls in policy code
- no seam for provider/client/region failures
- brittle setup that requires production-like credentials for ordinary unit tests
- missing edge-case tests around parsing, config precedence, retries, idempotency, and branching logic
- broad snapshot tests that hide behavior changes instead of specifying important contracts
