# Risk Surface Checklist

Use this when the production-readiness target is broad, high-impact, or intended to generalize beyond one case.

Check whether the change touches:

- shared libraries, helper modules, or reusable workflows
- public APIs, CLIs, plugin contracts, schemas, prompts, or generated artifacts
- validation, normalization, parsing, filtering, or matching logic
- auth, authorization, secrets, tokens, credentials, or tenant boundaries
- environment loading, feature flags, rollout controls, or kill switches
- cost, billing, forecasting, financial, or reporting calculations
- async jobs, retries, timeouts, locking, concurrency, or caching
- deployment config, runtime dependencies, external APIs, or network assumptions
- observability, audit trails, error messages, alerts, or support diagnostics
- docs, wiki, memory, runbooks, or leadership-facing artifacts

For each risky surface, require direct proof:

| Surface | Required proof |
|---|---|
| Validation or parsing | malformed, boundary, and bypass cases |
| Shared helper | at least two callers or fixture families |
| Runtime dependency | smoke check or explicit unavailable-runtime caveat |
| Reporting or finance logic | fixture-backed expected values or reconciliation |
| Deployment config | live config check, dry run, or explicit rollout caveat |
| Docs or memory | validation command or file-level consistency check |
