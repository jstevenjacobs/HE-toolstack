# HE-toolstack Phase 2 — QA Verification Report

**Document:** `docs/HE-TOOLSTACK-QA-REPORT.md` · v1.8 (rev 2026-11-17 r8: Q25 extended — OQ-1 RULED 2026-11-17 asserted; D-02 Accepted count 11. v1.7 (rev 2026-11-16 r7: Q26 network-coherence gate added; totals 26/26. v1.6 (rev 2026-11-16 r6: +Q25 decision-integrity gate — operator rulings recorded across ADR/TD registers; prior v1.5 (rev 2026-11-16 r5: +Q24 backup-coherence gate; r5 rewrote backup mechanics and invalidated three r2 claims (see §3-r5); prior v1.3 (rev 2026-11-15b: review-response 2
re-gate — 8 targeted corrections; +Q18…Q22) · r3 2026-11-16: +Q23 claim/ownership coherence; Q5/Q18/Q20/Q22 evidence refreshed (flock + submissions inbox) · 2026-11-14 (P2.5)
**Method:** machine-checked where possible (scripts re-run against the repo at HEAD, not
memory); manual where a human judgment is unavoidable (then stated as such). Baseline:
commit `b520931` (main); **v1.3 re-gate baseline = branch `review/architecture-revisions`
(r2 patch-set, TD / REQ v1.3 / ADR v1.3), harness `.hermes-tmp/gates_v13.py` (21 gates).**

## 1. Automated gate results (all re-run this pass)

| # | Gate | Result | Evidence |
|---|------|--------|----------|
| Q1 | TD has 19 top-level numbered sections | **PASS** | 19/19 headings scanned |
| Q2 | Diagram count | **PASS** | 9 mermaid blocks in TD (D1–D9) |
| Q3 | Diagrams parse with a real parser (mermaid **12.3.0** + jsdom 31 — headless `mermaid.parse()` against a mocked DOM; scratch harness, non-authoritative, this report records its output). Re-run after the r2 diagram redraws | **PASS** | 9/9 TD blocks parse, zero fails |
| Q4 | All 66 requirements (42 FR + 24 NFR) appear in the traceability matrix (range/slash rows expanded) | **PASS** | 66/66 req-IDs covered + T-01…19 rowed; first pass gave a FALSE FAIL from a literal-string matcher (matrix uses `FR-01…05` range rows) — checker corrected, result verified row-by-row |
| Q5 | Every T-test id referenced in the matrix is defined in REQ §4 | **PASS** | 23 test ids (T-01…T-23; r3: T-20/T-21 restated for the flock protocol, +T-23 SQLite submission/claim crash matrix), 0 undefined |
| Q6 | Every D-id referenced across all five docs resolves in the ADR register | **PASS** | D-ids resolve in the 17-record ADR register (records D-01 through D-12 and D-14 through D-18; there is no record numbered 13 — a stray ref to that non-existent record (a PD-ledger row number, not an ADR id) in D-15's Refs line was a dangling reference found by this gate and removed), 0 dangling |
| Q7 | Open-question register identical across TD ↔ ADR | **PASS** | OQ-1..7 in both (OQ-1 was missing from the TD §17.1 table — found by this gate, added) |
| Q8 | Assumption ids in TD all resolve (Phase-1 canonical A1–A12 + declared A13–A15) | **PASS** | max A15, none out of range (collision was real, fixed @f44c294) |
| Q9 | Stale-concept refs (gpu-broker etc.) appear only as rulings/lineage | **PASS (manual)** | 2 automated flags are FALSE POSITIVES: both are lineage-table rows "gpu-broker (designed) → deleted, never ran" / "replaces the never-built gpu-broker" — explicitly ruling context |
| Q10 | Design-state honesty statement present ("proposed, not yet built") | **PASS** | TD §1 |
| Q11 | Evidence-tag density [V]/[E]/[P]/[proposal]/[U] | **PASS** | 136 tags in TD |
| Q12 | Commits cited in review doc exist in git history | **PASS** | f44c294, 4c887f8, 0ed664b, 141249d all present |
| Q13 | Rev 2026-11-15 (D-14 backup-root ruling) cross-doc sweep: no doc names another authoritative backup destination; NFR-22 ↔ TD §6.9/§9.4/§12.2/D8/R-4/R-8/`BACKUP_ROOT` ↔ ADR-D-14 all resolve | **PASS** | post-rev grep: zero stale `second disk`-as-destination refs in the v2 doc set |
| Q14 | Sidecar method vocabulary identical across TD §6.2/§5.4b and ADR-D-16 | **PASS** | canonical 4 = `create_run`/`status`/`kill`/`logs` (rev-fixed 2026-11-15: TD said `run/...` + `POST /reap`, ADR said `inspect/reap` — a real contradiction caught by the independent-review sweep) |
| Q15 | §4 test table placement (no T-rows stranded in §3) | **PASS** | T-01…T-19 contiguous in §4; 0 stray rows elsewhere (defect found by self-sweep, repaired same day) |
| Q16 | Stale-count sweep (obsolete ID-count tokens; pattern set in harness) | **PASS** | 0 hits in the five Phase-2 docs (DESIGN-REVIEW updated in this revision) |
| Q17 | TD-internal §-refs resolve to existing headings | **PASS** | 0 dangling; `§3.1`/`§5.5` are intentional cross-document refs (REQ §3.1, review §5.5) |
| Q18 | Claim-arbiter consistency **r3**: single mechanism named everywhere (**flock held lock, TD §8.8 r3**), no residue of retracted designs (rename-"CAS", O_EXCL-as-arbiter, `§9.2a`, `lease_ttl`) | **PASS** | O_EXCL in TD+REQ; 0 `§9.2a`/`lease_ttl` mentions in REQ; TD §8.8 heading = "claim protocol — O_EXCL lockfile arbiter" |
| Q19 | Network-fact consistency [r2 item 1]: no doc still claims `host.docker.internal` is refused from containers; explicit retraction present in REQ + ADR | **PASS** | 0 "does not traverse" claims in REQ/TD/ADR; "retracted" present in both REQ NFR-07 area and ADR-D-15 Consequences |
| Q20 | WAL wording [r2 item 4 / r3]: TD states WAL admits **one committer db-wide** with **no fairness guarantee**; ownership is convention, not DB enforcement; r3: no doc gives the toolserver a queue UPDATE any more (grep-verified; toolserver write path = INSERT `submissions` only) | **PASS** | "no fairness guarantee" present in TD §8.4 area |
| Q21 | Lifecycle labels [r2 item 3]: REQ NFR-01 canonical lifecycle names `make down`; TD run-label `he-run` present | **PASS** | both strings grep-verified |
| Q22 | Tests T-20 (flock claim race — ≥2 processes, exactly one winner, crash+retry), T-21 (stale-claim supersede/expiry), T-22 (MinIO version-history sufficiency through staging), T-23 (SQLite submission-inbox concurrency + crash matrix) are
| Q23 | Claim/ownership coherence [r3]: no Toolserver queue-`UPDATE` grant remains in TD; §8.8 claim protocol = flock held lock (no rename-as-lock claim in normative text); §8.4b ownership table + submissions inbox present in TD and mirrored in ADR-D-08 A1 | **PASS** | gates_v13 Q23 |
| Q24 | **Backup coherence [r5]:** (a) no live normative text asserts cross-filesystem atomic rename to the OneDrive root or `mc mirror` version-history preservation (history/withdrawn mentions allowed); (b) `--allow-active` appears ONLY beside withdrawn/negative language; (c) T-11 no longer affirmatively requires backup-while-jobs-run; (d) quiesce-and-wait §6.9.1, restore spec §9.6, L1–L5 ladder §6.9.4, ADR OQ-8 and OQ-9 all exist; (e) `DONE.json` never described as upload proof in normative text | **PASS** | gates_v13 Q24 (added this pass) |
| Q25 | **Decision-integrity [r6]:** 2026-11-16 operator rulings recorded coherently — ADR D-15 Accepted (Option D he-agent net), D-16 Accepted (Option B sidecar), D-08+A1 Accepted; ADR OQ-5/OQ-6/OQ-7 carry RULED+CLOSED markers, OQ-9 RULED (Option A ritual), OQ-8 CONFIRMED contingent; TD shows zero stale pending/awaiting markers; TD §17.1 mirror rows updated | **PASS** | gates_v13 Q25 (added this pass) |
| Q26 | **r7 network-isolation coherence (added this pass):** TD carries two named layers (`TS_BIND=0.0.0.0` inside-container vs explicit **zero host publication**); T-15 six-leg matrix exists in TD §5.4b with per-leg source/dest/expected/enforcement; NO normative gateway-URL or `host.docker.internal` success requirement survives in TD/REQ (retraction/probe history only); agent client URL `http://toolserver:8100` present in TD+REQ | **PASS** | gates_v13 Q26 (added this pass) |

**Automated: 26/26 PASS** at the v1.7/r7 re-gate (Q1–Q26; Q26 added to lock the r7 network-isolation corrections — bind-vs-publish separation, six-leg T-15 matrix, no stale gateway-URL success requirement; the v1.6/r6 25/25 stands for the ruling-recording pass; the v1.5/r5 24/24 stands for the backup-mechanic rewrite;
r3's 23/23 stands for the flock/inbox layer; Q3 runs external to the Python harness). Interim FAILs during this revision were again real defects caught by gates —
a dangling ref to a non-existent ADR record and a missing OQ-1 row in TD — each fixed and re-gated. Harness
run recorded 2026-11-15b; Q13 path-sweep flags are legacy-context mentions explicitly marked as
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

### r5 backup-claim invalidations (recorded, not hidden)

- **Three r2/A1 mechanisms were false and are corrected in TD §6.9 (rewritten) + ADR-D-14 A2:** (1) atomic rename ext4→`/mnt/c` — impossible across filesystems → candidate + destination digest verify + NTFS-local publish rename; (2) `mc mirror` version-history preservation — vendor-documented as not preserved → §6.9.3 export design, falsifiable via T-22, fallback OQ-8 recorded **not adopted** (NFR-17 not silently weakened); (3) OneDrive completion via placeholder attributes — placeholder check is negative-only → L1–L5 ladder with the explicit statement that **no automated L4/L5 completion signal exists in this host environment today** (OQ-9); `DONE.json` demoted to L2 evidence.
- **One normative contradiction removed:** NFR-22/T-11 "backup while jobs run" vs §6.9 refuse-mode — single policy **quiesce-and-wait**; `--allow-active` withdrawn (never existed in any release).
- **Honesty floor:** no backup, drill, restore, or export has been executed — the stack is unbuilt. T-11/T-18/T-22 are *specified, not passed*; T-11's text now says so inline.

## 4. Residual actions

| ID | Action | Owner | Gate |
|----|--------|-------|------|
| FINDING-08 | Promote QA gate script into repo `scripts/qa/` for repeatable CI-style checks | author | M0 start |
| (from REVIEW §8) | C6 GPU re-measure ticket (FINDING-04) | Steven/OQ-2 | before GPU class enablement |
| (from REVIEW §9) | Independent reviewer sign-off ×3 | reviewers | design freeze |
