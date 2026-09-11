# Phase 3 — Root Cause and Blast Radius

**Goal:** understand the mechanism, and everything a change to it can break.

## 3.1 The mechanism, not the symptom

Write one paragraph that would let another engineer predict the bug from the code
without seeing the report. "Query is built by string concatenation, so any
metacharacter in `q` changes the parse" is a mechanism. "SQL injection
vulnerability" is a label.

If the audit's `root_cause` turns out to be wrong, say so and correct it in the
fix record. The audit is a hypothesis; you are the one holding the evidence now.

## 3.2 Map the blast radius

Before designing anything, enumerate:

- **Callers** — everything that reaches the code you will change.
- **Dependents** — what consumes its output, including serialized formats,
  persisted data, and API responses.
- **Public interfaces** — is any signature, schema, route, or event shape in
  scope? Changing one turns a local fix into a compatibility event.
- **Behavioural contracts** — anything relying on the *current, wrong* behaviour.
  Legacy clients depending on a lenient parser are the classic case.
- **Shared state** — caches, sessions, queues, and stored data written by the old
  code that the new code must still read.
- **Tests** — which existing tests cover this path, and are any asserting the
  buggy behaviour?

```bash
grep -rn "parseFrame" --include='*.c' --include='*.h' .
git log --oneline -20 -- src/protocol.c
```

## 3.3 Ask why it is there

Check the history. Code that looks wrong is sometimes a deliberate workaround for
something worse. `git log -S` on the relevant line and the linked ticket, if any,
takes two minutes and occasionally saves an incident.

## 3.4 Record it

Fix-record fields: `root_cause`, `blast_radius.callers`,
`blast_radius.dependents`, `blast_radius.public_interfaces`,
`blast_radius.behavioural_contracts`, `blast_radius.covering_tests`.

## Exit gate

- [ ] Root cause stated as a mechanism
- [ ] Callers and dependents enumerated, not assumed
- [ ] Public interface impact decided explicitly
- [ ] Existing test coverage identified
- [ ] Anything surprising in the history noted
