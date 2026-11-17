# HE-toolstack Architecture Decision Register (ADR)

**Document:** `HE-TOOLSTACK-ADR.md` · v1.7 (rev 2026-11-16 r7: r2-era filing-time lines annotated where superseded by the r6 rulings; records themselves unchanged. v1.6 r6: **operator rulings recorded** — D-15 approved as Option D (he-agent net), D-16 approved as Option B (spawn-sidecar), ADR-D-08 A1 accepted, OQ-9 ruled Option A (manual ritual), OQ-8 confirmed contingent-on-T-22; prior r5: ADR-D-14 **A2** — mirror-history + ADR-D-14 **A2** — mirror-history + atomic-cross-FS-rename + OneDrive-sync-status claims corrected, quiesce-and-wait policy ruled, OQ-8/OQ-9 opened; prior r3: ADR-D-08 A1 reworded to the submissions-inbox model (r2 per-table split withdrawn as self-contradictory); OQ-6 synced. Prior rev 2026-11-15b: review-response 2 — D-15 probe-matrix correction [V re-probe 15b], D-16 points at TD §6.2b normative API; prior v1.2: response 1 — D-01/D-08/D-14 A1, +D-15…D-18; prior v1.1: +D-14 backup root) · 2026-11-14
**Status:** Living register (Phase 2 deliverable B of DesignStandards §8). Updates are ledger-
backed commits; superseded ADRs stay visible with status `Superseded by …`.
**Companion:** `HE-TOOLSTACK-TECHNICAL-DESIGN.md` §17 summarizes this register; requirement
IDs referenced here are defined in `HE-TOOLSTACK-REQUIREMENTS.md`.
**Evidence tags:** [V] live probe 2026-11-14 · [E] PD-toolstack evidence artifact ·
[P] proposal in this design · [U] unverified assumption. `SA` = STACK-AS-BUILT.md,
`SD` = STACK-DESIGN-v3.md (v3.8.1), `P1` = docs/PHASE1-ARCHITECTURE-DISCOVERY.md @141249d.

Decision provenance classes, stated up front because reviewers must be able to audit them:
- **User-rulled**: accepted by Steven (chat ruling, 2026-11-14, recorded verbatim where quoted).
- **Inherited**: accepted in attempt-1 (PD-toolstack) documentation and carried forward because
  the evidence behind it still holds.
- **Proposed**: recommended by this design, **not yet accepted** — each needs explicit sign-off.

---

## 1. Accepted decisions

### ADR-D-01 — One Docker Compose application owns all stack services, including MinIO
- **Status:** Accepted (user ruling 2026-11-14, one of the five pivot observations)
- **Context:** Attempt-1 ended with an orphaned MinIO (`infra-minio-1`, compose project
  `infra`, no consumer) while the "real" stack was scaffolded elsewhere; MinIO had actually
  *worked* (backup/restore drill passed, SA Stage A) and still became dead infrastructure.
- **Alternatives:** (a) infra kept separate "for stability"; (b) managed/external object store;
  (c) no object store, filesystem only.
- **Evaluation criteria:** lifecycle integrity (what breaks when lifecycle ≠ ownership);
  portability invariant; operational surface.
- **Decision:** single compose project = single lifecycle. `make down` ⇒ zero stack
  containers (M0 acceptance). MinIO is `minio` service in that project.
- **Rationale:** the observed failure mode was ownership, not technology [E C4]. A separate
  "infra" project is exactly the seam where orphans form.
- **Consequences:** bring-up ordering and healthchecks become this project's problem (§11
  tech design); teardown must copy bucket contents before host-orphan removal (ticket C3).
- **Risks:** compose-project growth temptation (solved by profiles, NFR-10); single project =
  one bad healthcheck can block `up` (mitigated: profiles + `depends_on` conditions).
