# Round-05 — Grok ops-walk reply (verbatim, operator-delivered 2026-11-24)
# pinned SHA bc73dfce1b714a333ce4e53d4226f6dcf7c9741e · paste sha256 e700b2db7f3c97e7b8c45bf9acd7fea602e5eb73be0b90f9943a3feeec2b6759

GROK:
---------------------------------
Ops-reviewer walk — HE-toolstack

Pinned SHA: bc73dfce1b714a333ce4e53d4226f6dcf7c9741e

Role: council ops reviewer under single-human scheme (M3, M5, M7 + R-1…R-9 dry-runs)

HARD STOP observed: paper only. Walk executed from this pinned tree only; owner engineering transcript not consulted for these rows.

Q1 — M3 (D4 ↔ D-15 rev / zero host publication)
Verdict: PASS
From diagram text only (Diagram 4):
Quoted edge/node labels used as evidence:

Agent→toolserver edge:

AGENT[agent container<br/>default bridge +<br/>connected to he-agent net] -- "HTTP http://toolserver:8100<br/>(he-agent net member only; zero publish [V])" --> TS[toolserver]
Caption under D4:

“The agent↔toolserver path exists only on he-agent (zero host publication, D-15 Accepted). No inbound path is claimed from LAN or any non-member namespace…”
MinIO path on D4:

WE -- "S3 API :9000 in-net" --> MO[minio]

(in-project only; no host-publish edge for toolserver on this diagram).

Cross-check host-publication claim on adjacent Diagram 3 port label (same pin):

LB["host published ports: 9000/9001 minio only (operator,<br/>127.0.0.1 prefix; toolserver publishes NOTHING —<br/>reached via he-agent net, zero host listener [V D-15])"]
Exposure-path check on D4:

Sidecar edge: WE -- "spawn: 4-op HTTP<br/>(D-16 ACCEPTED 2026-11-16)" --> SC[spawn-sidecar<br/>he-internal only;<br/>sole docker.sock holder;<br/>root-equivalent if compromised] — confined to he-internal; no host-port publish.
No health-endpoint host-publish edge appears.
MinIO console access is only via the operator edge OPS -- "compose/CLI + :9001 console" --> STACK, and the D3 port label restricts 9000/9001 to 127.0.0.1 prefix.

No re-introduced exposure path found. Agreement with prose §5.3 / §5.4b / D-15: YES.
Sources: TD D4 mermaid ~L346; D3 ~L319; §5.3; DESIGN-REVIEW §2b M3.

Q2 — M5 (D9 ↔ NFR-01 six steps)
Verdict: PASS
Normative six steps (TD §6.10; NFR-01 restates the same ordered sequence):

Stop new job claims — docker compose stop -t <grace> workflow-engine (SIGTERM; stop claiming)
Gracefully terminate active class-J jobs — engine → sidecar POST /v1/runs/{id}/kill (SIGTERM, then kill within grace)
Record interruption/termination state write-ahead before engine exits
Stop class-C via Compose — docker compose down
Host-side janitor sweep of remaining he-stack=1 class-J remnants
Verify — docker ps -a --filter label=he-stack=1 -q = 0 and docker compose ps -a empty (class X excluded)

D9 element mapping (exact labels at this pin):

































StepD9 element1MD->>WE: step 1 compose stop -t grace<br/>SIGTERM: stop claiming2WE->>SC: step 2 POST /v1/runs/id kill<br/>(engine has NO socket, D-16) → SC->>JB: SIGTERM running jobs3WE->>WE: step 3 record interrupted/killed<br/>write-ahead BEFORE exit then WE->>WE: engine exits (drained)4MD->>CP: step 4 docker compose down<br/>(removes class C only)5MD->>MD: step 5 host-side janitor sweep<br/>rm label he-stack=1 remnants<br/>(works with engine AND sidecar dead)6Note over MD: step 6 assert: docker ps -a filtered by label he-stack=1 returns zero<br/>covers class C and J — class X host backup timer is not a container
Ordering (stop-orchestration vs confirm-no-container-created):

In both prose (§6.10 / NFR-01) and D9, stop-orchestration (steps 1–4) precedes the zero-container confirmation (step 6). Confirm is the final assertion, not an intermediate gate. No normative step is absent from D9; none is paraphrased so loosely that sequence is lost.
Note on §2b M5 parenthetical: the checklist row still carries an older paraphrase (“SIGTERM → drain → stop-orchestration → confirm-no-container-created → engine exits → sidecar → class-C core-5 → down --remove-orphans”). That parenthetical does not match the normative six-step list. The walk is against §6.10 / NFR-01 (the normative sources named by NFR-01 itself). D9 matches those sources. Minimum fix if desired: replace the §2b M5 parenthetical with the six numbered steps from §6.10 so the checklist text cannot drift again.
Sources: TD §6.10 ~L875–; D9 mermaid ~L902; REQ NFR-01; DESIGN-REVIEW §2b M5.

Q3 — M7 (D7/D8 ↔ §8 write-order + §6.9 backup)
Verdict: PASS
1. Write-order (artifacts → state → ledger)

D7 labels:
C->>HD: artifacts written + fsync, manifest.json
→ W->>HD: state.json atomic rename (boundary 1)
→ W->>L: ledger append + git push (ref: digests)
→ W->>HD: state.json promoted (boundary 3)
Prose: §5.4 principle 3 / D-05: “artifacts fsync → state.json atomic rename → ledger append + git push”.
Names and sequence match.

2. Quiesce-and-wait

