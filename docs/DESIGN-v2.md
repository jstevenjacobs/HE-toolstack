# HE-toolstack — Design v2

Supersedes PD-toolstack STACK-DESIGN v3.8.1. PD-toolstack is frozen as read-only evidence.
This document records what changes, why, and which first-attempt evidence (E1-E2b, D-ledger,
session record) each change traces to.
**Status: direction-setting draft.** Phase 1 discovery & validation (`PHASE1-ARCHITECTURE-DISCOVERY.md`)
supersedes parts of §1–§3 where marked; the engineering-grade spec is
`HE-TOOLSTACK-TECHNICAL-DESIGN.md` (Phase 2).

---

## 1. What v1 got right — keep unchanged

These are first-attempt assets; the rewrite reuses them as requirements and fixtures, not as
incidental context:

1. **Physics-gate methodology**: 5 independent checks (1st-law closure, exergy balance,
   Clausius-inequality, Carnot bound, 2nd-law efficiency) as design-time requirements, plus the
   proven **gate-script pattern** (`properties/d2/gate.py` in `ta-validation`: fresh frozen probe
   set, named dataset+digest inputs, p99 thresholds, corruption negative test exits 1). E1 and E2
   proved gates catch real physics errors the solver's own residual could not (fixed-(T,P) BC,
   ~73.8 bar entropy inconsistency). Note: no physics-gate *service* code exists — v1 shipped the
   methodology + scripts, not a running service (see correction below).
2. **Queue-serialization discipline (per user ruling v3.2)**: GPU tasks serialized by the job
   queue itself (resource class, max-concurrency 1) + entrypoint admission (queue token +
   free-VRAM floor), no lease daemon. **A `gpu-broker` service was never built and was deleted by
   ruling in design v3.2** before Stage E ran.
3. **Evidence-first workflow**: every acceptance gate is a committed artifact (run dir +
   report + ledger row); "done" means gate-pass + evidence committed, never "it looks fine".
4. **Numeric acceptance methodology**: frozen grid, worst-observed vs measured resolution
   floor, no curve-fitting to pass gates. E2b's gate design (≤2× floor, 52/52 PASS,
   worst 0.12) is the template for all future gates.
5. **Ledger / issue discipline**: numbered ledger rows (D1…D27), issues as durable
   memory — this is what let the Stage E sessions survive compaction at all.
6. **Digest launch path**: `orchestrator/resolve.py` (audits repo:tag → MANIFEST digest vs live
   image ID, runs BY DIGEST, refuses unmanifested) + `pull_policy: never` — verified code, carried.
7. **MinIO backup mechanics**: nightly backup + versioned buckets + passed restore drill
   (Stage A5/A6) — the ops discipline carried into the in-app MinIO service.

> **Correction (2026-11-14 source-integrity pass):** an earlier revision of this section listed
> "physics-gate/ (FastAPI service)" and "gpu-broker/" as carried-forward *code*. Verified false —
> no such service code exists in any repo (grep across all sources; see
> `PHASE1-ARCHITECTURE-DISCOVERY.md` §1.2/§4.1 C1–C3). Stage E's real tool surface was
> terminal+ssh+docker with the GitHub issue/ledger as state. What actually carries forward is
> listed above.

## 2. What failed and is removed in v2

1. **The 6-stage waterfall deploy plan** (A→B→C→D→E→F, exit-criteria-gated): Stage E alone
   consumed 4 sessions and multiple compactions. The plan's own re-baselining (v1.1) admits
   it. Replaced by vertical-slice Milestone 0 + thinning passes (§5).
2. **MCP as the tool-facing protocol for long-running jobs**: the MCP client cannot wait out
   GPU jobs; every long op became a poll-scripted terminal invocation and hand-maintained
   in-chat state (job ids, run paths). Replaced by plain HTTP/JSON tools + durable external
   state (§3, §4).
3. **Per-tool micro-containers** (8 images for 4 services): multiplied build, pin, health,
   and log surface without buying isolation. Consolidated to 4 images (§3).
4. **Side-car MinIO as a separate compose project** (`infra/minio-compose.yml`, project
   `infra`, still running as an orphan on the host): a second compose app has no business
   owning stack storage. Replaced by a service in the single compose app with its bucket
   defined in config (§3).
5. **The agent's chat context as the workflow state machine**: stage progression, gate
   bookkeeping, and evidence pointers lived in the conversation and had to be regenerated
   after every compaction. Replaced by externalized state read from disk at each step (§4).

## 3. System architecture

One repo, **one docker compose application** (`he/` in the repo). Everything the stack needs
runs inside it; nothing of the stack lives outside it.

