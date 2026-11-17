# HE-toolstack — Formal Architecture Review Response

**Document:** `docs/HE-TOOLSTACK-REVIEW-RESPONSE-2026-11-15.md` · 2026-11-15
**Responds to:** the Formal Architecture Review of 2026-11-15 (CHANGES REQUESTED,
FINDING-01…08 + review §5 independent areas + §9 verdict conditions).
**Change set:** branch `review/architecture-revisions` — batches `6be5b9e` (REQ v1.2/1.3 +
ADR v1.2), `392fcb9` (TD v1.2), `4a78a07` (QA v1.2 + DESIGN-REVIEW v1.1 + defect repairs).
**Scope discipline (review §2/§10):** this package is *documentation only*. No deployment
scripts, compose files, containers, tickets, or roadmap execution were produced. Proposed
items stay marked proposed. The two open operator calls (D-15 bind topology, D-16 spawn
channel) are **requests for decision**, not assumed approvals.

---

## A. Per-finding dispositions

| Finding | Disposition | Where | Evidence / note |
|---|---|---|---|
| FINDING-01 — loopback/`host.docker.internal` networking claim unverifiable | **ACCEPTED — fixed with measured evidence** | REQ NFR-07 rewrite, FR-01 client URL; TD §6.4, §10 network rows; ADR-D-01 amendment + **new ADR-D-15 (operator decision requested)** | Live probe from inside a container: `172.17.0.1:8100` reachable; `host.docker.internal` resolved to `192.168.65.254` and got ConnectionRefused on loopback services. Design now specifies the bridge-gateway form + published-port pattern `127.0.0.1:PORT:PORT` (no `0.0.0.0` exposure — NFR-07 conflict removed). Final bind-address choice = **D-15, yours**. **[2026-11-16 r7 annotation: the "bridge-gateway form + published-port pattern" text in this row documented the RETRACTED pre-D-15 topology; superseded by D-15 Option D (zero publish, `he-agent` membership, client `http://toolserver:8100`) as ruled 2026-11-16 — see Appendix E/F and REQ NFR-07 r7.]** GitHub #2 |
| FINDING-02 — container lifecycle ownership undefined | **ACCEPTED — fixed** | TD new §6.10 (lifecycle classes A/B/X), D9 diagram (validated), janitor rules, shutdown order, reconcile-on-start; REQ NFR-10 rewrite | Every container now has exactly one named owner across compose-managed / engine-spawned / host-timer classes; expired containers ≤15 min kept for log capture then reaped. GitHub #3 |
| FINDING-03 — Docker-socket privilege placement | **ACCEPTED — fixed; recommendation only, decision yours** | TD §6.2 (engine never sees a socket under any option), §5.4b security-boundary table, §13.1 spawn-seam code layout; **ADR-D-16 (3-option comparison, operator decision requested)** | Honest framing kept: a sidecar redistributes privilege, it does not remove it. Review §5.3 side-effect areas covered: uid alignment, audit logging, allow-list enforcement point. GitHub #4 |
| FINDING-04 — SQLite single-writer claim vs read path | **ACCEPTED — fixed** | TD §6.7 writer-ownership table per DB, §8.8 claim protocol (BEGIN IMMEDIATE + version check), WAL mode stated; REQ NFR-09 amended | One writer per file, readers via WAL; concurrent-session claim race is now a specified protocol with test T-12 + property check. GitHub #5  **(r3 supersession: this row and the r2 §8.8 O_EXCL revision are both superseded — see Appendix C.)** |
| FINDING-05 — backup atomicity/consistency (hot SQLite, OneDrive) | **ACCEPTED — fixed, then corrected r5** | TD new §6.9 host backup job (sqlite `.backup` API → staging → manifest → fsync → rename → DONE), RPO/RTO stated, OneDrive staleness alarm `backup_stale`; REQ NFR-22 amended, NFR-19 cross-ref; ADR-D-14 A1 amendment; T-18 drill | The review's durability demand is met with primitives named explicitly (`sqlite3 .backup`, fsync+atomic rename, write-ahead manifest ordering §5.4a). GitHub #6  GitHub #6  **(r5 correction: the A1 mechanism contained three false claims — cross-FS atomic rename, `mc mirror` version history, OneDrive placeholder-attribute sync proof — plus the §6.9-vs-NFR-22 active-job contradiction; all corrected in TD §6.9/§9.6 rewrite + ADR-D-14 A2. See Appendix D.)** |
| FINDING-06 — MinIO liveness conflated with dependency | **ACCEPTED — fixed** | TD §7 health model split `/healthz` vs `/readyz` vs `/deps`, §6.3 depends_on corrected (service_healthy only where truthful); REQ NFR-23 | MinIO is now an **optional dependency** (promotion/replay path), never a startup gate for the core loop; degradation is observable, not fatal. GitHub #7 |
| FINDING-07 — 202-vs-201 queue-accept semantics | **ACCEPTED — fixed** | FR-01 rewritten to **201 Created** + `{job_id, queue_pos}` with contract suite (T-08); **ADR-D-18 (new record)**; he-client + status-model text aligned | Review §5 note honored: semantics fixed at the requirement level, not silently in a client shim. GitHub #8 |
| FINDING-08 — ID-count / artifact mismatches across docs | **ACCEPTED — fixed + gated** | QA v1.2 gate Q16 (stale-token sweep) + Q4/Q5/Q15; DESIGN-REVIEW v1.1 counts; TD §14 "18 records" | Scripted gates now assert 66 requirement IDs, 19 tests, 9 diagrams, 18 ADR records — re-run, zero stale tokens. GitHub #9 |

