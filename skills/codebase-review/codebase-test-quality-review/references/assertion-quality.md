# Assertion Quality

Good tests fail when user-visible or system-visible behavior is wrong. Weak tests execute code but do not prove the important outcome.

## Strong Assertions

- Check observable output: returned value, persisted state, emitted event, generated file, response schema, status code plus body, CLI exit code plus stdout/stderr.
- Verify business invariants, not just one fixture value.
- Include negative, boundary, and malformed inputs where those cases are risky.
- Assert error type, message, status, retry behavior, or fallback behavior when callers depend on it.
- For data transforms, assert the full relevant record set, ordering if contractually meaningful, and exclusion of invalid rows.

## Weak Assertions To Flag

- "Does not throw" tests for behavior that should produce a specific result.
- Assertions that only check truthiness, non-null values, length greater than zero, or snapshot existence.
- Tests that only verify a mock method was called without validating the resulting behavior.
- Tests that assert private method calls, internal branches, or implementation details that can change while behavior remains correct.
- Golden snapshots that are too broad to review or that include volatile data.
- Tests where the assertion duplicates the implementation formula instead of checking an independent expected outcome.

## Review Questions

- If the core logic returned the wrong value, would this test fail?
- If a dependency returned an error or malformed response, would the test prove the caller handles it?
- If the implementation changed but the contract stayed the same, would the test fail unnecessarily?
- Does the expected value come from a human-readable fixture or independent calculation?

When recommending a better test, name the exact assertion that should become stronger.
