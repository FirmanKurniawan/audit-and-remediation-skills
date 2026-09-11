# Finding Fingerprints

## The problem

Line numbers move. If a finding's identity depends on `file:line`, then inserting
an import above the defect makes the next audit believe the old finding vanished
and a new one appeared. Teams lose history, fixes get re-litigated, and
"Verified Fixed" starts meaning "I could not find it at the old line".

## The construction

```
fingerprint = sha256(
    component                  ␟
    finding_class              ␟
    weakness_key               ␟
    semantic_location          ␟
    normalized_evidence
)[:16]
```

- **weakness_key** — the sorted CWE ids when the finding has them, otherwise the
  declared `category`. Two defects of different classes at the same spot are
  different findings.
- **semantic_location** — `normalized_path::symbol` for each location, sorted.
  The enclosing symbol (function, class, route, manifest element) is stable under
  edits elsewhere in the file. **No line number enters the hash.**
- **normalized_evidence** — the primary code excerpt with comments stripped,
  string literals replaced by `"S"`, numbers replaced by `N`, all whitespace
  removed, lowercased. Reformatting, reindentation, and changing a literal do not
  move the fingerprint.

Implementation: `compute_fingerprint()` in `scripts/auditkit.py`. The validator
recomputes it and rejects any record where the stored value differs (F006), so a
fingerprint cannot be typed in by hand or carried over from a different finding.

## What it survives, and what it does not

| Change | Fingerprint |
|---|---|
| Lines shift up or down | unchanged |
| File reformatted | unchanged |
| String or numeric literal edited | unchanged |
| Comment added or removed | unchanged |
| Local identifier renamed | **changes** |
| Function containing the defect renamed | **changes** |
| File moved | **changes** |
| Different weakness at the same place | changes (correctly) |

Renames deliberately move the fingerprint: making the hash blind to identifiers
would collapse genuinely distinct findings. The second line of defence handles it.

## Second line of defence: duplicate detection

`detect_duplicates()` reports two things:

- **D001 — exact duplicate.** Identical fingerprints. These are one finding; keep
  the lowest id and mark the others `DUPLICATE` with `duplicate_of`.
- **D002 — probable same root issue.** Same component, same weakness key,
  overlapping file, and either raw-token similarity ≥ 0.70 or a shared enclosing
  symbol. This is what catches the `BUG-014` / `BUG-037` case where a rename or a
  reworded excerpt moved the hash.

D002 is a warning, not an error: a genuine second instance of the same weakness
in the same function does exist sometimes. Resolve it explicitly by setting
`duplicate_of`, which suppresses the warning, or by leaving a note saying why the
two are distinct.

## Delta re-audits

On a re-audit, match by fingerprint first, then by D002 similarity, then by id.
The **canonical id is the earliest one**. When a rename moved a fingerprint, keep
the original id, update the stored fingerprint, and record `first_seen_commit`
unchanged. Never mint a new id for a finding you already have, and never conclude
a finding is fixed because its fingerprint no longer matches — search for the
weakness before deciding anything.
