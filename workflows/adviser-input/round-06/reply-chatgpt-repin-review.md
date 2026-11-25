CHATGPT:
-------------------------------------------------------
Round-06 repair re-review
Review pin: b125d6659e9f23a373405622eea4269cdc2c9875
Repository: jstevenjacobs/HE-toolstack
Branch: dp/round-06-runbook-repairs

I resolved the branch head and checked the exact pinned tree, rather than assuming the earlier 5315c37 tree contained these changes. The branch head is now 035738d, whose parent is the review pin b125d665. The comparison from 5315c37 to b125d665 shows the design and ledger changes, along with the archived review artifacts.

The nine fixes are substantially present. The important distinction in this re-review is between whether the specific correction is now in the text and whether the whole runbook is operationally proven. This is a paper review only.

Q1 — Per-fix verdicts
| # | Fix | Verdict |
|---|-----|---------|
| 1 | R-4 source selection | ACCEPT |
| 2 | R-4 versioned-tier recovery | ACCEPT |
| 3 | R-4 replacement-volume and seed sequence | ACCEPT |
| 4 | R-4 cold-session rule | ACCEPT |
| 5 | R-5 controlled create_run exercise | ACCEPT |
| 6 | R-5 Docker host-dependency classification | ACCEPT |
| 7 | R-7 work/ deletion safety | ACCEPT |
| 8 | R-7 archive and watermark corrections | ACCEPT |
| 9 | External errata and ledger reconciliation | PARTIAL |

1. R-4 source selection — ACCEPT
The corrected text now explicitly says:
newest dated dir under $ROOT/heat-data/ — the published-backup tier only (§6.9.2 step 7; never repo/ or drills/)
This is the right scope. §6.9.2 step 7 publishes dated backups under $ROOT/heat-data/; repo/ and drills/ are not candidates.
TD §11.8 R-4

2. R-4 versioned-tier recovery — ACCEPT
The corrected text says:
no ?versionId= read-back exists
and:
select the version in the version manifest, re-upload its exported payload as a new object, digest-compare vs ledger.
That now follows §6.9.3. It no longer prescribes an unavailable version-ID read-back. It uses the exported payload and manifest, with re-upload semantics and a digest comparison.
The T-22 qualification still matters: §6.9.3 says the export mechanism is proposed and its version coverage is not proven until T-22. R-4's procedure is therefore a design-time recovery instruction, not evidence that versioned recovery has passed.
TD R-4 · §6.9.3

3. R-4 replacement-volume and seed sequence — ACCEPT
The body now includes the steps missing from the prior pin:
provision + mount the replacement ext4 volume at the heat-data mount point
copy the selected backup's heat-data/ tree into the §9.2 layout
then the host seed script (pre-baked image tars, §11.5/§12.2) so make up can start without a registry
This directly addresses the former gap: the restore procedure now describes rebuilding the host storage, copying the backed-up data into the expected layout, and seeding images before starting the stack.
The host recipe remains explicitly [P]. That is appropriate: it is a paper procedure awaiting M0 execution, not an existing verified host script.

4. R-4 cold-session rule — ACCEPT
The text now states:
Cold-session rule (T0.5): this runbook must be executable from the paper alone with zero conversation context.
That is explicit and directly addresses the prior cold-session requirement.

5. R-5 controlled create_run exercise — ACCEPT
The status probe is now correctly qualified:
answering proves API liveness only — it can 404 while create_run still times out.
The runbook then adds the missing functional test:
one controlled POST /v1/create_run with an allowed digest under normal sidecar restrictions (§6.2b), confirm the container spawns, then POST /v1/cancel (or let it finish) + confirm state cleanup.
And it expressly disclaims the previous false proof:
make test-smoke is the backstop, not this runbook's proof ... it never exercises create_run.
That closes the specific false-positive I identified. The test now exercises the failed operation rather than merely checking that the API answers.

6. R-5 Docker host-dependency classification — ACCEPT
The new wording is precise:
docker engine is a §2.6 host prerequisite — NOT the §11.9 class-X unit, which is the backup timer
The command remains:
sudo systemctl status docker
That is a host dependency check. It is no longer misclassified as a class-X service. §11.9 continues to identify the backup timer as the class-X unit.

