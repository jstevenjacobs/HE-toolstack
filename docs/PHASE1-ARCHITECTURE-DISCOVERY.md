# HE-toolstack — Phase 1: Architecture Discovery & Validation

Date: 2026-11-14 · Status: **FOR REVIEW** — gate for Phase 2 (documentation production)
Method: every claim below was verified this pass against actual sources (repo working trees via
git/GIT_ASKPASS, live host/gpu1 state over SSH, image manifests, SQLite, deployed compose files).
Sources marked **[V]** verified first-hand this pass; **[E]** evidenced in a cited document;
**[P]** proposed (no artifact); **[X]** claimed but NOT found — treat as unverified.

---

## 1. Verified Component Inventory

### 1.1 Software that actually exists

| # | Artifact | What it is | Where | Source | Status |
|---|----------|-----------|-------|--------|--------|
| 1 | `pdtoolstack/openfoam-esi:2606` | OpenFOAM ESI v2606, from-source amd64, MPI | host images | MANIFEST.json digest `435e6ffa…`, smoke logs | [V][E] |
| 2 | `pdtoolstack/gmsh:4.15.2` | Gmsh CLI + Python API (OCC) | host images | MANIFEST `60f1b932…` | [V][E] |
| 3 | `pdtoolstack/calculix:2.23` | CalculiX ccx (SPOOLES patched), non-root uid 1001 | host images | MANIFEST `22e0c4f6…` | [V][E] |
| 4 | `pdtoolstack/property-pipeline:cp7.2.0` | python:3.12-slim + hash-pinned CoolProp 7.2.0/numpy/PyYAML | host images | MANIFEST `cb43496e…`; live probe: ρ(400K,10MPa)=161.53 | [V][E] |
| 5 | `pdtoolstack/agentcad:py3.12-ac0.7.1` | agentcad 0.7.1 on build123d/OCP | host images | MANIFEST `eb5afb67…` | [V][E] |
| 6 | `pdtoolstack/ta-solver-runtime:tasmet-e1` | TaSMET deps runtime (armadillo/SuperLU/boost/protobuf/Qt5/swig/GSL; TaSMET itself lives in the fork image) | host images | MANIFEST `f89d9cb0…` | [V][E] |
| 7 | `orchestrator/resolve.py` + `check-images.sh` | single launch path: audits compose repo:tag → MANIFEST digest vs `docker image inspect`; runs BY DIGEST; refuses unmanifested | PD-toolstack `scaffold/heat-engine-stack/orchestrator/` | code read this pass; negatives evidenced C4 | [V][E] |
| 8 | `compose/stack.yml` | profile-gated one-shot task services, `pull_policy: never`, shared data bindings | same repo | code read this pass | [V] |
| 9 | D2 production property dataset | `props-pT-sCO2-p0.5-25MPa_T250-800K-500x300-v1.0.npz`, 6,724,276 B, sha256 `8cb76712…`, valid 99.8%, provenance sidecar + CHECKSUMS.txt | GitHub `ta-data` main `8cf571cc` | as-built D2 row, PR #2 | [E] |
| 10 | physics-gate script | `properties/d2/gate.py`: fresh 600-probe LHS set seed `0xD2`, p99≤0.5% field errors, 60/60 OOD hard-rejects, **corruption negative test exits 1** | GitHub `ta-validation` | code + logs `heat-data/scratch/d2/d2_gate.log` | [E] |
| 11 | TaSMET fork + patches 0001–0003 | conditional-fork arm: CMake fixes, sCO₂ `Gas` subclass (grid-backed, relative stop rule), entropy interface (no-op, 3-level A/B proven) | GitHub `ta-solver` fork | E1/E2/E2b update-log entries, patch files | [E] |
| 12 | E1/E2/E2b-part1 evidence bundles | benchmark tables, drift vs D2 oracle (1e-12–1e-13), air regression 8/8, 52-pt V4 sweep at amended gate (52/52 PASS, worst ratio 0.12) | `ta-validation` `evidence/`, `PD-toolstack/evidence/e2b-fix/` | [E] |
| 13 | MinIO server + buckets + backup | Chainguard digest-pinned, buckets `ta-data`(versioned, 30d lifecycle)+`ta-scratch`, nightly backup cron → OneDrive root, **restore drill passed end-to-end incl. versioned round-trip** | host compose project `infra` (orphan) | compose file read, live container, backup logs | [V][E] |
| 14 | `run_index.db` | SQLite, single table `runs(id,name,status)`, 2 rows | host `PD-toolstack/run-index/` | queried this pass | [V] |
| 15 | GPU admission gate | `gpu-gate/run-gpu-gate.sh`, PASS 8/8, negative control image correctly rejected (sm_120 driver floor finding → D7) | `ta-validation` gpu-gate/ | [E] |
| 16 | Ledger + stage-prompt workflow discipline | STACK-AS-BUILT D1–D27, per-stage ops prompts with doc reading order, issue-per-stage, evidence-PR-closes-issue | PD-toolstack + `PD-toolstack-ops/` | read this pass | [V] |
| 17 | Embedding/Cognee config | `qwen3-embedding:8b-gpu30` at 4.98 GiB VRAM, recall@5 .7505 | host | Stage B; **closed area — not part of HE-toolstack scope** | [E] |

