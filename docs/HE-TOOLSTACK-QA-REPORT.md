# HE-toolstack Phase 2 — QA Verification Report

**Document:** `docs/HE-TOOLSTACK-QA-REPORT.md` · v2.3 (rev 2026-11-17 **r13: final independent review (read-only delegate) caught TD §14 '18 records', TD §18 filing-time self-assessment presented current, TD §8.2 stale pending status, RR un-annotated filing-time pending claims + T-01…23 — all closed r13, re-gated 27/27**; lesson: sweep exclusions must never cover appendices/self-assessment prose, and superseded appendix bodies carrying status claims get a document-level status banner; r12: Q16 hardened to concept-level
stale-coherence per brief §B; §5 evidence-class + reproducibility disclosure added; stale
row texts Q7/Q16 synced; prior r11: D-16 ruled ACCEPTED by operator — Q28 assertion + row updated; r10: Q28 API-contract-coherence gate added — canonical health trio w/ `/health` retired, locked `POST /jobs` body, no-reap, six-scenario fixtures, replay wording; suite 27/27; previously r9: Q27 lifecycle-ownership gate added — six-step `make down`, he-stack=1 labels, class-X exclusion, core-5 class-C, diagram/prose agreement; 26/26 at r9. v1.8 (rev 2026-11-17 r8: Q25 extended — OQ-1 RULED 2026-11-17 asserted; D-02 Accepted count 11. v1.7 (rev 2026-11-16 r7: Q26 network-coherence gate added; totals 26/26. v1.6 (rev 2026-11-16 r6: +Q25 decision-integrity gate — operator rulings recorded across ADR/TD registers; prior v1.5 (rev 2026-11-16 r5: +Q24 backup-coherence gate; r5 rewrote backup mechanics and invalidated three r2 claims (see §3-r5); prior v1.3 (rev 2026-11-15b: review-response 2
re-gate — 8 targeted corrections; +Q18…Q22) · r3 2026-11-16: +Q23 claim/ownership coherence; Q5/Q18/Q20/Q22 evidence refreshed (flock + submissions inbox) · 2026-11-14 (P2.5)
**Method:** machine-checked where possible (scripts re-run against the repo at HEAD, not
memory); manual where a human judgment is unavoidable (then stated as such). Baseline:
commit `b520931` (main); **r12 re-gate baseline = branch `review/architecture-revisions` @ HEAD
(REQ v1.10 / TD v1.13 / ADR v1.11 / QA v2.3), harness `.hermes-tmp/gates_v13.py` (27 gates Q1–Q2,
Q4–Q28; Q3 = external mermaid 12.3.0 parse, run separately, 9/9 blocks OK).**

## 1. Automated gate results (all re-run this pass)

| # | Gate | Result | Evidence |
|---|------|--------|----------|
| Q1 | TD has 19 top-level numbered sections | **PASS** | 19/19 headings scanned |
| Q2 | Diagram count | **PASS** | 9 mermaid blocks in TD (D1–D9) |
| Q3 | Diagrams parse with a real parser (mermaid **12.3.0** + jsdom 31 — headless `mermaid.parse()` against a mocked DOM; scratch harness, non-authoritative, this report records its output). Re-run after the r2 diagram redraws | **PASS** | 9/9 TD blocks parse, zero fails |
| Q4 | All 66 requirements (42 FR + 24 NFR) appear in the traceability matrix (range/slash rows expanded) | **PASS** | 66/66 req-IDs covered + T-01…19 rowed; first pass gave a FALSE FAIL from a literal-string matcher (matrix uses `FR-01…05` range rows) — checker corrected, result verified row-by-row |
| Q5 | Every T-test id referenced in the matrix is defined in REQ §4 | **PASS** | 24 test ids (T-01…T-24; r3: T-20/T-21 restated for the flock protocol, +T-23 SQLite submission/claim crash matrix; **r12: +T-24 ticket-file mutual-exclusion audit** — brief §C, distinct from T-12 discipline audit / T-05 queue persistence / T-20 claim race), 0 undefined |
| Q6 | Every D-id referenced across all five docs resolves in the ADR register | **PASS** | D-ids resolve in the 17-record ADR register (records D-01 through D-12 and D-14 through D-18; there is no record numbered 13 — a stray ref to that non-existent record (a PD-ledger row number, not an ADR id) in D-15's Refs line was a dangling reference found by this gate and removed), 0 dangling |
| Q7 | Open-question register coherent TD ↔ ADR | **PASS** | TD §17.1 rows OQ-1…OQ-7 ⊆ ADR §4 register OQ-1…OQ-9 (ADR canonical; OQ-8/OQ-9 ADR-only per r5 mirror note, gate passes on TD⊆ADR); OQ-1 was once missing from the TD table — found by this gate, added |
| Q8 | Assumption ids in TD all resolve (Phase-1 canonical A1–A12 + declared A13–A15) | **PASS** | max A15, none out of range (collision was real, fixed @f44c294) |
| Q9 | Stale-concept refs (gpu-broker etc.) appear only as rulings/lineage | **PASS (manual)** | 2 automated flags are FALSE POSITIVES: both are lineage-table rows "gpu-broker (designed) → deleted, never ran" / "replaces the never-built gpu-broker" — explicitly ruling context |
| Q10 | Design-state honesty statement present ("proposed, not yet built") | **PASS** | TD §1 |
| Q11 | Evidence-tag density [V]/[E]/[P]/[proposal]/[U] | **PASS** | 136 tags in TD |
| Q12 | Commits cited in review doc exist in git history | **PASS** | f44c294, 4c887f8, 0ed664b, 141249d all present |
| Q13 | Rev 2026-11-15 (D-14 backup-root ruling) cross-doc sweep: no doc names another authoritative backup destination; NFR-22 ↔ TD §6.9/§9.4/§12.2/D8/R-4/R-8/`BACKUP_ROOT` ↔ ADR-D-14 all resolve | **PASS** | post-rev grep: zero stale `second disk`-as-destination refs in the v2 doc set |
| Q14 | Sidecar method vocabulary identical across TD §6.2/§5.4b and ADR-D-16 | **PASS** | canonical 4 = `create_run`/`status`/`kill`/`logs` (rev-fixed 2026-11-15: TD said `run/...` + `POST /reap`, ADR said `inspect/reap` — a real contradiction caught by the independent-review sweep) |
| Q15 | §4 test table placement (no T-rows stranded in §3) | **PASS** | T-01…T-24 contiguous in §4 (r13-synced; observed T-01…T-19 at v1.2-era run); 0 stray rows elsewhere (defect found by self-sweep, repaired same day) |
| Q16 | **Stale-coherence (r12-hardened, brief §B):** stated counts re-derived from canonical tables (42 FR / 24 NFR / 24 T / 13 FM / 17 ADR / 9 diagrams), header versions vs App.-C declared baseline, superseded concept tokens (old endpoints, networks, lifecycle classes, topology, backup roots, test/health/schema tokens) absent from live text with quoted-history exemption | **PASS** (r12 re-gate) | 0 coherence failures; the OLD numeric-token sweep had passed while stale appendices existed — class defect recorded as FINDING-08 (DESIGN-REVIEW §8) |
| Q17 | TD-internal §-refs resolve to existing headings | **PASS** | 0 dangling; `§3.1`/`§5.5` are intentional cross-document refs (REQ §3.1, review §5.5) |
| Q18 | Claim-arbiter consistency **r3**: single mechanism named everywhere (**flock held lock, TD §8.8 r3**), no residue of retracted designs (rename-"CAS", O_EXCL-as-arbiter, `§9.2a`, `lease_ttl`) | **PASS** | O_EXCL in TD+REQ; 0 `§9.2a`/`lease_ttl` mentions in REQ; TD §8.8 heading = "claim protocol — O_EXCL lockfile arbiter" |
| Q19 | Network-fact consistency [r2 item 1]: no doc still claims `host.docker.internal` is refused from containers; explicit retraction present in REQ + ADR | **PASS** | 0 "does not traverse" claims in REQ/TD/ADR; "retracted" present in both REQ NFR-07 area and ADR-D-15 Consequences |
| Q20 | WAL wording [r2 item 4 / r3]: TD states WAL admits **one committer db-wide** with **no fairness guarantee**; ownership is convention, not DB enforcement; r3: no doc gives the toolserver a queue UPDATE any more (grep-verified; toolserver write path = INSERT `submissions` only) | **PASS** | "no fairness guarantee" present in TD §8.4 area |
| Q21 | Lifecycle labels [r2 item 3]: REQ NFR-01 canonical lifecycle names `make down`; TD run-label `he-run` present | **PASS** | both strings grep-verified |
| Q22 | Tests T-20 (flock claim race — ≥2 processes, exactly one winner, crash+retry), T-21 (stale-claim supersede/expiry), T-22 (MinIO version-history sufficiency through staging), T-23 (SQLite submission-inbox concurrency + crash matrix) are defined in REQ §4 **and** rowed in the §5 matrix | **PASS** | defined + matrixed; network reachability proof remains T-17 (from-container probe). **[DP-R2a 2026-11-23 row repair:** this row was truncated on disk from its r3 filing through main `4b0838c`; the missing completion is reconstructed from the intact r2-era row (`3feb698`) plus the `gates_v13.py` Q22 predicate, and the predicate re-ran green against main @ `4b0838c` (27 PASS / 0 FAIL, 2026-11-23). See `workflows/adviser-input/round-02/` evidence.] |
| Q23 | Claim/ownership coherence [r3]: no Toolserver queue-`UPDATE` grant remains in TD; §8.8 claim protocol = flock held lock (no rename-as-lock claim in normative text); §8.4b ownership table + submissions inbox present in TD and mirrored in ADR-D-08 A1 | **PASS** | gates_v13 Q23 |
| Q24 | **Backup coherence [r5]:** (a) no live normative text asserts cross-filesystem atomic rename to the OneDrive root or `mc mirror` version-history preservation (history/withdrawn mentions allowed); (b) `--allow-active` appears ONLY beside withdrawn/negative language; (c) T-11 no longer affirmatively requires backup-while-jobs-run; (d) quiesce-and-wait §6.9.1, restore spec §9.6, L1–L5 ladder §6.9.4, ADR OQ-8 and OQ-9 all exist; (e) `DONE.json` never described as upload proof in normative text | **PASS** | gates_v13 Q24 (added this pass) |
| Q25 | **Decision-integrity [r6]:** 2026-11-16 operator rulings recorded coherently — ADR D-15 Accepted (Option D he-agent net), D-16 Accepted (Option B sidecar), D-08+A1 Accepted; ADR OQ-5/OQ-6/OQ-7 carry RULED+CLOSED markers, OQ-9 RULED (Option A ritual), OQ-8 CONFIRMED contingent; TD shows zero stale pending/awaiting markers; TD §17.1 mirror rows updated | **PASS** | gates_v13 Q25 (added this pass) |
| Q26 | **r7 network-isolation coherence (added this pass):** TD carries two named layers (`TS_BIND=0.0.0.0` inside-container vs explicit **zero host publication**); T-15 six-leg matrix exists in TD §5.4b with per-leg source/dest/expected/enforcement; NO normative gateway-URL or `host.docker.internal` success requirement survives in TD/REQ (retraction/probe history only); agent client URL `http://toolserver:8100` present in TD+REQ | **PASS** | gates_v13 Q26 (added this pass) |
| Q27 | **r9 lifecycle-ownership coherence (added this pass):** canonical labels `he-stack=1` (+ `he-run`/`he-job-id` job labels) asserted in TD §6.11 and NFR-01; six-step `make down` with host-side final sweep and the no-already-stopped-engine rule in TD+REQ; class-X explicit exclusion in TD AND the NFR-01 row; class-C core-5 enumeration in TD+ADR with no stale '(6 services'; diagrams + prose free of superseded constructs — RR terminology-drift annotations excluded by design, `docker.sock-ALTERNATIVE`/legacy-OQ-5-open markers and engine-direct-spawn edges absent from TD | **PASS** | gates_v13 Q27 (added this pass) |
| Q28 | **r10 API-contract coherence (added this pass):** three canonical health endpoints asserted in REQ+TD+ADR with `/health` retired; `POST /jobs` example exactly `{job_id, queue_pos}` + REQ `201 Created`; no engine-facing `reap` path anywhere; six-scenario health table incl. promotion-delayed→never-`failed` + four-state evidence ladder; `Idempotent-Replay` wording in TD+REQ; §6.2b cross-cutting rows + root-equivalence caveat present; D-16 status ACCEPTED per operator ruling (r6, confirmed 2026-11-17 — r10/r11 conflict resolved) | **PASS** | `gates_v13.py` Q28 (7 assertions) |

**Automated: 27/27 PASS** at the r12 and r13 re-gates (hardened Q16; r13 closed the final-review exceptions and re-gated clean; other gates unchanged) (suite is Q1–Q2, Q4–Q28 — 27 gates, Q3 external by design; Q27 added to lock the r9 lifecycle-ownership corrections — six-step `make down`, canonical labels, class-X exclusion, core-5 enumeration, diagram/prose agreement; Q1–Q26 re-verified at r9 — Q9's ruled-token context list extended with the r9 vocabulary, and interim Q27 FAILs were genuine self-caught defects: an uncontextualized compose-down mention and correction-annotation text read as live drift; the v1.7/r7 26/26 stands for the network-isolation pass (Q26: bind-vs-publish separation — bind-vs-publish separation, six-leg T-15 matrix, no stale gateway-URL success requirement; the v1.6/r6 25/25 stands for the ruling-recording pass; the v1.5/r5 24/24 stands for the backup-mechanic rewrite;
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

## 5. Evidence classes and reproducibility scope (r12 honesty disclosure, brief §D)

Every PASS in this report belongs to exactly one class:

| Class | What it proves | Where the tooling lives | Independently reproducible by a reviewer today? |
|-------|----------------|-------------------------|--------------------------------------------------|
| **Static automated gates (Q1–Q28)** | Text/table coherence of the docs in the PR branch — counts, refs, tokens, contract strings | `.hermes-tmp/gates_v13.py` — **scratch dir, NOT committed** | ❌ **No.** The harness is deliberately not promoted into the repo (D-05: docs repo holds design, not tooling; promotion deferred to M0 per this report's own follow-up table). A reviewer cannot rerun these checks without the harness. **We do not claim independent reproducibility for this class.** Limitation stated plainly, not papered over. |
| **Mermaid syntax parse** | The 9 diagram sources parse under mermaid 12.3.0 (jsdom headless) | external scratch harness | ❌ No (same reason). Proves syntax ONLY — semantic diagram↔prose agreement is a human checklist: DESIGN-REVIEW §2b. |
| **Manual author review** | Author read every statement changed and re-derived it from content, not counters | prose itself | Partially — a reviewer can redo the reading; our conclusions are not machine-checkable. |
| **Independent reviewer action** | DesignStandards §8-D sign-offs (×3) | not started | — (outstanding; this is a freeze gate, not a QA claim) |
| **Runtime tests T-01…T-24** | Would prove behavior | **specified only; NONE executed** — no code, no deployment exists | ❌ Nothing to run. Every mention of a T-id in this branch denotes a specification, never a result. |

**Command (author-side, for the record):** `python3 .hermes-tmp/gates_v13.py` from the repo
root prints one line per gate + `TOTAL/FAILS`; exit-agnostic by design. Re-run points at the
current HEAD at each round; results above are the r12/r13 tree (`T-24` present, REQ v1.10,
TD v1.13, QA v2.3). **[DP-R2a 2026-11-23: suite re-run against main @ `4b0838c` — 27 PASS /
0 FAIL (Q22 row repaired same commit; harness path-adapted copy, gate logic byte-identical);
full run log: `workflows/adviser-input/round-02/gate-run-main-4b0838c.txt`. Harness location
decision (R-09/FINDING-08) still open — due at M0 start, see plan P2c.]**
