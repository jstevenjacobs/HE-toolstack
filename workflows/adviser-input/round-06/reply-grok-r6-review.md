# Round-06 council reply — Grok (runbook repair review)

**Pin reviewed:** 5315c372cc0774427e54a69bc30199232f3831b4
**Paste sha256:** e2d2207e135c9f959ee9f7e7dba42f5158b5815d67434b020bb21f5287b5ac08
**Archived:** 2026-11-25 (owner-mediated relay, single-human scheme)
**Verdict (Grok):** APPROVE-WITH-CHANGES — 1 non-blocking [minor]; R-4/5/7 all CLOSED per Grok
**Verdict (ChatGPT, same relay file):** APPROVE-WITH-CHANGES — 5 required changes; R-4/5/7 all PARTIAL per ChatGPT

---

GROK:
---------------------------------
Round-06 — M0 runbook repair review (Grok)

Pinned SHA: 5315c372cc0774427e54a69bc30199232f3831b4

Increment under review: adca8a4..5315c372 (TD §11.8 + FM-13/RC-4/RC-5 + ledger DP-R6-rb)

HARD STOP observed. Yardstick = own round-05 gaps (R-4/R-5/R-7).

Q1 — Gap closure, per runbook
R-4 — CLOSED
Round-05 demand: concrete restore sequence (source selection, validation, fresh-volume rebuild, verification).
Staged text supplies all four:

Source selection: “newest dated dir under $ROOT (§6.9) with a schema-valid DONE.json; dir without valid DONE.json = incomplete tree → excluded”
Validation: re-hash vs manifest.src; scratch PRAGMA integrity_check + quick_check
Fresh-volume rebuild: “heat-data/ per §9.2 layout into fresh ext4 dirs on the owner disk (drill mode: disposable isolation dir, never the authoritative path — §9.6)”; ledger tier from GitHub remote or git bundle
Verification: make up → §8.6 reconcile + healthz trio; pull one promoted object by versionId + digest-compare; make test-smoke → ledger note

Matches the round-05 minimum fix (“add one concrete restore command block or numbered pointer into §9.6”).
R-5 — CLOSED
Round-05 demand: correct service target + exact invocation (not make up workflow-engine).
Staged text:

Explicitly names the defect: “former text named make up workflow-engine, which is the WRONG target”
Correct target: docker compose up -d spawn-sidecar (scoped; class-C)
Direct sidecar verification: GET /v1/runs/{id}/status (§6.2b) answers or 404 no_such_run
Host docker check only if socket unreachable; D-16 restated: “Do not grant the engine a socket … a ‘fix’ that exposes the socket to the engine is a violation, not a repair”

R-7 — CLOSED
Round-05 demand: exact du invocation + defined archive destination (or operator-chooses + ledger).
Staged text:

Report: du -sh heat-data/runs/* | sort -rh | head -20 (make disk-report = this + df [proposal, M0 build])
Eligibility: terminal + gate_report + ledger line + promoted objects present in MinIO
Destination: /home/steven/backups/archive/ [E] — “never to $ROOT (backup root is not an archive)”
Keep-list: state.json, journal/, gate_report.json, manifest.json
Fallback if archive dir absent: delete locally only after step-2 verification (MinIO holds the copy)


Q2 — New-defect hunt
Findings on the ~35 lines of new operational prose:

[nit] Epistemic tag correct for make disk-report.

Quoted: “Makefile target make disk-report = exactly this + df of the owner disk [proposal, M0 build].”

Correctly marked non-existent. No other command in the three runbooks presents a [P] artifact as live.
[nit] Archive path extends legacy second-disk precedent, consistent with §9.4.

§9.4: “the legacy second-disk copy (/home/steven/backups [E]) is optional extra local redundancy, never a restore source.”

R-7 destination /home/steven/backups/archive/ [E] is a subdirectory of that precedent and is explicitly barred from $ROOT. No contradiction with “backup-root-is-not-archive.”
No D-16 / class-boundary / six-step contradiction found.

R-5 restart is compose-scoped to spawn-sidecar only; engine is left serving; socket is never granted to the engine. R-4 restore does not invoke make down out of order or claim class-X is in-scope.
No internal contradiction with §6.9 / §9.4 / §11.5.

Source selection rules match §6.9.2 step 8 / §9.6 step 1 (no DONE.json → not a restore source). Eligibility and keep-list match §9.4 human-only deletion. Smoke step points at §11.5.
[minor residual, non-blocking] Ledger DP-R6-rb summarizes R-4 as including “minio recovery → seed → T-11”. The staged R-4 text has versioned-tier proof (step 6) but does not name the seed-script step inside the runbook itself; seed remains in the broader §12.2 RTO path (“seed script … + make up + restore … + R-4 drill”). Not a gap reopening — the round-05 demand was procedure concreteness, which is met — but the ledger gloss is slightly richer than the runbook body. Optional alignment: either drop “seed” from the ledger gloss or add one explicit seed-if-images-missing bullet under R-4 step 5.

No blocker-class new defect found.

Q3 — Legacy erratum check





























CitationWasStaged correctionMatches §11.8?FM-13 recovery columnR-5“R-4 restore procedure (was mis-pointed to R-5; corrected round-06 — R-5 is the spawn-channel runbook)”YES — R-4 is restoreRC-5 evidence columnR-5“R-4 full restore drill + T-11 … (round-06 erratum: pointed at R-5 …)”YESRC-4 evidence columnR-5 drill“R-1 + R-9 drill (round-06 erratum: row said ‘R-5 drill’ … R-9 is the matching drill class)”YES — R-9 is daemon-restart drill; reboot tears the daemon down
Fourth-mis-pointing sweep (R-n citations outside §11.8 body):

R-1 → R-4 for WAL-corrupt restore: correct
R-2 → R-5 for spawn-channel: correct
FM-6 → R-7 archive path: correct
FM-11 → R-9 drill: correct
§12.2 RTO → R-4 drill: correct
Risk table “R-7 archive path”: correct
D8 caption “T-11 / R-4 normalized”: correct

No surviving fourth mis-pointing of the R-5-for-restore/reboot family found in the TD at this pin.

Q4 — Status discipline
PASS — staged drafts, not passes.
Ledger DP-R6-rb (quoted):
“Exceptions stay recorded exceptions until an M0 walk re-executes the repaired procedures — staged drafts are NOT passes (§9 annotation unchanged).”
Runbook bodies themselves use the phrasing “round-05 gap fix” only as a change-log label; they do not claim the §9 exception is closed, do not mark R-4/R-5/R-7 as executed, and do not alter the HARD STOP. No wording was found that could reasonably be read as closing an exception on paper alone.

Overall verdict
APPROVE-WITH-CHANGES

[minor] Optional ledger/R-4 gloss alignment on the seed-script step (Q2 finding 5) — non-blocking; does not reopen any gap.
All three round-05 gaps (R-4 / R-5 / R-7) are CLOSED by the staged text.
Legacy FM-13 / RC-4 / RC-5 mis-pointings are correctly repaired; no fourth of that family found.
Status discipline holds: staged drafts ≠ exception closure; M0 re-execution still required.

No REJECT-class finding. No deployment authorization implied.

CHATGPT:
-------------------------------------------------------
Round-06 M0 runbook repair review
Pinned commit: 5315c372cc0774427e54a69bc30199232f3831b4
Scope: the increment from adca8a4 to the pinned commit. The GitHub comparison shows one commit changing exactly two files: docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md and workflows/ledger.md.

Overall assessment: the repairs are substantive, but they do not all close the original operational gaps. R-4 and R-7 remain partial; R-5 corrects the wrong service target, but its new verification can produce a false positive. I also found a surviving historical R-8 restore mispointing in the ADR.
Q1 — Gap closure, per runbook
Runbook	Verdict	Assessment
R-4 — restore	PARTIAL	Source selection and integrity checks are added, but the restore/rebuild procedure is incomplete and its MinIO verification contradicts §6.9.3.
R-5 — spawn channel	PARTIAL	Correct service target and direct sidecar API probe are added. The probe does not verify the failing create_run operation.
R-7 — disk full	PARTIAL	Destination, eligibility conditions, and keep-list are added, but the deletion fallback can discard data not held in MinIO.

R-4 — PARTIAL
The staged text is materially better. It now specifies:
(1) Select source: newest dated dir under $ROOT (§6.9) with a schema-valid DONE.json

It adds re-hashing against manifest.src, scratch-database validation using:
PRAGMA integrity_check + quick_check

And it says to restore heat-data/ into fresh ext4 directories, obtain the workflow/ledger tier from GitHub or a git bundle, start the stack, reconcile, and run the M0 smoke test.

Those are meaningful additions. They do not yet constitute a complete restore procedure.

Residuals:

1. The source-selection path is underspecified and inconsistent with the canonical layout. §6.9.2 step 7 publishes backups to $ROOT/heat-data/<yyyymmdd>.<runid>/. R-4 says to select a dated directory “under $ROOT,” which also contains repo/ and drills/. It should explicitly select from $ROOT/heat-data/.

2. Fresh-volume reconstruction is not operationally specified. The instruction:
heat-data/ per §9.2 layout into fresh ext4 dirs on the owner disk

does not say how to provision and mount the replacement volume after /dev/sdf failure, how to copy the selected backup tree into it, or how to run the host seed procedure before make up. “Fresh ext4 dirs” is not the same thing as rebuilding the lost volume and restoring its contents.

3. The MinIO verification instruction is incorrect. R-4 says:
pull one promoted object by versionId (§6.9.3 export list), digest-compare vs ledger.

But §6.9.3 explicitly says the export mechanism does not provide ?versionId= read-back. Its procedure is to select the required version's exported payload using the version manifest and re-upload it as a new object. §9.6 step 5 likewise tests version-export counts; it does not prescribe pulling an object by its original version ID.

4. The staged ledger overstates what R-4 contains. The DP-R6-rb ledger entry describes “minio recovery → seed” and a “cold-session rule.” Those steps/rules are not actually present in the R-4 text at lines 1469–1481. The ledger and runbook should agree.

Minimum correction: specify $ROOT/heat-data/ as the source directory; give the replacement-volume, restore-copy, and seed sequence; and replace the versionId pull with the §6.9.3 exported-payload restoration method. Add the claimed cold-session rule to R-4 or remove it from the ledger description.

Source: TD §11.8 R-4, §6.9.2–§6.9.3, §9.6.
R-5 — PARTIAL
The original service-target defect is corrected. The new text says:
docker compose up -d spawn-sidecar

That is the correct service, and the instruction is properly scoped. It also explicitly says not to grant the engine a Docker socket:
Do not grant the engine a socket (D-16 invariant — a "fix" that exposes the socket to the engine is a violation, not a repair).

That is consistent with D-16 and §6.2b.

The new direct probe is:
GET /v1/runs/{id}/status … (or 404 no_such_run for a probe id = alive)

This is a direct sidecar API check, but it verifies API liveness, not the operation that failed in the stated scenario. A sidecar can answer GET /status with 404 no_such_run while every POST /v1/create_run still returns 500 spawn_timeout. The check can therefore pass while the spawn channel remains broken.

make test-smoke does not close that gap by itself: §11.5 defines it as T-01 echo, the healthz trio, and a zero-orphan down/up cycle. It does not establish that create_run can create a container through the sidecar.

Minimum correction: retain the direct status probe, but add a safe, controlled create_run test using an allowed digest and the sidecar's normal restrictions, followed by direct status verification and cleanup. Do not give the engine socket access.

Source: TD §11.8 R-5, §6.2b, §11.5.
R-7 — PARTIAL
The original undefined destination is addressed:
/home/steven/backups/archive/

The runbook also adds a useful eligibility rule:
terminal (state.json terminal + gate_report present + ledger line appended + all promoted objects verified present in MinIO ...)

And it retains:
state.json, journal/, gate_report.json, manifest.json

It also explicitly prohibits using $ROOT as the archive destination. Those are good improvements.

Residuals:

1. The no-archive-directory fallback can lose unpromoted work. The runbook says:
if absent, operator may delete locally ONLY after step-2 verification, since MinIO holds the copy

But the eligibility test establishes that promoted objects are present in MinIO. It does not establish that the contents of work/ are in MinIO. §9.2 defines work/<job_id>/ as the per-job writable solver-I/O directory. The promoted tier is not a blanket copy of every working directory. The keep-list does not retain work/.

Therefore, the stated fallback can authorize deleting work/ data that has no verified copy elsewhere. That is a data-loss risk.

2. The MinIO eligibility test cites the wrong kind of evidence. §6.9.3 describes a proposed backup export of MinIO version history. It is not a live check that every promoted object is currently present and readable in MinIO. The mechanism is explicitly proposal/runtime-verify T-22, not an established operational capability. R-7 should specify a live MinIO object verification and distinguish it from the backup export.

3. The archive path's evidence tag is too strong. §9.4 records /home/steven/backups as an [E] legacy second-disk location. It does not establish that the child directory /home/steven/backups/archive/ already exists. That child path is a proposed destination and should be tagged [P], not [E].

4. The archive operation is still underspecified. “Move selected cold-run work/ + heavy artifacts/” gives a destination root but not a per-run destination layout, collision behavior, or a post-move digest/verification procedure. The du command is now concrete, but the archive transfer itself is not yet a reproducible sequence.

Minimum correction: prohibit deletion of work/ unless it has its own verified archive copy; verify promoted objects against the live MinIO service rather than relying on the §6.9.3 export; mark the new archive subdirectory [P]; and specify the per-run archive layout and post-transfer verification.

Source: TD §11.8 R-7, §9.2 and §9.4.

Q2 — New-defect hunt
I checked the staged runbook text against D-16, the lifecycle classes and shutdown sequence, the backup-root rules, and the referenced backup/retention sections.
Findings
1. R-4 selects from the wrong directory level.
newest dated dir under $ROOT (§6.9)

The canonical published backup path is:
$ROOT/heat-data/<yyyymmdd>.<runid>/

This is a concrete path mismatch. The selection instruction should name $ROOT/heat-data/.

2. R-4's versionId command contradicts the MinIO export design.
pull one promoted object by versionId (§6.9.3 export list)

§6.9.3 says:
no ?versionId= read-back

And specifies that a particular version is recovered by selecting its exported payload and re-uploading it as a new object. R-4 currently prescribes a verification operation the referenced design explicitly says is unavailable.

3. R-5's direct status probe can falsely pass a broken spawn channel.
404 no_such_run for a probe id = alive

That establishes that the status endpoint answers. It does not establish that POST /v1/create_run works or that the sidecar can successfully use its Docker socket. This matters because the runbook's triggering failure is specifically create_run returning 500/spawn_timeout.

4. R-5 misclassifies the host Docker service check as class X.
host docker service check (host action, out-of-stack, class-X owner §11.9)

§6.10 enumerates the backup systemd timer as class X. §11.9 likewise identifies the backup timer as class X and separately identifies Hermes and inference containers as external. The host Docker Engine is a host dependency (§2.6), but the document does not declare it a class-X container or unit.

The command itself:
sudo systemctl status docker

is a reasonable host-level check. The class-X label and §11.9 attribution are the problem. Call it a host prerequisite/dependency check instead.

5. R-7's deletion fallback is unsafe for work/.
operator may delete locally ONLY after step-2 verification, since MinIO holds the copy

The preceding step verifies promoted objects, not the complete working directory. This is not a safe basis for deleting work/. See Q1 R-7.

6. R-7 presents a proposed watermark as an established behavior.
engine refuses new at the 95 % hard watermark (FM-6; §9.4)

§11.6 declares:
DISK_WARN_PCT / DISK_HARD_PCT | 80 / 95 [proposal]

The runbook should carry the [P] qualification. The existence of a proposed 95% threshold does not establish that the engine already enforces it.

7. R-7's archive subdirectory is not itself evidenced.
/home/steven/backups/archive/ [E]

The [E] precedent in §9.4 is the parent /home/steven/backups. The new archive/ child directory is not established by that evidence. Mark the child directory [P] unless there is separate evidence that it exists.

8. The ledger describes R-4 content that is not present in the runbook.

The staged ledger says:
fresh heat-data → minio recovery → seed → T-11 digest-compare → M0 smoke; cold-session rule

The actual R-4 text does not specify a MinIO recovery sequence, a seed-script invocation, or a cold-session rule. This is another label-versus-prose mismatch. Either add the missing instructions or make the ledger description accurately describe the staged text.
Invariant checks
Invariant	Result
D-16: engine never receives Docker socket	No violation found. R-5 explicitly prohibits granting it.
§10 class boundaries	One label defect: R-5 calls the host Docker service check class X.
§6.10 six-step shutdown	No contradiction found. R-5's scoped sidecar restart is not a shutdown sequence and does not omit or reorder the six shutdown steps.
Backup root is not archive	No direct path violation. R-7 explicitly says never to archive to $ROOT; its local archive path is separate.
§6.9 backup semantics	One substantive contradiction: R-4's versionId retrieval conflicts with §6.9.3's export/re-upload semantics.
§9.4 retention/deletion	Safety gap: R-7's fallback can delete work/ without a verified copy.
§11.5 build/deploy	No shutdown conflict, but R-4's restore sequence still lacks the seed/rebuild steps implied by the ledger.
§11.6 parameter epistemics	One missing [P]: R-7's 95% refusal behavior.


Q3 — Legacy erratum check and R-reference sweep
The three stated corrections
FM-13 → R-4: CORRECT.

FM-13 is the /dev/sdf disk-loss case. R-4 is now the restore procedure. The FM-13 row's corrected pointer:
R-4 restore procedure

matches §11.8 R-4's subject. T-11 is the appropriate restore-drill evidence.

RC-5 → R-4 + T-11: CORRECT.

RC-5 is host disk failure and total state loss. Its required action is restoration from backup to fresh WSL/host storage. R-4 is the relevant runbook, and T-11 is the restore drill. This is the right mapping.

RC-4 → R-1 + R-9 drill: CORRECT WITH A SCOPE QUALIFICATION.

RC-4 is host reboot. R-1 covers bringing the stack up after it is down:
make up (runbook R-1) + boot reconcile

R-9 is the Docker-daemon restart drill. A host reboot also tears down the Docker daemon, so R-9 is a relevant recovery-class drill. However, R-9 explicitly exercises sudo systemctl restart docker; it is not itself a Windows/WSL host-reboot drill. The row should not imply that R-9 proves the complete host-reboot scenario. The current erratum's explanation that R-9 is the “matching drill class” is appropriately narrower.
Fourth surviving mispointing
FOUND
There is another surviving restore mispointing in the ADR's historical Amendment A1 text:

ADR §2, Amendment A1, line 347:
Restore sequence R-4/R-8 is fixed: quiesce stack → restore registry + DB (integrity_check) → start services → verify manifests → resume

R-8 is the backup-health/staleness runbook, not a restore runbook. The current restore runbook is R-4.

This sentence appears in the older A1 amendment, and the following A2 paragraph explains that A1's mechanics were corrected and superseded. That historical context reduces the operational risk, but it does not make the R-8 citation accurate. Since the request is a tree-wide erratum sweep, this is a surviving mispointing and should be annotated as superseded or corrected to avoid future copy-forward.
Other R-reference findings
I checked the textual/configuration files in the pinned tree, including the current design, ADR, requirements, design review, QA report, review response, ledger, tickets, residual-risk register, and archived adviser material.

The principal current references are consistent:
- DESIGN-REVIEW O3's R-1..R-9 list matches §11.8.
- DESIGN-REVIEW O6's R-8 stale-backup reference is correct.
- Requirements T-18's R-8 reference is correct for backup staleness.
- TD FM-6 → R-7, FM-7 → R-6, FM-11 → R-9, and FM-13 → R-4 are correctly mapped.
- TD RC-3 → R-9, RC-4 → R-1 + R-9, and RC-5 → R-4 + T-11 are appropriately mapped, subject to the RC-4 scope qualification above.
- The ADR's D8/R-4 digest-compare references are valid.
- The ADR's general D-14 trace to both R-4 and R-8 is valid: one is restore, the other is backup-health monitoring.
Two additional stale references are worth cleaning, though they are not restore/reboot mispointings:
1. workflows/for-adviser-review-2026-11-22.md still says runbooks R-1…R-8, omitting R-9. The later residual-risk annotation explicitly corrects this to R-1…R-9.
2. workflows/adviser-prompts/round-05/prompt-chatgpt-followup.md lists R-8 among my previous stalls. The archived follow-up reply correctly records that R-8 was FOLLOWED, not stalled. This is a historical prompt error, not a runbook mapping error.
Q3 conclusion: the FM-13 and RC-5 corrections are correct. The RC-4 correction is reasonable as a failure-class mapping, but R-9 should not be represented as an exact host-reboot drill. The ADR's historical R-4/R-8 restore citation is the surviving fourth mispointing.

One numbering correction to the prompt itself: in the pinned TD, FM-13 is in §12.1, not §12.4. §12.4 is “Operational readiness vs long-term ops.” RC-4/RC-5 are in §12.5.

Q4 — Status discipline
PRESERVED
The staged increment correctly records the repairs as staged paper drafts, not as completed operational passes.

The ledger entry begins:
Round-06 STAGED — M0 runbook repairs (R-4/R-5/7) paper drafts.

It concludes:
Exceptions stay recorded exceptions until an M0 walk re-executes the repaired procedures — staged drafts are NOT passes (§9 annotation unchanged).

That is consistent with the unchanged DESIGN-REVIEW §9 annotation:
Runbook gaps R-4 ... R-5 ... R-7 ... owner ruling 2026-11-24: accept as recorded exceptions; repair is M0-gated work (HARD STOP §10), not a document fix.

The annotation still distinguishes council review from independent-human approval and preserves the owner's responsibility for residual-risk acceptance.

The wording in the commit message and ledger also correctly calls the work “staged,” rather than claiming the runbooks have passed. I do not read the current status record as closing any of the three exceptions on paper alone.

There is one qualification: the ledger's description of the R-4 repair overstates its actual contents, as noted in Q2. That should be corrected, but it does not convert the entry into a pass.

M0 remains a hard stop. No runbook has been executed against a deployed stack; T-11 and other runtime evidence remain unearned. This review is read-only and grants no implementation, deployment, or ticket-execution authorization.

Source: DESIGN-REVIEW §9 exception annotation, staged ledger entry.

Overall verdict
APPROVE-WITH-CHANGES
The staged repair direction is sound, and the round-05 findings have been taken seriously. I would not accept this increment as fully closing the three runbook gaps yet.

Required changes before treating the paper repairs as complete:
1. R-4: select from $ROOT/heat-data/; specify replacement-volume provisioning, actual restore/copy, and seed sequence; correct the unsupported versionId verification; reconcile the runbook with the ledger's claimed MinIO recovery and cold-session instructions.
2. R-5: add a direct create_run verification, not only a GET /status liveness probe; remove the incorrect class-X attribution from the host Docker service check.
3. R-7: prohibit deletion of work/ without a verified archive copy; use live MinIO verification for promoted objects; tag /home/steven/backups/archive/ as proposed; specify archive layout and post-transfer verification; mark the 95% enforcement behavior [P].
4. ADR erratum: annotate or correct the surviving historical R-4/R-8 restore citation in Amendment A1.
5. Ledger accuracy: make the DP-R6-rb description match the actual R-4 text, particularly the missing seed, MinIO recovery, and cold-session steps.
The corrections should remain staged until the owner re-walks them. Even after the paper review is accepted, the R-4/R-5/R-7 exceptions remain open until the applicable M0 execution and evidence are completed. No deployment approval or M0 authorization is implied by this verdict.