D8 label: H->>HD: quiesce pause file then wait active jobs to zero else abort
Prose: §6.9.1 “Chosen for M0: quiesce-and-wait; no live-state override exists”; active job at start → abort exit 2, nothing published.
Match.

3. OneDrive root + digest verify

D8 labels:
participant C as OneDrive root candidate then dated dir on NTFS
H->>C: robocopy snapshot into candidate dir L2 local copy
H->>C: verify every destination digest then write DONE.json
H->>C: publish rename within NTFS volume into dated runid dir
Note: OneDrive upload completion NOT provable locally L4 L5 gap OQ-9 manual web read-back is the L5 evidence
Prose: §6.9 destination /mnt/c/Users/steven/OneDrive/Backup/HE-toolstack/ ($ROOT); §6.9.2 steps 4–7 candidate → digest verify → DONE.json → same-volume NTFS publish rename; §6.9.4 L2 = local digest-verified, L4/L5 unproven without manual web read-back.

Diagram uses the role label “OneDrive root”; prose uses the absolute $ROOT path. Sequence and digest-verify step are identical; no conflicting sequence or renamed root.
Sources: D7/D8 mermaid (Appendix B ~L1766/L1793); TD §5.4, §6.9.1–§6.9.4; DESIGN-REVIEW §2b M7.

Q4 — Runbook dry-runs (R-1…R-9)
Paper-only. Scenario invented per runbook; walk symptom → verify → act → verify strictly as written.

































































IDScenarioWalkVerdictR-1Windows update restarts WSL; operator finds no stack containers, old agent session still open.Symptom: stack absent. Verify: make ps → empty. Act: make up (WAL recovers per §8.6). Verify: smoke + ledger note.EXECUTABLE-BLINDLYR-2CFD job shows running 4 h with no log progress; lease age > 2× timeout.Symptom: stuck job. Verify: make doctor lease scan. Act: cancel via API (§7.2); if container live → engine cancel path; if spawn broken → R-5.EXECUTABLE-BLINDLYR-3Agent submits GPU-class job; response gpu-class-disabled.Symptom: GPU refuse. Verify: GPU_CLASS_ENABLED + C6 ticket state + probe file. Act: do not toggle flag (FR-18). Expected normal until C6.EXECUTABLE-BLINDLYR-4Host disk /dev/sdf replaced; heat-data empty.Symptom: total state loss. Verify: empty heat-data. Act: restore fresh host dirs from nightly backup at canonical root (§6.9) → make up → T-11 (pull one promoted object by versionId, digest-compare) → M0 slice smoke.GAP — “fresh host dirs from nightly backup” does not name the exact restore command sequence or which files under $ROOT to copy first. Minimum fix: add one concrete restore command block (or numbered pointer into §9.6).R-5Sidecar returns 500 on every create_run; engine logs spawn_timeout.Symptom: spawn channel broken. Act: sidecar restart (make up workflow-engine scoped) → make test-smoke; if docker.sock class → host docker service check (out-of-stack).GAP — “make up workflow-engine scoped” is undefined (compose filter? profile? make target?). Minimum fix: replace with the exact invocation (docker compose up -d spawn-sidecar or the real make target).R-6Run reaches degraded-evidence after overnight MinIO restart.Symptom: degraded-evidence. Verify: minio healthz + creds env. Act: promote retries auto; if bucket-missing, recreate (idempotent). Succeeded runs stand.EXECUTABLE-BLINDLYR-7Engine refuses new jobs; logs show hard watermark.Symptom: disk full. Verify: engine refuse (FM-6). Act: archive cold runs to archive disk (promotion copies in MinIO); decision support: du report command.GAP — du invocation not given; “archive disk” path undefined. Minimum fix: supply exact du command and canonical archive destination (or “operator chooses, record in ledger”).R-8make doctor fails; sentinel age 48 h; OneDrive was paused over a weekend.Symptom: stale backup. Verify: (i) no fresh DONE.json / sentinel > 36 h; (ii) drills/onedrive-readback.log mtime > 7 d. Act: re-mount/enable → make backup → confirm DONE; for L5, manual web read-back + log.EXECUTABLE-BLINDLYR-9Operator runs sudo systemctl restart docker with one synthetic job live (WSL2 daemon-restart class).Symptom: all containers return; possible orphaned running rows. Verify: reconcile log shows re-adopt or re-queue per §8.6. Act: automatic. Verify: job completes, ledger gapless.EXECUTABLE-BLINDLY (acceptance drill; unplanned path covered by R-1 + §8.6).
Scenario list for independent re-run:

WSL restart after Windows update, stack gone.
CFD job running 4 h, no log progress, lease overdue.
GPU-class submit returns gpu-class-disabled.
/dev/sdf replaced, heat-data empty.
Sidecar 500 / spawn_timeout on every create.
Overnight MinIO restart → degraded-evidence.
Hard watermark refuse, disk full.
OneDrive paused over weekend, sentinel 48 h old.
Planned systemctl restart docker with one synthetic job live.


Ops-row summary for §9

M3 PASS · M5 PASS · M7 PASS · Runbooks: 6 EXECUTABLE-BLINDLY, 3 GAP (R-4 restore command sequence, R-5 scoped make target, R-7 du/archive path).
Optional non-blocking doc fixes: (a) §2b M5 parenthetical → replace with the six numbered §6.10 steps; (b) the three runbook GAPs above. None of these affect the diagram walks.
This transcript is the ops evidence record under the single-human scheme at pin bc73dfce1b714a333ce4e53d4226f6dcf7c9741e. Sign-off weight is the owner’s witness of the walk, not a claim of independent-human review.