## B. Review §5 independent areas (beyond the 8 findings)

| Area | Disposition | Where |
|---|---|---|
| §5.1 durability primitives unspecified | FIXED | TD §5.4a write-order/durability matrix (fsync/os.replace/rename where each state transition needs it) |
| §5.2 security boundaries table absent | FIXED | TD §5.4b (trust zones, what crosses each boundary, enforcement point) |
| §5.3 sidecar side-effects | FIXED | ADR-D-16 consequences + TD §6.2 (audit log, allow-list server-side, socket never mounted into engine) |
| §5.4 concurrent sessions / claim races | FIXED | TD §8.8 + T-12 property test |
| §5.5 failure-class taxonomy | FIXED | TD §12.5 seven classes RC-1…7 (detection → affected state → recovery → evidence), FM-11…13 added to FMEA, R-9 daemon-restart drill + T-19 |
| §5.6 reconcile / orphan gapless ledger | FIXED | TD §8.6 reconcile invariant (container-without-row → reap; row-without-container → interrupted → requeue idempotent) + NFR-24 + T-19 |

## C. Items preserved unchanged (review §3 — all 14)

Single host; one compose project incl. MinIO; narrow images separate (D-10); HTTP/JSON not
MCP; file-externalized workflow state; SQLite queue/registry; no GPU broker daemon; GB10
excluded; CPU-only acceptance; RTX 5060 Ti admission **disabled** pending C6; physics-gate;
`heat-data` authoritative root (D-05); OneDrive backup root (D-14); PD-toolstack frozen as
evidence. No preserved item was altered.

## D. Open operator decisions (NOT assumed)

| Record | Question | Recommendation |
|---|---|---|
| **ADR-D-15** | Agent→engine bind form: bridge-gateway `172.17.0.1:8100` vs published `127.0.0.1:8100:8100` (probe evidence both viable; design currently specifies gateway form with published-port fallback) | gateway form as default (fewer moving parts, verified) |
| **ADR-D-16** | Job-spawn channel: A = socket in engine; B = hardened spawn-sidecar; C = rootless/systemd-run | **B**, with the honest caveat in the record |
| ADR-D-17 | MinIO = optional dependency status formalized | accept as written |
| ADR-D-18 | 201 contract | accept as written |

## E. Residual risks after this revision

1. GPU-class numbers still rest on one pre-C6 measurement (FINDING-04-of-original-review
   is fixed *as a claim*, not as data — C6 re-measure stays the gate; admission disabled).
2. T-01…T-19 are **specified, not executed** — zero runtime claims are made anywhere.
3. D-15/D-16 unresolved means §6.2/§6.4 text is "specified to recommendation level"
   until ruled; flagged in-paragraph, not hidden.
4. QA harness lives in scratch (promotion to `scripts/qa/` is an M0 action, per QA §4).

## F. Verdict requested

DesignStandards §7 readiness for this package: **APPROVE WITH EXCEPTIONS** — exceptions
being (a) operator rulings D-15/D-16, (b) C6 GPU re-measure before any GPU-class
enablement, (c) the three independent human sign-offs required for design freeze.
Self-approval of this response is not approval: per review §10 the package now **stops
here for human review**.

---

# Appendix B — Round-2 response (2026-11-16): "Changes requested" dispositions

Review received: **CHANGES REQUESTED — NOT APPROVED FOR MERGE** (8 required corrections,
overall direction accepted). This appendix dispositions each correction against commit
`3feb698` on `review/architecture-revisions`. Re-run verification: 21/21 documentation
integrity gates (`gates_v13.py`) + all 9 diagrams parse (mermaid 12.3.0); documentation
checks only — **not** runtime validation. No deployment or implementation activity
performed.