### 1.2 Components claimed/proposed that DO NOT exist as code

| Claimed component | Reality | Evidence |
|---|---|---|
| **gpu-broker** | **Does not exist — anywhere.** Deleted by *user ruling* in design v3.1→v3.2 ("GPU broker service deleted… serialized by the job queue itself, max-concurrency 1 + entrypoint admission"). No source in any repo or scratch dir. | STACK-DESIGN-v3 v3.2 note [E]; find over repos/scratch [V] |
| **Toolserver / tool API** | Never built. Stage E's real tool surface was **terminal(ssh) + docker + manual GitHub issue/PR ledger**. No FastAPI server code exists. | grep across all sources [V] |
| Job queue (run/index + lease) | Designed (Stage I, contract §3) — **PENDING, not built**. `run_index.db` is a 3-column stub. | as-built stage table; db inspected [V] |
| Solver service, physics-gate **service**, candidate registry, workflow engine, `he` client, optimizer loop, fleet/monitoring | All [P] — design text only | as-built stage table F–J PENDING [E] |

### 1.3 Infrastructure state (live this pass)

- **Host JSJ-Office** (WSL2, x86_64, 31 GiB usable WSL RAM): all six stack images present at
  MANIFEST digests; stack root `/home/steven/PD-toolstack` (160 MB); `heat-data/{runs,campaigns,scratch}`
  on ext4 `/dev/sdf` (runs/campaigns empty, scratch 55 MB); MinIO container `infra-minio-1` up 3 days,
  **orphaned** (its intended consumer stack was torn down). `nvidia-smi` over SSH returned no rows on
  this probe (prior-session evidence: RTX 5060 Ti, 16370 MiB; re-measure ticket in §5).
- **gpu1 `gx10-9d06`**: NVIDIA **GB10 (ARM64)** running sglang LLM. **Cannot host the amd64 stack images.**
  The v3 design's "gpu1 = CUDA worker (DGX Spark)" premise is architecturally dead: it is the LLM host
  and the wrong CPU arch. The only CUDA device for compute is the host's RTX 5060 Ti, currently owned
  by Ollama embeddings (4.98 GiB pinned) + sglang remote.
- **Container (Hermes)**: PD-toolstack clone + ops prompts; ~1.4 GB scratch dirs (stageE/e2bfix) unpruned.

---

## 2. Requirements Baseline (draft — refined into IDs in Phase 2)

Initial release = Milestones M0–M2 (vertical slice + engine breadth + fleet). M3+ = subsequent release.

