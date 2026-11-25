# Round-04 — ChatGPT reply (verbatim, operator-delivered 2026-11-24)

HE-toolstack M0-readiness review — main @ 79beb57

Overall assessment: REVISE the proposed execution and sign-off plan before treating these residual risks as closed. The broad direction is sound, but there are several important scope and evidence problems in the prompt and risk register. The most consequential are:
1. T-19 is not a safe agent-only test as currently defined; it requires a Docker-daemon restart and should be operator-controlled.
2. The design-review checklist has M1–M9, not M1–M10. The risk register also misidentifies where the diagram sign-offs live.
3. D-05 is not a defined backup fallback. The D-05 decision establishes the authoritative local state directory; it does not establish off-host durability.
4. The disk sample is stale and inconsistent with other recorded samples.
5. The QA report still describes the old scratch-only harness, despite the promotion recorded elsewhere.

Reviewed the five named documents and the ADR at the specified commit. This is a review of the documented design and proposed procedures — not a claim that the runtime tests were executed or a deployed stack inspected.

## Q1 — R-03: execution split and witnessing protocol — REVISE
The agent can execute most of the proposed test legs, but it must not be the sole author, executor, and judge of its own evidence. The operator should witness the destructive boundaries and independently verify the results. The key distinction is between the agent running a test and the agent being trusted to establish that the test passed. The latter requires an independent oracle or witness.

| Test | Execution recommendation | False-pass risk and required witness evidence |
|---|---|---|
| T-01 M0 vertical slice | Agent executes; operator witnesses acceptance | The agent could author a workflow and a test that merely confirms its own expected output. Require a frozen input/config fixture, source and image digests, run manifest, raw solver output, physics-gate report, and ledger entry. The witness independently checks the expected physics result and gate outcome. |
| T-02 cold-session resume | Agent prepares the test; a genuinely fresh agent session executes it | The original agent must not create the scenario, perform the recovery, and grade its own success. Require a pre-existing run with known state, a clean session with no inherited conversation context, its transcript, files/API evidence consulted, final state, and an independent checklist comparing the recovered state with the original. |
| T-05 queue persistence and restart | Agent executes the engine-kill/restart leg; operator executes the host-reboot leg | A test can pass if the test harness reconstructs or normalizes state incorrectly. Require before/after SQLite snapshots, integrity-check output, queue/job ID comparison, engine and container timestamps, and reconciliation logs. Keep the host reboot under operator control. |
| T-07 crash-boundary matrix | Agent executes controlled failure injection; operator witnesses the acceptance result | Particularly vulnerable to a self-authored harness that omits a failure window or verifies the same assumptions as the implementation. Require the complete enumerated crash-point list, injected failure identifiers, raw pre/post filesystem snapshots, state and ledger comparisons, and a separate read-only verifier. |
| T-19 Docker-daemon restart reconciliation | Move to operator-executed unless run against a dedicated disposable Docker daemon/VM | Restarting dockerd is a host-level operation, not an ordinary agent action. Require operator authorization, confirmation of the target daemon, pre-restart container/job inventory, restart timestamps, post-restart container inventory, reconciliation logs, and final job/ledger state. |
| T-20 flock claim race | Agent executes; operator witnesses | A serialized test harness can falsely pass a concurrency test. Require independent OS process IDs, start barriers/timestamps, lock acquisition results, exit statuses, ledger event count, and the claimant-crash plus inherited-descriptor test evidence. |
| T-21 stale-claim supersede | Agent executes; operator witnesses | The test must prove that a live-but-hung claimant cannot be superseded and that a dead claimant can be superseded only after the kernel releases the lock. Require process state, lock state, timestamps, ledger events, and the two-superseder race result. |
| T-23 SQLite submission concurrency/crash matrix | Agent executes; operator witnesses | A test that only counts successful HTTP responses can miss duplicate or lost queue entries. Require raw request IDs and idempotency keys, response bodies/statuses, before/after database snapshots, row counts, transaction outcomes, and restart/replay evidence. |

**Minimal witnessing protocol** — one consistent evidence package for every agent-executed test:
1. Pre-register the test: test ID, exact scenario, inputs, expected result, failure conditions, and cleanup steps recorded before execution.
2. Separate implementation from verification: the test verifier should not import the implementation's internal success predicate. Prefer a small, read-only verifier that checks externally observable state.
3. Preserve raw evidence: logs, command output, database snapshots, process IDs, manifests, digests, generated artifacts — not just a PASS line.
4. Record the witness: operator identity, date/time, test commit, test artifact location, any deviations.
5. Require an explicit disposition: PASS, FAIL, or BLOCKED. Missing evidence, incomplete scenarios, or a verifier error must never become PASS.
For the highest-risk tests — T-01, T-07, T-19, T-20, T-23 — the operator should also inspect the verifier's inputs and acceptance logic before trusting its result.