## Correction 1 — Lifecycle requirements
**Done.** NFR-01 (REQ v1.4) now states the canonical rule: `make down` is the *only* stop
path for stack-owned containers; `docker compose down` is permissible solely as the
class-C/class-J ownership command invoked *through* the Makefile, never as an operator-
parallel path. Container labels (`com.docker.compose.project=he`, run-scope `he.run=<id>`)
standardized in TD §5.6 (lifecycle narrative + sequence diagram 7 re-verified). Shutdown
semantics, ownership classes, and labels use one vocabulary across REQ §2.1, TD §5.6/§11.

## Correction 2 — Network security (the substantive one)
**Done, with a retraction and a stronger design.**
- *Contradiction removed:* the old text claimed `host.docker.internal` was refused while
  `172.17.0.1` was the path. Both were wrong for this environment. Probe [V 2026-11-16,
  reproduced in-container and in WSL2]: from a default-bridge container **both**
  `172.17.0.1` and `host.docker.internal` (= `192.168.65.254`) traverse to host-published
  listeners; `127.0.0.1` inside the container is its own loopback (refused). Host Ollama
  bind re-verified `*:11434` [V ss]. All contradictory statements in REQ/ADR/TD are
  retracted and replaced by the probe matrix; D-15's old "isolation premise" is explicitly
  retracted in its record.
- *Accessibility demonstrated:* proposed mechanism (D-15 rev, still **operator-pending**):
  dedicated isolated network `he-agent` — toolserver joins it and **publishes no port**;
  only the Hermes agent container joins it. Verified by live probes on the host engine
  [V 2026-11-16]: (a) member→member service-DNS HTTP 200; (b) default-bridge peer probe of
  `toolserver:8100` **fails — no path**; (c) non-member probe of the *loopback-published*
  port via `172.17.0.1:8100` **connects** — which disproves "loopback publish = container
  isolation" (the gateway alias reaches published ports indiscriminately). That negative
  result is exactly why the design is membership, not bind-prefix alone: bind `127.0.0.1:`
  remains as host-firewall hygiene (blocks LAN/WAN), he-agent membership is the container
  control. **[2026-11-16 r7: superseded — the final D-15 design publishes NO host port at
  all, so the loopback hygiene prefix no longer exists for :8100; zero-listener absence
  replaced hygiene.]**
- *Reviewer's exact test is specified as the gate:* T-15/T-21 = another container on the
  same default bridge MUST fail to reach the toolserver; Ollama embed-side gets its own
  dedicated service network; host CLI health path keeps the loopback-only publish (host
  cannot route into dedicated nets [V probe], so both paths are needed).
- D-15 remains an **open operator decision** (options A–D, recommendation D); no approval
  assumed. Pre-deployment re-probe on the deployment host is a stated condition (this was
  proven on a WSL2/5.15 host; production is RTX-5060-Ti WSL2).

## Correction 3 — Workflow concurrency
**Done.** §8.8's "atomic rename ≈ CAS" was withdrawn as unsound (rename mutualizes the
*file*, not the transition — two sessions can both observe `open` before either renames).
TD §8.8 now specifies the real arbiter: `open(…, O_CREAT|O_EXCL)` lockfile claim (kernel-
enforced single winner) **plus** the SQLite transition guarded as compare-and-swap —
`BEGIN IMMEDIATE` + `UPDATE tickets SET status='claimed'… WHERE id=? AND status='open'`
with rowcount==1 verification (SQLite has no CAS primitive; this is the CAS *pattern*,
stated as such, not claimed as a primitive). §8.8a adds the honest WAL caveat (correction
7). Test **T-20** defined + matrixed: N≥8 concurrent claimants on one ticket → exactly one
rowcount==1 winner, others 409 [P — test defined, not executed].

## Correction 4 — Backup integrity
**Done.** `mc mirror` documented as NOT preserving MinIO version history (known gap,
[D]); TD §6.9 now specifies the actual mechanism: versioned objects exported to an
ext4 staging manifest-digest set (`sha256sum -c` verified), staged set → OneDrive via
robocopy per D-14, receipt (counts+digests) committed to the ledger repo; OneDrive
FinalItems V1 shadow-copy remains an additional, non-authoritative layer [V mechanism
exists; drill T-22 P]. Active-job policy reconciled with T-11: queue DB is WAL-snapshotted
(hot copy), and T-11's abort/restart semantics apply to a *transfer* interrupted mid-flight
— the two tests no longer contradict.

## Correction 5 — Diagrams
**Done.** All 9 TD diagrams now depict the revised architecture: he-agent isolated network
+ zero publish (diagrams 1/3), spawn-sidecar holding docker.sock with he-internal-only
reach (1/3/6), host engine socket via sidecar (5), `make down` shutdown + run labels (7),
O_EXCL claim path (state diagram re-checked). Verified: **9/9 parse under mermaid
12.3.0 + jsdom 31** (real parser; earlier headless failures were harness artifacts).
Superseded `host.docker.internal`-as-trust-boundary edges removed.