**Functional** (draft IDs; all P0 unless noted)
- FR-01 Tool invocation: agent starts/reads/aborts solver jobs through a documented JSON API; jobs survive agent disconnect.
- FR-02 Engine configuration: parameterized engine spec (geometry, gas, operating point) → solver input decks; all knobs machine-readable (linearity thresholds per D25 lesson).
- FR-03 Meshing + CFD + FEA: gmsh/OpenFOAM/CalculiX reachable via the same surface [P1, M1].
- FR-04 1D thermoacoustic solver: TaSMET fork with grid-property Gas subclass; sCO₂ runs; entropy-BC fix (patch 0004 equivalent) accepted.
- FR-05 GPU resource management: one-writer serialization + admission check before launch (v3.2 ruling shape; §5 decision pending).
- FR-06 Physics validation: every result → gate report with named checks, named dataset+digest inputs, negative test in suite (D2 pattern).
- FR-07 Workflow orchestration: durable workflow definition, per-run state file, append-only ledger; resume from state after total agent-context loss.
- FR-08 Artifact management: per-run manifest (git SHA, image digests, dataset version, state.json, gate report); write-before-index ordering.
- FR-09 Run tracking & comparison: list/get/diff runs; compare across runs and historical evidence.
- FR-10 Candidate registry: candidate id ↔ run ids ↔ evidence ↔ ledger row.
- FR-11 Recovery/resumption: any component restart → jobs either resume or return honest `failed(attempt n)`; no lost/duplicated side effects (idempotency keyed).
- FR-12 Agent interaction: cold session answers "what's done / what's next / where's evidence" from `workflows/` files alone.
- FR-13 (M3) Optimizer loop: Bayesian/RL propose → batch-evaluate under budget cap, linearity-envelope guard.
- FR-14 (M3+) Fleet monitoring; cadence/2D/3D validation tiers.

**Non-functional** (each gets IDs + acceptance in Phase 2)
- NFR-01 Reliability: crash restart leaves zero orphans (containers); queue survives daemon restart.
- NFR-02 Performance: M0 slice e2e < 10 min wall (CPU-only assumption, §3-A4); no invented GPU targets (§15 open).
- NFR-03 Scalability: single → multi worker path exists but is not load-bearing in initial release.
- NFR-04 Security: no secret in any diff (gitleaks CI, proven); loopback-only API bind; containers non-root where upstream allows.
- NFR-05 Maintainability: ≤4 stack images; one compose project; per-ticket cleanup clause.
- NFR-06 Observability: health endpoints + structured logs mandatory; metrics/Grafana optional profile.
- NFR-07 Portability: whole app = repo + `.env` + compose bring-up (the v3 invariant, retained).
- NFR-08 Data integrity: digests on every dataset/artifact; append-only ledger; versioned objects + restore drill (retain Stage A discipline).
- NFR-09 Recoverability: cold-session resume ≤10 min without chat context; restore drill re-passes on the in-app MinIO.
- NFR-10 Extensibility: new solver = new service + one adapter row, no engine-specific logic in core (the v3 "thin and domain-agnostic" principle, inherited).

---

## 3. Assumptions (each: status = verified / to-verify / decision-needed)

- **A1 [verified]** Host reachable via SSH key (port 2222), no passwordless sudo (docker-run chown workaround established).
- **A2 [verified]** ext4 data volume `/dev/sdf` mounted; stack root + heat-data on it; `/mnt/c` banned for compute I/O.
- **A3 [decision needed]** Only CUDA device for compute = host RTX 5060 Ti shared with Ollama embeddings (closed area, 4.98 GiB) and it's 16 GB class. GPU compute tier budget/ownership must be ruled (§5 D-04).
- **A4 [verified→drives decision]** All evidence-producing work so far ran **CPU-only**; GPU tier never admitted real jobs. Therefore M0's physics loop must run CPU-only, and all prior perf evidence is CPU evidence.
- **A5 [decision needed]** gpu1 (GB10/ARM64) is LLM-only — removed as compute worker. Any second CUDA worker must be amd64 or arm64-native built (D14 lesson).
- **A6 [verified]** No container registry; images live only on host at MANIFEST digests. `pull_policy: never` compensates.
- **A7 [verified]** All repos private on `jstevenjacobs`; container can push via askpass PAT.
- **A8 [single-operator]** One human (Steven) is operator and final gate authority; agents are interchangeable workers.
- **A9 [decision needed]** WSL long-run: the design v3.7 decided the stack lives on the WSL side, but *observed reality* put MinIO + all heavy state on the host and the agent in a container — three filesystems per run today. The compose app must pick ONE owner of state (host) explicitly (§5 D-05).
- **A10 [verified]** TaSMET benchmark tolerances from its publication are usable as acceptance numbers (E1 precedent); openthermoacoustics is ideal-gas reference only (contract).
- **A11 [to-verify]** Chainguard MinIO rebuild track remains available/pinnable (upstream pulled official images 2025-10-23).
- **A12 [verified]** Hermes container + desktop app is the agent surface; there is no guarantee of chat-context durability — hence the external-state requirement.

