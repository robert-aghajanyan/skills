# Visual Regression Review

Use this reference when reviewing screenshot coverage, visual stability, and regression risk.

## What To Inspect

- Routes or components with high user impact, dense data, critical forms, dialogs, charts, or custom layout primitives.
- States that screenshots often miss: loading, empty, error, permission denied, validation error, long text, many rows, no rows, one row, narrow viewport, and high zoom.
- Shared components: buttons, inputs, select controls, modals, menus, tables, cards, toasts, banners, nav, and design-system tokens.
- Asset loading: fonts, icons, images, charts, maps, and canvas content render consistently.
- Theming: light/dark mode, brand tokens, status colors, disabled states, focus rings, and contrast.

## Screenshot Strategy

When a dev server can run, capture screenshots for the smallest set of routes and states that cover the risky surface. Prefer deterministic data, fixed time, stable viewport sizes, and animation disabled where possible.

Pair screenshots with interaction checks. A screenshot can pass while keyboard focus, submit behavior, or stale state is broken.

## Common Failure Modes

- Text clips or overlaps only with realistic long labels, translated strings, user names, IDs, or error messages.
- Layout jumps between loading and loaded states.
- Sticky headers or action bars cover focused content.
- Modal content overflows on mobile or high zoom.
- Chart, table, or card components become unreadable in empty or dense states.
- Visual tests cover only Storybook happy paths, not routed product workflows.

## Validation Recommendations

Recommend Playwright, Cypress component tests, Storybook visual tests, Percy, Chromatic, Loki, or repo-native tooling only when it fits the existing stack. Tie each proposed screenshot to a user-visible regression it would catch.
