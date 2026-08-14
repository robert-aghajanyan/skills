# Finding Ledger

Use one ledger row per confirmed or plausible finding.

Required fields:

- `id`: stable local id such as `SEC-001` or `TEST-003`.
- `source_skill`: originating skill name.
- `title`: concise issue-style title.
- `severity`: `Blocker`, `High`, `Medium`, `Low`, or `Nit`.
- `confidence`: `High`, `Medium`, or `Low`.
- `category`: security, reliability, performance, cleanup, tests, docs, API contract, data correctness, frontend, dependency, LLM-agent, architecture, or DX.
- `affected_files`: files and line numbers when known.
- `evidence`: concrete code/config/test/doc evidence.
- `impact`: user, production, developer, security, cost, compatibility, or correctness impact.
- `recommendation`: smallest useful fix.
- `validation`: tests, commands, repro, audit, screenshot, or manual verification needed.
- `issue_candidate`: `yes`, `no`, or `needs-confirmation`.
- `labels`: suggested GitHub labels.
- `related_findings`: ids that may share a root cause.

Severity guidance:

- `Blocker`: exploitable security issue, data loss, production outage risk, broken release path, or severe correctness break.
- `High`: likely user-visible, security, correctness, compatibility, or production risk.
- `Medium`: important maintainability or reliability issue with plausible impact.
- `Low`: cleanup, documentation, or improvement with limited immediate risk.
- `Nit`: minor issue that should not usually become a GitHub issue.

Confidence guidance:

- `High`: directly evidenced by code/config/tests/docs and likely reproducible.
- `Medium`: strong evidence but needs one missing runtime or domain confirmation.
- `Low`: plausible concern without enough evidence for an issue.

Only `High` or `Medium` confidence findings should become issue candidates by default.
