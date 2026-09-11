# Phase 5 — Deep Analysis

**Goal:** find real defects along the critical paths. Load only the playbooks for
platforms detected in Phase 1, plus the universal section below.

Playbooks: `playbooks/web-frontend.md`, `backend-api.md`, `mobile.md`,
`desktop.md`, `hybrid-crossplatform.md`, `embedded-iot.md`, `data-ml-ai.md`,
`infra-devops.md`.

## 5.1 Universal defect classes

Work through these against the critical paths, not against the whole tree.

**Correctness** — off-by-one, wrong operator, inverted condition, wrong default,
unhandled enum case, silent type coercion, timezone and locale handling,
floating-point money, string/byte length assumptions, pagination boundaries.

**Error handling** — swallowed exceptions, `catch` that logs and continues into a
broken state, error paths that leak internals to the user, retries on
non-idempotent operations, missing cleanup on the failure branch, errors that
cannot be distinguished by the caller. (OWASP Top 10:2025 added a category for
mishandling exceptional conditions — treat this as first-class, not cosmetic.)

**Concurrency** — shared mutable state without synchronization, check-then-act
races, work that outlives its owner, cancellation not propagated, double-start of
a background loop, callbacks firing after teardown, deadlock ordering, blocking
calls on a latency-critical thread, unbounded parallelism, non-atomic
read-modify-write on flags that gate physical or financial actions.

**Lifecycle** — initialization order, teardown that misses a resource,
re-entrancy on restart, state restored inconsistently after process death or
reload, listeners registered more than once, singletons that outlive their config.

**Resources** — file handles, sockets, cursors, native buffers, timers,
subscriptions, event listeners, thread pools, and connections that are opened on
one path and closed on only some paths. Look specifically at early-return and
exception branches.

**State integrity** — the UI, the cache, and the source of truth disagreeing;
optimistic updates never reconciled; stale writes overwriting fresh ones; missing
idempotency keys; no single source of truth for connection/session state.

**Input handling** — every boundary crossing needs validation: empty, oversized,
truncated, malformed encoding, unexpected type, injected control characters,
out-of-range numerics, duplicate or replayed messages, and messages arriving in
an unexpected order or from an unexpected peer.

**Time and resilience** — missing timeouts, infinite retry, retry without
backoff or jitter, reconnect storms, no circuit breaker, no bound on queue growth,
no degradation path when a dependency is down.

**Observability** — failures that are invisible, logs without correlation ids,
logs that contain secrets or PII, metrics that cannot answer "is it working right
now", and errors surfaced only as a crash.

## 5.2 Boundary analysis for any parser or deserializer

Run each of these mentally against the implementation and record the outcome:
empty input · single byte · truncated mid-field · length field larger than buffer ·
length field negative or overflowing · unknown type/opcode · nested depth ·
duplicate fields · invalid UTF-8 · maximum-size input · input from an unexpected
source · replayed input · interleaved sessions.

## 5.3 Recording findings

This phase owns the ledger. Append one JSON object per finding to
`.audit/findings.jsonl` against `references/evidence-contract.md` (machine-readable
form: `schemas/finding.schema.json`). Later phases append through the same
contract; none of them keeps a private list.

Assign `BUG-001`, `BUG-002`, … in discovery order and never renumber. Compute the
fingerprint — do not author it:

```bash
python3 scripts/detect-duplicate-findings.py --findings .audit/findings.jsonl
python3 scripts/validate-findings.py --findings .audit/findings.jsonl
```

Run both after every few findings rather than once at the end. A schema error
found at finding 4 costs a minute; found at finding 40 it costs an hour, and the
temptation to paper over it is exactly what the contract exists to prevent.

Three rules that decide most records:

- **CWE** is required for `security`, `privacy` and `supply_chain` classes, and
  should be left empty for ordinary functional defects. A forced mapping is worse
  than none.
- **EPSS and KEV** are only meaningful with a real CVE. On a first-party source
  defect they are `Not Applicable`.
- **CVSS** needs a defensible vector or it is
  `"Not Scored — Insufficient Evidence"`. Never a bare number.

## 5.4 Verification pass (mandatory)

The script checks structure; these five checks are the part only you can do.
Before any finding leaves this phase:

1. Re-open the file and confirm the cited line still contains what you claim.
2. Confirm the code is reachable — find a caller chain from a real entry point.
   If you cannot, downgrade to `Potential` and say why.
3. Check whether a guard elsewhere already mitigates it. If so, it is a
   `False Positive` and belongs in the rejected-hypotheses section, not the bug list.
4. Confirm the severity matches `references/severity-and-confidence.md`, not
   your first impression.
5. Confirm no secret value leaked into the excerpt.

## Exit gate

- [ ] Every critical path examined or explicitly deferred
- [ ] Every finding verified against the file
- [ ] Reachability assessed for each finding
- [ ] False positives moved to the rejected list
- [ ] `validate-findings.py` and `detect-duplicate-findings.py` clean
- [ ] `verify-evidence.py` resolves every citation against the working tree
