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
| FINDING-01 — loopback/`host.docker.internal` networking claim unverifiable | **ACCEPTED — fixed with measured evidence** | REQ NFR-07 rewrite, FR-01 client URL; TD §6.4, §10 network rows; ADR-D-01 amendment + **new ADR-D-15 (operator decision requested)** | Live probe from inside a container: `172.17.0.1:8100` reachable; `host.docker.internal` resolved to `192.168.65.254` and got ConnectionRefused on loopback services. Design now specifies the bridge-gateway form + published-port pattern `127.0.0.1:PORT:PORT` (no `0.0.0.0` exposure — NFR-07 conflict removed). Final bind-address choice = **D-15, yours**. GitHub #2 |
| FINDING-02 — container lifecycle ownership undefined | **ACCEPTED — fixed** | TD new §6.10 (lifecycle classes A/B/X), D9 diagram (validated), janitor rules, shutdown order, reconcile-on-start; REQ NFR-10 rewrite | Every container now has exactly one named owner across compose-managed / engine-spawned / host-timer classes; expired containers ≤15 min kept for log capture then reaped. GitHub #3 |
| FINDING-03 — Docker-socket privilege placement | **ACCEPTED — fixed; recommendation only, decision yours** | TD §6.2 (engine never sees a socket under any option), §5.4b security-boundary table, §13.1 spawn-seam code layout; **ADR-D-16 (3-option comparison, operator decision requested)** | Honest framing kept: a sidecar redistributes privilege, it does not remove it. Review §5.3 side-effect areas covered: uid alignment, audit logging, allow-list enforcement point. GitHub #4 |
| FINDING-04 — SQLite single-writer claim vs read path | **ACCEPTED — fixed** | TD §6.7 writer-ownership table per DB, §8.8 claim protocol (BEGIN IMMEDIATE + version check), WAL mode stated; REQ NFR-09 amended | One writer per file, readers via WAL; concurrent-session claim race is now a specified protocol with test T-12 + property check. GitHub #5 |
| FINDING-05 — backup atomicity/consistency (hot SQLite, OneDrive) | **ACCEPTED — fixed** | TD new §6.9 host backup job (sqlite `.backup` API → staging → manifest → fsync → rename → DONE), RPO/RTO stated, OneDrive staleness alarm `backup_stale`; REQ NFR-22 amended, NFR-19 cross-ref; ADR-D-14 A1 amendment; T-18 drill | The review's durability demand is met with primitives named explicitly (`sqlite3 .backup`, fsync+atomic rename, write-ahead manifest ordering §5.4a). GitHub #6 |
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
  control.
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
