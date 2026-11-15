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
