# HE-toolstack — Deploy Plan v2 (ticket-based)

Replaces PD-toolstack STACK-DEPLOY-PLAN v1.1. Structural differences from v1:

| v1 property | v2 property | Why (evidence) |
|---|---|---|
| 6 stages, each a multi-session epic | Milestone 0 + horizontal thinning passes M1–M4 | Stage E = 4 sessions, ≥3 compactions; the plan itself had to be re-baselined mid-flight (v1.1) |
| Exit criteria checked at stage end | Each ticket carries its own ≤3-line done-check, verified same session it's claimed | E2b.1 sub-slice only appeared under context pressure; make it the size law |
| Agent's chat = workflow state | `workflows/` on disk = state machine; chat is disposable | Stage E survived compaction only via ledger luck, not design |
| Infra stood up before any physics worked | M0 proves one full physics route before breadth | v1 had observability (Stage C) before a validated engine result |
| New deploy surface each stage | `make up / verify / down` frozen after M0; passes change stacks/ and tickets, never compose shape | Orphan `infra-minio-1` proves side-car creep |

**State law**: one session claims ONE ticket (`workflows/tickets/<id>.md`), executes, verifies
its done-check, appends the ledger row (with `ref:` source for every non-trivial decision),
writes the handoff note, ends. A ticket that cannot state its done-check in ≤3 lines splits
before work starts.

---

## Pass C — Cleanup & migration (mechanical; no physics)

- **C1 seed repo** — Done-check: HE-toolstack has first commit with `docs/`, `he/` client
  stub, `Makefile`; `make help` runs. *(1 session)*
- **C2 evidence archive** — copy PD-toolstack run scripts + E1/E2b evidence dirs + open
  issues (#41, #42) text into `evidence/pd-archive/`. Done-check: `make verify-archive`
  counts committed evidence files vs manifest; fresh-context delegate can answer "what was
  E2b's gate result" from repo alone. *(1 session)*
- **C3 host orphan teardown** — copy (not move) orphan MinIO bucket contents into the app
  bucket (D-01; §7 item 2), then stop/remove compose project `infra` (`infra-minio-1`,
  config `/home/steven/PD-toolstack/infra/minio-compose.yml`) + its volume; verify Cognee
  stack untouched. Done-check: object counts copied == source before removal;
  `docker ps -a | grep -c minio` == 0 on host after app MinIO is up; Cognee healthcheck
  green. *(1 session)*
- **C4 working-copy archival** — host `~/PD-toolstack` + container `~/PD-toolstack` +
  `PD-toolstack-ops` → one tarball each in archive dir, then remove; runbooks extracted to
  `he/docs/runbooks/`. Done-check: `du` clean; runbooks reachable in new repo. *(1 session)*
- **C5 scratch prune + hygiene cron** — remove `stageE`, `e2bfix`, stray snap scripts;
  keep `pd-analysis` until design sign-off then tarball; register scratch 24 h prune.
  Done-check: `ls scratch` == {pd-analysis.tar.gz}; cron entry listed. *(1 session)*

## Pass 0 — Milestone 0 (the vertical slice; all green or M1 does not open)

- **T0.1 compose skeleton** — `compose.yaml` single project: toolserver, workflow-engine,
  physics-gate, minio (+bucket env), postgres optional-off; the 6 verified tool images
  registered profile-gated (D-10: kept separate, no consolidation). Images minimal:
  stub endpoints. Done-check: `make up` all-healthy under ONE project label;
  `make down` → `docker ps -a` empty. *(1 session)*
- **T0.2 serialized queue wired** — job JSON → workflow-engine SQLite FIFO queue (D-03/D-04:
  no broker daemon; host is the sole worker, D-11; CPU class) → execution via the existing
  digest-pinned tool images → log/run capture, via `he` HTTP client only. Done-check:
  submitted no-op job finishes; run dir exists; queue survives engine restart without job
  loss (write-ahead ordering per D-05). *(1 session)*
- **T0.3 TaSMET trivial solve on host** — minimal closed sCO2 loop config built on the host
  (TaSMET fork source pin recorded in `stacks/`; patches 0001–0003 replayed); solve returns
  converged run through the queue on the `ta-solver-runtime` digest.
  Done-check: run dir contains solution files + entropy-residual readout; pin committed. *(1–2 sessions — largest risk, sized first)*
- **T0.4 physics-gate carry-forward + M0 verdict** — gate image from PD-toolstack code;
  E1/E2b regressions become unit tests. Done-check: `make gate RUN=<m0>` emits 5-check
  verdict JSON; regression tests green. *(1 session)*
- **T0.5 registry + state machine files** — `registry/` JSONL + `workflows/` state files
  + handoff-note template + ledger with `ref:` field enforced. Done-check: **cold-session
  test** — a delegate with zero context states done/next correctly from `workflows/` only. *(1 session)*
- **T0.6 M0 acceptance run** — `make verify` chains M0a–M0e; evidence committed.
  Done-check: verify green, evidence dir committed, ledger closed. *(1 session)*

## Passes M1–M4 (each pass = one ticket at a time; scope, not schedule)

- **M1 engine breadth**: sCO2 recompression + combined Brayton/Rankine build manifests;
  registry fills; gate verdicts on all canonical points (E2b grid becomes M1 regression).
- **M2 fleet readiness**: worker registration contract exercised with the host as sole
  worker; GPU class enabled only after C6 re-measure passes (D-04: 8 GiB ceiling, 5.5 GiB
  protected floor, max-concurrency 1); concurrency/throughput ticket on the serialized queue.
- **M3 design-time/operate-time split**: optimizer as queue job-type; data-lake layout in
  MinIO (`he-artifacts` bucket); the old Stage E surface rebuilt against a working loop.
- **M4 observability**: prometheus/loki/tempo/grafana under `--profile observability` only;
  never required for green.

Deferred (tracked, not planned): registry DB upgrade, MCP facade, LangGraph adoption at
DESIGN-v2 §4 trigger conditions, optimizer service-vs-job decision.

## Session protocol (every session, mechanical)

1. Read `workflows/state.json` + latest ledger rows + open tickets. No other history needed.
2. Claim one unclaimed ticket (git mv to `tickets/claimed/`).
3. Execute; internet-first — any non-trivial decision gets a fetched-source `ref:` in the
   ledger row before the step is called done.
4. Verify done-check; only on PASS: write checkpoint (state.json cursor advance + ledger row
   + evidence commit). Failed step → record failure + effects outside the resume point.
5. Cleanup pass (§6 of DESIGN-v2 checklist) — part of acceptance, not optional.
6. Handoff note appended; release claim; end turn.
