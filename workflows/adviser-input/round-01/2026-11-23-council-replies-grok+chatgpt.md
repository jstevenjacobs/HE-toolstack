I have deceided to remove Gemini from the council due to that agent's lack of access to Github.

GROK:
---------------------------------
VERDICT: APPROVE-WITH-CHANGES

FINDINGS:

[major] Q22 row in docs/HE-TOOLSTACK-QA-REPORT.md is truncated mid-sentence on disk (ends after "are"); the claimed 27/27 cannot be text-verified from the checked-in file without external knowledge of the missing Result/Evidence cells. This matches residual-risk R-10 and must be repaired before any claim of gate completeness is treated as authoritative.
[minor] TD §8.8 flock-based claim protocol is sound for the T-20/T-21 failure classes under current kernel semantics, but the design should explicitly document that the lock-holding process must keep the fd open for the entire critical section (no early close of any fd referring to the lockfile) because flock locks are tied to the open-file description.
[nit] For the orphan MinIO case the done-check should assert both container absence and volume absence (or an explicit decision to retain the volume); a pure docker ps check is insufficient against the data-loss trap of accidental -v.
ANSWERS:

The four-op surface (create_run ≈ ContainerCreate + ContainerStart, inspect-or-status ≈ ContainerInspect / ContainerList filtered, kill ≈ ContainerKill, logs ≈ ContainerLogs) is sufficient for TD §6.2b M0 needs (CPU-only, single Compose project, one-shot tool containers). Current Docker Engine API (v1.47+ / current 1.57) exposes exactly these endpoints; no additional capability required by the M0 description (image pull is assumed pre-seeded via pull_policy: never + MANIFEST, networking is the default project network, no GPU, no exec, no volume management beyond the host bind already owned by the engine) is missing from the four ops. Source: [docs.docker.com/reference/api/engine](https://docs.docker.com/reference/api/engine/) (accessed 2026-11-23); [docs.docker.com/reference/api/engine/sdk/examples](https://docs.docker.com/reference/api/engine/sdk/examples/) (accessed 2026-11-23).

Yes — flock(2) locks are released when all file descriptors referring to the open-file description are closed. Process termination (normal exit, SIGTERM, or SIGKILL) causes the kernel to close every open fd, releasing the lock. The same holds for a container killed by the runtime (SIGKILL delivered to PID 1 / the process group). No containerd-specific caveat alters this for an ordinary Linux container on ext4; the lock is a kernel VFS object. Source: [man7.org/linux/man-pages/man2/flock.2.html](https://man7.org/linux/man-pages/man2/flock.2.html) (accessed 2026-11-23); [kernel.org/doc/man-pages/online/pages/man2/flock.2.html](https://www.kernel.org/doc/man-pages/online/pages/man2/flock.2.html) (accessed 2026-11-23). (fcntl record locks are likewise released on process termination — [man7.org/linux/man-pages/man2/fcntl_locking.2.html](https://man7.org/linux/man-pages/man2/fcntl_locking.2.html).)

Correct upstream sequence for an orphan container that still belongs to a named Compose project: docker compose -p <project> down --remove-orphans (optionally -v only after confirming the volume is disposable). If the volume is named and declared in the (possibly absent) Compose file, -v removes it; external volumes are never removed. Data-loss trap the done-check must guard: -v (or a subsequent docker volume rm) permanently discards MinIO object data with no recovery path; the check should therefore verify container gone and either volume retained or an explicit “purge approved” flag before considering the teardown complete. Source: [docs.docker.com/reference/cli/docker/compose/down](https://docs.docker.com/reference/cli/docker/compose/down/) (accessed 2026-11-23).

Permalink used: [raw.githubusercontent.com/jstevenjacobs/HE-toolstack/dp/round-01-dp0/docs/HE-TOOLSTACK-QA-REPORT.md](https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/dp/round-01-dp0/docs/HE-TOOLSTACK-QA-REPORT.md) (accessed 2026-11-23). The Q22 table row is truncated after the description text:
| Q22 | Tests T-20 (flock claim race — ≥2 processes, exactly one winner, crash+retry), T-21 (stale-claim supersede/expiry), T-22 (MinIO version-history sufficiency through staging), T-23 (SQLite submission-inbox concurrency + crash matrix) are
The Result and Evidence columns (and the rest of the sentence) are absent on disk. The subsequent Q23 row begins normally. This matches the residual-risk claim that the on-disk file is incomplete and the 27/27 assertion is not text-verifiable from the repo alone.

No gotcha that would break TD §7.2. Healthchecks are executed by the Docker daemon inside the container’s network namespace; they reach the service on its container port regardless of whether that port appears in ports: or only in expose: (or is merely listened on). expose documents the port for inter-service discovery on the Compose network but does not publish to the host; omitting ports: simply means the host cannot reach the endpoints, which is the desired zero-host-publication posture. Source: [docs.docker.com/compose/how-tos/networking](https://docs.docker.com/compose/how-tos/networking/) (accessed 2026-11-23); [docs.docker.com/reference/compose-file/workload-spec](https://docs.docker.com/reference/compose-file/workload-spec/) (expose / healthcheck / ports sections, accessed 2026-11-23).

CHATGPT:
-------------------------------------------------------
VERDICT: APPROVE-WITH-CHANGES

FINDINGS:

1. [major] OneDrive durability is incorrectly treated as deferrable across the destructive Pass-C boundary. R-04 permits L4/L5 durability proof or D-05 fallback acceptance to wait until M0 close, but C3 stages the orphan MinIO contents under the OneDrive backup path and subsequently deletes the original MinIO volume. Matching local object counts and byte totals does not establish that the staged data has reached durable off-host storage. If synchronization has not completed, the original may be destroyed while the only surviving copy remains on the local disk. Require verified independent durability or explicit operator acceptance of a tested fallback before C3's volume-removal step. This is a data-preservation gate, not merely an M0 acceptance item.

2. [major] The M0 dependency chain omits a necessary T0.4 → T0.5 dependency. T0.4's physics-gate implementation requires the registry to refuse a succeeded state when the gate report is missing or erroneous. T0.5 owns the registry and its write-time enforcement. T0.4 currently requires T0.3 but does not list T0.5 as a precondition. This creates a risk that the gate implementation is built against an undefined registry contract or that the registry enforcement is retrofitted after the gate has already been implemented. Explicitly establish T0.5's registry contract before T0.4 integration.

3. [minor] The action-plan phase order and the residual-risk GO statement are not sufficiently aligned. The register permits Pass-C cleanup while R-05, R-09 and R-10 remain open. However, the action plan places freeze repairs and build-readiness rulings in P2, before the Pass-C execution plan in P3. The distinction between permission to prepare or execute C1–C5 and permission to begin M0 must be explicit. Otherwise, the agent may interpret the GO statement as authorization to bypass P2.

4. [minor] C3's data-equivalence test is insufficient for an irreversible deletion. Recursive object counts and aggregate byte totals are useful but cannot detect an object being replaced by different content of identical size. Require per-object checksums where supported, or an equivalent content-integrity verification, before the source volume is removed.

5. [minor] The 1-turn-per-ticket policy needs a stronger checkpoint rule. A ticket can finish within the context budget while leaving an incorrect architectural assumption embedded in the next ticket's implementation. The ledger currently provides continuity, but continuity is not independent validation. Require explicit verification of upstream contracts and evidence before downstream implementation begins.

ANSWERS:
1. Pass-C GO versus R-05/R-09/R-10
The separation is defensible, with one qualification: GO must mean permission to execute the five cleanup tickets, not permission to begin M0 or claim the design is frozen.
- R-05 — D-06/OQ-4: Does not gate C1–C5. It absolutely gates T0.4 and therefore M0 completion. Its ruling must be recorded before any T0.x build, as the register specifies.
- R-09 — QA harness promotion: Does not gate C1–C5. It gates the M0 start/re-gate decision. I recommend promoting the harness into scripts/qa/ rather than accepting an author-only reproducibility model.
- R-10 — freeze repairs: Does not gate C1–C5, but it gates the integrity of the frozen design package and the first M0 build handoff. The Q22 truncation is particularly important: a 27/27 claim must have 27 independently inspectable results.
There is no reason to prevent non-build cleanup while these items remain open. However, P2 should close before M0 authorization, and the action plan should state whether P2 is also a prerequisite to formally declaring P3 open.
2. Pass-C claim order and M0 dependencies
Pass C: C1 → C2 → C3 → C4 → C5 is defensible. I found no dependency inversion that would strand a ticket, but the ordering is more restrictive than strictly necessary.
Ticket	Dependency assessment
C1	Correct first. Establishes Makefile and he/ scaffold.
C2	Correct before destructive cleanup. Archives the PD-toolstack evidence needed by later work.
C3	Correct after C2. Requires independent durability verification before volume deletion.
C4	Correct after C3. Explicitly requires the orphan service to be retired.
C5	Correct after C2. Does not technically require C3 or C4.

C5 could be moved immediately after C2, but there is no compelling reason to introduce parallel execution.

M0: the proposed dependency chain needs correction.

The actual dependencies are:
#chatgpt-mermaid-_r_gi_{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;fill:rgb(237, 237, 237);}@keyframes edge-animation-frame{from{stroke-dashoffset:0;}}@keyframes dash{to{stroke-dashoffset:0;}}#chatgpt-mermaid-_r_gi_ .edge-animation-slow{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 50s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_gi_ .edge-animation-fast{stroke-dasharray:9,5!important;stroke-dashoffset:900;animation:dash 20s linear infinite;stroke-linecap:round;}#chatgpt-mermaid-_r_gi_ .error-icon{fill:rgb(48, 48, 48);}#chatgpt-mermaid-_r_gi_ .error-text{fill:rgb(237, 237, 237);stroke:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ .edge-thickness-normal{stroke-width:1px;}#chatgpt-mermaid-_r_gi_ .edge-thickness-thick{stroke-width:3.5px;}#chatgpt-mermaid-_r_gi_ .edge-pattern-solid{stroke-dasharray:0;}#chatgpt-mermaid-_r_gi_ .edge-thickness-invisible{stroke-width:0;fill:none;}#chatgpt-mermaid-_r_gi_ .edge-pattern-dashed{stroke-dasharray:3;}#chatgpt-mermaid-_r_gi_ .edge-pattern-dotted{stroke-dasharray:2;}#chatgpt-mermaid-_r_gi_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_gi_ .marker.cross{stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_gi_ svg{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:16px;}#chatgpt-mermaid-_r_gi_ p{margin:0;}#chatgpt-mermaid-_r_gi_ .label{font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ .cluster-label text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ .cluster-label span{color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ .cluster-label span p{background-color:transparent;}#chatgpt-mermaid-_r_gi_ .label text,#chatgpt-mermaid-_r_gi_ span{fill:rgb(237, 237, 237);color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ .node rect,#chatgpt-mermaid-_r_gi_ .node circle,#chatgpt-mermaid-_r_gi_ .node ellipse,#chatgpt-mermaid-_r_gi_ .node polygon,#chatgpt-mermaid-_r_gi_ .node path{fill:rgb(9, 23, 44);stroke:rgb(31, 78, 148);stroke-width:1px;}#chatgpt-mermaid-_r_gi_ .rough-node .label text,#chatgpt-mermaid-_r_gi_ .node .label text,#chatgpt-mermaid-_r_gi_ .image-shape .label,#chatgpt-mermaid-_r_gi_ .icon-shape .label{text-anchor:middle;}#chatgpt-mermaid-_r_gi_ .node .katex path{fill:#000;stroke:#000;stroke-width:1px;}#chatgpt-mermaid-_r_gi_ .rough-node .label,#chatgpt-mermaid-_r_gi_ .node .label,#chatgpt-mermaid-_r_gi_ .image-shape .label,#chatgpt-mermaid-_r_gi_ .icon-shape .label{text-align:center;}#chatgpt-mermaid-_r_gi_ .node.clickable{cursor:pointer;}#chatgpt-mermaid-_r_gi_ .root .anchor path{fill:rgb(175, 175, 175)!important;stroke-width:0;stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_gi_ .arrowheadPath{fill:rgb(175, 175, 175);}#chatgpt-mermaid-_r_gi_ .edgePath .path{stroke:rgb(175, 175, 175);stroke-width:1px;}#chatgpt-mermaid-_r_gi_ .flowchart-link{stroke:rgb(175, 175, 175);fill:none;}#chatgpt-mermaid-_r_gi_ .edgeLabel{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-_r_gi_ .edgeLabel p{background-color:rgb(0, 0, 0);}#chatgpt-mermaid-_r_gi_ .edgeLabel rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-_r_gi_ .labelBkg{background-color:rgba(0, 0, 0, 0.5);}#chatgpt-mermaid-_r_gi_ .cluster rect{fill:rgb(48, 48, 48);stroke:rgba(255, 255, 255, 0.15);stroke-width:1px;}#chatgpt-mermaid-_r_gi_ .cluster text{fill:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ .cluster span{color:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ div.mermaidTooltip{position:absolute;text-align:center;max-width:200px;padding:2px;font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";font-size:12px;background:rgb(48, 48, 48);border:1px solid rgba(255, 255, 255, 0.15);border-radius:2px;pointer-events:none;z-index:100;}#chatgpt-mermaid-_r_gi_ .flowchartTitleText{text-anchor:middle;font-size:18px;fill:rgb(237, 237, 237);}#chatgpt-mermaid-_r_gi_ rect.text{fill:none;stroke-width:0;}#chatgpt-mermaid-_r_gi_ .icon-shape,#chatgpt-mermaid-_r_gi_ .image-shape{background-color:rgb(0, 0, 0);text-align:center;}#chatgpt-mermaid-_r_gi_ .icon-shape p,#chatgpt-mermaid-_r_gi_ .image-shape p{background-color:rgb(0, 0, 0);padding:2px;}#chatgpt-mermaid-_r_gi_ .icon-shape .label rect,#chatgpt-mermaid-_r_gi_ .image-shape .label rect{opacity:0.5;background-color:rgb(0, 0, 0);fill:rgb(0, 0, 0);}#chatgpt-mermaid-_r_gi_ .label-icon{display:inline-block;height:1em;overflow:visible;vertical-align:-0.125em;}#chatgpt-mermaid-_r_gi_ .node .label-icon path{fill:currentColor;stroke:revert;stroke-width:revert;}#chatgpt-mermaid-_r_gi_ .node .neo-node{stroke:rgb(31, 78, 148);}#chatgpt-mermaid-_r_gi_ [data-look="neo"].node rect,#chatgpt-mermaid-_r_gi_ [data-look="neo"].cluster rect,#chatgpt-mermaid-_r_gi_ [data-look="neo"].node polygon{stroke:url(#chatgpt-mermaid-_r_gi_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_gi_ [data-look="neo"].swimlane.cluster rect{filter:none;}#chatgpt-mermaid-_r_gi_ [data-look="neo"].node path{stroke:url(#chatgpt-mermaid-_r_gi_-gradient);stroke-width:1px;}#chatgpt-mermaid-_r_gi_ [data-look="neo"].node .outer-path{filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_gi_ [data-look="neo"].node .neo-line path{stroke:rgb(31, 78, 148);filter:none;}#chatgpt-mermaid-_r_gi_ [data-look="neo"].node circle{stroke:url(#chatgpt-mermaid-_r_gi_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_gi_ [data-look="neo"].node circle .state-start{fill:#000000;}#chatgpt-mermaid-_r_gi_ [data-look="neo"].icon-shape .icon{fill:url(#chatgpt-mermaid-_r_gi_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_gi_ [data-look="neo"].icon-shape .icon-neo path{stroke:url(#chatgpt-mermaid-_r_gi_-gradient);filter:drop-shadow( 1px 2px 2px rgba(185,185,185,1));}#chatgpt-mermaid-_r_gi_ .node text{font-size:14px;font-weight:600;letter-spacing:normal;fill:rgb(153, 206, 255);}#chatgpt-mermaid-_r_gi_ .edgeLabels text{font-size:13px;font-weight:600;letter-spacing:-0.08px;fill:rgb(153, 206, 255);}#chatgpt-mermaid-_r_gi_ .node tspan[font-weight="normal"],#chatgpt-mermaid-_r_gi_ .edgeLabels tspan[font-weight="normal"]{font-weight:600;}#chatgpt-mermaid-_r_gi_ .edgeLabel .label rect{opacity:1;rx:13px;ry:13px;fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-width:1px;}#chatgpt-mermaid-_r_gi_ .node rect,#chatgpt-mermaid-_r_gi_ .node circle,#chatgpt-mermaid-_r_gi_ .node ellipse,#chatgpt-mermaid-_r_gi_ .node polygon,#chatgpt-mermaid-_r_gi_ .node path{fill:rgb(0, 40, 77);stroke:rgba(255, 255, 255, 0.1);stroke-width:1px;}#chatgpt-mermaid-_r_gi_ .node rect{rx:16px;ry:16px;}#chatgpt-mermaid-_r_gi_ .mermaid-decision .label-container{fill:rgb(0, 14, 26);stroke:rgb(26, 62, 95);stroke-dasharray:2,2;}#chatgpt-mermaid-_r_gi_ .edgePaths .flowchart-link{stroke:rgb(175, 175, 175);stroke-width:1px;stroke-linecap:round;stroke-linejoin:round;}#chatgpt-mermaid-_r_gi_ .marker{fill:rgb(175, 175, 175);stroke:rgb(175, 175, 175);}#chatgpt-mermaid-_r_gi_ :root{--mermaid-font-family:-apple-system-body,ui-sans-serif,-apple-system,system-ui,"Segoe UI",Helvetica,"Apple Color Emoji",Arial,sans-serif,"Segoe UI Emoji","Segoe UI Symbol";}T0.1 Compose skeletonT0.2 QueueT0.3 TaSMET solveT0.5 Registry and stateT0.4 Physics gateT0.6 M0 acceptance





The important correction is that T0.3 and T0.5 can proceed independently after T0.2, but T0.4 needs both:
- T0.3 supplies the real solver run and its artifacts.
- T0.5 supplies the registry enforcement contract.
- T0.4 integrates the physics gate with that registry.
T0.4's step 3 explicitly requires registry refusal of an invalid succeeded transition. That enforcement belongs to T0.5.

I would make T0.5 a mandatory T0.4 precondition and explicitly establish the registry interface before T0.4 implementation.

T0.6 correctly remains dependent on all five preceding M0 tickets and all five Pass-C tickets.
3. Largest remaining execution risk with the 81,920-token context
The largest remaining risk is cross-ticket architectural drift caused by incomplete reconstruction of upstream decisions.

The 1-turn-per-ticket approach controls context consumption, but it introduces a different problem: the agent may correctly execute an individual ticket against an incorrect interpretation of the architecture.

For example:
- A ticket may implement an API contract that differs subtly from the ADR.
- A downstream ticket may assume a registry behavior that was never implemented.
- A supposedly completed upstream requirement may have evidence that proves something narrower than the downstream ticket assumes.
This is more dangerous than ordinary context exhaustion because the resulting implementation can appear internally consistent and pass its local done-check.

One rule I would add:
L4 — Dependency contract verification. Before starting any ticket, the agent must enumerate its upstream dependencies and verify each dependency's actual committed implementation, acceptance evidence, and relevant ADR/REQ contract. A ticket cannot claim an upstream dependency satisfied solely because its ledger status says CLOSED. Any mismatch becomes a blocking discrepancy recorded before implementation begins.

This should be a short, mandatory preflight section in every ticket's Result, not another large document to load.
4. Residual-risk classification review
ID	Assessment	Recommendation
R-01	Correct	Hard for freeze; interim authorization before M0 build.
R-02	Correct	Soft. Human diagram reviews can proceed during M0.
R-03	Correct	Hard for M0 acceptance. Zero executed tests means no runtime acceptance claim.
R-04	Mis-gated	Hard before C3's irreversible volume deletion, not merely Deferred until M0 close.
R-05	Correct	Hard for T0.x build, not Pass-C cleanup.
R-06	Needs correction	Soft is defensible, but the ADR descriptions are incorrect. D-07 concerns artifact layout/promotion into MinIO; D-11 concerns exclusion of the GB10/ARM64 host from the compute tier. Neither should be described as the other decision.
R-07	Correct	Deferred under the explicitly accepted single-host security posture, with the D-12 trigger retained.
R-08	Correct	Deferred to M2+ and the relevant conditional investigations.
R-09	Correct	Hard at M0 start, before claiming the QA re-gate reproducible.
R-10	Correct	Hard before freeze or first M0 build handoff.
R-11	Correct	Soft during planning; hard at M0 close because ledger integrity is part of acceptance.
R-12	Correct	Deferred to M0 execution, where import-time smoke checks must actually occur.

The significant correction is R-04. The OneDrive mechanism was already ruled as a manual web read-back ritual under ADR OQ-9, Option A. That is acceptable as the chosen mechanism, but it does not mean the required read-back has actually occurred for the C3 staging operation.

I would amend R-04 to distinguish:
1. The durability mechanism has been selected.
2. The particular C3 copy has not yet been proven durable.
3. C3 volume deletion is prohibited until the second condition is satisfied.
I would also correct R-06's ADR descriptions rather than silently carrying forward the incorrect decision mapping.
5. Operator decision with the largest hidden cost
OneDrive L4/L5 durability is the highest-consequence issue.

There are two different costs to consider:
- D-06 wrapper shape: Highest immediate schedule risk. It blocks T0.4 and prevents M0 completion if unresolved.
- OneDrive L4/L5: Highest potential irreversible-loss risk. If the agent deletes the original MinIO volume after a locally successful copy but before off-host durability is established, recovery may be impossible.
The other decisions are less consequential if delayed:
- QA harness location: Creates reproducibility and audit debt, but can be corrected.
- Sign-off grid: Prevents formal freeze, but the interim authorization mechanism allows controlled M0 progress.
- D-06: Has a clearly identified build dependency and can be made a hard precondition.
My recommendation:
1. Retain ADR OQ-9 Option A (manual web read-back).
2. Require a successful read-back and recorded evidence for C3's actual staged data before deleting the source volume.
3. Do not interpret acceptance of the OneDrive mechanism as proof of successful backup.
4. Keep the D-06 ruling as a hard M0 build-start gate.

Final recommendation

Approve the deployment-planning approach with the following required changes before execution:
1. Reclassify R-04 as a hard gate for C3's destructive deletion step.
2. Add T0.5 as an explicit T0.4 dependency.
3. Introduce L4 dependency-contract verification.
4. Correct R-06's ADR descriptions.
5. Clarify the P2/P3 transition so Pass-C authorization cannot be confused with M0 build authorization.
These changes do not require redesigning the architecture or abandoning the incremental planning strategy.

The overall sequencing is sound. The primary concern is ensuring that the cleanup phase does not destroy the evidence or data needed by the implementation phase, and that the M0 tickets implement the same contracts that the design actually specifies.

Council disposition: APPROVE-WITH-CHANGES. This is one adviser response, not a quorum decision.