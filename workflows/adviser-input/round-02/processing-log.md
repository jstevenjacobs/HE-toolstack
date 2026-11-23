# Round-2 council processing log — PR #13 (R2a), 2026-11-23

Quorum: **met** — Grok `APPROVE` + ChatGPT `APPROVE-WITH-CHANGES` (both verbatim in this dir).

| CD | Source | Finding (severity) | Disposition |
|---|---|---|---|
| CD-R2-001 | Grok 1–3 | Pre-repair truncation, post-repair row, reconstruction integrity **confirmed from live GitHub** | Recorded — repair method externally verified |
| CD-R2-002 | Grok 4 | TD §8.8 faithful to man-page rule; fork-inherited-fd edge case noted (non-blocking) | Superseded by CD-R2-004 (ChatGPT raised the same point as major — adopted once, covering both) |
| CD-R2-003 | Grok 5 / ChatGPT close | Gate logs not independently verifiable (harness absent, R-09/FINDING-08); absence ≠ refutation | Recorded — reinforces R2c (harness location) as real; stays an open operator decision, not an R2a defect |
| CD-R2-004 | ChatGPT 3 [major] | §8.8 wording too absolute: flock binds the **open file description**; fork/dup'd fd keeps lock alive; recommended replacement + carry constraint into T-20 | **ADOPTED** — TD §8.8 item 4 rewritten to the open-file-description formulation with explicit no-fork+exec-leak clause + T-20 crash-leg inheritance check; annotated `[DP-R2a 2026-11-23 clarification]` |
| CD-R2-005 | ChatGPT 2 [minor] | TD §8.8 edit lacked `[DP-R2a]` annotation although PR body claimed all three annotated — true (grep confirmed 0 hits pre-fix) | **ADOPTED** — annotation present in CD-R2-004 rewrite; PR body statement now true |
| CD-R2-006 | ChatGPT 2 addendum | "r16-era" typo in evidence file — true (line 30) | **ADOPTED** — corrected to r13-era |
| CD-R2-007 | ChatGPT 4b [minor] | Q22 predicate checks T-21/22/23, not T-20, though the row claims T-20 — true (harness line 146); T-20 exists REQ §4 L275 + §5 rows | **ADOPTED** — predicate extended in harness (`T-20 in mtx` + `"\| T-20 \|"`), label renamed `T-20..T-23 defined+matrixed`; re-run 27/0 → `gate-run-r2a-final.txt`; note appended to evidence file |
| CD-R2-008 | ChatGPT 4a | Whole-package truncation sweep (QA Q1–Q28 subset + RR R-01–R-12): **no further truncation found** | Recorded — Q22-class damage confined to that row; no sweep ticket needed |
| CD-R2-009 | ChatGPT 1 | Reconstruction rule acceptable; qualification that the predicate proves structure not historical prose correctness | Recorded — matches our own evidence-file framing (no action) |
| CD-R2-010 | ChatGPT 2 + close | Errata-without-version-bump defensible; no Q16 re-pin; no full 27-gate rerun demanded by bump alone | Recorded — operator-confirmed policy (2026-11-23): in-row annotations + evidence dir = audit trail |

Changes on follow-up commit: TD §8.8 rewrite (CD-R2-004/005), evidence typo (006), predicate note + final gate log (007), verbatim replies stored. Harness is not in the repo (R-09) — the extension is recorded via the evidence note + final log until R2c places the harness under version control.

Council ask now: confirm the follow-up diff closes ChatGPT's items 1–4 and (Grok) the §8.8 rewording still reads faithfully. ChatGPT's own words: "I recommend merging PR #13 after these adjustments" — merge waits for that confirmation.
