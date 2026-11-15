# HE-toolstack Architecture Decision Register (ADR)

**Document:** `HE-TOOLSTACK-ADR.md` · v1.0 · 2026-11-14
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
  explicit (FR-29: gate-passed + ledger + dataset tier only); backup = heat-data + git.
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
- **Status:** Proposed (sign-off needed)
- **Decision/rationale:** WAL-mode SQLite is the minimum durability primitive that already
  exists in the runtime; three stores (queue + registry + lease) would triple the
  consistency problem D-05 just collapsed. Contention at single-operator write rates is
  negligible [P]. Alternatives: Postgres (extra service to operate, deferred — compose
  profile exists for it), separate queue (Redis — rejected: durability requires AOF
  gymnastics SQLite gives by default).
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
| X-8 | /mnt/c (Windows FS) for solver I/O | inherited (D9) | measured 28–39× penalty [E] |

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
| OQ-2 | Confirm/adjust D-04 numbers (8/5.5 GiB) at review with C6 re-measure data in hand. | GPU-class enablement |
| OQ-3 | Migration stance detail: PD-toolstack evidence repos stay frozen (user ruling says source-of-information only — confirm *read-only mirror* vs *do-not-touch* for the copy-into-registry step, ticket C3). | C3 execution |
| OQ-4 | physics-gate endpoint wrapper (D-06) and registry/SQLite colocation (D-08) acceptance. | M0 design freeze |
| OQ-5 | Job spawn channel: docker.sock mount vs scoped sidecar vs host-unit engine (TECHNICAL-DESIGN §6.2/§17.1). Security-critical; **M0 blocker**. | M0 build start |
| OQ-6 | toolserver shares engine's SQLite WAL vs engine-internal HTTP (TECHNICAL-DESIGN §7.5). Coupling vs one-less-hop; reviewer call. | design freeze |