---

## 4. Design Gaps & Contradictions

### 4.1 Contradictions requiring resolution (recommended resolution in parentheses)

- **C1 — "gpu-broker survives as a code asset" is false.** Both the pre-compaction ledger notes and
  DESIGN-v2 §1 list gpu-broker/toolserver/E2b-httpx-surface as carried-forward code. Verified: no such
  code exists; broker was deleted by ruling pre-Stage-E; the E2b "surface" was the C++ patch series.
  *(Resolution: Phase 2 documents carry only verified artifacts; broker/queue redesigned from the
  v3.2 ruling text — "queue serialization + admission, no broker daemon" — not from my earlier prose.)*
- **C2 — DESIGN-v2 §3 service list ("solver, physics-gate, gpu-broker, MinIO, workflow engine")**
  inherits from C1. *(Resolution: treat §3 as proposals with evidence tags, §6 details what's verified.)*
- **C3 — v3 claimed "GPU jobs run through queue, max-concurrency 1" as the serialization mechanism;
  the queue was never built (Stage I pending).** *(Resolution: v2's M0 includes the minimal queue slice;
  no mechanism may be described as existing unless §1.1 lists it.)*
- **C4 — MinIO: worked (restore drill!) yet became an orphan with no consumer.** Ownership/lifecycle,
  not tech, failed. *(Resolution: MinIO is a compose service; lifecycle + backup retained.)*
- **C5 — "8 images → consolidate to 4" (my v2 draft) not yet feasibility-checked:** gmsh/calculix/property
  images have different bases (Ubuntu noble / Debian-patched / python:3.12-slim) and one has GPU-neutral
  but conflicting apt package sets. *(Resolution: Phase 2 §6 states target image contents concretely or
  defers consolidation with per-image verification tickets.)*
- **C6 — host `nvidia-smi` over SSH returned no rows this pass** while prior sessions measured 16370 MiB.
  Either transient GPU lock (sglang/exclusive mode) or WSL state change. *(Resolution: re-measure ticket
  before any GPU-tier acceptance; do not carry the old number silently.)*

### 4.2 Gaps to close in Phase 2 (each maps to a doc section)

- G1 API contract: toolserver endpoints, error envelope, idempotency keys, timeouts, auth → §7.
- G2 State schema: state.json fields, allowed values, transition rules, checkpoint commit protocol
  (write-ahead order artifact→state→ledger) → §8–9.
- G3 Consistency across filesystem ↔ MinIO ↔ SQLite registry: single write-ahead rule + reconciliation
  sweep → §9.
- G4 GPU admission mechanism (post-broker-deletion redesign; VRAM floor check; coexistence with
  embeddings + sglang) → §6/§10, tied to decision D-04.
- G5 Registry schema + candidate lifecycle states → §6.8.
- G6 Retention policy: runs, scratch, artifacts, logs, ledger — with the cleanup-clause mechanism → §9/§11.
- G7 Security model for loopback API + PAT + agent permissions + image provenance → §10.
- G8 Failure-mode matrix (FMEA) incl. "artifact written but state not committed" → §12.
- G9 Test strategy preserving physics-gate methodology + cold-session acceptance + corruption negative
  tests + bit-identity A/B pattern (from patch-0003 3-level proof) → §14.
- G10 Cold-session acceptance: the harness itself must be specified (who tests it, how, pass criteria) → §14.16.
- G11 Migration plan for orphaned live state (MinIO buckets/data, images, heat-data, dead dirs) → §16.

---

## 5. Architecture Decision Register (seed — full ADRs in Phase 2 `HE-TOOLSTACK-ADR.md`)

| ID | Decision | Status | Basis / revisit condition |
|----|----------|--------|---------------------------|
| D-01 | Single compose app owns all stack services incl. MinIO | Accepted (user ruling 2026-11-14) | Orphan evidence C4; refs: compose specs |
| D-02 | Workflow control = externalized files (state.json + ledger + handoff notes) + ~200-line runner; **no LangGraph yet** | Proposed (my recommendation; supersedes nothing) | O'Reilly checkpoint pattern; LangGraph OSS resume docs (self-healing only on durable-exec platform); AWS durable-exec docs; **revisit on**: parallel fan-out, durable multi-day waits, crash-restart supervision |
| D-03 | **gpu-broker stays deleted** (v3.2 ruling honored): queue serialization + admission, no broker daemon | Proposed (restores the actual ruling, correcting my DESIGN-v2 error) | v3.2 text [E]; revisit if multi-host fleet lands |
| D-04 | GPU tier ownership on 5060 Ti: budget for compute vs embeddings (4.98 GiB pinned, closed) vs sglang remote | **OPEN — needs user ruling** | C6 re-measure first |
| D-05 | Single state owner = host `/home/steven/HE-toolstack` (+ named container bind); artifact → state → ledger write-ahead order | Proposed | C7/A9 evidence; fixes three-filesystems-per-run |
| D-06 | physics-gate: keep script methodology (gate.py + probes + negative test), expose behind one toolserver endpoint | Proposed | D2 gate evidence [E] |
| D-07 | Artifact layout `heat-data/runs/<run-id>/` on host, hot; MinIO receives gate-passed + ledger + dataset tier only | Proposed | C4 retention discipline; backup/restore drill carried |
| D-08 | One SQLite (run registry + queue + lease) co-located with workflow engine | Proposed | revisit if contention/fleet |
| D-09 | `he` client in the agent container, HTTP/JSON, no MCP (v3.8.1 ruling retained) | Proposed (already in force) | contract v3.8.1 [E] |
| D-10 | Image consolidation target ≤4 (ta-runtime, fea-mesh-cad, python-tools, base) | **OPEN** — content check pending | C5 |
| D-11 | gpu1 excluded from compute tier (ARM64 + LLM duty) | Proposed | 1.3 [V] |
| D-12 | Physics core (TaSMET fork, dataset, gate, evidence) migrates as-is; patches 0004-equivalent is M0 scope | Accepted (direction) | E/E2b evidence [E] |

---

## 6. What this changes vs my DESIGN-v2 draft (self-correction, source integrity)

1. §1's "carry-forward code" list **overstated**: gpu-broker/toolserver/httpx surface don't exist.
   Carry-forward *verified* set = images+MANIFEST+resolve.py, TaSMET fork+patches, D2 dataset, gate.py,
   evidence, ledger discipline, MinIO backup/restore mechanics.
2. §3's service list must be relabeled proposed (C2), with D-03 restoring the no-broker ruling.
3. The GPU story in both v3 and my v2 draft was built on an untested premise; verified reality is
   CPU-only so far (A4). M0 is defined CPU-only; GPU tier is a ruled decision (D-04), not an assumption.
4. MinIO section upgrades from "adopt in-app" to "adopt in-app **and retain A5/A6 backup+restore
   discipline**" — that discipline is verified working and was the best ops artifact of attempt 1.

---

## 7. Human decisions required before/at Phase 2 sign-off

1. **D-04 GPU tier** (budget on 5060 Ti, or CPU-only for the whole initial release?).
2. **D-05 state owner** confirmation (host-owned + bind-mount vs container-managed volume).
3. **D-10 image consolidation**: approve concrete target contents, or defer consolidation to build tickets.
4. Approve **D-02** (files-first, LangGraph-with-tripwires) as the workflow-decision posture for review.
5. Confirm migration stance (§16 preview): new app = new names; PD-toolstack evidence repos stay frozen;
   orphan MinIO data copied (not moved) into the app bucket before teardown.