```
he/
  compose.yaml            # single app: all services, one network, one project name
  .env.example            # every knob; no secrets committed
  services/
    toolserver/           # image 1: ALL read/inspect tool endpoints (FastAPI)
                          #   read_solution, inspect_case, solve_job_status, list_runs,
                          #   diff_runs, entropy-residual readout ...
                          #   (replaces pd-read + pd-solve-gate + pd-browse: 1 image)
    solver/               # image 2: TaSMET build baked in at deploy time (pin recorded);
                          #   long-running solve endpoints; writes runs to workspace volume
    physics-gate/         # image 3: carry forward from PD-toolstack (proven);
                          #   E1/E2b regressions become its unit tests
    gpu-broker/           # image 4: carry forward (proven); gpu1 host as remote worker
    minio/                # service, NOT a side-car app; bucket `he-artifacts` defined
                          #   via compose environment; MinIO CONSOLE + S3 API on the
                          #   internal network only
  stacks/                 # per-engine build manifests (what gets built on gpu1)
  workflows/              # §4 state: goal.md, ledger.md, tickets/, runs/<id>/
  registry/               # candidate registry (flat files on volume, MinIO for blobs)
  he/                     # tiny python client (pip -e) the agent uses for HTTP calls,
                          #   json_get/json_post pattern from Stage D kept
```

Consumption surface for the agent: **plain HTTP/JSON + `he` client**. Rationale (internet,
not model memory): MCP's own spec/task-notification story for long-running work is immature,
and what we actually used MCP for was request/response reads — plain REST removes a protocol
layer and its poll-scripting overhead. If editor/IDE integration is wanted later, an MCP
facade can wrap the same REST tools without changing the stack (LangGraph's deep
MCP/LangChain integration makes that a one-node change).

Host topology unchanged: WSL2 boxes, one GPU (gpu1), no nested virtualization on host —
the proven pattern: heavy solver builds compile on gpu1, containers mount artifacts.

## 4. Workflow engine (the #1 fix)

**Durable state machine outside the model context.** First-attempt evidence: Stage E passed
through ≥3 context compactions; each handoff worked only because a ledger and evidence files
happened to exist on disk; conversely all *live* progress bookkeeping (job queues, gate
status, next steps) was reconstructed from summary text each time — lossy and expensive.