Scope distinction: T-19's REQ definition is a Docker-daemon restart drill, not an engine restart. TD explicitly identifies dockerd restart as a distinct WSL2 failure class with its own R-9 runbook — hence not ordinary agent-executed.
Sources: REQ §4 T-01..T-24 · TD §8.6 crash recovery · TD §11.8 R-9.

## Q2 — R-02: human review and sign-off — REVISE
Three distinct humans is defensible for the three formal sign-off roles, but not for every individual checklist row. More fundamental problem: the prompt and register refer to M1–M10; the actual checklist contains only M1–M9 (DESIGN-REVIEW §2b, nine rows; author pre-fill explicitly says independent confirmation still required).

Minimum scheme: Owner / decision authority = Steven (accept residual risks, confirm operator decisions, sign owner row). Engineering reviewer = independent person (architecture, interfaces, state management, concurrency, diagram/prose consistency). Operations reviewer = independent person (deployment, shutdown, recovery, backup, runbooks).
Formal §9 grid: three distinct people; the owner should not also be the sole independent engineering or operations reviewer; engineering ≠ operations (validating architecture vs validating operability/recoverability are different things).
Checklist rows allocated by subject matter: engineering reviewer M1–M2, M4, M6, M8, M9; operations reviewer M3, M5, M7; owner reviews conclusions, resolves operator decisions, signs owner row.
r12 author self-walk: does NOT count toward independent human sign-off. Useful preliminary evidence, may reduce review effort; explicitly author self-review; retain as such.

Corrections required in the risk register: change M1–M10 to M1–M9. The diagram-to-prose checklist is DESIGN-REVIEW §2b; §9 contains the sign-off grid; QA-REPORT §5 is the requirements traceability matrix, not a diagram sign-off section. T-11 is a backup/restore drill — it does not close the human diagram-review requirement; do not make T-11 completion a substitute.
Sources: DESIGN-REVIEW §2b · §9 · REQ §4–§5.

## Q3 — R-04: backup sequence, D-05, disk headroom — ACCEPT A, WITH SEQUENCING CHANGES
A is the safer path: execute backup/restore and consistency tests, establish evidence for the actual staged copy, only then authorize destructive removal of the source MinIO volume.

Three separate questions that must not be collapsed:
1. **D-05 is not a backup fallback.** ADR-D-05 establishes /home/steven/HE-toolstack/heat-data as authoritative host directory + write-ahead ordering. It defines no off-host backup destination or durability proof. The relevant decision is OQ-9: A = recurring manual OneDrive web read-back recorded in drills/onedrive-readback.log; B = automated Microsoft Graph read-back; C = explicitly accept host-local durability. Option A was accepted → a procedure for obtaining L5 evidence is selected; NOT that every backup copy passed it. Hence the wording "close OQ-9 proof gap by acceptance" is unacceptable: OQ-9's mechanism decision is closed; the evidence obligation remains.
2. **Recommended sequence:** (1) T-11 backup+restore drill — restore succeeds in a disposable copy; SQLite integrity, artifact digests, MinIO version export, Git recovery all pass. (2) T-18 consistency + staleness checks. (3) OneDrive read-back of the ACTUAL C3 copy — the specific pd-minio-orphan/ copy remotely readable, evidence in drills/onedrive-readback.log. (4) Authorize source-volume removal ONLY after read-back evidence exists, or an explicit operator purge-approval acknowledging remaining loss risk. Step 3's distinction is essential: a T-11 pass against a test backup does not prove the C3-staged copy reached OneDrive. If the actual copy cannot be verified, defer removal; a purge approval is available but must be recorded as an exception, never represented as successful durability.
3. **Disk headroom — re-sample required.** The ~66 GB / 81.5% sample is [U], not a reliable deployment baseline, and conflicts with ADR-D-05 / TD §17 (813 GB free on /dev/sdf [V]). Re-measure immediately before first make up (total/used/available/%, timestamp, device identity); repeat before C3's destructive step. Retain the standing watermark policy (80% warning, 95% hard refusal); do not substitute historical samples for live checks. If 81.5% is confirmed on /dev/sdf, the warning threshold is already crossed — a reason to investigate capacity, not to refuse all M0 work; the 95% hard threshold protects in-flight workloads.
Milestone inconsistency to resolve explicitly: TD §16 places T-11 in M2 acceptance while R-04 asks T-11/T-18 before M0 close; REQ NFR-22 is P0.
Sources: ADR-D-05 · ADR OQ-9 · REQ NFR-22 · TD §9.4 watermarks · TD §11.6.

