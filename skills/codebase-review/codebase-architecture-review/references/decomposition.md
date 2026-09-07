# Decomposition Review Checks

Use decomposition recommendations sparingly. A good recommendation explains the boundary and a safe migration path, not just that a file is large.

## Decomposition Signals

Investigate units with:

- large files, classes, or functions plus multiple reasons to change
- high conditional density, especially by client, region, tenant, provider, mode, or agent
- orchestration code that also owns policy decisions, persistence, transport, rendering, or notifications
- shared libraries that import app-specific modules or concrete runtime clients
- duplicated business rules across API, CLI, worker, batch, and UI code paths
- tests that require unrelated infrastructure because small behavior is not isolated
- generated code mixed with hand-written logic

Large size alone is a triage signal, not a finding.

## Boundary Patterns

Prefer boundaries that reflect real change axes in the repo:

- `domain` or `policy`: pure business rules, validation, calculations, eligibility, and decision records
- `adapters`: provider/client/tenant/region-specific IO behind narrow contracts
- `orchestration`: workflow sequencing, retries, compensation, and progress tracking
- `persistence`: storage models, repositories, migrations, and transaction handling
- `transport`: HTTP, CLI, queue, event, or UI-specific request/response shaping
- `rendering`: reports, email, HTML, templates, charts, and presentation logic
- `config`: parsing, precedence, defaults, and runtime environment validation
- `agents` or `workflows`: agent roles, tool routing, prompt assembly, and state transitions

Avoid moving code into generic `utils`, `common`, or `helpers` modules unless the extracted behavior has a narrow, named responsibility.

## Recommendation Template

For each decomposition candidate, include:

```markdown
### [Candidate Name]

- Current problem: [specific observed code and why it is hard to change]
- Proposed boundary: [new responsibility split]
- Suggested layout:
  - `path/to/new_module.py`: [responsibility]
  - `path/to/existing_module.py`: [remaining responsibility]
- Incremental migration:
  1. [small behavior-preserving step]
  2. [next step]
  3. [cleanup step]
- Behavior-preservation tests: [existing or new tests that prove no behavior drift]
- Risk of doing it now: [merge/conflict/runtime risk]
- Risk of not doing it: [specific future-change or defect risk]
```

## When Not To Decompose

Put justified non-changes in the do-not-change section:

- generated files or vendored code where edits should occur upstream
- cohesive modules that are large because they encode one table, grammar, schema, or protocol
- local duplication that keeps two simple workflows independent
- stable compatibility layers with real external callers
- hot paths where abstraction would add measurable overhead or obscure performance-critical behavior

## Migration Safety

Prefer behavior-preserving steps:

- extract pure functions before changing callers
- introduce narrow adapter interfaces around existing concrete clients before swapping implementations
- move tests first when they define contracts already relied on by multiple units
- keep old public entrypoints as forwarding shims until callers are migrated
- add characterization tests before touching risky legacy logic
- avoid broad renames and layout rewrites in the same change as behavior fixes