7. R-7 work/ deletion safety — ACCEPT
The new safety rule is unambiguous:
work/ has no verified copy elsewhere (promotion is not a copy of the working dir, §9.2) and may not be deleted without first being archived with its own post-move verification.
It also limits deletion when the archive destination is unavailable:
local deletion is limited to the promoted tier covered by step-2 verification
This corrects the previous data-loss authorization. The runbook no longer treats MinIO promotion as a backup of the writable solver working directory.

8. R-7 archive and watermark corrections — ACCEPT
All the requested changes are present:
- Archive destination: /home/steven/backups/archive/ [P]
- The text correctly distinguishes the proposed child directory from its evidenced parent: new child dir under the §9.4 legacy second-disk root [E] — does not yet exist
- Per-run layout: …/archive/<yyyymmdd>.<run_id>/ mirroring the run dir
- Collision behavior: .N suffix on name collision
- Post-move verification: digest-compare moved files vs pre-move digests before removing the source.
- Live MinIO verification: verified readable from the live MinIO service — head/get by key + digest-compare vs ledger
- Explicit separation from the proposed export: distinct from the §6.9.3 backup export, which is [proposal]/T-22 and not a liveness check
- Watermark qualification: thresholds are §11.6 [proposal] until M0 builds them
This addresses the earlier overclaim about the archive child directory and the 95% threshold, and separates live MinIO object checks from the proposed backup-export mechanism.

9. External errata and ledger reconciliation — PARTIAL
The three external corrections are present, but the ledger gloss is not yet fully faithful to the R-4 body.
ADR A1 — ACCEPT.
The old reference is now explicitly marked:
R-4/R-8 is fixed [round-06 erratum — superseded text; do not copy forward: the restore runbook is R-4 only; R-8 is the backup-health/staleness runbook ...]
That corrects the historical mispointing without silently rewriting the historical record.
RC-4 scope note — ACCEPT.
The RC-4 row now explicitly says:
R-9 exercises daemon restart, NOT a Windows/WSL host-reboot drill; the full RC-4 reboot scenario still earns its own evidence at M0
This is accurate. R-9 is relevant to the daemon-restart component of a host reboot, but it does not substitute for the complete host-reboot test.
Ledger DP-R6-rb rev-2 — PARTIAL.
The new note says:
at 5315c37 the R-4 body did not yet contain the seed/MinIO/cold-session steps the gloss claimed — at DP-R6-r2 the body was raised to match this gloss, not the gloss lowered
That is an honest account of the correction direction. The body now does contain the seed-script sequence and cold-session rule.
However, the gloss still claims:
quarantine re-drill → fresh heat-data → minio recovery
The body does not explicitly prescribe quarantining an invalid/incomplete backup tree or a separate quarantine re-drill. It says:
dir without valid DONE.json = incomplete tree → excluded, never a restore source
And its MinIO step is specifically:
Versioned-tier proof ... select the version in the version manifest, re-upload its exported payload as a new object, digest-compare vs ledger.
That is versioned-tier recovery, not a complete MinIO recovery procedure. The ledger should narrow those two phrases or the body should add the missing actions.

Q1 result: eight ACCEPT, one PARTIAL. The nine listed corrections are substantially implemented. The residual is the precision of the ledger's description, not a return to the original R-4 gap.

Q2 — New-defect hunt on the increment
I reviewed the changed runbook text against the cited invariants and design sections. The following are the findings that remain.
Finding 1 — Ledger gloss still overstates two R-4 actions
As above, the gloss says:
quarantine re-drill ... minio recovery
The body says invalid backups are excluded, and it prescribes a versioned-tier recovery proof. Those are not equivalent to a quarantine operation and full MinIO recovery.
This is the only concrete body-versus-ledger mismatch I found in the revised runbook descriptions.
Finding 2 — R-5 symptom sentence is slightly inconsistent with its verification sequence
The symptom is described as:
create_run returns 500/spawn_timeout in engine logs while status calls fail.
The recovery verification then says:
a GET /v1/runs/{id}/status ... answering proves API liveness only — it can 404 while create_run still times out.
These statements can be reconciled as "status calls were failing before the restart, but may answer afterward." However, the text does not say that explicitly. I recommend changing the symptom to identify which status call fails and making clear that the later GET is a post-restart liveness probe. This is a clarity issue, not a recurrence of the old false-positive proof: the controlled create_run exercise is now explicit.

