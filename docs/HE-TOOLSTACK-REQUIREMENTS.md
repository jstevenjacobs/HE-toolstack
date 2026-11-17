# HE-toolstack Requirements Baseline

**Document:** `HE-TOOLSTACK-REQUIREMENTS.md` · v1.6 (rev 2026-11-16: round-5 backup/MinIO/OneDrive/restore corrections below; round-3 flock/inbox/T-23 revision:— FR-26 claim arbiter = flock(2) held lock (TD §8.8 r3; r2 O_EXCL/rename retracted); T-20/T-21 restated for flock; T-23 added (SQLite claim/submission crash matrix); NFR-09 digest-chain wording unchanged. Earlier rev 2026-11-15b: review-response 2 — FR-26 claim arbiter upgraded to O_EXCL lockfile (TD §8.8 r2); NFR-01 `make down` single-stop-path; NFR-07/T-15 alias facts corrected [V re-probe 15b]; T-20 claim-mutex + T-21 stale-claim + T-22 MinIO-version tests added; T-12 disambiguated; prior v1.3: NFR-07 gateway URL, T-17/18/19; prior v1.2: FINDING-01…07 revisions; +NFR-22 v1.1 D-14) · 2026-11-14
**Status:** Baseline for review (Phase 2 deliverable C of DesignStandards §8)
**Upstream sources:** Phase 1 report (`docs/PHASE1-ARCHITECTURE-DISCOVERY.md`, commit `141249d`)
§2–§5; PD-toolstack `STACK-DESIGN-v3.md` (v3.8.1) and `STACK-AS-BUILT.md` (D-ledger D1–D27);
user rulings D-01…D-12 (decision register, Phase 1 §5) with the three final rulings of
2026-11-14 (D-04 Option B, D-05 Option 1, D-10 separate images).

## 0. Reading conventions

**Evidence tags** (every requirement carries at least one source class):

| Tag | Meaning |
|----|---------|
| [V] | Verified live during Phase 1 discovery (host/container probes, 2026-11-14) |
| [E] | PD-toolstack as-built evidence (D-ledger row, as-built doc, on-disk artifact) |
| [P] | Proposed behavior — not yet implemented anywhere; this document is its first definition |
| [U] | Assumption that could not be verified; appears in the risk register |

**Release scope.** Initial release = milestones M0–M2 (per Phase 1 §2). Priorities:
**P0** = required at M0 (vertical slice); **P1** = required at M1 (tool breadth);
**P2** = required at M2 (fleet readiness) or later; **[M3+]** = subsequent release, listed for
boundary clarity only. No P1/P2 requirement may block the M0 gate.

**Reference rule** (standing project law): a decision or requirement with no `ref:` to a
fetched source or observed artifact is a gate failure. `SA` below = `STACK-AS-BUILT.md`;
`SD` = `STACK-DESIGN-v3.md`; `P1` = Phase 1 report; `host` = live probe this session.

**Status discipline:** this document specifies *proposed* requirements. Nothing in it asserts
implemented functionality except where tagged [E]/[V], which describe PD-toolstack-era or
host-level facts that remain true.

---

## 1. System vocabulary (fixed naming for all Phase 2 documents)

| Name | Kind | Note |
|------|------|------|
| `toolserver` | service (new, [P]) | HTTP/JSON surface for the agent; thin, domain-agnostic |
| `workflow-engine` | service (new, [P]) | durable runner + SQLite (queue, run registry, lease) — D-02/D-08 |
| `physics-gate` | methodology + endpoint [E→P] | gate.py/probes/negative-test carried; one toolserver endpoint exposes it — D-06 |
| `minio` | service (compose, [E]) | artifact/object store; proven backup-restore mechanics — D-01/D-07 |
| `tasmet` | solver service | image `ta-solver-runtime:tasmet-e1` — 1D thermoacoustic, fork+patches [E] |
| `openfoam-esi` | solver service | image `openfoam-esi:2606` — CFD [E] |
| `gmsh` | solver service | image `gmsh:4.15.2` — meshing, **CLI path only** (OCC Python API segfaulted, SA Stage D) [E] |
| `calculix` | solver service | image `calculix:2.23` — FEA [E] |
| `property-pipeline` | service | image `property-pipeline:cp7.2.0` — hash-pinned CoolProp provenance [E] |
| `agentcad` | service | image `agentcad:py3.12` — build123d/CadQuery geometry [E] |
| `he-client` | python client in agent container [P] | HTTP/JSON; no MCP (ruling D-09) |
| `heat-data` | host directory (canonical state owner) | `/home/steven/HE-toolstack/heat-data` on `/dev/sdf` — D-05 |
| `gpu-admission` | mechanism inside workflow-engine [P] | **not a daemon** — v3.2 broker deletion honored (D-03) |
| host | JSJ-Office WSL2 box, RTX 5060 Ti [V] | only CUDA device in scope; embeddings co-resident |
| sglang host | `gx10-9d06` GB10/ARM64 [V] | LLM only; excluded from compute tier (D-11) |

Per D-10: one narrow image per capability; new capability ⇒ new image, never additions to
existing solver images.

---

## 2. Functional requirements

