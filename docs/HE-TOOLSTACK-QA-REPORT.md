# HE-toolstack Phase 2 — QA Verification Report

**Document:** `docs/HE-TOOLSTACK-QA-REPORT.md` · v1.2 (rev 2026-11-15: full re-gate of
the FINDING-01…08 revision set, +Q14…Q17) · 2026-11-14 (P2.5)
**Method:** machine-checked where possible (scripts re-run against the repo at HEAD, not
memory); manual where a human judgment is unavoidable (then stated as such). Baseline:
commit `b520931` (main); **v1.2 re-gate baseline = branch `review/architecture-revisions`
(batches 1–2, TD v1.2 / REQ v1.3 / ADR v1.2), harness `.hermes-tmp/gates_v12.py`.**

## 1. Automated gate results (all re-run this pass)

| # | Gate | Result | Evidence |
|---|------|--------|----------|
| Q1 | TD has 19 top-level numbered sections | **PASS** | 19/19 headings scanned |
| Q2 | Diagram count | **PASS** | 9 mermaid blocks in TD (D1–D9) |
| Q3 | Diagrams parse with a real parser (mermaid 11 + jsdom, node 26.5); `mermaid.parse()` OK (harness `mmcheck/parse.mjs` — scratch tool, non-authoritative, this report records its output) | **PASS** | 9/9 blocks across all docs, zero fails |
| Q4 | All 66 requirements (42 FR + 24 NFR) appear in the traceability matrix (range/slash rows expanded) | **PASS** | 66/66 req-IDs covered + T-01…19 rowed; first pass gave a FALSE FAIL from a literal-string matcher (matrix uses `FR-01…05` range rows) — checker corrected, result verified row-by-row |
| Q5 | Every T-test id referenced in the matrix is defined in REQ §4 | **PASS** | 19 test ids, 0 undefined |
| Q6 | Every D-id referenced in TD resolves in the ADR register | **PASS** | D-ids resolve in the 18-record ADR register, 0 dangling |
| Q7 | Open-question register identical across TD ↔ ADR | **PASS** | OQ-1..6 in both |
| Q8 | Assumption ids in TD all resolve (Phase-1 canonical A1–A12 + declared A13–A15) | **PASS** | max A15, none out of range (collision was real, fixed @f44c294) |
| Q9 | Stale-concept refs (gpu-broker etc.) appear only as rulings/lineage | **PASS (manual)** | 2 automated flags are FALSE POSITIVES: both are lineage-table rows "gpu-broker (designed) → deleted, never ran" / "replaces the never-built gpu-broker" — explicitly ruling context |
| Q10 | Design-state honesty statement present ("proposed, not yet built") | **PASS** | TD §1 |
| Q11 | Evidence-tag density [V]/[E]/[P]/[proposal]/[U] | **PASS** | 112 tags in TD |
| Q12 | Commits cited in review doc exist in git history | **PASS** | f44c294, 4c887f8, 0ed664b, 141249d all present |
| Q13 | Rev 2026-11-15 (D-14 backup-root ruling) cross-doc sweep: no doc names another authoritative backup destination; NFR-22 ↔ TD §6.9/§9.4/§12.2/D8/R-4/R-8/`BACKUP_ROOT` ↔ ADR-D-14 all resolve | **PASS** | post-rev grep: zero stale `second disk`-as-destination refs in the v2 doc set |
| Q14 | Sidecar method vocabulary identical across TD §6.2/§5.4b and ADR-D-16 | **PASS** | canonical 4 = `create_run`/`status`/`kill`/`logs` (rev-fixed 2026-11-15: TD said `run/...` + `POST /reap`, ADR said `inspect/reap` — a real contradiction caught by the independent-review sweep) |
| Q15 | §4 test table placement (no T-rows stranded in §3) | **PASS** | T-01…T-19 contiguous in §4; 0 stray rows elsewhere (defect found by self-sweep, repaired same day) |
| Q16 | Stale-count sweep (obsolete ID-count tokens; pattern set in harness) | **PASS** | 0 hits in the five Phase-2 docs (DESIGN-REVIEW updated in this revision) |
| Q17 | TD-internal §-refs resolve to existing headings | **PASS** | 0 dangling; `§3.1`/`§5.5` are intentional cross-document refs (REQ §3.1, review §5.5) |

**Automated: 17/17 PASS** at the v1.2 re-gate (several interim FAILs during revision were
real document defects — stranded T-rows, sidecar-vocabulary drift, stale counts — each
fixed and re-gated, plus checker false-positives documented above). Harness run recorded
2026-11-15; Q13 path-sweep flags are legacy-context mentions explicitly marked as
pre-ruling history (`/home/steven/backups` [E], PD-toolstack paths in Phase-1 evidence) —
not authoritative-destination claims.

## 2. Manual QA (author, flagged non-authoritative)

- Internal narrative coherence TD §§1–19: ✅ read-through complete; the load-bearing
  claims (single compose, N-image rule D-10, host-dir state D-05, GPU budget D-04-B)
  are stated identically in REQ, ADR, TD, and REVIEW. No contradictions found.
- Diagram-vs-prose name drift: partially machine-checked (node ids match §6 names);
  full visual rendering check **owed to the ops reviewer** (🧑) — mermaid *parses* ≠
  humans find the layout readable.
- REVIEW checklist self-assertions were spot-verified against TD at random (§5
  completeness rows, §6 TR rows): held.

## 3. Known limits of this QA pass (DesignStandards §2 honesty)

1. No stack was built; **zero runtime claims** are QA'd here — every T-test is still
   unexecuted [proposal]. This report certifies *documentation integrity*, not behavior.
2. Mermaid validation proves syntax, not semantics/readability.
3. The QA harness itself lives in the scratch dir (non-authoritative per D-05); its
   result is recorded here as evidence-in-document. For repeatability it should be
   promoted into `scripts/qa/` at M0 — filed as FINDING-08 below (repo-`scripts/qa/` promotion; distinct from the GitHub-issue FINDING-08 numbering of the formal review).
4. Review-cycle findings (REVIEW §8 FINDING-04..07) remain open *by design* pending
   owner decisions (OQ-1..6) and M0 execution.

## 4. Residual actions

| ID | Action | Owner | Gate |
|----|--------|-------|------|
| FINDING-08 | Promote QA gate script into repo `scripts/qa/` for repeatable CI-style checks | author | M0 start |
| (from REVIEW §8) | C6 GPU re-measure ticket (FINDING-04) | Steven/OQ-2 | before GPU class enablement |
| (from REVIEW §9) | Independent reviewer sign-off ×3 | reviewers | design freeze |
