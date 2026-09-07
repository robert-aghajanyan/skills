# Output Format

Use this structure for frontend quality review reports.

## Frontend Map

Summarize framework, package manager, routes/pages, layouts, major components, state stores, API clients, forms, styling/design system, tests, Storybook or preview tooling, build commands, and how the app can be run.

## Findings Ordered By User Impact

For each finding include:

- Severity: Blocker, High, Medium, or Low.
- Affected file/component.
- User-visible failure mode.
- Reproduction path or state.
- Recommended fix.
- Validation method.

## Accessibility Issues

List accessibility findings separately when useful. Include keyboard, focus, semantic, label, ARIA, contrast, reduced-motion, dialog, and screen-reader risks.

## Responsive/Layout Issues

List viewport-specific defects, overflow, clipping, sticky/fixed element problems, mobile navigation issues, table/chart behavior, dialog fit, and touch-target problems.

## State/Routing/Form Issues

List stale state, races, duplicate requests, route guard defects, cache invalidation gaps, form validation drift, duplicate submit, and client/server contract mismatches.

## Missing States

Name missing loading, empty, error, disabled, permission, auth, offline, slow-network, optimistic, conflict, and partial-data states. Tie each missing state to a concrete route, component, or workflow.

## Visual Verification Notes

State whether a dev server, browser screenshots, UI tests, accessibility tools, or Storybook were used. If not, state the limitation and what review evidence replaced it.

## Test Recommendations

Recommend focused tests that would catch the reported defects. Prefer repo-native tools and small coverage additions over broad test rewrites.

## Commands Run

List commands and outcomes, including failed commands and environment limitations.