### 2.1 Tool invocation and execution

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-01 | Agent submits a solver job via documented HTTP POST returning `job_id` immediately (async model). | P0 | [P] Agent must not hold an HTTP connection open for hours; P1 §2 FR-01 | T-08 (contract), T-01 (e2e) | POST returns **201 Created** + `{job_id, queue_pos}` < 2 s while job runs to completion (canonical code = tech design §7.2, aligned v1.2 per FINDING-07); OpenAPI schema published by toolserver |
| FR-02 | Job status — canonical set per tech design §8.2 (queued/running/blocked_retryable/succeeded/failed/cancelled/orphaned), evidence-promotion sub-state (FR-15), per-attempt log tail, and artifact URIs readable via GET by `job_id`. | P0 | [P]; D25 lesson: agent blind to job state after disconnect [E SA D25] | T-08, T-02 | Status transitions observable within 5 s of occurrence; failed jobs carry attempt count and last 100 log lines |
| FR-03 | Agent may cancel a queued job (best-effort) or request abort of a running job (SIGTERM then grace-window SIGKILL). | P1 | [P]; long CFD runs need an escape hatch | T-08, T-09 | Cancel of queued = terminal `cancelled` no side effects; abort of running stops container within grace window and records exit code |
| FR-04 | Submission is idempotent via client-supplied `Idempotency-Key`: duplicate POST with same key returns the original `job_id`, never enqueues twice. | P0 | [P]; duplicate job = duplicated side effects (P1 G1) | T-08 | 100 duplicate POSTs → exactly 1 queued job |
| FR-05 | Every mutation endpoint is documented in a machine-readable contract committed to the repo (OpenAPI + error envelope schema). | P0 | [P]; DesignStandards §7 prohibits fabricated interfaces — contract is the artifact | T-08 | Schema validates all request/response fixtures; error envelope identical across endpoints (§6 of tech design) |

### 2.2 Engine configuration and generation

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-06 | Engine configuration is a schema-validated document (geometry, working fluid, operating point, solver deck parameters) — no free-text config. | P0 | [P]; v3 "all knobs machine-readable" [E SD §contract] | T-01, T-08 | Invalid config rejected pre-solve with field-level errors; M0 loop config validates against schema at commit |
| FR-07 | Solver input decks are *generated* from the engine config by versioned generators; decks are stored per run. | P0 | [P]; D25 lesson: hand-mutated decks diverged from state [E SA D25] | T-01, T-04 | Deck in run manifest regenerates bit-identically from config + generator version |
| FR-08 | Config validation enforces the solver's linearity envelope (e.g. TaSMET linearized-model thresholds) at intake, not post-run. | P1 | [E SA D25: threshold knobs silently non-linear outside envelope] | T-09 | Out-of-envelope config refused with named threshold + measured value |
| FR-09 | Every accepted config records provenance: repo git SHA, engine-config digest, generator version. | P0 | [E] resolve.py/MANIFEST digest discipline carried forward | T-01 | Manifest row contains git SHA + digests; `git archive` of that SHA reproduces generator |

### 2.3 Solver execution

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-10 | 1D thermoacoustic: `tasmet` executes forked TaSMET (patch 0004-equivalent entropy-BC fix accepted) on parameterized sCO₂ loops; benchmark tolerances from the fork's publication [E SA E1] act as acceptance numbers. | P0 | [E] fork + patches verified on host | T-01, T-09 | M0 closed sCO₂ loop completes; entropy residual below gate threshold; fork regression suite green inside container |
| FR-11 | Meshing: `gmsh` service runs the CLI on a geometry + mesh-parameter input; the OCC-embedded Python API path is **prohibited** (known segfault). | P1 | [E SA Stage D lesson] | T-09 | Deterministic mesh (digest-stable) for frozen test geometry; .msh + journal in run dir |
| FR-12 | CFD: `openfoam-esi` service runs parameterized OpenFOAM cases (blockMesh/snappy + solver) through the same job API. | P1 | [E] image verified running | T-09 | Lid-driven cavity reference case reaches documented residual target |
| FR-13 | FEA: `calculix` service runs ccx input decks (thermal-stress) through the same job API. | P1 | [E] image verified, non-root | T-09 | Reference plate case within published tolerance |
| FR-14 | Properties: `property-pipeline` answers CoolProp queries **only** from its hash-pinned environment; every returned value carries the pin-set digest. | P0 | [E SA D10/D13: pin is the provenance] | T-04, T-09 | D2 probe set bit-identical; digest mismatch ⇒ refusal + error |
| FR-15 | Geometry: `agentcad` service exports build123d/CadQuery models to STEP/STL consumed by meshing. | P2 | [E] image verified | T-09 | Test parametric model exports; geometry digest recorded |

