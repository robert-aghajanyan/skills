# Responsive Layout Review

Use this reference when reviewing mobile, tablet, desktop, and edge-case viewport behavior.

## Viewports

Prefer the app's own breakpoints when available. Otherwise use a practical matrix:

- Mobile narrow: 360 x 740
- Mobile common: 390 x 844
- Tablet portrait: 768 x 1024
- Tablet or small desktop: 1024 x 768
- Desktop: 1440 x 900
- Wide desktop if the product uses dense data views

Also test zoom or larger text when accessibility risk is likely.

## What To Inspect

- No unintended horizontal scrolling, clipped text, hidden controls, overlapping elements, or viewport-width font scaling.
- Navigation remains usable: sidebars, drawers, breadcrumbs, tabs, top bars, command bars, and account menus.
- Tables, grids, charts, code blocks, and long labels have a deliberate mobile treatment.
- Sticky or fixed headers, footers, filters, and action bars do not cover content, dialogs, or focused inputs.
- Dialogs, popovers, menus, tooltips, and date pickers fit in the viewport and remain reachable by keyboard and touch.
- Touch targets are comfortably sized and spaced, especially icon buttons, row actions, checkboxes, and drag handles.
- Empty, loading, and error states preserve layout instead of causing jumps that hide actions or content.

## Review Technique

Use real screenshots when a dev server can run. Capture before and after key interactions such as opening navigation, filtering, editing forms, expanding rows, opening dialogs, and triggering validation errors.

When the app cannot run, inspect CSS for brittle patterns: fixed pixel widths, unbounded `min-width`, viewport-height containers, absolute positioning, table overflow, hidden overflow used to mask problems, and breakpoint-specific duplicated markup.

## Severity Signals

Raise severity when layout defects block primary actions, hide data, make navigation unreachable, break forms, or affect common mobile/tablet sizes. Cosmetic spacing drift is lower severity unless it indicates an unstable layout primitive.
