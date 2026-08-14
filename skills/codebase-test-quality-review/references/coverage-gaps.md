# Coverage Gaps

Use coverage as a clue, not a conclusion. The review should identify important untested behavior, not chase every uncovered line.

## Meaningful Gap Patterns

- High-risk branches lack negative, boundary, or error-path tests.
- Public entrypoints have unit tests for helpers but no contract tests for the API, CLI, worker, or adapter.
- New production files have no nearby tests and no higher-level tests that exercise them.
- Tests cover parsing of valid input but not malformed, missing, duplicate, empty, or oversized input.
- Retry and fallback logic is tested only for success.
- Migrations, config precedence, and environment defaults are untested.
- Data transformations are tested with one fixture that cannot catch sorting, filtering, grouping, or rounding regressions.

## How To Avoid Noise

- Do not report untested logging-only branches unless logs are contractual or operationally critical.
- Do not demand direct tests for pass-through wrappers when a higher-level contract test proves behavior.
- Do not require tests for generated code unless local customization creates risk.
- Prefer one integration test over many brittle unit tests when the risk is in wiring, serialization, or persistence.

## Traceability Check

For every recommended test, answer:

- What production behavior could regress?
- Which current test would still pass?
- What minimal test would fail on that regression?
- Why is unit, integration, contract, property-based, regression, or end-to-end coverage the right shape?
