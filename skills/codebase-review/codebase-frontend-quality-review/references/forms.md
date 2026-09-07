# Forms Review

Use this reference when reviewing data entry, validation, submission, and edit workflows.

## Form Map

For each meaningful form, identify:

- Route or component.
- Fields, defaults, required markers, validation rules, helper text, and error text.
- Client validation library or hand-written validation.
- Server action or API endpoint.
- Submit, cancel, reset, save draft, destructive actions, and navigation-away behavior.
- Success, pending, validation error, server error, conflict, permission denied, and retry states.

## What To Inspect

- Labels and descriptions are programmatically connected. Placeholder text is not the only label.
- Required and optional states are clear and consistent with server validation.
- Submit is disabled only when it should be, and pending state prevents duplicate writes without trapping the user.
- Errors are specific, near the field when field-specific, summarized when useful, and announced for assistive tech.
- Server-side errors, conflicts, expired auth, rate limits, and network failures remain recoverable.
- Inputs preserve user-entered values across validation errors and accidental re-renders.
- Keyboard flow, Enter/Escape behavior, tab order, focus on first invalid field, and focus after successful submit are deliberate.
- Autocomplete, input type, masks, locale, time zone, numeric precision, and date handling match the data domain.
- File uploads show type, size, progress, cancel, retry, and failure behavior where applicable.

## Common Failure Modes

- Client and server validation drift.
- Double submit creates duplicate records or repeated side effects.
- Cancel or route change loses unsaved edits without warning when data loss is likely.
- Field arrays or dynamic sections lose values after add, remove, reorder, or failed submit.
- Date, currency, percentage, and time-zone values render differently than they submit.

## Validation Recommendations

For important forms, recommend tests that submit valid data, invalid client data, server-rejected data, duplicate submit attempts, edit flows with existing data, and keyboard-only completion.
