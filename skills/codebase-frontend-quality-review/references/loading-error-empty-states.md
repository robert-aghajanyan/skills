# Loading, Error, Empty, And Disabled States

Use this reference when reviewing non-happy-path UI states.

## Required State Coverage

For each primary route or workflow, look for:

- Initial loading, background refetch, slow network, partial data, and skeleton or spinner behavior.
- Empty data with clear next action when an action exists.
- Recoverable error with retry or navigation path.
- Permission denied, unauthenticated, expired session, and feature unavailable states.
- Disabled, pending, saving, deleting, uploading, optimistic, conflict, and cancelled states.
- Offline or flaky-network behavior when the product can reasonably encounter it.

## Quality Bar

- State text and actions match the actual condition. Do not show a generic failure for auth, permission, validation, or not-found errors.
- Loading states preserve layout enough to avoid disorienting shifts.
- Empty states do not hide filters, navigation, creation actions, or context needed to recover.
- Error states expose useful recovery paths without leaking internal details.
- Disabled controls explain why when the reason is not obvious.
- Optimistic updates roll back or reconcile after failure.
- Background refetch does not wipe useful content or reset user input.

## Common Failure Modes

- Infinite spinner when a request fails or is skipped by missing params.
- Blank page because error boundaries or nullable data paths are missing.
- Empty state shown while filters are still loading, misleading users into thinking no data exists.
- Stale previous route data displayed under the new route title.
- Deleting or saving state blocks unrelated actions indefinitely after an exception.
- Permission errors treated as not found, causing confusing navigation loops.

## Review Technique

If the app can run, simulate slow network or mocked API states where practical. Otherwise inspect query/mutation code, error boundaries, API client error normalization, and route-level conditional rendering.