### 2.4 GPU resource management (gated by D-04 / C6)

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-16 | GPU jobs serialize: exactly **1** concurrent GPU-class job (D-04). Admission is a check in the workflow-engine queue dispatcher — no separate broker daemon (D-03, v3.2 ruling [E SD]). | P0 (mechanism) | [P]; contention analysis P1 §5 D-04 | T-05, T-06 | N GPU submissions ⇒ ≤1 running; queue ordering FIFO; survives engine restart |
| FR-17 | VRAM admission: refuse GPU job if free VRAM < requested ceiling + **5.5 GiB protected floor** (pinned Ollama embeddings ≈4.98 GiB [E]); per-job request ceiling **8 GiB** (D-04 defaults, still [P] numbers pending C6 re-measure). | P0 (mechanism) | [P] + [E embeddings footprint] | T-06 | Admission refuses at simulated free-VRAM < floor + request; embeddings container stays healthy during admitted job |
| FR-18 | GPU compute class stays **inert** until ticket C6 passes (re-measure RTX 5060 Ti state over SSH + driver floor ≥591.59 for sm_120, Windows side [P1 C6]). Until then GPU-class submissions are rejected with `gpu-class-disabled`. | P0 | [V] nvidia-smi returned no rows this pass; D7 driver-floor lesson [E] | T-06 | Flag off ⇒ machine-readable refusal; flag on requires C6 evidence path populated in ledger |
| FR-19 | No M0–M2 acceptance criterion depends on GPU execution (D-04 ruling). All M0–M2 physics evidence runs CPU-class. | P0 | [V A4: all evidence so far CPU-only] | T-01 | M0–M2 acceptance suites contain zero GPU-class jobs; CI-equivalent run passes with GPU flag off |

### 2.5 Physics validation

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-20 | Every solver result passes the physics-gate: named checks (entropy residual, energy balance, expected BC behavior) executed against named datasets identified by digest. | P0 | [E SA D2 gate.py pattern] | T-01, T-03 | Gate report names each check, its inputs, dataset digest, pass/fail; loop run without a gate report cannot reach `succeeded` |
| FR-21 | The gate methodology ships with a **negative test** (corrupted probe → gate must fail) executed in the test suite. | P0 | [E SA D2: negative test proven] | T-03 | Suite fails if gate is neutered; corruption variant documented |
| FR-22 | Any change to a solver image or property pin-set triggers **bit-identity A/B**: frozen-grid references (52-pt sweep, D2 probes [E]) re-run and must match digest-for-digest before the new image is admitted. | P0 | [E patch-0003 3-level proof pattern]; D-10 blast-radius argument | T-04 | A/B harness exists at M0; mismatch ⇒ image not admitted, ledger row records divergence |

### 2.6 Workflow orchestration

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-23 | Workflow definition is a versioned file in `workflows/`; the runner (~200-line loop [P], D-02) executes steps, no durable-exec platform in initial release. | P0 | [P]; O'Reilly checkpoint pattern; LangGraph deferred on named tripwires (D-02) | T-01, T-02 | Definition file + runner drive M0 loop end-to-end; tripwires documented as revisit conditions |
| FR-24 | Per-run state file `state.json` (schema §9 of tech design) is the single authoritative run record, updated by atomic rename (D-05). | P0 | [E D25 divergence lesson] | T-07 | Torn-write impossible (rename); schema validation on every read; resume uses state alone |
| FR-25 | Append-only ledger rows with mandatory `ref:` to fetched source/observed artifact; missing ref = gate failure. | P0 | [E] ledger discipline is attempt-1's best ops artifact | T-01 | Every state transition's ledger row parses + has resolvable ref; ledger never rewritten |
| FR-26 | Ticket protocol: `workflows/tickets/*.md` claimed **under the per-ticket flock (§8.8 r3)** before execution; ≤3-line done-check verified in-session before completion. | P0 | [E] claim/done discipline enforced at Stage E (discipline [E]; flock mechanism [P]) | T-01, T-12 (process audit), **T-20/T-21 (concurrency)** | No two claimed tickets same file; done-check text appears in the session's own outputs |

### 2.7 Artifact management

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-27 | Per-run directory `heat-data/runs/<run-id>/` (hot, host-owned per D-05) holds deck, raw results, logs, `state.json`, gate report, `MANIFEST` (git SHA, image digests, dataset version, digests of all files). | P0 | [E MANIFEST discipline] | T-01 | Manifest completeness check passes on M0 run dir |
| FR-28 | **Write-ahead ordering is normative**: (1) artifacts written + fsync → (2) state.json atomic rename → (3) ledger append + git push. Deviation is a defect. | P0 | [E SA D25] | T-07 (crash matrix) | Kill at each inter-step boundary recovers per §12 matrix: abandoned-artifact sweep (crash 1–2) or clean resume (crash 2–3); zero silent divergence |
| FR-29 | Gate-passed artifacts + ledger + dataset tier are promoted to MinIO (versioned objects); hot working set stays on host filesystem. Scratch dirs are non-authoritative — deletable without asking (D-05). | P1 | [E restore-drill proven; C4 orphan lesson] | T-11, T-12 | Restore drill re-passes on in-app MinIO; scratch deletion breaks nothing (verified by drill) |

### 2.8 Run tracking and historical comparison

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-30 | List/get runs and read run details via API (registry-backed, SQLite per D-08). | P0 | [P] | T-08 | M0 run discoverable by id/tag; detail view names every artifact |
| FR-31 | Diff two runs: config, generator version, image digests, gate results, numeric result delta. | P1 | [P]; comparing runs is the whole point of evidence | T-08, T-01 | Diff of two identical decks shows zero config drift; digest columns populated |
| FR-32 | Historical PD-toolstack evidence (runs, D2 dataset, ledger) remains queryable read-only after migration (§16). | P1 | [E] DesignStandards: preserve lessons | T-10 | Old D2 dataset digest answers property probe identically |

