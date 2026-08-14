# Web And API Checks

Use this reference for HTTP APIs, web apps, RPC services, webhooks, gateway handlers, and service-to-service endpoints.

## Route And Middleware Mapping

- Enumerate routes and handlers from framework declarations, router registration, OpenAPI specs, generated clients, gateway config, and reverse-proxy rules.
- Verify middleware order. Auth, tenant scope, body size limits, CSRF protections, and input validation must run before handlers and dangerous sinks.
- Check route precedence and wildcard patterns for shadow routes, public aliases, trailing slash differences, method confusion, and admin route exposure.
- Confirm internal-only routes are actually protected by network policy, auth, or deployment config. Mark as conditional if the repo lacks that evidence.

## Auth And Authorization

- Authentication bypass: missing middleware, optional auth treated as sufficient, unsigned or weakly verified tokens, stale sessions, trust in user-controlled headers, and dev-only bypasses enabled outside tests.
- Authorization confusion: role checks that do not include object ownership, project scope, tenant scope, environment scope, or operation-level permission.
- IDOR and confused deputy: user-supplied IDs, URLs, account IDs, workspace IDs, or provider resource names used by a privileged service without re-checking ownership.
- Admin and service accounts: overbroad tokens, impersonation without audit, break-glass paths, background jobs acting on user-controlled resources, and missing deny paths.

## Input To Sink Risks

- Injection: SQL, NoSQL, LDAP, shell, template, expression language, GraphQL, XPath, log injection, and header injection. Prefer parser/parameterized API evidence over string concatenation heuristics.
- SSRF: user-controlled URLs, redirects followed by default, metadata service access, DNS rebinding, internal host allowlists, proxy support, file schemes, and cloud credential endpoints.
- Path traversal: user-controlled paths, archive extraction, symlink handling, path normalization, prefix checks before normalization, URL-decoded separators, and platform path differences.
- Unsafe deserialization: pickle, marshal, YAML unsafe loaders, Java serialization, PHP unserialize, object hooks, dynamic class loading, and untrusted cache payloads.
- Command execution: shell=True, child_process with shell, exec/eval, build scripts, templated command arguments, and environment injection.
- File uploads: content type trust, extension checks, size limits, archive bombs, malware scanning expectations, public readback, path generation, and metadata parsing.

## Web-Specific Controls

- CSRF: state-changing cookie-authenticated routes need CSRF tokens, same-site controls, or equivalent protection.
- CORS: avoid reflecting arbitrary origins with credentials; confirm preflight and credential behavior.
- Cookies and sessions: secure, httponly, samesite, expiration, rotation, logout invalidation, and session fixation.
- Redirects: user-controlled redirect targets need strict allowlists.
- Error handling: avoid leaking stack traces, tokens, internal URLs, tenant IDs, SQL, or policy decisions.

## Negative Tests

Prefer tests that prove the boundary:

- unauthenticated request receives deny status;
- low-privileged user cannot access another user's object;
- tenant A cannot read, write, export, or infer tenant B data;
- malicious URL cannot reach localhost, metadata IPs, private ranges, or file schemes;
- traversal payload cannot escape the intended root;
- injected query, template, or shell metacharacters are handled as data.
