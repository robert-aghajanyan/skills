# State And Routing Review

Use this reference for client state, server cache, route behavior, auth and permission flows, and data synchronization.

## What To Inspect

- Route definitions, nested layouts, route guards, redirects, deep links, query params, hash links, and back/forward behavior.
- Auth states: anonymous, loading session, expired session, logged-in user, denied permission, changed role, and logout.
- Server data state: cache keys, invalidation, refetch triggers, stale data, pagination, filters, sorting, optimistic updates, retries, and deduplication.
- Local state: derived state drift, duplicated source of truth, stale closures, effect dependency gaps, unmounted updates, race conditions, and debounce or throttle cleanup.
- Route transitions: previous page data does not flash as the next page, pending navigation is visible when needed, focus and scroll behavior are deliberate.
- API contracts: frontend assumptions match server status codes, response shapes, nullable fields, error payloads, pagination metadata, and permission responses.

## Framework Cues

- React: inspect `useEffect` dependencies, stale callbacks, derived state, context blast radius, uncontrolled-to-controlled transitions, Suspense boundaries, query keys, and mutation invalidation.
- Vue: inspect watcher cleanup, computed state drift, route guards, store subscriptions, and stale refs.
- Svelte: inspect store subscriptions, reactive statement ordering, load functions, invalidation, and route data reuse.
- Next.js or Remix: inspect server/client component boundaries, hydration, data loaders/actions, redirects, error boundaries, and cache policy.

## Common Failure Modes

- Duplicate requests on mount, filter changes, or route transitions.
- Optimistic UI that never rolls back after failure.
- Race where slow earlier request overwrites newer data.
- Route guard that flashes restricted content before redirecting.
- Search, sort, pagination, or filters lost on back navigation or deep links.
- Cache invalidation that leaves stale rows, counts, badges, or detail pages.
- Client validation accepts input that the server rejects, or the reverse.

## Review Technique

Trace representative workflows from route entry through API calls, state updates, rendering, mutation, invalidation, and navigation away. For each finding, name the state transition that breaks and the user-visible result.
