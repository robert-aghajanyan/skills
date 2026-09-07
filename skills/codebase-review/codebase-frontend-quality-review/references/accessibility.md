# Accessibility Review

Use this reference when reviewing semantic HTML, keyboard behavior, focus, screen-reader affordances, and form or dialog accessibility.

## What To Inspect

- Landmarks, heading order, page titles, lists, tables, buttons, links, and form elements use native semantics before ARIA.
- Interactive elements are keyboard reachable, have visible focus, activate with expected keys, and do not trap focus except inside active dialogs.
- Route changes, modal open/close, drawers, menus, tabs, toasts, validation errors, and async updates manage focus deliberately.
- Controls have stable accessible names. Labels, descriptions, required indicators, helper text, and error text are programmatically connected.
- ARIA is accurate and necessary: no fake buttons, invalid roles, stale `aria-expanded`, detached `aria-controls`, or live regions that spam users.
- Color contrast supports normal text, large text, icons, disabled states, focus rings, selected states, charts, and status badges.
- Motion respects reduced-motion settings. Autoplay, shimmer, scrolling, and animation do not block comprehension or interaction.
- Dialogs expose title, description when useful, focus trap, Escape and close behavior, inert background, and return focus to the opener.

## Review Technique

Use keyboard-only navigation through core workflows. If the app can run, combine manual keyboard checks with available tooling such as axe, eslint-plugin-jsx-a11y, Playwright accessibility checks, Storybook a11y, or browser devtools.

For each issue, capture the assistive path: route, component, state, input method, and what a keyboard or screen-reader user cannot do or understand.

## Common High-Impact Failures

- Clickable `div` or icon-only buttons without accessible names.
- Error messages shown visually but not announced or associated with the invalid field.
- Modals that allow background tabbing or lose focus when content updates.
- Custom selects, comboboxes, tabs, menus, and accordions missing expected keyboard behavior.
- Focus disappearing after route transitions, optimistic updates, filtering, pagination, or dialog close.
- Placeholder-only labels, ambiguous link text, and status colors with no text alternative.