- **Amendment A1 (2026-11-15, FINDING-02, GitHub #3; supersedes the blanket "owns every
  service" reading, decision history preserved):** compose owns the **long-running services**
  (6 services incl. MinIO): start/stop/health/restart. **One-shot job containers are
  engine-owned** — created through the Docker API with label `he-stack=1`, lifecycle class J
  (§6.10): create→run→exit-record→janitor sweep; graceful shutdown SIGTERMs running jobs and
  records `interrupted` *before* compose stops services. The **host backup timer is a declared
  infrastructure exception** (class X, §6.9), never a stack dependency. `docker compose down`
  removes only compose-managed containers — that is its real scope; `make down` = compose down
  **+ janitor sweep**, and the zero-container acceptance (T-13) is asserted over classes C∪J
  union. The architecture no longer claims compose owns what it does not manage.
- **Revisit when:** stack outgrows one host (multi-node compose/swarm — not planned before
  M3+) or object store requirements exceed MinIO (none identified).
- **References:** SA §infra + restore-drill rows; `pd-analysis/infra/minio-compose.yml` [E];
  P1 §4 C4; NFR-01/10, FR-29/T-11/T-13.

### ADR-D-02 — Workflow control = externalized files + ~200-line runner; no orchestration framework in the initial release
- **Status:** **Proposed** (awaiting explicit sign-off — see §4 OQ-1)
- **Context:** v3 leaned toward LangGraph; research during the pivot (session
  `20261114_133606_df5042`) established: LangGraph's self-healing resume requires
  *durable-execution* infrastructure (Temporal-class platform) the stack does not have; the
  checkpoint-pattern literature (O'Reilly) achieves resume from lost context with
  serialized state + step identifiers alone. Attempt-1's hard-won practice — claim/done
  ticket files + append-only ledger — already implements 80% of it. User ruling: prior plan
  "not iterative enough to be feasible within context-window limits".
- **Alternatives:** (a) LangGraph + checkpointer on SQLite (resume works only for
  graph-internal state; agent-context loss still needs external files); (b) Temporal (adds
  a server class the stack can't yet operate); (c) pure cron + files (no job API).
- **Evaluation criteria:** survives total agent-context loss (FR-36); ~1 operator; M0-sized
  surface; zero framework lock-in.
- **Decision:** `workflows/` (tickets, state.json, ledger) + SQLite queue/registry + a thin
  runner is the workflow engine. Named tripwires that force re-evaluation toward a framework:
  parallel fan-out of >1 workflow, durable multi-day waits, or supervision (restart policy)
  beyond compose's own.
- **Rationale:** the guarantee we need (resume from files after context loss) is precisely
  what checkpointing gives and durable-exec platforms give *in addition to* what we don't
  want to operate. [P] + refs in P1 §5 D-02.
- **Consequences:** we own the runner (~200 LOC) and its tests (T-02/T-05/T-07); engine
  semantics are file-system semantics + write-ahead ordering (D-05).
- **Risks:** hand-rolled runner bugs (mitigated: crash matrix T-07 is a required M0 artifact);
  scope creep toward Temporal features (mitigated: tripwire text).
- **Revisit when:** a tripwire fires, or M3 optimizer parallelism needs real fan-out.
- **References:** LangGraph OSS resume docs; O'Reilly checkpoint-pattern article; AWS
  durable-execution docs (comparison set); Stage-E claim/done practice [E SA]; FR-23–26/36.

### ADR-D-03 — gpu-broker stays deleted: queue serialization + admission, no broker daemon
- **Status:** Accepted (v3.2 ruling [E SD], re-affirmed by user via D-04 ruling 2026-11-14)
- **Context:** DESIGN-v2 draft (pre-Phase-1) falsely listed gpu-broker as a carried-forward
  code asset; Phase 1 verified **no broker code ever shipped** — it was deleted by ruling
  before Stage E, and GPU jobs never ran (A4: all evidence CPU-only).
- **Alternatives:** (a) rebuild the deleted broker as a service; (b) serialize inside the
  workflow-engine dispatcher.
- **Evaluation criteria:** mechanisms must exist where code exists (DesignStandards source
  integrity); one-writer discipline; operator count.
- **Decision:** serialization = property of the queue (max-concurrency per class); admission
  check = function in the dispatcher (FR-16/17). No daemon, no extra API, no lease protocol.
- **Rationale:** a broker daemon is only justified by multi-host leases (M3+); a single-host
  queue already gives one-writer ordering. Re-introducing a deleted component without its
  justification reproduces attempt-1's phantom-component failure (C1).
- **Consequences:** lease semantics reduce to "dispatcher picks next job"; worker seam (NFR-05)
  keeps the multi-host door open without it being load-bearing.
- **Risks:** dispatcher becomes a god-object later (mitigated: `Worker` seam review at M2).
- **Revisit when:** second physical worker registers (then leases re-enter as an ADR).
- **References:** SD v3.2 deletion ruling [E]; P1 §4 C1/C3; session search 12.7K-char
  gpu-broker record; FR-16–19.

### ADR-D-04 — GPU compute tier: shared RTX 5060 Ti with hard budget (Option B)
- **Status:** **Accepted** (user ruling 2026-11-14: "My decision for D-04 is option B")
- **Context:** v3 assumed gpu1 (DGX Spark) + gpu2 (5090, never purchased) as compute workers.
  Phase 1 verified: gpu1 = GB10 **ARM64** running sglang (LLM duty; can't run our amd64
  images) [V]; the only CUDA device is the host's RTX 5060 Ti 16 GB, shared with pinned
  Ollama embeddings (≈4.98 GiB closed area) [E]; and `nvidia-smi` over SSH returned **no
  rows** this pass (C6 — card state must be re-measured before GPU acceptance) [V].
- **Alternatives considered:** (A) CPU-only for the whole initial release; (B) shared GPU
  with hard budget (chosen); (C) GPU made exclusive to the stack (rejected: would evict
  embeddings, breaking the memory subsystem this agent runs on); (D) buy hardware (rejected:
  no evidence a GPU job is on the critical path).
- **Evaluation criteria:** does not endanger co-resident LLM/embeddings service; no
  milestone depends on an unverified premise; budget math visible, enforced at admission.
- **Decision:** one concurrent GPU-class job; per-job VRAM ceiling **8 GiB**; admission
  refuses below **5.5 GiB protected floor**; GPU class **inert until ticket C6 passes**
  (re-measure + driver floor ≥591.59 for sm_120, per D7 lesson); **no M0–M2 acceptance
  criterion may depend on GPU**. The two GiB numbers are D-04 defaults — Phase 2 review may
  adjust them; C6 is prerequisite either way.
- **Rationale:** user chose Option B as explained: queue/admission machinery is built from
  day one (it's the same machinery as the CPU queue), but the class stays switched off until
  hardware state is re-verified — zero schedule risk, zero contention risk, no phantom GPU.
- **Consequences:** VRAM admission tests run against simulated numbers (T-06) until C6;
  all physics evidence stays CPU-class (FR-19), preserving A4 consistency.
- **Risks:** WSL GPU passthrough state volatility (C6 is that risk materialized — contingency:
  Option A remains available at any time since nothing depends on GPU); sm_120 wheel
  availability for pytorch-class probes [U].
- **Revisit when:** C6 evidence lands (numbers may be re-baselined); a second CUDA worker is
  proposed (needs D14 arch check + ADR-D-03 revisit).
- **References:** P1 §1.2/§4 C5–C6, §5 D-04; SA D7 (driver floor), B5.1 (embeddings);
  FR-16–19, NFR-21, OR-02.

### ADR-D-05 — Canonical state owner: host directory `/home/steven/HE-toolstack/heat-data`, write-ahead ordering normative (Option 1)
- **Status:** **Accepted** (user ruling 2026-11-14: "My decision for D05 is Option 1")
- **Context:** a single run today spans three filesystems (container scratch, host tree,
  git remote) with no declared owner; D25 showed state/artifact divergence when ownership is
  implicit; docker-run uid friction forced a chown workaround [E A1]; host data disk is
  `/dev/sdf` ext4 1 TB, 813 GB free, where Docker itself already stores bind-mount-backed
  data [V]; `/mnt/c` is 28–39× slower for solver I/O [E D9 measurement].
- **Alternatives:** (2) named Docker volumes (hides data behind dockerd, restore = tar
  surgery); (3) MinIO-as-hot-store (network hop per solver scratch I/O; object store is the
  wrong shape for per-step working files).
- **Evaluation criteria:** crash-consistency without distributed transactions; uid alignment
  (kills the chown workaround); cold-session inspectability (`ls`/`jq`, no client library);
  performance on ext4.
- **Decision:** host dir owns run state, bind-mounted into services. **Write-ahead ordering
  is normative:** (1) artifacts written + fsync → (2) state.json atomic rename → (3) ledger
  append + git push. Agent scratch dirs are **non-authoritative by definition** — deletable
  without asking. Crash windows: between 1–2 ⇒ artifacts swept as `abandoned` (quarantine,
  not delete); between 2–3 ⇒ resume detects committed state, unpushed ledger replays safely
  (append-only + idempotency keys).
- **Rationale:** one authoritative filesystem + git-for-evidence collapses the three-
  filesystem problem into a known crash-consistency protocol; uid 1000 ownership removes the
  documented workaround; user cleanup observation becomes enforceable (scratch deletion is
  *defined* safe).
- **Consequences:** compose carries bind mounts + uid config; promote path to MinIO is
  explicit (FR-29: gate-passed + ledger + dataset tier only); backup = heat-data + git,
  destination fixed by D-14 (canonical backup root).
- **Risks:** host-dir discipline drift (manual edits) — mitigated by manifest digest checks
  (NFR-16); single disk is SPOF (risk register R-07; versioned MinIO tier is the copy).
- **Revisit when:** state outgrows one disk, or multi-host workers force a shared FS
  (M3+ ADR).
- **References:** P1 §1.3/§5 D-05; host probes [V] (findmnt/docker inspect); SA D9/D25;
  FR-24/27/28/38, NFR-16; tech design §8–9/§12.

### ADR-D-06 — physics-gate: keep the script methodology, expose one endpoint
- **Status:** Proposed (sign-off needed)
- **Context:** attempt-1's gate is methodology + scripts (gate.py + probes + negative test),
  proven end-to-end (D2) — *not* a service; DESIGN-v2 draft overstated it as "FastAPI,
  entropy-residual verdicts" (C2).
- **Decision:** methodology ships inside the images; toolserver exposes
  `POST /gate/run` as a convenience wrapper; the endpoint adds no validation logic of its
  own — it runs the committed scripts and stores the report.
- **Alternatives:** full gate service (more surface, no new capability); agent runs gate ad
  hoc (what attempt-1 did; no enforcement point).
- **Rationale:** the value proven in D2 is the *checklist + negative test*, not a daemon;
  one endpoint gives FR-20's enforcement (no `succeeded` without a gate report) without a
  phantom service.
- **Consequences/Risks:** thin wrapper drift from scripts (mitigated: wrapper is 1:1 exec of
  repo scripts, T-03 runs both paths).
- **Revisit when:** gate checks grow beyond scripts (multiple engines/cadence tiers).
- **References:** SA D2 gate rows [E]; P1 §4 C2; FR-20–22.

### ADR-D-07 — Artifact layout: hot host dir, promoted immutable tier in MinIO
- **Status:** Proposed (flows from accepted D-01/D-05)
- **Decision:** `heat-data/runs/<run-id>/` hot; MinIO receives gate-passed artifacts +
  ledger + dataset tier with object versioning; scratch non-authoritative (D-05). Retention:
  hot tier kept per-run-size budget, promoted tier kept indefinitely, scratch deletable
  always; exact budgets = open item OR-04 (measure M1, no invented numbers).
- **Rationale:** preserves the *only proven* backup/restore discipline from attempt-1 while
  not putting network storage in the solver hot path.
- **References:** SA restore drill [E]; FR-29, NFR-17, T-11.

### ADR-D-08 — One SQLite (run registry + queue + lease-state) co-located with the workflow engine
- **Status:** **ACCEPTED incl. Amendment A1 by operator ruling 2026-11-16 — OQ-6 closed; §8.4b/§7.5/§6.1 freeze as written (T-23 = acceptance test).**
- **Decision/rationale (r3 status note, now resolved: the A1 model below was explicitly accepted
  by the operator 2026-11-16):** WAL-mode SQLite is the minimum durability primitive that already
  exists in the runtime; three stores (queue + registry + lease) would triple the
  consistency problem D-05 just collapsed. Contention at single-operator write rates is
  negligible [P]. Alternatives: Postgres (extra service to operate, deferred — compose
  profile exists for it), separate queue (Redis — rejected: durability requires AOF
  gymnastics SQLite gives by default).
- **Amendment A1 (r3 rewrite, 2026-11-16 — reviewer round-3 finding accepted; resolution of OQ-6;
  ACCEPTED by operator ruling 2026-11-16):** the r2 model
  ("one writer per table; toolserver sole writer of `queue` + `idempotency_keys`") was
  **internally contradictory** — TD §7.5 simultaneously granted the engine an
  `UPDATE queue SET state='claimed'…` operation, so two processes wrote `queue` while two
  other sections asserted per-table single-writer. Withdrawn. **Model now (reviewer option
  2, explicit inbox):** toolserver's *only* write anywhere in the engine DB is `INSERT INTO
  submissions(id, kind, payload_json, idempotency_key UNIQUE, …)`; the engine consumes each
  row in ONE `BEGIN IMMEDIATE` transaction — dedup `idempotency_key` against
  `idempotency_keys` (authoritative dedup at consume), `INSERT INTO queue` (+immutable
  job_spec), `DELETE` the consumed submission — commit; and is the **sole writer of every
  other table including `queue`** (transitions: `BEGIN IMMEDIATE` + affected-rows==1
  conditional updates). WAL admits **one committer db-wide**; ownership is an application
  convention the DB does not enforce; `busy_timeout` (5 s) buys wait-time, **not fairness**
  — bounded retries, then honest `503`. Crash windows: submission-not-yet-consumed ⇒
  replay-safe via key; consumed ⇒ queue row exists in the same commit (half-consumed
  impossible); duplicate execution prevented by single dispatcher + conditional
  transitions. Normative table: TD §8.4b; API path: TD §7.5. Rejected B (engine-internal
  enqueue API) unchanged: adds a hop + engine-liveness hostage on the submit path (against
  the FINDING-06 degraded posture). Rejected C (r3): dual-writer ON `queue` itself with
  operation-level ownership — deliberately NOT accepted: no benefit over the inbox at equal
  WAL contention, and it keeps the contradiction surface.
- **Revisit:** fleet or >1 writer → Postgres profile flips on. **Refs:** FR-30/33, NFR-02;
  P1 §5 D-08.

### ADR-D-09 — `he` client in the agent container over HTTP/JSON; no MCP
- **Status:** Accepted (inherited: v3.8.1 ruling [E SD], unchanged by Phase 1 evidence)
- **Rationale:** the ruling's reason held empirically — the MCP surface was never needed by
  any executed workflow; HTTP/JSON contract is testable (T-08) and language-agnostic.
  Agent-side convenience stays a thin python client.
- **Revisit:** if a non-HTTP consumer class appears. **Refs:** FR-39; SD v3.8.1 [E].

### ADR-D-10 — No image consolidation: narrow-scope images, one per capability (append-frozen solver images)
- **Status:** **Accepted** (user ruling 2026-11-14 — verbatim: *"I believe more images with
  more narrowly defined scopes will be more maintanable as the established toolstack needs
  to be adapted in the furture."*)
- **Context:** six verified images (measured this pass: openfoam-esi 2.82 GB, agentcad
  1.97 GB, ta-solver-runtime 1.78 GB, gmsh 1.55 GB, calculix 1.0 GB, property-pipeline
  0.31 GB [V]) with incompatible bases (from-source OpenFOAM on noble; python:3.12-slim
  hash-pinned; OCC kernels at differing builds). Both the v1 design ("8 images for 4
  services") and my DESIGN-v2 draft ("consolidate to ≤4") treated count as the problem.
- **Alternatives:** consolidate to ≤4 (rejected); hybrid fold-CoolProp-into-toolserver
  (rejected — user ruling supersedes); status quo + narrow-scope rule (chosen).
- **Evaluation criteria (from the ruling):** maintainability under *future adaptation* —
  the toolstack will change; swaps should touch one image, never a monolith rebuild; blast
  radius per digest; independent rebuildability given from-source recipes that took days
  (D8) and pins whose identity is the provenance (D13).
- **Decision:** the 6 verified images stay as proven; **new capability ⇒ new narrow image**;
  solver images are append-frozen (version bumps of *their* tool only); the v1 defect was
  8 images for 4 services — the corrected invariant is **1 image ↔ 1 capability ↔ 1
  service**. No count cap exists or is required; the compose file grows with services, each
  independently rebuildable.
- **Consequences:** build/CI matrix = per-image checks only (NFR-11 CI); disk grows per
  capability (cheap vs. rebuild risk); bit-identity A/B (FR-22) is the admission gate for
  every image change.
- **Risks:** image sprawl drifts to duplicate tools across images (mitigated: MANIFEST-list
  CI + review checklist item); `pull_policy: never` means each new image needs a host seed
  step (documented, T-13).
- **Revisit when:** a capability is removed (garbage-collect the image), or a registry makes
  count a non-issue anyway.
- **References:** host `docker images` measurements [V 2026-11-14]; SA D8/D13/D14; P1 §4 C5,
  §5 D-10; NFR-09/11, FR-22.

### ADR-D-11 — sglang host (`gx10-9d06`, GB10/ARM64) excluded from the compute tier
- **Status:** Proposed — strongly evidence-backed (accept as part of D-04 sign-off)
- **Rationale:** verified ARM64 [V] vs amd64-only stack images (D14 lesson: TaSMET amd64
  wheels fail on ARM64); its CUDA device is on the LLM's critical path. v3's gpu1-as-worker
  premise is architecturally dead, not merely inconvenient.
- **References:** host probes [V]; SA D14; P1 §4 C4, §5 D-11.

### ADR-D-12 — Physics core migrates as-is (fork, dataset, gate, ledger discipline); patch-0004-equivalent entropy-BC fix is M0 scope
- **Status:** Accepted (direction; user pivot ruling — PD-toolstack evidence is the
  foundation's content)
- **Rationale:** the fork + patches + D2 dataset + gate methodology are the only
  validated-physics assets that exist; rebuilding them would discard attempt-1's entire
  return. Migration = copy + re-verify (bit-identity T-04), not rewrite.
- **References:** user pivot ruling; SA E/E2b; FR-10/22, T-04.

---

## 2. Rejected alternatives (kept visible for audit)

| Alt | Rejected alternative | Rejected by | One-line reason |
|-----|---------------------|-------------|-----------------|
| X-1 | Rebuild gpu-broker as a service | D-03 (ruling honored) | justification was multi-host leases; single host doesn't need it |
| X-2 | LangGraph/Temporal as workflow engine | D-02 (pending final OQ-1) | resume-from-context-loss is a checkpoint pattern; platform cost outweighs function now |
| X-3 | Consolidate images ≤4 | **D-10 user ruling** | narrow scope = adaptability; blast radius per digest |
| X-4 | GPU-exclusive mode | D-04 | evicts embeddings = self-inflicted memory outage |
| X-5 | MinIO as hot solver store | D-05 | network hop in hot path; wrong shape for step files |
| X-6 | Named docker volumes for state | D-05 | hides data from the cold-session contract (`ls`/`jq`) |
| X-7 | gpu1 as compute worker | D-11 | ARM64 vs amd64 images + LLM duty |
| X-8 | /mnt/c (Windows FS) for solver I/O | inherited (D9) | measured 28–39× penalty [E]. Scope note: applies to **hot solver paths only** — cold backup copies to OneDrive (/mnt/c) are ruled separately and accepted (D-14). |

### ADR-D-14 — Canonical backup root = `/mnt/c/Users/steven/OneDrive/Backup/HE-toolstack/`
- **Status:** **Accepted — user ruling, 2026-11-15** ("the design needs to specify … as the root
  directory for all backups")
- **Context:** D-05 makes one host dir (`heat-data`) the single authoritative state owner; D-01 keeps
  MinIO's volume inside it, so backup = one directory tree + the git ledger. TD §9.4 had left the
  destination as the previous project's convention (`/home/steven/backups`, second disk). The owner
  ruled the destination explicitly instead: OneDrive's Backup folder, HE-toolstack subfolder.
- **Ruling (verbatim rule):** every backup artifact of the stack — heat-data mirror, git bundle of
  `workflows/`/ledger, restore-drill evidence — lands **only** under
  `/mnt/c/Users/steven/OneDrive/Backup/HE-toolstack/`. Layout: `heat-data/`, `repo/`, `drills/`.
  Restore reads the same root.
- **Verified fit [V 2026-11-15]:** path exists on the host (`Backup/HE-toolstack/` already present,
  alongside the frozen `Backup/PD-toolstack/` archive); `/mnt/c` is WSL-visible from both host-WSL
  and the Hermes agent container; 841 GB free on C:. Attempt-1's *proven* nightly backup cron already
  targeted the OneDrive root (PHASE1 inventory row 13, restore drill passed) — this rule codifies
  what demonstrably worked.
- **Consequences:** `BACKUP_ROOT` env knob (§11.4) is the single source of the path; timer is a host
  unit, not a compose service (compose stays 100% of stack lifecycle, D-01). OneDrive adds cloud
  versioning + off-site replication at zero extra tooling; the second local disk becomes optional
  extra redundancy, never a restore source.
- **Risks & mitigations:** OneDrive Files-On-Demand placeholders + sync races on a folder rsync
  writes into ⇒ restore procedure forces full download and verifies sha256 vs registry digests
  (D8/R-4 already do digest compare); large heat-data churn could fight OneDrive sync — monitor at
  M1, and if sync proves unreliable the fix is a per-item exclusion or rclone-side copy, decided with
  evidence, not now. 28–39× /mnt/c I/O penalty (D9) does **not** apply: backups are cold sequential
  copies off the hot path (X-8 scope note updated).
- **Amendment A1 (2026-11-15, FINDING-05, GitHub #6 — destination ruling UNCHANGED; procedure hardened):**
  the destination stays exactly as ruled. What the review corrected is the **method**: a plain
  nightly `rsync` of a live tree containing SQLite (WAL), MinIO objects, and active solver
  artifacts can be internally inconsistent even when rsync exits 0, and a silent OneDrive outage
  means the "backup" never left the machine. The backup is now a **6-step application-consistent
  job** (§6.9): (1) preflight (free space ≥2× payload, destination writable, sync client running);
  (2) `jobs` snapshot at `queued` (no force-kill of running jobs); (3) SQLite via the online-backup
  API (WAL-safe; copy ends with a checkpoint) + `PRAGMA integrity_check` on the copy;
  (4) `mc mirror` per bucket + sha256 manifest — `mc` is confirmed inside
  `chainguard/minio@sha256:915a4a…` [V 2026-11-15 probe], no new image; artifacts are copied
  content-addressed, so a concurrent writer cannot corrupt them; (5) **stage on ext4, verify,
  complete atomically**: a directory is a *backup* only once its `_READY/<seq>.json` marker is
  written last; (6) **OneDrive read-back verification** (enum + digest of at least one marker +
  one sample object; `sync_status` recorded) + 7-day retention pruning. Interrupted backups
  self-heal (rsync resumable; incomplete = no marker = never a restore source). Restore sequence
  R-4/R-8 is fixed: **quiesce stack → restore registry + DB (integrity_check) → start services →
  verify manifests → resume** — no split-brain reads of a half-restored tree. New RPO 24 h /
  RTO ≤ 2 h + drill. A successful rsync command is explicitly **not** treated as proof of an
  application-consistent backup.
- **Amendment A2 (2026-11-16, review round 5 — root-path ruling UNCHANGED again; four A1 mechanics corrected):** A1 hardened the procedure but itself asserted three unverified cross-boundary properties and one policy that contradicted TD §6.9. Round-5 corrections, all in TD §6.9/§9.6 (rewritten): **(1) Publish path.** A1 step 5's stage-then-"complete atomically" rename cannot cross ext4 → `/mnt/c` (different filesystems, different superblocks — POSIX rename does not span them). Publication is now copy-to-`$ROOT/.candidate-<runid>/` (robocopy) → **verify every destination file digest against the manifest** → write `DONE.json` inside the candidate → rename **within the NTFS volume** to `<yyyymmdd>.<runid>/`. Interrupted transfers are detected (no DONE ⇒ never a restore source; `.candidate-*` aged past one cadence → `.quarantine/` after a ledger line) and resumed (robocopy skips digest-matching destination files). **(2) Active-job policy.** A1 step 2 ("snapshot at queued, no force-kill") left live solver output changing during copy — not application-consistent by definition. Single M0 policy: **quiesce-and-wait** (§6.9.1: pause file → submissions 409 `backup_paused` → wait active jobs to zero, bounded; else abort); a proven live-state snapshot mechanism (LVM-thin etc.) does not exist on this WSLv2 layout and is NOT assumed. NFR-22/T-11 ("while jobs run") rewritten to match. **(3) OneDrive proof.** A1 step 6's read-back + `sync_status` had no credential-free mechanism behind it — the `attrib` placeholder check is **negative-only** (set ⇒ not yet uploaded; cleared ⇒ still unproven) and robocopy exit 0 proves nothing about OneDrive. TD §6.9.4 now separates L1 exists-in-WSL-dir / L2 copied+verified locally (= what `DONE.json` proves, **nothing more**) / L3 file attributes / L4 OneDrive-processed / L5 remote read-back; **this host environment has no automated L4/L5 signal today — stated explicitly; RPO claims are local-completion RPO until OQ-9 resolves** (manual web read-back ritual [M0] or Graph app registration). **(4) MinIO version history.** A1 step 4's `mc mirror` cannot carry version history (vendor-documented: mirror replicates current object data; versions and bucket versioning config are not replicated). History ships via the **§6.9.3 export** (rclone `--s3-versions` payload-per-version + `mc ls --versions --json` manifest), restore-site semantics = re-upload as new versions; **falsifiable at runtime via T-22**, with OQ-8 recording the honest fallback (latest-only + explicit NFR-17 relaxation) as *required-if-triggered, not adopted*. The A1 line "attempt-1's proven nightly backup cron … restore drill passed" [E] stands as history for PD-toolstack's *plain-copy* design; it neither verified nor can retro-validate these mechanisms.
- **Traces to:** NFR-22 (revised v1.2), NFR-17/19, FR-29; TD §6.9 (rewritten), §9.1/§9.4, §12.2, D8, R-4, R-8.

## 3. Deferred decisions (explicitly not made here)

| D-id | Item | Deferred to | Why |
|------|------|-------------|-----|
| F-1 | API authN/authZ beyond loopback binding | pre-multi-user release | single-operator model (A8); nothing to authorize yet |
| F-2 | Postgres flip for registry | fleet/second-writer trigger | SQLite + WAL sufficient [D-08] |
| F-3 | Observability profile contents (metrics/tracing) | post-M2 ops review | C4 lesson: no infra before traffic |
| F-4 | MinIO retention budgets (GB numbers) | M1, OR-04 | measure growth first |
| F-5 | Registry for images (vs host-seed) | when >2 hosts | A6 status quo is workable single-host |

## 4. Unresolved questions (require human decision at review)

| OQ | Question | Needed by |
|----|----------|-----------|
| OQ-1 | Sign off ADR-D-02 posture (files-first + tripwires) — the only structural decision Phase 1 left *proposed*. | M0 design freeze |
| OQ-2 | Confirm/adjust D-04 numbers at review with C6 data. **2026-11-15 (review §5.3): static reservation alone is inadequate on a SHARED GPU — §6.8 adds a runtime used-memory re-check at dispatch + cuda-use-gate container on the device; GPU admission stays disabled until C6 passes; the accepted sharing decision (D-04) is unchanged.** | GPU-class enablement |
| OQ-3 | Migration stance detail: PD-toolstack evidence repos stay frozen (user ruling says source-of-information only — confirm *read-only mirror* vs *do-not-touch* for the copy-into-registry step, ticket C3). | C3 execution |
| OQ-4 | physics-gate endpoint wrapper (D-06) and registry/SQLite colocation (D-08) acceptance. **2026-11-16: the D-08 half is CLOSED by the operator ruling (ADR-D-08 + A1 Accepted); the D-06 physics-gate half stays open for reviewer sign-off.** | M0 design freeze (D-06 half only) |
| OQ-5 | Job spawn channel. **Decision request ADR-D-16 filed 2026-11-15 (FINDING-03, GitHub #4): recommendation = Option B hardened spawn-sidecar (socket never leaves its container; engine reaches only a 4-method HTTP API; allow-list enforces image pins, network=none, cap-drop, cpuset/mem, masked mounts). Honestly stated: a sidecar is privilege REDISTRIBUTION, not removal — a compromised sidecar is still root-equivalent on the host; what shrinks is the attack surface (4 audited methods vs the whole daemon API) for the container that also holds git PATs and user code. Option A rejected for that reason; Option C rejected for splitting one compose app (D-01). Operator decision required — nothing assumed.** **RULED 2026-11-16: operator selected Option B (scoped spawn-sidecar) — see ADR-D-16 Accepted. CLOSED.** | M0 build start |
| OQ-6 | **Proposed resolution re-filed 2026-11-16 (r3) as ADR-D-08 Amendment A1:** shared-DB with explicit **submissions inbox** — toolserver INSERT-only on `submissions`; engine sole writer of `queue` + everything else; consume under `BEGIN IMMEDIATE` (r2 per-table dual-writer WITHDRAWN — TD §7.5's engine-side queue UPDATE contradicted it). Option B (engine enqueue API) and option C (dual-writer on `queue`) rejected with reasons. **Reviewer/operator verdict required — status Proposed, not Accepted.** **RULED 2026-11-16: operator ACCEPTED A1 — §8.4b/§7.5/§6.1 freeze as written. CLOSED.** | design freeze |
| OQ-7 | **Bind topology** — D-15 (published `127.0.0.1:` ports + gateway-URL clients). Probe matrix (TD §5.4b) shows v1.0 loopback-only publish unreachable from containers, and the Ollama isolation premise in the pre-r2 text is factually false today (host bind `0.0.0.0:11434` [V 15b]). Operator accept required; do not assume approval. **RULED 2026-11-16: operator ACCEPTED Option D (dedicated he-agent network, 8100 unpublished) — see ADR-D-15 Accepted. CLOSED.** | agent reachability vs host-service exposure | operator (Steven) | design freeze |
| OQ-8 | **MinIO version-history fallback (r5).** T-22 must prove the TD §6.9.3 export (payload-per-version + version manifest) at the deployed rclone/MinIO versions — the r2 `mc mirror`-history premise was verified false and retracted. If export sufficiency fails: latest-version-only backup + **explicit NFR-17 relaxation decision**. Lost capability if taken: restoring *superseded* promoted-object versions after total bucket loss (in-app versioning D-12 runtime + git-side promoted copies persist). Recorded *required-if-triggered*; **not adopted** — no silent weakening. **CONFIRMED 2026-11-16 by operator ruling: no action until T-22 reports; fallback activates only on T-22 failure.** | T-22 runtime result | reviewer + operator (Steven) | open (conditional — operator confirmed) |
| OQ-9 | **OneDrive upload-completion proof (L4/L5) (r5).** Design-time host inventory: no credential-free automated signal reaches L4/L5 (TD §6.9.4) — placeholder attrs are negative-only, `DONE.json` stops at L2, robocopy exit 0 stops at L2. Options: **(A, M0 default)** recurring **manual web read-back** ritual logged to `drills/onedrive-readback.log`, R-8(ii) reminds if >7 d stale; **(B)** provision Microsoft **Graph** app registration (delegated token) → automated L5 read-back of the uploaded item. Until one lands, off-host durability — and any RPO resting on it — is **unproven** (NFR-19 says so). Verdict needed: accept A as routine / commission B / explicitly accept host-local durability. **RULED 2026-11-16: operator ACCEPTED Option A — manual web read-back ritual is the standing mechanism (logged to drills/onedrive-readback.log, R-8(ii) staleness nudge >7 d); B may be revisited later, C not taken. Off-host durability remains honest-by-ritual, not automated.** | design freeze | operator (Steven) | **open — RPO honesty depends on it** |

---

## 5. Records filed in the 2026-11-15 architecture-review response

Provenance class at filing: all four **Proposed** (§0 vocabulary). D-15/D-16 changed
security-relevant exposure and privilege and were explicit operator decision requests
(review §7) — **[2026-11-16: operator ruled — D-15 ACCEPTED (Option D), D-16 ACCEPTED
(Option B); see their records and Appendix E of the review response; this filing-time line
is retained for history.]** D-17/D-18 are contract/semantics corrections inside author
authority, marked Proposed pending the independent review.

### ADR-D-15 — Toolserver reach topology: dedicated `he-agent` network, ZERO published ports (FINDING-01; review round-2 item 2)
- **Status:** **ACCEPTED by operator ruling 2026-11-16 — Option D: dedicated `he-agent` compose network whose only members are the toolserver and the Hermes agent container; port 8100 is never published.** (was Proposed — network-topology change class; ruling recorded verbatim from operator). **Date:** 2026-11-15; rewritten 2026-11-16 after the r2 probes below invalidated the earlier draft.
- **Context (all measured, never assumed):** the Hermes agent container runs on Docker-default
  bridge, netns `172.17.0.0/24`. Measured facts that the design must respect:
  1. Agent's own `127.0.0.1:8100` → refused (per-netns loopback — the v1.0 client URL was wrong, FINDING-01) [V 2026-11-15].
  2. A port published `127.0.0.1:` on the host IS reachable from **any** container on the engine
     via the gateway alias (`host.docker.internal`/`192.168.65.254`): same-engine listener
     published loopback-only was hit from an unrelated throwaway container [V 2026-11-16
     probe: 127.0.0.1:8197 published → foreign container → gateway alias **REACHABLE**;
     unused control port refused]. **Loopback publishing therefore provides host/LAN exposure
     control, NOT container isolation** — the earlier draft's claim that same-bridge access
     "rests on the published-loopback bind holding" as an isolation property is **retracted**.
  3. Both `172.17.0.1` and `host.docker.internal` traverse to host listeners from this
     container (rev-a's `hdi refused` reading did not reproduce; retracted, see §5.1 TD) [V].
- **Options:** (A) agent `network_mode: host` — rejected: agent on every host interface,
  violates D-09. (B) join agent to the compose project default network — rejected: puts the
  agent beside workflow-engine/MinIO, violates NFR-07 direction. (C) toolserver published
  `127.0.0.1:8100:8100` + agent client via gateway IP — **superseded by this revision**: probe
  fact 2 shows any unauthorized container reaches it the same way Hermes does, so it fails the
  reviewer's negative requirement by construction. (D) **RECOMMENDED — dedicated
  `he-agent` compose network whose only members are the toolserver service and the Hermes
  agent container; toolserver publishes NOTHING for 8100.** Agent is joined once by the
  operator: `docker network connect <project>_he-agent <hermes-container>` (manual connects do
  not survive agent recreation — re-run after re-creation; `he doctor` checks membership and
  re-runs both probes). Client URL `http://toolserver:8100` via network service DNS,
  `HE_API_BASE` override retained.
- **Demonstration (review r2 item 2 — both directions MEASURED 2026-11-16 on the real engine,
  [V]; equivalents of production names used, throwaway objects removed after):**
  - *authorized:* container multi-homed default-bridge + `docker network connect r2net`
    (equivalent of `he-agent`) → `r2svc:8100` service DNS → TCP connect OK, **HTTP GET 200**.
  - *unauthorized (fresh container, default bridge):* service name unresolvable (`gaierror`),
    gateway alias :8100 → **refused** (nothing published), `172.17.0.1:8100` → **refused**.
    Isolation is structural: there is NO route from a non-member to the port at all — it does
    not depend on a bind flag staying correct.
  - *host-side note (measured):* the WSL host does not route to dedicated-net container IPs
    [V probe: host curl to 172.31.77.2:8100 failed], so host operator health/CLI uses
    `make health` = `docker run --rm --network <project>_he-agent <curl-image> http://toolserver:8100/healthz`
    — consistent with existing doctrine that host-side curl was never the acceptance test
    (F1/T-15).
- **Consequences:** §5.3/§5.4b/§6.4/§7.1/§11.3 carry mechanism D: compose gains top-level
  `he-agent` network (in-project — the single-compose-project constraint holds); preflight
  asserts **no `:8100` listener exists on the host at all** (strictly stronger than the old
  "bare publish is a failure" rule); §10.2's "loopback = control" reframes to "**network
  membership = control**" (still no HTTP auth — the boundary is now unambiguously the docker
  network ACL, and Docker-desktop-managed vs manual-connect DNS behavior is covered by the
  probe, not assumed). Residual, documented honestly: MinIO's operator-only published
  `127.0.0.1:9000/9001` ARE gateway-reachable from any engine container [V probe fact 2] —
  accepted residual, credential-gated, revisit if NFR-07 scope widens; the Ollama `*:11434`
  corrective (bind `127.0.0.1`, operator action) stands on its own merits since gateway-path
  reach is measured fact. T-15/T-17 carry both probe directions (positive 200 from member,
  triple-refusal from non-member) as the acceptance test.
- **Refs:** FINDING-01 (GitHub #2), review round-2 item 2, NFR-07, NFR-16, FR-01…08, D3; ADR-D-09 unchanged.

### ADR-D-16 — Job-spawn privilege: scoped spawn-sidecar (Option B hardened) — operator decision requested (FINDING-03 / OQ-5)
- **Status:** **ACCEPTED by operator ruling 2026-11-16 — Option B: scoped spawn-sidecar** (socket confined to the sidecar container; engine reaches only the 4-method API of TD §6.2b over `he-internal`; server-side allow-list enforcement as specified). **OQ-5 closed.** The honestly-stated residual stands: a compromised sidecar is still root-equivalent — the ruling adopts privilege *redistribution*, not elimination. **Date:** 2026-11-15; ruled 2026-11-16.
- **Options evaluated in full at §13.1 (11 dimensions × 3 options). Summary:**
  - **A. Mount `/var/run/docker.sock` into workflow-engine.** Zero new components; but the
    engine container — the one that also mounts user-supplied ticket trees and holds git
    credentials reachability — gains the **full daemon API = root-equivalent host control**
    (any image, any mount incl. `/`, privileged, escape). Auditability: daemon logs only, no
    semantic log. Enforceability: none at the caller.
  - **B. Dedicated spawn-sidecar holding the socket; engine calls a 4-method HTTP API
    (`create_run`, `status`, `kill`, `logs` — HTTP paths + payload schemas normative in TD §6.2b,
  the single definitive spec) over the `he-internal` network.** Honest framing
    (per the review's warning): **this is privilege redistribution, not elimination** — a
    compromised sidecar is still root-equivalent on the host. What genuinely shrinks: the
    attack surface reachable from the two containers that execute untrusted user code and
    hold long-lived credentials (engine, toolserver) drops from *the entire daemon API* to
    **four named operations** whose server side hard-enforces: image must be in the
    digest-pinned allow-list (§11.2), `network=none`, `cap_drop=ALL` + non-root user,
    cpuset/memory ceilings from §6.8, bind mounts restricted to `he-scratch`/`job-scratch`/
    `inputs` path prefixes (rejects `/`, `/home/steven`, docker.sock itself — the sidecar
    refuses requests A could honor), every call audited to `reconcile_log` with caller id.
    Sidecar itself: read-only rootfs, no env secrets, no outbound network, restart=always.
  - **C. workflow-engine as host systemd unit.** Smallest container privilege (engine gets no
    socket at all; systemd unit runs as a dedicated non-root user added to the `docker`
    group — still daemon-root-equivalent process on host, just not containerized). But it
    splits the single compose application (D-01), loses image-pinned deploys for the engine
    itself, and its crash/upgrade story is worse; the host process still touches state dirs
    owned per D-05.
- **Recommendation: B.** Smallest practical privilege boundary without new infrastructure
  beyond one ~100-line container; keeps D-01 one-compose; audit log is semantic (who/what/
  digest/limits per spawn). **This is a privilege arrangement and per review §7 it is the
  operator's call: A buys simplicity with maximal blast radius, C buys engine de-containerizing
  at the cost of D-01, B is recommended.**
- **Refs:** FINDING-03 (GitHub #4), OQ-5, §6.2/§13 (threat model), D-01/D-05/D-10 digest pins.

### ADR-D-17 — MinIO is an optional dependency for execution; required only for promotion (FINDING-06)
- **Status:** Proposed (independent review pending). **Date:** 2026-11-15.
- **Resolution of the contradiction:** the design *intended* "solver runs while MinIO is down,
  promotion degraded" but encoded "engine start depends_on MinIO healthy." Canonical now:
  **MinIO is NOT required to start the engine or to run solvers** — `depends_on: minio:
  condition: service_healthy` → `condition: service_started` + non-fatal probe; engine
  retries bucket-existence lazily per promotion. **Promotion backlog is the DB table
  `promotion_queue`** (already in the schema — now normative): engine enqueues promotion
  intents transactionally with job completion, drains FIFO when MinIO returns; backlog
  survives any outage because it lives in the WAL DB on the authoritative disk (D-05).
  Liveness vs dependency health separated in the API: `/healthz` = process liveness only;
  `/health` = component map with MinIO `ok|unavailable` + `promotion_backlog` depth; per
  NFR-23 (new) job/run payloads carry `evidence_available: bool`, and T-10 proves
  `submitted → passed (promotion pending) → +promoted` across a kill-MinIO window.
  toolserver `/health` reports the same map (single source: engine's).
- **Refs:** FINDING-06 (GitHub #7), NFR-08 (unchanged), NFR-23, FR-27, §6.1, §7.2, D5/D6.

### ADR-D-18 — One canonical API/state contract: HTTP 201 on POST /jobs; strict run⊃job boundaries (FINDING-07)
- **Status:** Proposed. **Date:** 2026-11-15.
- **Resolution:** FR-01 said 202, §7.2 said 201. **Canonical = 201 Created** (POST /jobs is
  creation of a persistent resource; body `{job_id, queue_pos}`; OpenAPI 3.1 spec at
  `/api/openapi.json` is the contract-of-record, requirements cite it — the doc set had no
  OpenAPI before, and §7.2 now states examples match it). Requirement updated (v1.2), not the
  design backwards. State boundaries (one table, every transition owner+trigger, §8.1):
  **Run** = agent-file lifecycle (owner: engine runner / agent via `he`); **Job** = toolserver
  queue + engine claim record (owner: toolserver until claimed, engine after); **gate result /
  promotion** are run-scoped, not job states — the confusion surface FR-02 flagged. Physics
  completion ≠ evidence promotion, stated as the invariant: a run may be `passed` with
  `evidence_available=false` pending `promotion_queue` drain (ties to D-17). Error envelope +
  error code table added §7.3 (previously scattered). **Refs:** FINDING-07 (GitHub #8), FR-01…03,
  §7.2/§8, T-01, T-12, T-15.
