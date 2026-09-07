# Mocking, Fixtures, And Snapshots

Mocks and fixtures are useful when they isolate behavior. They become confidence risks when they replace the contract the test is supposed to prove.

## Mocking Risks

- Tests mock the unit under test or the helper that contains the real behavior.
- Assertions verify calls instead of checking state or output.
- Mock responses are simpler than real provider responses, especially for pagination, nulls, errors, nested fields, or partial data.
- Mocks hide serialization, request signing, retry, timeout, or authentication behavior.
- Tests patch global state but do not restore it, creating order dependence.

## Fixture Risks

- Fixtures are so large that expected behavior is hard to inspect.
- Fixture builders default to valid happy-path objects and hide required fields.
- Tests mutate shared fixtures across cases.
- Golden files are regenerated without human-readable diffs or targeted assertions.
- Production-like inputs are absent for known edge cases: empty sets, duplicate rows, timezone boundaries, missing optional fields, and provider error payloads.

## Snapshot Risks

- Snapshot covers a huge output where reviewers cannot see the meaningful contract.
- Snapshot includes volatile fields: timestamps, random IDs, object ordering, absolute paths, or environment-specific values.
- Snapshot is used when a few semantic assertions would be clearer.
- Snapshot update workflow normalizes accepting unrelated changes.

## Better Shapes

- Use contract tests for external clients and adapters.
- Keep unit mocks at service boundaries and assert the observable result after the mocked interaction.
- Build minimal fixtures that make the case readable.
- Split broad snapshots into focused assertions plus small snapshots for stable schemas or rendered structures.
- Add one real integration path when mocks cannot prove serialization, persistence, or provider contract behavior.
