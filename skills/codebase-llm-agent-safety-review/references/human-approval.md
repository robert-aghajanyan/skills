# Human Approval

Human approval is a safety control only when it happens before the side effect, is bound to the exact action, and cannot be spoofed by model text or untrusted content.

## Actions That Usually Need Approval

- deleting, overwriting, publishing, merging, deploying, purchasing, billing, permission changes, account changes, or infrastructure changes;
- sending data to external recipients, webhooks, plugins, MCP servers, public comments, or third-party APIs;
- running shell commands, generated code, migrations, browser actions on authenticated sites, or broad file operations;
- persisting long-term memory from sensitive or untrusted content;
- changing policies, allowlists, credentials, tenant settings, or automation schedules.

## Review Checks

- Approval must occur before the irreversible or external action.
- Approval text must show the exact action, target, destination, data class, and requester.
- The approval decision must be represented as trusted UI or server-side state, not a model-generated phrase.
- Changing action arguments after approval must invalidate the approval.
- Automation and background jobs need equivalent policy gates, not only interactive prompts.
- Failed, interrupted, ambiguous, or missing approval must fail closed.
- Audit logs should capture who approved what, when, and which tool/action was executed.

## Weak Patterns

- The model asks itself whether an action is safe.
- A prompt says "ask for approval" but the tool can still run without checking approval state.
- Approval is collected after the side effect for logging only.
- A user or retrieved document can include text that looks like approval.
- Approval covers a broad class of future actions without scope, TTL, or revocation.

## Probes

- Attempt a side effect with no approval, stale approval, modified arguments, and spoofed approval text.
- Try approval for one target and execution against another target.
- Interrupt or timeout the approval prompt and confirm execution stops.
- Run the same path through scheduled automation or API mode and confirm gates still apply.
