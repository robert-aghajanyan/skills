---
name: codebase-test-quality-review
description: Reviews test suites for regression-catching value, risk coverage, flaky behavior, weak assertions, over-mocking, and CI confidence. Use when the user asks to review tests, improve test quality, find missing coverage, assess flaky tests, check whether tests catch regressions, or identify high-risk code paths without meaningful tests.
---

# Test Quality Review

Review whether a repository's tests would catch real regressions, not just whether tests exist or coverage is high.

## Instructions

Start by building a test map and risk map. If useful, run the read-only helper:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/test_inventory.py" <repo>
```

Use the helper as a starting point only; validate important claims by reading the production and test code.

- For prioritizing risky behavior, see [references/test-risk-model.md](references/test-risk-model.md).
- For weak or misleading assertions, see [references/assertion-quality.md](references/assertion-quality.md).
- For mocks, fixtures, snapshots, and generated data, see [references/mocking-fixtures.md](references/mocking-fixtures.md).
- For timing, ordering, randomness, and isolation risks, see [references/flakiness.md](references/flakiness.md).
- For coverage gaps that matter, see [references/coverage-gaps.md](references/coverage-gaps.md).
- For the report shape, see [references/output-format.md](references/output-format.md).

## Default Workflow

1. Map languages, package managers, frameworks, test commands, CI test jobs, coverage tools, source directories, test directories, fixtures, snapshots, mocks, and integration setup.
2. Identify high-risk production behavior: auth, permissions, money or cost logic, transformations, persistence, external clients, async jobs, concurrency, retries, errors, config, migrations, CLI/API contracts, and user-visible outputs.
3. Compare the tests against those risks. Focus on whether the current assertions would fail if important behavior regressed.
4. Report findings with the affected production file, test file if present, behavior at risk, why current tests miss it, recommended test shape, test type, and minimal cases.
5. If asked to edit, add the smallest deterministic tests first, reuse repo-native helpers, and run focused tests plus the relevant broader test command.

## Calibration

Before finalizing, remove generic advice. Every recommendation must name the regression it would catch.

## Gotchas

- High line coverage can still miss broken behavior when assertions only check status codes, mocks, snapshots, or no exception thrown.
- Do not demand tests for every uncovered line; prioritize uncovered branches that carry product, operational, security, financial, or data-loss risk.
- Integration tests matter when unit tests replace the real contract with mocks, especially for persistence, serialization, external clients, CLIs, and queues.
- Preserve valuable existing tests even if they are imperfect; recommend rewrites only when the current shape creates real confidence risk.
