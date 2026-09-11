# Runtime Verification Contract

Static analysis cannot settle concurrency, lifecycle, timing, hardware, or
integration behaviour. `Needs Runtime Verification` is the honest status for
those, and this file defines what discharging it looks like.

## The record

Every runtime verification produces one record in
`.audit/manifest.json` under `runtime_verifications`, shaped by
`schemas/command-evidence.schema.json`:

```json
{
  "finding_id": "BUG-014",
  "environment": "staging",
  "device_or_platform": "Pixel 6a / Android 14",
  "timestamp": "2026-09-10T14:22:05Z",
  "prerequisites": ["logged in as a standard user", "network shaped to 5% loss"],
  "command": "adb shell am start ... && scripts/repro-014.sh",
  "exit_code": 1,
  "expected": "no callback invocation after dispose()",
  "observed": "callback fired twice, 340 ms after dispose()",
  "result": "FAIL",
  "artifact_path": ".audit/evidence/BUG-014-runtime.log",
  "artifact_sha256": "…",
  "operator": "audit agent, session 2026-09-10"
}
```

## Result vocabulary

| Result | Meaning |
|---|---|
| `PASS` | The expected behaviour was observed. For a *finding* verification this means the defect did **not** reproduce. |
| `FAIL` | The defect reproduced. This confirms the finding. |
| `BLOCKED` | The environment was unavailable — no device, no credentials, no network. |
| `NOT_EXECUTED` | Nobody ran it. |
| `INCONCLUSIVE` | It ran, but the observation does not settle the question. Say what would. |

`PASS` and `FAIL` require an artifact (M015). `NOT_EXECUTED` may not carry an
observation (M016) — if you observed something, it executed.

**`NOT_EXECUTED` never becomes `PASS`.** Not after a code review, not because the
code looks correct, not because time ran out. This is the single most common way
audit and remediation reports become dishonest.

## Confidence transitions

| Before | Runtime result | After |
|---|---|---|
| Needs Runtime Verification | `FAIL` (defect reproduced) | `Confirmed` |
| Needs Runtime Verification | `PASS` (did not reproduce) | `Potential` or `False Positive` — decide explicitly, with the reason |
| Needs Runtime Verification | `BLOCKED` / `NOT_EXECUTED` | unchanged; the finding stays open and the limitation is reported |
| Needs Runtime Verification | `INCONCLUSIVE` | unchanged; refine the procedure |

A single non-reproduction is not proof of absence for a race condition. Say how
many iterations were run and under what conditions; "did not reproduce in 200
iterations under 5% packet loss" is evidence, "could not reproduce" is not.

## Writing a procedure that someone else can run

At discovery time, `verification.procedure` must name the environment, the
preconditions, the exact trigger, the observation point, and the expected
evidence. If a second engineer could not execute it without asking questions, it
is not finished. The remediation skill executes this same procedure after the fix
— which only works if it was written to be executable rather than descriptive.

## Where the artifacts live

`.audit/evidence/<FINDING-ID>-<stage>.log`, hashed and referenced. Redact before
storing: runtime logs are the most likely place for a token or a customer
identifier to end up in an audit artifact.