External research (LangChain checkpointer docs; Temporal's LangGraph integration post; AWS
Well-Architected agentic checkpointing guidance; O'Reilly "When Context Collapses")
converges on one design, which we adopt:

- **State**: `workflows/goal.md` (task continuity, written once) + per-run
  `runs/<id>/state.json` (execution continuity: plan version, step cursor, gate results,
  external run ids, budget) + `ledger.md` (accepted decisions, append-only).
- **Transitions**: one turn = one claimed ticket → run step → verify acceptance → write
  checkpoint. Checkpoint **after acceptance passes**, never after mere execution (vishal /
  AWS guidance: a resumed run must never resume into a failed-check state).
- **Idempotency**: every side effect carries an idempotency key (job names, commit topics,
  registry keys), so a replayed/resumed step cannot duplicate effects (AWS guidance).
- **Session hygiene**: the ledger is also the cross-session handoff. Each session ends with
  an explicit handoff note in `ledger.md`: state snapshot, 3-5 sentence narrative of why
  state looks as it does, priority queue for the next session (Zylos handoff pattern).
- **Fresh context per ticket is the default, not the exception**: heavy work (solver builds,
  sweeps, gate runs, code edits) is dispatched to `delegate_task` children or cron jobs that
  run *against the filesystem contract*, not against conversation. The orchestrator session
  stays small: read state, dispatch, verify evidence, checkpoint, end turn.

**On LangGraph specifically**: adopted as *inspiration now, dependency later*. Its
checkpointer/interrupt model is the right skeleton, but a self-written ~200-line JSON state
machine with idempotent steps gives the same recovery properties for single-operator,
file-backed use, at zero dependency cost — and it lives *in the same compose app* so it is
auditable. Migration trigger (written into the design so it is a decision, not drift): when
the workflow needs parallel fan-out across workers, durable multi-day HITL waits, or
crash-restart supervision, move the state machine to LangGraph + PostgresSaver (and Temporal
only if runs must survive process death — per Temporal's own docs, checkpoints are durable
data, not durable execution).

## 5. Delivery plan — vertical slices, not stages

**Milestone 0 ("trivial engine, whole loop", one compose up, one engine, one route)**:

> Deploy `he` stack → agent builds a minimal **closed sCO2 loop** engine config on gpu1 →
> run solve → entropy-residual readout → physics-gate verdict → run dir + registry entry →
> ledger checkpoint. Nothing else exists until this route works end to end.

Milestone 0 acceptance (all mechanical, all visible in one `make verify`):
- M0a: `docker compose up -d --build` reaches all-healthy; single project label; `compose down`
  leaves zero containers (v1's orphan problem, tested explicitly).
- M0b: one solve job completes via broker queue on gpu1 through HTTP only.
- M0c: physics-gate returns a verdict JSON on the M0 run with all 5 checks computed.
- M0d: registry + ledger rows written; a fresh session can answer "what is done / what's next"
  by reading `workflows/` only — verified by a delegate_task child with no other context.
- M0e: internet-first rule exercised: at least one design decision cites a fetched source
  (this document's §4 already does).

**Then thin horizontally, each pass a ticket-sized increment**:
- M1: engine breadth — real sCO2 recompression + combined Brayton/Rankine configs;
  candidate registry fills.
- M2: fleet — gpu2 joins broker pool; throughput sweep.
- M3: optimizer + data lake (the old Stage E design-time/operate-time split), now built
  against a working loop, not ahead of one.
- M4: observability (Prometheus/Loki/Grafana/Tempo as *optional compose profiles*
  — `docker compose --profile observability up`), never required for a green run.

Every increment must terminate **green** before the next is opened (v1's E2a→E2b rule,
generalized): an increment ends when its gate evidence is committed, never "when it compiles".

## 6. Working agreements (process fixes made mechanical)

1. **Internet-first**: any non-trivial design/implementation choice logs one fetched source
   next to the decision (file: `workflows/ledger.md` row carries a `ref:` field). v1's
   worst failure mode — silently substituting model priors for documentation — becomes a
   visible missing-field per ledger row.
2. **Cleanup is part of acceptance, not hygiene**: per-step checklist — exit temp worktrees,
   remove temp containers/volumes (`compose down -v` semantics), prune scratch to the
   documented dirs (`/opt/data/cache/scratch/{pd-analysis,e2bfix}` exceptions until archive,
   §7). M0a makes the container case untestable-to-fail explicitly.
3. **One increment per session-turn-class**: a turn's scope is one ticket; if a ticket cannot
   state its own done-check in ≤3 lines, it is too big and must split (Stage E's
   E2→E2a→E2b→E2b.1 split was evidence discovered under duress; here it is the size law).
4. **PD-toolstack remains frozen** — no commits; archive issues/PRs to the new repo's
   `.archive/` (§7); the old MinIO orphan handled per §7 cleanup pass.

## 7. Migration & cleanup pass (first tickets, by definition mechanical)

- C1: create HE-toolstack seed commit: this doc + `he/` scaffold + `Makefile` targets.
- C2: archive evidence from PD-toolstack: run scripts (`scripts/verify_e1.py`,
  `scripts/verify_e2.py`, `scripts/e2b_*`), the E1/E2b evidence dirs, and open issues #41,
  #42 into HE-toolstack `evidence/pd-archive/` + issue text; close PD-toolstack with a final
  README pointer commit **only if** the user later reopens writes — until then PD-toolstack
  receives nothing.
- C3: host: stop + remove orphan `infra-minio-1` (compose project `infra`, config
  `/home/steven/PD-toolstack/infra/minio-compose.yml`); confirm Cognee unaffected (it is:
  Cognee embed env has no MinIO refs); prune its volume.
- C4: host `~/PD-toolstack` (160 MB) and container `~/PD-toolstack` (6.8 MB) → tarball to
  archive location, then remove working copies; `PD-toolstack-ops` removed (runbooks copied
  to `he/docs/runbooks/`).
- C5: container scratch: keep `pd-analysis` until this design is signed off, then keep as
  single tarball; remove `stageE` (219 MB), `e2bfix` (126 MB), stray snapshot scripts;
  add the 24 h-prune cron explicitly.

## 8. Open design decisions (deliberately deferred, tracked as tickets)

1. Registry format: flat JSONL vs SQLite vs Postgres-in-compose (defer until M1; files-first
   per filesystem-state pattern).
2. MCP facade for editor integration (defer; see §3).
3. LangGraph adoption at the trigger conditions in §4.
4. Whether the optimizer (M3) is a service image or a broker job type.

---
*Evidence anchors: STACK-DESIGN v3.8.1, STACK-DEPLOY-PLAN v1.1 (re-baseline note),
STACK-AS-BUILT ledger D1–D27, sessions "Build Local Agentic Heat Engine Stack" + Stage B–E
chain (4 sessions for Stage E, ≥3 compactions), external sources listed in §4.*
