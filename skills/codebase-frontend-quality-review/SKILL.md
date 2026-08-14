---
name: codebase-frontend-quality-review
description: Review frontend codebases for user-facing quality, accessibility, responsive behavior, state correctness, visual regressions, routing issues, form behavior, and interaction quality. Use when the user asks for frontend quality review, UI review, accessibility review, responsive review, visual regression risk, loading/error states, form UX, state bugs, routing bugs, or frontend maintainability.
---

# Frontend Quality Review

Review whether the frontend works correctly for real users across realistic states, data conditions, permissions, and viewports.

## Instructions

Start by building a frontend map. If useful, run the read-only helper:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/frontend_inventory.py" <repo>
```

Use the helper as a starting point only. Validate important claims by reading the frontend code, routes, component state, API clients, styles, tests, and available preview tooling.

- For accessibility checks, see [references/accessibility.md](references/accessibility.md).
- For responsive layout checks, see [references/responsive-layout.md](references/responsive-layout.md).
- For state, data, and routing checks, see [references/state-and-routing.md](references/state-and-routing.md).
- For form behavior checks, see [references/forms.md](references/forms.md).
- For loading, error, empty, disabled, and permission states, see [references/loading-error-empty-states.md](references/loading-error-empty-states.md).
- For visual regression review and screenshot strategy, see [references/visual-regression.md](references/visual-regression.md).
- For the expected report shape, see [references/output-format.md](references/output-format.md).

## Default Workflow

1. Map the frontend: framework, routes/pages, layouts, components, state stores, forms, API clients, design system, styling approach, tests, Storybook or preview tooling, and build commands.
2. Review user-facing behavior: loading states, empty states, error states, disabled states, optimistic updates, stale data, route transitions, auth states, permission states, and offline or slow-network behavior.
3. Review accessibility: semantic structure, keyboard navigation, focus management, labels, ARIA use, contrast, reduced motion, screen-reader affordances, modal behavior, and form errors.
4. Review responsive behavior: mobile, tablet, and desktop layout, overflow, text clipping, fixed dimensions, sticky elements, tables, navigation, dialogs, and touch targets.
5. Review frontend correctness: state synchronization, stale closures, races, duplicate requests, validation drift, route guards, cache invalidation, and client/server contract mismatches.
6. If a dev server can run, verify with browser screenshots, interaction checks, accessibility tooling, or UI tests where practical. If it cannot run, state the limitation clearly.
7. Report findings with affected file or component, user-visible failure mode, reproduction path or state, severity, recommended fix, and validation method.

## Calibration

Prioritize issues users can experience. Do not pad the report with generic UI advice. A finding should name the broken state, viewport, route, component, interaction, or assistive technology path.

## Gotchas

- Static code review misses layout, focus, and timing bugs. Use screenshots or UI tests when the app can run.
- A polished happy path is not enough. Check slow data, failed data, empty data, denied permissions, expired auth, and repeated interactions.
- Screenshot diffs can hide accessibility and state defects. Pair visual review with keyboard, form, and data-state checks.
- Treat design-system components as shared blast-radius surfaces; one broken primitive can affect many pages.