### 2.9 Candidate registry

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-33 | Candidates (engine designs under evaluation) carry lifecycle states (`proposed→queued→evaluating→gated/rejected→archived`) recorded in the registry with state-transition timestamps. | P1 | [P]; registry SQLite (D-08) | T-10 | Illegal transitions refused; every state change has run id + ledger ref |
| FR-34 | Candidate ↔ run ids ↔ evidence artifacts ↔ ledger rows are linked bidirectionally. | P1 | [P] | T-10 | From any ledger row, walk to candidate and run dir, and reverse |

### 2.10 Recovery and resumption

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-35 | Jobs survive agent disconnect: engine owns execution; agent reconnects by polling FR-02. | P0 | [P]; v3 invariant | T-01 | Kill agent HTTP session mid-job; job completes; artifacts present |
| FR-36 | Resume from total agent-context loss: a **cold session** (no chat history) completes/finances an in-flight workflow reading only `workflows/` + heat-data state. | P0 | [V A12: no chat-context durability guarantee] | T-02 | Fresh session answers "done/next/evidence" correctly; resume ≤10 min wall [P target] |
| FR-37 | Any component restart ⇒ each in-flight job is either resumed or marked `failed(attempt n)` honestly; no lost side effects; side-effect steps keyed by idempotency key. | P0 | [P] | T-05, T-07 | Restart matrix (§12 FMEA) executed; no job disappears; no double-push/double-promote |
| FR-38 | Crash sweep: artifacts dir scanned vs state.json set; artifact-without-state = `abandoned`, quarantined not deleted. | P0 | [P]; D-05 write-ahead corollary | T-07 | Synthetic crash 1–2 leaves quarantined dir + ledger note, next run unaffected |

### 2.11 Agent interaction

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| FR-39 | `he-client` python library in the agent container provides the full surface over loopback HTTP; no MCP (D-09, v3.8.1 ruling [E SD]). | P0 | [E] ruling in force | T-08 | Client passes contract suite; zero import-time dependency outside container |
| FR-40 | The agent's canonical work loop is file-driven: claim ticket → act → done-check → ledger → push. API is for jobs, not for workflow memory. | P0 | [E Stage E practice] | T-02, T-12 | Cold-session test (§14 of tech design) passes with filesystem + API only |

### 2.12 Subsequent release (boundary markers only)

| ID | Description | Pri |
|----|-------------|-----|
| FR-41 | [M3+] Optimizer loop (Bayesian/RL propose + batch evaluate under budget cap, linearity-envelope guard). | M3+ |
| FR-42 | [M3+] Multi-host workers (amd64/arm64-native built; D14 lesson); fleet monitoring; cadence/2D/3D validation tiers. | M3+ |

---

## 3. Non-functional requirements

### 3.1 Reliability

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-01 | **Canonical lifecycle (2026-11-15r2):** every stack container — compose-managed (class C) *and* spawned one-shots (class J) — carries label `he-stack=1` (compose `labels:` / sidecar spawn `--label`; class J also `he-run=<id>`). **`make down` is the controlled shutdown**: engine graceful stop → `docker compose down` → janitor sweep; it must leave **zero** `he-stack=1` containers (classes C∪J). A raw `docker compose down` is an operator escape hatch: it removes only class C by design; class-J disposition is healed by janitor + reconcile-on-start (§6.10) at next `make up`. `make down` is the **acceptance target**; raw compose-down is never the acceptance criterion. Restart via `make up` re-creates the full stack, no manual steps. | P0 | [U→V pending M0] user observation "single compose app"; C4 orphan lesson; r2-review item 1 | T-13 | after `make down`: `docker ps -a --filter label=he-stack=1 -q` empty **and** `docker compose ps -a` empty; up→healthy from cold clone |
| NFR-02 | Queue and registry (SQLite) survive engine/container restart without job loss (FR-37); SQLite opened in WAL mode. | P0 | [P]; standard SQLite durability mechanism | T-05 | Kill -9 engine mid-queue; on restart, queue set identical to pre-kill snapshot |

### 3.2 Performance

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-03 | M0 vertical slice (config→deck→1D solve→gate→ledger) completes **< 10 min wall** CPU-only. Flagged as a **proposal** — first measurement may amend it; no GPU numbers are stated anywhere (none measured). | P0 | [P proposal]; all prior evidence CPU-only [V A4] | T-01 | Timed run recorded in ledger; amendment ticket if actual lands outside 0.5×–2× of target |
| NFR-04 | Job-state read latency (GET status) < 500 ms p95 while one solver job is running on the same host. | P1 | [P]; agent polling must stay cheap while solvers hog cores | T-09 | p95 measured during CPU-saturated CFD run |

### 3.3 Scalability

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-05 | The worker path is an interface, not a load-bearing dependency: job dispatch goes through a `Worker` seam so a second (amd64) host could register later (M3+); initial release runs host-as-sole-worker without rearchitecture. | P2 | [P]; D14 lesson (arch matters); FR-42 boundary | T-14 | M2 exercise registers a second worker identity (even if it runs on the same host) and executes one job through the seam |

