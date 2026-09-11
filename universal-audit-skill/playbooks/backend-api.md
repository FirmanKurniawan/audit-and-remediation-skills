# Playbook — Backend / API

Standards: OWASP Top 10:2025, ASVS 5.0, API Security Top 10, CWE Top 25.

## Authorization (the highest-yield area)
- Build an endpoint × role matrix. For every endpoint: who may call it, is that
  enforced, and where?
- **BOLA/IDOR**: every route that takes an object id — is ownership checked, or
  does the query trust the id? Check the query itself, not the controller comment.
- Object *property* level: can a client set fields it should not (mass assignment,
  role escalation via a PATCH body)?
- Function-level: admin routes distinguished only by path obscurity
- Multi-tenant isolation: is the tenant id derived from the token or accepted
  from the request?
- Middleware ordering: an auth middleware registered after the route it protects
- Sub-resources and batch/bulk endpoints, which routinely miss the per-item check

## Authentication and session
- Password hashing algorithm and parameters; legacy hashes still accepted
- Token signature verification, `alg` confusion, expiry, audience, issuer checks
- Session fixation, rotation on privilege change, revocation on logout
- Rate limiting and lockout on login, reset, and OTP endpoints
- Password reset token entropy, single-use, and expiry
- Timing-safe comparison for secrets

## Injection and deserialization
- SQL/NoSQL string concatenation; ORM escape hatches (`raw`, `literal`, `$where`)
- Command execution with interpolated input
- Path traversal in file endpoints; archive extraction (zip slip)
- Template injection (SSTI) in email/report rendering
- Unsafe deserialization (pickle, Java, YAML `load`, PHP `unserialize`)
- SSRF: any server-side fetch of a client-supplied URL — check for allowlisting,
  redirect following, and cloud metadata endpoint reachability
- XXE in XML parsing; entity expansion limits

## Data and secrets
- Secrets in code, config, or environment defaults committed to the repo
- Encryption at rest for sensitive columns; key management
- PII in logs, traces, error responses, and analytics
- Backup and export paths and their access control
- Soft-delete leaving data reachable through another endpoint

## Reliability
- Timeouts on every outbound call; retry policy with backoff and jitter
- Idempotency keys on non-idempotent operations exposed to retry
- Transaction boundaries: partial writes on failure, missing rollback
- Connection pool sizing and exhaustion
- N+1 queries and missing indexes on the hot path
- Unbounded result sets, missing pagination limits
- Background jobs: at-least-once handling, poison messages, dead-letter queues
- Graceful shutdown: in-flight requests, unacked messages

## API design and contracts
- Versioning strategy and breaking-change handling
- Input validation at the boundary with a schema, not ad-hoc checks
- Consistent error model; internal details (stack traces, SQL) leaking to clients
- Content-type confusion, HTTP verb tunnelling
- Resource consumption limits: body size, upload size, query depth (GraphQL),
  complexity limits, batch size

## Observability
- Structured logs with correlation ids across services
- Health checks that actually check dependencies (not `return 200`)
- Metrics for error rate, latency percentiles, saturation
- Alerting on the failure modes discovered in this audit