Invariant and epistemic checks
| Area | Result |
|---|---|
| D-16 socket boundary | PASS. R-5 explicitly prohibits granting the engine a Docker socket. |
| Lifecycle classes | PASS. The Docker Engine is now identified as a §2.6 host prerequisite, not class X. |
| Six-step shutdown §6.10 | PASS. No changed runbook command changes or bypasses the shutdown sequence. |
| Backup-root-is-not-archive | PASS. R-7 explicitly prohibits archiving to $ROOT. |
| §6.9 backup semantics | PASS. R-4 now follows the export/re-upload semantics and acknowledges the absence of ?versionId= read-back. |
| §9.2 storage ownership | PASS. R-7 explicitly recognizes that promotion does not copy work/. |
| §9.4 retention | PASS with the R-7 safety rule. Evidence and ledger deletion remain human-only. |
| §11.5 | PASS. make test-smoke is correctly described as T-01 echo, healthz, and down/up—not a create_run test. |
| §11.6 proposals | PASS. The 80/95 watermark remains [proposal]; the 95% behavior is not asserted as live. |
| §11.9 | PASS. Only the backup timer is called class X. |
| R-7 archive evidence | PASS. The parent path is [E]; the new child directory is [P]. |

I found no new command that violates D-16, no lifecycle-class boundary violation, and no changed command that contradicts the six-step shutdown sequence.

One epistemic distinction deserves emphasis: the commands docker compose up -d spawn-sidecar and sudo systemctl status docker are presented as operational commands, but the procedure as a whole remains a staged runbook. That does not mean the commands or their effects have been runtime-verified. R-4's host replacement-volume recipe is explicitly [P], and R-7's make disk-report is explicitly [proposal, M0 build]. I found no additional proposal that is unambiguously represented as an already-installed Make target or completed runtime capability.

Q3 — Status discipline
PRESERVED
The increment does not state that R-4, R-5, or R-7 has passed, nor does it close the §9 exceptions.
The ledger continues to call the work:
Round-06 STAGED — M0 runbook repairs ... paper drafts.
And it says:
Exceptions stay recorded exceptions until an M0 walk re-executes the repaired procedures — staged drafts are NOT passes (§9 annotation unchanged).
The DESIGN-REVIEW §9 annotation remains unchanged in meaning. It continues to record the three original runbook gaps as exceptions and states that repair is M0-gated work under the §10 HARD STOP.

Is the gloss-versus-body reconciliation now honest in both directions?
Mostly, but not completely.
- The ledger honestly acknowledges that the earlier body was behind its gloss.
- The body now contains the replacement-volume, copy, seed, and cold-session instructions.
- The remaining mismatch is that the gloss still describes quarantine and MinIO recovery more broadly than the actual R-4 instructions.
That is a documentation-accuracy correction still required. It does not turn the staged work into a pass.

The three exceptions close only after M0 re-execution with evidence. T-11 restore-class evidence and the corresponding spawn-channel and disk-pressure drills must be executed and recorded. This review supplies no such evidence.

Q4 — Final verdict
APPROVE-WITH-CHANGES
I accept the substance of the nine staged fixes, subject to the following small corrections:
1. Ledger/R-4: narrow quarantine re-drill and minio recovery to what the body actually specifies, or add those missing actions to R-4.
2. R-5 symptom wording: distinguish the pre-restart status failure from the post-restart liveness probe.
These are paper-accuracy and clarity changes. They do not invalidate the major repairs. In particular, the former R-4 source-selection, versionId, and missing host-rebuild/seed steps are corrected; R-5 now tests the actual spawn operation; and R-7 no longer permits deletion of unarchived work/ data.

Final status: the round-06 drafts are acceptable as staged paper repairs after those two corrections. R-4/R-5/R-7 remain recorded exceptions until M0 re-execution produces the required evidence. No deployment approval, implementation authorization, ticket-execution authorization, or waiver of the §10 HARD STOP is granted.