### 3.4 Security

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-06 | No secret is ever committed; gitleaks runs in CI on every push. | P0 | [E SA: gitleaks CI proven] | T-13 | CI fails on seeded fake secret; clean on merge |
| NFR-07 | Toolserver is reachable **only via host loopback**: compose publishes `127.0.0.1:8100:8100` (published-address binds host loopback — no LAN/compose-net path; internal bind `0.0.0.0` inside its own namespace is required for the `-p` mapping and is not exposure). The agent's client URL is **`http://172.17.0.1:8100`** (docker bridge gateway; auto-discovered by
`he`, `HE_API_BASE` overrides) — verified reachable end-to-end from inside the Hermes container
2026-11-15 [V]. Neither the agent's own `127.0.0.1:8100` (namespace-local) nor
`host.docker.internal` (refused host loopback binds in the same probe battery [V]) is the client
URL. Auth deferred behind this boundary and documented as deferred (tech design §10). | P0 | [V probes 2026-11-15 + FINDING-01]; single-operator trust model [E A8] | T-15 | Test executed **from inside the Hermes runtime container**: `host.docker.internal:8100` succeeds; agent-side `127.0.0.1:8100` fails (namespace isolation proof); port scan from a second container on the compose net fails; host-loopback scan succeeds; host-side curl alone does NOT count as passing |
| NFR-08 | Containers run non-root where upstream allows (calculix already proven [E]); any root container is an explicit, logged exception with reason. | P1 | [E] | T-15 | compose audit lists user per service; exceptions carry reason strings |
| NFR-09 | Image provenance: only digests in the repo `MANIFEST` run (`pull_policy: never`); a digest outside MANIFEST is refused by the dispatcher. | P0 | [E resolve.py/MANIFEST discipline; A6 no registry] | T-16 | Submit job with foreign digest ⇒ refused with named check |