## Correction 6 — Spawn-sidecar interface
**Done.** One normative spec: TD §6.2b — `POST /v1/spawn` (`create_run`),
`GET /v1/runs/{id}` (`status`), `POST /v1/runs/{id}/kill`, `GET /v1/runs/{id}/logs` —
4 ops, JSON, no auth (network membership = the control). ADR-D-16 and QA Q14 now point at
§6.2b as the single source; every other mention is prose referring to it. Stale alias
sweep (`POST /spawn`, bare `run/status/kill/logs` verb-lists, `run`+`status` combined path)
= 0 residual tokens across all five docs (gate Q14).

## Correction 7 — SQLite concurrency
**Done.** TD §8.8a (new): table-level writer ownership (D-08 A1) is explicitly
an **application convention**, not DB enforcement — any holder of the DB file can write
any table; the rule holds only via code discipline + CI lint test (T-19 [P]). WAL is
stated correctly: a **single writer for the whole database at a time** (db-wide
serialization), readers non-blocking; the old "commit-time serialization per table" and
any fairness implication is corrected — WAL has **no fairness guarantee**, a writer
re-acquires immediately; documented ceiling + escalation path (per-DB files) retained.

## Correction 8 — Documentation traceability
**Done.** QA report v1.3 + DESIGN-REVIEW v1.2 resynced to this exact tree: stale counts
removed (22 T-ids T-01…T-22, 17 ADR records, 136 [V]/[E]/[P] tags, OQ-1…OQ-7 — OQ-1 row
restored in TD §17.1, and gate found+removed a dangling ref to a non-existent record
— the phantom D-13 was a PD-ledger row number, not an ADR). **T-12 disambiguated:** T-12 =
process-write-audit only; concurrent-claim-race is its own test **T-20**, digest-chain is
T-04/T-10 — stated in REQ v1.4, every T-12 cite checked. New rows Q18–Q22 record the
round-2 gates.

## Additional expectations — compliance
- All 14 preserved decisions untouched (single compose, separate images D-10, backup root
  D-14, heat-data authority D-05, CPU-only acceptance, physics gate, state-as-files…).
- **D-15/D-16 remain operator decisions** — records say "operator-pending", recommendations
  flagged as recommendations, no approval assumed.
- No GPU execution enabled; GPU admission stays disabled pending HW verification; no
  resource-sharing change.
- Zero implementation/deployment activity this round (design docs only; probes were
  throwaway containers on the host engine, removed — no stack deploy).
- Proposed-vs-verified discipline maintained; new claims carry [V]/[P]/[D] tags.
- Documentation QA re-run (21/21 gates + parser) **is stated as documentation integrity
  only**; QA report header says runtime validation remains outstanding.

## Disposition
All 8 corrections addressed in `3feb698`. **STOP per §10 of round-1 protocol remains in
force:** nothing merged, nothing implemented, nothing deployed; awaiting human re-review
of PR #11.


---

# Appendix C — Round-3 response (2026-11-16): "Ticket concurrency and SQLite ownership"

**Mode: documentation-only.** No mechanism implemented, no containers run, nothing merged,
no issues closed.

## C.1 — Ticket claims were not mutually exclusive: ACCEPTED

The reviewer is correct on both counts against the branch text:
- The original §8.8 sequence (`read → check → atomic-rename write → ledger append`) is not
  compare-and-swap. Two sessions can read the same unclaimed ticket, pass the check, and
  both rename successfully — the last writer silently overwrites the first claim. Atomic
  rename guarantees *whole-file visibility*, not mutual exclusion. The stale-claim
  supersede path had the identical race.
- The r2 "correction" (`O_CREAT|O_EXCL` lockfile) fixed crash-release but **not**
  mutual exclusion either: `O_EXCL` is a *point* create-race arbiter; every claimant
  removes the lockfile after use, so a claimant that creates the lock after that removal
  reads and writes the ticket while a previous holder is still inside its critical
  section.

**Resolution (TD §8.8 r3 rewrite):** a real held lock — **`flock(2)` advisory lock on
`workflows/tickets/.locks/<id>.lock`** (dir 0755 / file 0644, single HE user; flock is
mandatory against itself, so the protocol is race-free even in one process). Same claimant
acquires the same per-ticket lock **before reading** — timeout via bounded
`HE_CLAIM_WAIT_MAX` (default 5 s [P], 100 ms backoff) ⇒ `409 already_claimed`, and a loser
never reads or modifies the ticket — and holds it through: classify → `claimed:` line
(write→fsync) → ledger claim event → claim payload → release; `he ticket done` uses the
same lock. Process-crash release is kernel-guaranteed (§8.8a);
stale claims are superseded **while holding** the lock after heartbeat staleness
(payload `heartbeat_at`, tick 60 s [P], stale beyond `HE_CLAIM_STALE_MIN` 30 min [P] **and**
no current lock holder); a hung-but-alive holder keeps the lock by design (ops path =
deliberate `kill`, kernel then releases); documented
assumptions: one host, one Docker engine, Linux Local FS (flock per open file description
— NFS/fuse/CIFS explicitly unsupported), no lock daemon (consistent with the D-03
no-daemon ruling). Rename and O_EXCL are no longer called a lock or CAS anywhere, and no rename acts as
arbiter in any path — supersede waits for the lock, never clobbers.

