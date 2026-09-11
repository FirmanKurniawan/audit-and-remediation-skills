# Delta Re-audit Prompt

For a repository that already has `BUG_ANALYSIS.md` and/or
`PRODUCT_FEATURE_ANALYSIS.md` from a previous pass.

---

Re-audit this repository **incrementally**. The goal is a stable diff, not a
rewritten document.

Do not modify source code.

**Steps**

1. **Read the existing reports.** Extract every `BUG-XXX` and `FEAT-XXX` with its
   current status, location, and severity. Note the commit the last pass audited.
2. **Compute the delta:**
   ```bash
   git log --oneline <last_audited_commit>..HEAD
   git diff --stat <last_audited_commit>..HEAD
   git diff --name-only <last_audited_commit>..HEAD
   ```
3. **Match findings by fingerprint first**, then by near-duplicate similarity,
   then by id. The earliest id is canonical: when a rename moved a fingerprint,
   keep the original id and update the stored fingerprint. Never mint a new id
   for a finding you already have.
4. **Re-verify every open finding** against the current code:
   - Still present at the cited location → `Open`, update the line number if it moved
   - Location changed and the defect moved with it → `Open`, new location, note the move
   - Genuinely fixed → `Verified Fixed`, cite the commit and what changed
   - Fixed then reintroduced → `Regressed`, cite both commits
   - Cannot find the code at all → `Superseded`, explain (removed, rewritten, dead)
   - Never mark something fixed because the line number no longer matches. Search
     for the pattern before concluding anything.
5. **Audit only the changed surface** for new findings — the diffed files plus
   anything that calls into them. Assign new ids continuing from the highest
   existing number. Never reuse or renumber an id.
6. **Re-check the standards registry.** If a standard has a new version since the
   last pass, note it and flag any finding whose mapping changed.
7. **Re-check dependencies** against current advisories, even for files that did
   not change — the code stays still while the advisory landscape moves.
8. **Update the product document** only where the delta changes it: new
   capabilities shipped, features unblocked because their blocking bug is now
   `Verified Fixed`, and roadmap phases that have moved.
9. **Add a changelog entry** at the top of each document:
   ```
   ## Pass N — <date> — <prev_commit>..<new_commit>
   Fixed: BUG-004, BUG-011 · Regressed: BUG-007 · New: BUG-021..BUG-024
   Unblocked: FEAT-002 (BUG-004 resolved)
   ```

**Report** a short delta summary: what closed, what regressed, what is new, net
change in severity counts, and whether the release verdict has changed.

**Rules**

- Preserve all historical ids and the rejected-hypotheses section.
- Re-verify before changing any status — a status change without evidence is worse
  than a stale document.
- If the previous pass's evidence looks wrong, say so explicitly rather than
  silently correcting it.
- Re-run the quality gate at the end. A delta pass that does not validate is a
  draft, exactly like a full one.