### 3.5 Maintainability

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-10 | Ownership is by declared class (tech design §6.10, D-01 A1): **C** — one compose project owns every long-running stack service incl. MinIO; **J** — one-shot job containers are engine-owned, labeled `he-stack=1`, janitor-reconciled; **X** — documented infrastructure exceptions (host backup timer; §11.9 externals). Nothing stack-owned runs outside these classes. After `make down` (= compose down + janitor sweep), **zero containers of classes C∪J exist**; running jobs at shutdown are SIGTERMed and recorded `interrupted`, never silently orphaned. | P0 | [E C4: orphaned infra-minio-1 with no consumer]; FINDING-02 [GitHub #3] | T-13 | `docker compose ls` shows exactly one he-project (plus §11.9 externals); after `make down`, `docker ps -a -f label=he-stack=1` is empty AND compose ps is empty; shutdown with a running job yields state `interrupted` in registry + ledger entry |
| NFR-11 | Narrow-scope images (D-10 ruling): one capability per image; new tool = new image; solver images are **append-frozen** (no new tools added to them). | P0 | [U ruling 2026-11-14, user rationale: future adaptability] | T-16 | CI check: image tag list == MANIFEST list; PRs touching solver Dockerfiles beyond tool version bump flagged |
| NFR-12 | Every implementation ticket carries a cleanup clause; transient artifacts (scratch, probes, clones) deleted or declared durable in the done-check. | P0 | [E] user observation on cleanup; Stage-E practice | T-12 | Done-check text includes cleanup attestation; stale-scratch sweep reports clean tree at each milestone gate |

### 3.6 Observability

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-13 | Every service: JSON structured logs + `/healthz`. Mandatory. Metrics/tracing/Grafana are an **optional profile** off by default (attempt-1 lesson: observability built before services had traffic [E C4-adjacent]). | P0 | [E] | T-15 | healthz green for all; log lines parse as JSON with run_id/job_id fields where applicable |
| NFR-14 | Job and workflow status are answerable from the API **and** the filesystem without reading container logs (agent-visible state = first-class observability). | P0 | [E D25 lesson] | T-02 | Cold session answers run questions with API + files only |

### 3.7 Portability

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-15 | Whole stack = repo + `.env` + host image pre-seed step (documented; consequence of A6 no-registry). Bring-up procedure verbatim-reproducible on a second WSL2 host. | P1 | [E v3 invariant, retained] | T-13 | Documented dry-run on a clean WSL instance (or scripted checklist with all state files listed) passes M2 review |

### 3.8 Data integrity

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-16 | SHA-256 digest on every dataset, artifact-manifest entry, and promoted MinIO object; manifest is the root of trust per run. | P0 | [E] | T-04 | Verification script re-hashes a random sample per run; mismatch fails gate |
| NFR-17 | Ledger + git history are append-only/immutable tiers. MinIO **runtime**: in-app versioning protects hot-promotion mistakes. MinIO **backup**: version history ships **only** via the TD §6.9.3 **export** (rclone `--s3-versions` payload-per-version + `mc ls --versions --json` manifest); **`mc mirror` preserves no versions or versioning metadata (vendor-documented; the r2 mirror-history claim is retracted).** Restored-site semantics = re-upload as new versions (no old-`?versionId=` read-back at the restored site); coverage **specified, not proven** until T-22 runs at real MinIO+rclone versions; failure ⇒ OQ-8 (latest-only + *explicit* NFR relaxation — recorded, **not adopted**). Restore drill (§9.6) passes against the canonical destination. | P1 | [E A5/A6 runtime; export design pending T-22] | T-11, T-22 | Current-version restore reproduces digests **and** version-export payload count == N overwrites (T-22) |

### 3.9 Recoverability

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-18 | Cold-session resume ≤ 10 min wall incl. harness (FR-36); state is never *only* in agent context. | P0 | [V A12] | T-02 | Timed cold-session run in ledger |
| NFR-19 | Documented host-reboot recovery: compose `restart: unless-stopped` brings stack back; in-flight jobs resolved per FR-37 matrix with zero manual repair. Data-loss paths depend on §6.9 chain — **RPO is a local-completion RPO** (last `DONE.json` + git on host disk); off-host durability is **unproven** pending OQ-9 (no automated OneDrive L4/L5 completion signal exists in this environment, §6.9.4). | P1 | [P] | T-05 | Reboot drill logged at M1 |
| NFR-22 | Canonical backup root: **all backups** land under `/mnt/c/Users/steven/OneDrive/Backup/HE-toolstack/` (`$ROOT`; operator ruling D-14; restore reads the same path; no other destination is authoritative). Layout: `heat-data/`, `repo/` (git bundle), `drills/`, `.quarantine/`, transient `.candidate-*`. **Consistency & publication are normative (D-14 A1/A2, TD §6.9):** (a) **quiesce-and-wait** — `.backup-pause` set + active jobs == 0 before any copy; **no live-state override exists** (`--allow-active` withdrawn; a tree with active solver output can never be called application-consistent); (b) SQLite via online-backup API (WAL folded), MinIO via version export (§6.9.3), artifact copy only while quiet; (c) publish = robocopy → `$ROOT/.candidate-<runid>/` → **verify every destination digest vs manifest** → write `DONE.json` in candidate → rename **within the NTFS volume** to `<yyyymmdd>.<runid>/`; an ext4→`/mnt/c` rename crosses filesystems and is **not** atomic — every earlier such claim retracted; an interrupted run (no DONE) is never a restore source → quarantined, resumable via robocopy re-copy; (d) **OneDrive proof ladder L1–L5 (§6.9.4):** `DONE.json` = **L2 evidence only, never upload proof**; `attrib` placeholder = negative-only diagnosis; **no automated L4/L5 completion signal exists today** — L5 = manual web read-back log (M0) or Graph (OQ-9); robocopy exit 0 ≠ consistency, completion, or upload. | P0 | [V ruling 2026-11-15 + host path check; GitHub #6, rounds 1–5] | T-11, T-18 | Drill under quiesce policy: active job at start ⇒ abort, nothing published, `backup_stale` within grace; pause window ⇒ submission 409 `backup_paused`; happy path candidate→verify→DONE→NTFS publish rename; restore per §9.6 (SQLite/WAL, digests, version export, git bundle, L5 evidence) |

### 3.10 Extensibility

| ID | Description | Pri | Rationale / refs | Verification | Acceptance criteria |
|----|-------------|-----|------------------|--------------|---------------------|
| NFR-20 | New solver = new image + new compose service + one adapter row (job-type registry entry). Engine-specific logic stays out of toolserver/engine core ("thin and domain-agnostic", v3 inheritance [E SD]). | P1 | [E] | T-14 | M1 adds gmsh **through this path only** — diff review proves no core-file edits beyond the registry row |
| NFR-21 | GPU-class enablement is one config flag + C6 evidence, not a code change (FR-18). | P2 | [P] | T-06 | Flag flip rehearsed in staging compose profile |

---

| NFR-23 | Health reporting distinguishes **liveness** (`/healthz`: process serving), **readiness** (`/readyz`: required deps usable — DB, engine for toolserver), and **dependency health** (`/deps`: per-dependency ok/degraded/down + backlog depth). MinIO never gates liveness/readiness of solver execution. Agents see the three states distinctly in responses. | P0 | FINDING-06 [GitHub #7] | T-10 | With MinIO killed: `/healthz`+`/readyz` 200, `/deps` minio=down + backlog>0; with engine killed: toolserver `/readyz` 503 while `/healthz` 200; agent status payload carries the degraded marker |
| NFR-24 | Container/state reconciliation invariant: no container labeled `he-stack=1` exists that is not either (a) a compose service, (b) a running/claimed job with a registry row, or (c) pending janitor cleanup within grace (≤15 min [P]). Hourly janitor + boot reconciliation enforce; every sweep writes `reconcile_log`. |

## 4. Verification suite (test IDs referenced above; full strategy in tech design §14)

| ID | Name | Kind | Covers |
|----|------|------|--------|
| T-01 | M0 vertical-slice e2e (loop run) | e2e | FR-01/02/06/07/09/10/20/23/25/27/28, NFR-03 |
| T-02 | Cold-session resume harness (fresh agent, files+API only) | recovery e2e | FR-36/40, NFR-14/18 |
| T-03 | Physics-gate suite incl. negative (corruption) test | component | FR-20/21 |
| T-04 | Bit-identity A/B harness (frozen grids, digest checks) | regression | FR-07/14/22, NFR-16 |
| T-05 | Queue persistence + restart matrix (kill -9 engine, host reboot) | failure injection | FR-16/37, NFR-02/19 |
| T-06 | GPU admission tests (floor math, flag-off refusal, simulated VRAM) | component | FR-16/17/18, NFR-21 |
| T-07 | Crash-boundary matrix (artifact↔state↔ledger windows) | failure injection | FR-24/28/37/38 |
| T-08 | API contract suite (OpenAPI fixtures, idempotency, error envelope) | contract | FR-01/02/03/04/05/30/31/39 |
| T-09 | Per-tool smoke fixtures (gmsh CLI determinism, OpenFOAM cavity, ccx plate, CoolProp probes, agentcad export, envelope refusal, p95 latency under load) | integration | FR-08/11/12/13/14/15, NFR-04 |
| T-10 | Registry + history tests (lifecycle, bidirectional links, legacy D2 digest probe) | integration | FR-31/32/33/34 |
| T-11 | Full backup+restore drill **under the §6.9.1 quiesce-and-wait policy** (r5: the r2 framing "taken **while jobs run**" is **withdrawn** — it contradicted §6.9 refuse-mode and no live-state mode exists): negative case (active job at start → exit 2, nothing published, stale alarm within cadence+grace), pause-window case (submission attempt → 409 `backup_paused`), happy path (quiet → ext4 snapshot → candidate → destination verify → DONE → NTFS publish rename), then §9.6 restore against the **canonical destination**: SQLite integrity + WAL consistency, FR-37 reconciliation in a disposable copy, artifact digests, git-bundle recovery, marker/manifest integrity, MinIO current + version-export integrity, L5 read-back evidence recorded. **Specified design; NOT executed (stack unbuilt) — passing status must never be implied.** | ops drill | FR-29, NFR-17, NFR-22 |
| T-12 | Ticket/cleanup discipline audit (done-check attestation, scratch sweep) | process | FR-26/40, NFR-12 |

> **ID disambiguation (r3):** **T-12** = ticket/cleanup *process* audit only — it proves
> discipline, **not** concurrency. The §8.8 flock mutual-exclusion proof is **T-20**,
> supersede/expiry is **T-21**, SQLite queue/submission races + crash windows are **T-23**;
> digest-chain verification is **T-04/T-10**.
> TD §5.4-principle-4 and ADR-D-18 refs corrected accordingly.
| T-13 | Compose lifecycle (up/down zero-orphan, cold bring-up, gitleaks CI) | deployment | NFR-01/06/10 |
| T-14 | Worker-seam + extensibility exercises (add-solver-path review, second worker identity) | architecture test | NFR-05/20 |
| T-15 | Boundary **probe matrix, executed from inside the Hermes container** (1–4 executed 2026-11-15 [V], recorded ADR-D-15): (1) container-internal `127.0.0.1:8100` on the published port → **reachable** (service alive); (2) agent-side `127.0.0.1:8100` → **fails** (namespace isolation proof); (3) bridge-gateway `172.17.0.1:8100` → **reachable** (canonical agent path, authorized); (4) `host.docker.internal:8100` → **reachable** [V re-probe 2026-11-15b: BOTH the gateway IP and the `host.docker.internal` alias traverse to the WSL host from this container (identity-cross-checked via Ollama version bytes); an earlier `refused` reading did not reproduce and is retracted; the gateway IP stays canonical — `ip route`-derived, alias-independent]; **M0 additions**: (5) second container on default bridge, scan → **port 8100 closed** (unauthorized-container non-access); (6) non-root audit; (7) healthz/logs JSON | security/ops | NFR-07/08/13 |
| T-16 | Digest admission + MANIFEST CI check | security/supply-chain | FR-16 mechanism, NFR-09/11 |
| T-17 | Agent-container connectivity probe (FINDING-01; runs **from inside** a container like the agent's, host-side curl does not count) | e2e network | NFR-07, FR-01 |
| T-18 | Backup consistency + **two-part staleness** (r5, policy-aligned): sqlite online-backup product passes `PRAGMA integrity_check`; (i) no fresh valid `DONE.json` within cadence + grace → `backup_stale` (L2 alarm); (ii) L5 read-back evidence older than 7 d → operator reminder (§6.9.4 / R-8 ii); interrupted-transfer matrix: `.candidate-*` without DONE **and** dated-dir without DONE both excluded from restore selection and quarantined by the next run | drill | NFR-22 |
| T-19 | Daemon-restart reconciliation drill RC-3 (restart dockerd mid-job → re-adopt/re-queue per §8.6, gapless ledger) | drill | NFR-24, §12.5 RC-3 |
| T-20 | Concurrent ticket-claim **mutual exclusion** (TD §8.8 **r3 flock protocol**): **≥2 independent OS processes** (independent `flock()` calls; harness must not serialize) race `he ticket claim` on one fresh ticket — **exactly one** acquires the lock and claims, losers bounded-wait → `409 already_claimed`, **no loser reads or writes the ticket**; ledger holds exactly one claim event; the same race run with the supersede path armed (stale payload present) yields exactly one winner; **claimant-crash test:** `kill -9` the holder mid-critical-section → kernel releases the lock → a fresh claimant acquires and completes coherently; **retry test:** losers retry after winner releases and observe done/claimed states, never double-claim; 10× repetition, zero double-claims | concurrency test | FR-23…26, NFR-11 |
| T-21 | **Stale-claim supersede + expiry** (TD §8.8 **r3**): kill a claimant mid-session → after heartbeat staleness (`HE_CLAIM_STALE_MIN`, default 30 min [P]) **and** kernel-released lock, a second session acquires, re-verifies staleness under the lock, supersedes (ledger notes `superseded:`), and claims; **two concurrent superseders ⇒ exactly one proceeds** (flock serializes; loser 409); hung-but-alive holder is NOT supersedeable by design (test asserts 409 until the pid is killed); no ticket stuck unclaimable forever | concurrency test | FR-23…26, NFR-11 |
| T-22 | MinIO **version-history export** sufficiency (r5 rewrite — the r2 premise "`mc mirror` + server-side versioning ⇒ version-aware restore" was verified **false** and retracted): N overwrites of a gate-passed object in a versioned bucket → run the §6.9.3 export (`rclone --s3-versions` payload set + `mc ls --versions --json` manifest) into candidate → assert payload count == N, manifest↔payload 1:1, current-version digest match, re-upload-at-restore-site semantics documented. **Fail ⇒ OQ-8** (latest-only + explicit NFR-17 relaxation decision — no silent weakening). | backup-integrity test | NFR-22, NFR-17, FR-29 |
| T-23 | **SQLite queue/submission concurrency + crash matrix** (TD §7.5 r3 submissions inbox, §8.4b): (a) N≥4 concurrent `POST /v1/jobs` with **distinct** keys → N queue rows exactly (no loss/dup); (b) same `idempotency_key` raced 4× → **exactly one** queue row, dup requests resolve to the existing job id (dedup at consume); (c) engine `kill -9` between submission-insert and consume → after restart the submission is consumed once (idempotent replay), no half-consumed row; (d) `BEGIN IMMEDIATE` contention: concurrent consumes never interleave (affected-rows checks hold); busy/`503` behavior bounded-retry-then-honest | concurrency/failure-injection test | FR-16/37/39, NFR-02 |

## 5. Requirements traceability matrix (v1.4: +T-20; T-12 scope disambiguated) (requirement → components → tests)

Components: TS=toolserver, WE=workflow-engine(+queue/gpu-admission), PG=physics-gate,
MO=minio, REG=registry(SQLite-in-WE), HEA=he-client, HD=heat-data(host dir), IM=images
(6 narrow + future), OPS=compose/CI/host.

| Req | Components | Tests |
|-----|-----------|-------|
| FR-01…05 | TS, WE, HEA | T-08, T-01, T-09 |
| FR-06…09 | TS, HD, IM(property), WE | T-01, T-04, T-08, T-09 |
| FR-10…15 | IM(tasmet/gmsh/openfoam/calculix/property/agentcad), WE, TS | T-01, T-09, T-04 |
| FR-16…19 | WE(gpu-admission), OPS | T-05, T-06, T-23 |
| FR-20…22 | PG, HD, IM, WE | T-01, T-03, T-04 |
| FR-23…26 | WE, HD(workflows/), OPS | T-01, T-02, T-07, T-12, T-20, T-21 |
| FR-27…29 | HD, MO, WE | T-01, T-07, T-11, T-12 |
| FR-30…32 | TS, REG, MO | T-08, T-10 |
| FR-33…34 | REG, TS | T-10 |
| FR-35…38 | WE, HD | T-01, T-02, T-05, T-07, T-23 |
| FR-39…40 | HEA, HD, TS | T-08, T-02, T-12 |
| FR-41…42 | *(M3+ — excluded from initial-release matrix)* | — |
| T-17…23 (finding-response + r2/r3 tests; reqs themselves rowed above) | NFR-07, NFR-02, NFR-11, NFR-22, NFR-24 | T-17, T-18, T-19, T-20, T-21, T-22, T-23 |
| NFR-01…02 | OPS, WE | T-13, T-05 |
| NFR-03…04 | WE, TS, host | T-01, T-09 |
| NFR-05 | WE(worker seam) | T-14 |
| NFR-06…09 | OPS, TS, WE, IM | T-13, T-15, T-16 |
| NFR-10…12 | OPS, IM, HD | T-13, T-16, T-12 |
| NFR-13…14 | TS, WE, all services | T-15, T-02 |
| NFR-15 | OPS(repo+.env+seed) | T-13 |
| NFR-16…17 | HD, MO, REG | T-04, T-11 |
| NFR-18…19 | HD, WE, OPS | T-02, T-05 |
| NFR-22 | OPS, HD, WE | T-11 |
| NFR-23 | TS, WE, HEA | T-10 |
| NFR-24 | WE, OPS | T-09, T-13 |
| NFR-20…21 | IM, WE, TS(core) | T-14, T-06 |

No requirement is unmapped; no component appears without at least one requirement
(vocabulary §1 services: `agentcad`→FR-15; every T-id is referenced above).
Counts v1.2: 23 FR + 43 NFR = 66 IDs (FR-41/42 = M3+ boundary rows, excluded from the
initial-release matrix per design standards §15).

## 6. Open requirements (numbers not established — DesignStandards §15 rule)

| ID | Item | Status |
|----|------|--------|
| OR-01 | M0 wall-clock target (NFR-03 <10 min) | proposal; amend after first timed run |
| OR-02 | GPU VRAM floor/ceiling numbers (FR-17 5.5/8 GiB) | D-04 defaults; C6 re-measure is prerequisite to activation |
| OR-03 | Multi-worker throughput targets | no second host exists — M3+, no number invented |
| OR-04 | Artifact storage growth rate | measure at M1 (first real run corpus) |
| OR-05 | Chainguard MinIO rebuild availability (A11) | to-verify ticket before M1 promote-path acceptance |