## C.2 — SQLite table ownership was internally contradictory: ACCEPTED

The reviewer is right: §6.7/§8.4 asserted toolserver sole-writer of `queue` while §7.5
gave the engine an `UPDATE queue SET state='claimed'…` — under a per-table ownership
model these cannot all be true. The r2 traceability gate validated each row in
isolation, so it never caught the cross-section conflict; that is a genuine QA blind
spot, now closed by a new ownership-coherence gate (QA Q23) and grep evidence.

**Resolution (reviewer option 2 — explicit inbox; ADR-D-08 A1 rewritten, stays
Proposed):** toolserver's *only* write anywhere in the engine DB is `INSERT INTO
submissions(... idempotency_key UNIQUE ...)`; the engine consumes each row in ONE
`BEGIN IMMEDIATE` transaction (dedup against `idempotency_keys` at consume → `INSERT
queue` + immutable job_spec → `DELETE` consumed row → commit) and is sole writer of
`queue` and every other table. §8.4b is now a normative SQL-ownership table (every
mutation, owning process, txn boundary, affected-rows semantics). WAL admits one
committer db-wide; no doc claims per-table concurrent writers or `busy_timeout`
fairness (r2 text corrected); busy → bounded retry → honest `503`. Crash windows
enumerated (§8.4b bullet 7): submission-not-consumed replays idempotently via key;
half-consumed is impossible by the consume-transaction boundary; duplicate execution
prevented by single dispatcher + conditional `WHERE state='queued'` transitions
(affected-rows==1, else re-read + 409 — never blindly overwrite). Dual-writer on
`queue` itself (option 3) considered and **rejected** with reasons; no PostgreSQL;
SQLite retained.

## C.3 — Test/ADR alignment: ACCEPTED

- **T-12 stays a process/discipline audit only** — the docs now state this explicitly in
  the REQ disambiguation note; no doc claims T-12 proves concurrency.
- **T-20 (restated):** ≥2 independent OS processes race `he ticket claim` — exactly one
  winner; losers never read/write the ticket; supersede path armed ⇒ one winner;
  claimant-`kill -9` ⇒ kernel release ⇒ fresh claim completes; retry ⇒ no double-claim.
- **T-21 (restated):** flock supersede + expiry, two concurrent superseders serialize
  (loser 409), hung-but-alive holder NOT supersedeable until pid death (asserted).
- **T-23 (new):** SQLite submissions/claim crash matrix (4× distinct-key race = exactly
  4 rows; 4× same-key race = exactly 1 queue row via consume-time dedup; `kill -9`
  between submission and consume → replay once; `BEGIN IMMEDIATE` contention; bounded
  busy behavior).
- Matrix, REQ/QA headers, test counts (23) and QA gates updated; diagrams re-validated.
- **ADR-D-08 remains Proposed** with an explicit status note that acceptance is gated on
  the reviewer/operator ruling on this ownership model (OQ-6 reworded).

## Files changed (round 3)
- `HE-TOOLSTACK-TECHNICAL-DESIGN.md` v1.4 — §8.8 full rewrite + §8.8a–c (flock, flock
  semantics, supersede/heartbeat, acquisition policy, boundaries), §7.5 submissions-inbox
  rewrite, §8.2 note, **new §8.4b ownership/transaction table**, §6.1/§6.2/§6.7 synced,
  D1 (toolserver DB edge + zero-publish label) / D2 (submissions inbox) labels, §14 pointer.
- `HE-TOOLSTACK-REQUIREMENTS.md` v1.5 — FR-26 arbiter named; T-20/T-21 restated; **T-23
  added**; disambiguation note; matrix rows + T-23.
- `HE-TOOLSTACK-ADR.md` v1.4 — **ADR-D-08 A1 rewritten** (inbox model, options 1–3
  evaluated, C rejected), status note on the record; OQ-6 reworded.
- `HE-TOOLSTACK-QA-REPORT.md` — Q5/Q18/Q20/Q22 evidence refreshed; **new Q23**
  (ownership-coherence gate: grep-verifies no doc grants the toolserver a `queue` UPDATE
  and that §8.8 never calls rename/O_EXCL a lock/CAS); totals updated.
- Diagrams: D1 (toolserver edge → INSERT-submissions-only), D2 (submissions inbox label);
  state-flow (claims) already labels flock from r2 — verified.

## Remaining risks & decisions
1. **ADR-D-08 (r3 A1) = OQ-6: reviewer/operator accept required.** Proposed, not assumed.
   *[2026-11-16: operator ruled — A1 **accepted**, OQ-6 closed; see Appendix E and ADR D-08/OQ-6.]*
2. **flock is advisory**: a hand-edited ticket that bypasses `he ticket` invalidates the
   guarantee — documented boundary, enforcement is a Stage-E code-lint item, not a DB
   constraint.
3. Non-Local filesystems break flock (same class as SQLite) — stated and out of scope.
4. T-20/T-21/T-23 remain **[P]** until Stage-B/C; nothing in this appendix is runtime
   evidence.
5. Stale-claim heartbeat tuning (30 min default) stays **[P]**.

## Disposition
Both round-3 findings accepted; corrections applied documentation-only. **STOP per §10
remains in force:** nothing implemented, deployed, merged, or closed.

---

# Appendix D — Round-5 response (2026-11-16): "Backup, MinIO versioning, OneDrive, and restore"

Documentation-only, same discipline. Scope-inspected first (TD §§5.4a/6.9/9.1/9.2/9.4/12.2/D8, REQ NFR-17/19/22 + T-11/T-18, ADR-D-12/D-14, this file's FINDING-05 row).

| # | Correction | Disposition | Where |
|---|-----------|-------------|-------|
| A | Cross-FS "atomic rename" was false (ext4→`/mnt/c` cannot rename atomically — different superblocks; the earlier text conflated ext4 rename atomicity with the cross-boundary case) | **ACCEPTED — corrected** | TD §6.9.2: copy into `$ROOT/.candidate-<runid>/` → verify EVERY destination digest → write `DONE.json` inside the candidate → rename **within the NTFS volume** → `prune_retention` after DONE (A1's prune-before-DONE ordering was itself a correctness bug — a pruned newest-with-no-DONE set could leave zero sources). Interrupted run = candidate without DONE ⇒ never eligible; `.candidate-*` stale past one cadence → ledger line → `.quarantine/`; robocopy is the resume engine (digest-skip). §5.4a gets a boundary note limiting all rename guarantees to same-FS ext4. Solver I/O stays on ext4 — `heat-data` untouched as working dir, `/mnt/c` appears ONLY as backup destination (D-14 root unchanged, verbatim) |
| B | `mc mirror` + `--overwrite` does NOT preserve noncurrent versions or versioning config — the r2 claim was asserted, not verified | **ACCEPTED — retracted, mechanism replaced, fallback recorded not adopted** | TD §6.9.3: bucket versioning stays (D-12); nightly ships objects (rclone server-side copy) + **all version payloads** (rclone `--s3-versions`, payload-per-version layout; restore-site semantics = re-upload as new versions, original VersionIds don't survive — honest capability statement) + `mc ls --versions --json` manifest + bucket config capture. **T-22 is the falsifiable runtime test** (version count + digest + restore-through-staging per object); export failure ⇒ **OQ-8** (latest-only + explicit NFR-17 relaxation *decision*) recorded **required-if-triggered, not adopted** — no silent weakening. Deployed-version confirmation itself is a runtime task: vendor docs say versions are not currently replicated by `mc mirror`; no deployed version was probed (nothing is deployed) |
| C | `attrib`/`sync_status` OneDrive proof was a placeholder | **ACCEPTED — replaced with an honest ladder + open OQ** | TD §6.9.4: L1 exists-in-WSL-dir / L2 copied+digest-verified locally (**all `DONE.json` proves**) / L3 placeholder attrs = **negative-only** (set ⇒ not uploaded; clear ⇒ still unproven; `attrib -r` is not an upload tool) / L4 OneDrive-processed / L5 remote read-back. **Design-time inventory verdict: this environment has no credential-free automated L4/L5 signal today** — stated explicitly; NFR-19/RPO reclassified: *local-completion RPO* until **OQ-9** resolves (A: manual web read-back ritual + R-8(ii) 7-day staleness nudge [M0 default]; B: Graph app registration for automated L5). §9.4 line rewritten accordingly |
| D | NFR-22/T-11 "while jobs run" contradicted §6.9 refuse-mode and contradicts application-consistency (solver output changes mid-copy) | **ACCEPTED — one policy: quiesce-and-wait** | TD §6.9.1 behavior matrix (running-at-start → wait, bounded, no force-kill; submitted-during → 409 `backup_paused` via pause file, §6.2 + §8.7 rows added; starts-after-check → impossible, admission serialized on the pause gate; crash → lock released with the process, candidate never eligible; incomplete-run restore → §9.6 reconciliation, orphan quarantine). Proven live-state snapshot (LVM-thin etc.) does not exist on this WSLv2 layout — **not assumed**; `--allow-active` withdrawn (it never shipped — text claimed a flag the design had not described). Tradeoff stated: nightly window may push past cadence under long batch. NFR-22 + T-11 + T-18 + T-08 rewritten to test the policy |
| E | Restore proof | **ACCEPTED — specified, and T-11 explicitly NOT claimed** | TD §9.6: restore drill from the canonical destination with 8-point acceptance (immutable-DB verify (WAL/SHM not restorable by design — the DB is immutable while a run is held); run-state/job-state reconciliation; artifact digest vs `manifest.json`; MinIO object + version-history check per the chosen mechanism; git repo/bundle recovery; DONE+manifest integrity; OneDrive read-back evidence per OQ-9 outcome; post-restart reconciliation at steady state). "T-11 passed" requires executed evidence; the QA report states none has been executed and never will be by a doc change |

Counts verified at commit time (measured, not asserted): TD top-level sections **19** (9.6 is a subsection of §9; §6.9 gained subsections 6.9.1–6.9.4); REQ test register **T-01…T-23** unchanged in size — T-11/T-18/T-08 **rewritten** and **T-22 rewritten** (it existed since r3; r5 replaced its false `mc mirror` premise, it was not newly added); QA gates 23→**24** (Q24 backup-coherence added this round). Residual risk is deliberately kept in the docs: OQ-8/OQ-9/D-15/D-16 all still open, RPO is explicitly local-only for now — the review's whole point was that unproven claims were being designed around as proven.

## Disposition (r5)
All five items accepted; corrections applied documentation-only — no scripts written, OneDrive not touched,
no backup/drill run, nothing deployed, merged, or closed. **STOP per §10 remains in force.**

---

# Appendix E — Round-6: operator rulings recorded (2026-11-16)

**Decision brief delivered 2026-11-16; operator rulings received the same day, verbatim:**

| # | Ruling | Recorded as |
|---|--------|-------------|
| D-15 bind topology | dedicated `he-agent` compose network, members only toolserver + Hermes agent | **ADR D-15 → ACCEPTED (Option D)**; TD §5.5 + §17.1 mirror; OQ-5 CLOSED; residual MinIO 127.0.0.1-bind gateway reachability stands as documented, credential-gated (probes r2) |
| D-16 spawn privilege | scoped spawn-sidecar | **ADR D-16 → ACCEPTED (Option B)**; 4-method API over `he-internal`; server-side policy enforcement (digest-pinned allow-list, network=none, cap_drop=ALL, non-root, CPU/mem ceilings, mount-prefix restriction); OQ-7 CLOSED |
| ADR-D-08 / OQ-6 | Accept A1 → §8.4b/§7.5/§6.1 freeze as written | **ADR D-08 + Amendment A1 → ACCEPTED**; OQ-6 CLOSED; toolserver sole writer of `submissions` only; T-23 [P] stays the acceptance gate (documentation acceptance ≠ runtime proof) |
| OQ-9 OneDrive proof | manual ritual | **RULED — Option A**: quarterly manual web read-back ritual [M0] per TD §6.9.4; no Graph API app registration at M0 |
| OQ-8 MinIO version fallback | no action until T-22 reports | **CONFIRMED**: required-if-triggered fallback, not adopted; activates only if T-22 shows rclone `--s3-versions` insufficient |

**Documentation changes (this round, docs-only):** ADR status blocks D-15/D-16/D-08 (+A1) flipped
Proposed→Accepted with `DECIDED 2026-11-16 (operator ruling)` provenance; ADR OQ register rows
OQ-5/6/7 → CLOSED, OQ-9 → RULED, OQ-8 → CONFIRMED-contingent; TD header, §5.5 matrix note,
§6.9.4, and §17.1 mirror rows updated; QA +Q25 decision-integrity gate (locks the flips against
regression): **25/25 PASS, 0 FAILS**; Mermaid revalidated 9/9.

**What these rulings do NOT change:** no implementation or deployment was performed; [PRE-M0]/[P]
markers stay; T-20/T-21/T-22/T-23 remain unexecuted; acceptance of A1 is a design-contract
acceptance only — T-23 must still pass at Stage B before the contract is runtime-evidenced.

**Open items remaining after round 6 (superseded by the 2026-11-17 ruling — OQ-1 was RULED CLOSED that day, ADR-D-02 accepted as written; retained as round-6-era text):** OQ-1 (ADR-D-02 files-first + tripwires posture) was then the
only open **M0-freeze-blocking** operator decision (target: M0 design freeze). OQ-2 (GB10
exclusion — D-11 Proposed) targets Stage A; OQ-3 (RTX 5060 Ti co-scheduling re-measure) gates
GPU-class enablement; OQ-4 is not an M0 blocker. ADR records remaining Proposed at that time: D-02 (since Accepted 2026-11-17), D-06,
D-07, D-11, D-17, D-18 (all carry recommendations; their sign-off tracks the OQs above).

## Disposition (r6)
Five operator decisions recorded verbatim into the registers, documentation-only — nothing
implemented, deployed, merged, or closed. **STOP per §10 remains in force for
implementation/deployment; the next operator action is OQ-1. **[2026-11-17: that action was taken — OQ-1 RULED, ADR-D-02 accepted as written; see ADR §4 and Appendix F.]**

---

## Appendix F — Round-7 correction: agent connectivity & network isolation (docs-only, 2026-11-16)

Reviewer item-by-item:

- **A — measured facts preserved.** The four probe facts (agent-netns loopback refused;
  `host.docker.internal:8100` refused in the measured r2 environment; `172.17.0.1:8100`
  reachable **when a port was published**; host publication pattern `127.0.0.1:8100:8100`
  as the then-model) remain recorded as [V]-tagged measurement history in TD §5.1, the ADR-D-15
  Context block, and this response's r2 text. No fact was deleted; conclusions drawn from them
  were corrected.
- **B — bind vs publish separated.** Two named settings, one concept each: **inside-container
  listen address** `TS_BIND=0.0.0.0` (TD §6.1/§11.6 layer 1 — Docker's forwarding path cannot
  reach a loopback in-namespace bind; not exposure) vs **host publication** (TD §11.6 layer 2 —
  none exists for :8100; any host `:8100` listener = preflight failure). The old single
  `TS_BIND=127.0.0.1` conflated the two namespaces — corrected in §6.1, §11.3, §11.6.
- **C — boundary proven by mechanism, tested by matrix.** New TD §5.4b **T-15 six-leg matrix**
  (agent member / default-bridge peer / compose-net peer / host-local / LAN-side / other bridges),
  each leg with source namespace, destination, expected result, and enforcement mechanism.
  Expectations are structural (zero host listener + named-network membership), so the peer
  negative legs are defensible **without** relying on loopback binding — the reviewer's point
  that loopback ≠ authZ is now an explicit anti-claim guard in the table. Leg 3 (compose-net)
  is marked the design's discriminating test. **NFR-07 acceptance is conditional on executing
  this matrix at M0 — no claim of satisfaction before execution.**
- **D — operator decision preserved.** ADR-D-15 records the ruling (Option D, 2026-11-16) with
  full measurement provenance; this appendix records what the gateway route proves (published
  ports are gateway-reachable engine-wide, so option C fails isolation by construction) vs what
  it doesn't (it never proved membership control works — that is the zero-publish demonstration
  [V 2026-11-16] plus the M0 matrix). Nothing was newly approved here; r6's ruling stands, r7
  corrected the reasoning text around it.
- **E — diagrams & text aligned.** D1 (agent→`http://toolserver:8100` over he-agent, zero
  publish) and D4 caption (no inbound claims beyond mechanism-derived, to-be-executed matrix)
  updated; §7.1 stale `Base http://127.0.0.1:8100` → `http://toolserver:8100`; §10.2/R rows now
  state membership is access control, not authN. No normative success requirement references
  `host.docker.internal:8100` anywhere; remaining mentions are retraction/probe history.

