# Security Baseline

Include security observations only when they are visible while reviewing architecture and maintainability. If the user's main request is security-focused, recommend a dedicated security review.

## Baseline Checks

Look for architecture-level security risks:

- authentication or authorization decisions scattered across handlers, workers, clients, or UI code
- tenant, client, provider, or region isolation implemented with ad hoc conditionals instead of a consistent policy boundary
- secrets read from many places, logged, passed through generic config objects, or mixed into generated artifacts
- input parsing, path handling, URL fetching, shell execution, or deserialization embedded in business logic
- missing validation boundaries between transport models, persistence models, and domain objects
- dependency, plugin, or generated-code surfaces that execute untrusted code or data
- logs and error paths that can expose tokens, user data, customer identifiers, or internal topology

## Reporting Rules

- Cite the exact file and line where the security-relevant architecture risk appears.
- Explain the maintainability connection, such as duplicated authorization rules or unclear tenant boundaries.
- Avoid exploit speculation unless the code path and input source are both visible.
- Separate baseline observations from deep vulnerability findings.

## Useful Recommendations

Prefer architecture changes that reduce future security drift:

- centralize authorization or tenant checks behind a small policy module
- separate transport input validation from business decisions
- make secret/config loading explicit at process boundaries
- use typed domain objects or schemas between untrusted input and internal logic
- add tests that prove cross-tenant, cross-client, or cross-region boundaries cannot be bypassed