## Q4 — R-12: smoke-check acceptance — ACCEPT WITH A RISK-TIERED STANDARD
Import-only smoke is insufficient as a universal acceptance criterion.

| Artifact class | Minimum M0 check | Why |
|---|---|---|
| Pure Python utilities, no side effects | Import + dependency check, CLI help/version | Cheap detection of broken imports/missing deps |
| Path/manifest/digest utilities (resolve.py) | Fixture invocation in a temp dir with known files + expected digests | Import success ≠ correct resolution, digesting, refusal behavior |
| Physics-gate scripts | Valid fixture invocation + corrupted-input negative test | A gate that always passes is far more dangerous than one that fails to import |
| Solver wrappers and generators | Small CPU fixture invocation; compare generated decks/outputs against known references | Catches interface drift, changed defaults, missing binaries, altered numerics |
| Backup/restore scripts | Isolated fixture backup+restore + integrity + digest checks | A backup script can run cleanly while producing an unusable restore |
| Containerized tools | Image digest verification + minimal representative invocation | An image can start while its capability is broken |

Highest-risk unchanged claims: (1) physics-gate methodology + negative-test path (highest consequence — central value is trustworthy physics evidence; needs known-good AND deliberately-corrupted fixtures); (2) resolve.py + MANIFEST/digest discipline (artifact identity/provenance; use known digest fixtures + explicit mismatch/refusal cases); (3) backup/restore mechanisms (T-11 must prove recoverability, not file-exists); (4) solver generators + CPU physics loop (frozen input, compare against known references; established benchmark tolerances where bit-identity is not a valid expectation).
Practical rule: import-only for low-risk utilities; fixture invocation for data-transforming/external-invoking code; behavioral/digest checks for code that determines whether scientific results, provenance, or recoverability can be trusted.
Qualification: TD §4 is a retained-assets list, not an executable-file inventory. Enumerate the actual Phase-1 scripts under the "reusable unchanged" claim, map each to owner + check. No unenumerated script inherits unchanged status from a narrative list.
Sources: TD §4.1 · REQ T-03/T-04/T-11 · RR R-12.

## Q5 — mis-framed questions — REVISE
| Item | Problem | Correction |
|---|---|---|
| R-02 | Says M1–M10; §2b has M1–M9 | Correct range |
| R-02 | Says rows closed by T-11 | Remove — T-11 is backup/restore, not human diagram review |
| R-01 | Attributes diagram sign-offs to QA §5 | DESIGN-REVIEW §2b + §9; QA §5 is requirements traceability |
| R-01 | Says runbooks R-1…R-8 | TD §11.8 has R-1…R-9; R-9 daemon-restart drill matters to M0 |
| R-03 | Says harness scratch-only | Separate runtime-test status from static-harness status (harness now promoted) |
| R-04 | Calls route B a "D-05 fallback" | Name the exact fallback; D-05 defines local authoritative state, not a tested backup fallback |
| R-04 | Frames T-11/T-18 execute-vs-accept as simple A/B | Separate: test execution / OQ-9 policy decision / actual C3-copy L5 evidence / explicit purge approval |
| R-12 | Assumes reusable-script set already identified | Require inventory of exact script paths + smoke-check classifications |

**Documentation-integrity issues found:** (a) QA report at this commit still describes the harness as .hermes-tmp/gates_v13.py, "not committed," with the old scratch-path command — while R-09's owner-action says promoted to scripts/qa/gates_v13.py. A reviewer following the QA report goes to the wrong place; §5 reproducibility table + command must sync with the tracked harness. (b) R-09 internally inconsistent: row text says the location decision is unmade while owner-action says resolved/promoted. Rewrite the row to the resolved state.

**Final recommendation (most important):** keep three separate states in the M0 evidence record — Decision accepted / Test passed / Destructive action authorized. Never let one imply another. Accepting OQ-9 Option A does not prove a backup copy is remotely durable; accepting D-05 does not authorize deleting the only recoverable copy.

Advisory only; HARD STOP remains in force.