**Reviewer-cited "REQ NFR-16":** in the REQ registry NFR-16 is digest-on-artifacts (untouched —
not network-related). The connectivity/trust items the review targets are **NFR-07, T-15, T-17**
and the traceability rows citing them; all corrected under r7. Flagged for mapping confirmation. **CLOSED 2026-11-17: operator confirmed the mapping ("NFR-16 mapping confirmed") — the brief's item maps to NFR-07/T-15/T-17, our NFR-16 stays digest-on-artifacts and untouched.**

Files changed this round: TD v1.6→v1.7 (§5.4b matrix, §6.1, §7.1, §10.2 risk row, §11.3, §11.6,
D1/D4 captions); REQ v1.6→v1.7 (NFR-07 rewrite, T-15 six-leg restatement); ADR v1.6→v1.7
(§5 intro annotation, D-15 record unchanged — ruling already recorded); this response
(FINDING-01 row annotation, hygiene-line annotation, Appendix F). **STOP per §10 remains in
force: no network configuration, firewall, Docker network, container, or deployment-script
change was made or will be before approval; PR #11 stays open and unmerged.**

**Operator acceptance (2026-11-17):** the operator ACCEPTED the r7 corrections as written ("r7 accepted") and CONFIRMED the NFR-16 mapping above — closing this appendix operator-side. NFR-07's satisfaction stays conditional on the T-15 six-leg matrix at M0 by the operator's own ruling; reviewer-independent re-review of v1.7 (if the reviewers issue one) remains their prerogative, and this acceptance is by the operator, not of the reviewers.
