GROK:
---------------------------------
Pin declared: content verified at b125d6659e9f (fix commit named by branch tip 035738d4704a re-pin note). All quotes below are from that tree.

Q1 — Per-fix ACCEPT / REOPEN
1. R-4 source selection scoped to $ROOT/heat-data/ — ACCEPT

Quoted: "(1) Select source: newest dated dir under $ROOT/heat-data/ — the published-backup tier only (§6.9.2 step 7; never repo/ or drills/) — with a schema-valid DONE.json"

Closes the $ROOT-level over-scope.
2. R-4 step-(6) ?versionId= removed; export-reupload proof — ACCEPT

Quoted: "(6) Versioned-tier proof: per §6.9.3 export semantics (no ?versionId= read-back exists) — select the version in the version manifest, re-upload its exported payload as a new object, digest-compare vs ledger."

Aligns with §6.9.3.
3. R-4 body: replacement-volume + seed-script sequence — ACCEPT

Quoted: "(4) Restore: host steps first [P, host recipe]: provision + mount the replacement ext4 volume at the heat-data mount point (§2.6 host prerequisite — a host action, not a compose op), copy the selected backup's heat-data/ tree into the §9.2 layout … then the host seed script (pre-baked image tars, §11.5/§12.2) so make up can start without a registry"

Body now carries the steps the DP-R6-rb gloss claimed.
4. R-4 cold-session rule (T0.5) explicit — ACCEPT

Quoted: "Cold-session rule (T0.5): this runbook must be executable from the paper alone with zero conversation context."
5. R-5 status = liveness-only + controlled create_run + smoke disclaimer — ACCEPT (with Q2 defect on cancel path)

Quoted: "a GET /v1/runs/{id}/status (§6.2b) answering proves API liveness only — it can 404 while create_run still times out. The failing operation must be exercised: one controlled POST /v1/create_run with an allowed digest under normal sidecar restrictions (§6.2b), confirm the container spawns, then POST /v1/cancel (or let it finish) + confirm state cleanup. make test-smoke is the backstop, not this runbook's proof (it is T-01 echo + healthz + down/up, §11.5 — it never exercises create_run)."

Intent of the fix is met; see Q2 for the cancel-path label defect.
6. R-5 host docker check reclassified (§2.6, not §11.9 class-X) — ACCEPT

Quoted: "host docker dependency check (host action, out-of-stack; docker engine is a §2.6 host prerequisite — NOT the §11.9 class-X unit, which is the backup timer) → sudo systemctl status docker"
7. R-7 data-loss fallback reversed (work/ protected) — ACCEPT

Quoted: "Data-loss rule: if the archive destination is unavailable, local deletion is limited to the promoted tier covered by step-2 verification — work/ has no verified copy elsewhere (promotion is not a copy of the working dir, §9.2) and may not be deleted without first being archived with its own post-move verification."
8. R-7 archive child [P]; live-MinIO vs export; layout/collision/post-move verify; 95% [proposal] — ACCEPT

Quoted:

"95 % hard watermark (FM-6; §9.4 — thresholds are §11.6 [proposal] until M0 builds them)"
"verified readable from the live MinIO service — head/get by key + digest-compare vs ledger; distinct from the §6.9.3 backup export, which is [proposal]/T-22"
"/home/steven/backups/archive/ [P] (new child dir under the §9.4 legacy second-disk root [E] — does not yet exist…), layout …/archive/<yyyymmdd>.<run_id>/ … .N suffix on name collision; after each move, digest-compare moved files vs pre-move digests before removing the source"

9. External corrections (ADR A1, RC-4, ledger gloss) — ACCEPT

ADR A1: "Restore sequence R-4/R-8 is fixed [round-06 erratum — superseded text; do not copy forward: the restore runbook is R-4 only; R-8 is the backup-health/staleness runbook — this A1 mechanics text was superseded by A2, TD §11.8 is normative]"
RC-4: "R-1 + R-9 drill … scope note: R-9 exercises daemon restart, NOT a Windows/WSL host-reboot drill; the full RC-4 reboot scenario still earns its own evidence at M0"
Ledger DP-R6-rb: "[gloss rev-2 note, per council C8: at 5315c37 the R-4 body did not yet contain the seed/MinIO/cold-session steps the gloss claimed — at DP-R6-r2 the body was raised to match this gloss, not the gloss lowered]"

Q2 — New-defect hunt (increment only)
Finding 1 — [major] R-5 cancel path is not a §6.2b operation

Quoted R-5: "then POST /v1/cancel (or let it finish) + confirm state cleanup"

§6.2b normative ops at this pin: POST /v1/create_run, GET /v1/runs/{id}/status, POST /v1/runs/{id}/kill, GET /v1/runs/{id}/logs. There is no POST /v1/cancel on the sidecar.

Minimum fix: replace with POST /v1/runs/{id}/kill (and optional follow-up status check), matching the contract and the shutdown path in §6.10/D9.
Finding 2 — no other live-vs-[proposal] overclaim found.

make disk-report remains [proposal, M0 build]; 95% watermark qualified via §11.6 [proposal]; archive child dir is [P]; volume provision/seed marked [P, host recipe].
Finding 3 — no D-16 / lifecycle-class / six-step / §6.9 / §9.2 / §9.4 contradiction beyond Finding 1.

R-5 still forbids granting the engine a socket; R-4 restore is host-recipe then make up; R-7 never archives to $ROOT.
Finding 4 — gloss-vs-body at this pin.

DP-R6-rb gloss + DP-R6-r2 note now match the R-4 body (seed, volume, export-reupload, cold-session present). R-5/R-7 bodies match the DP-R6-r2 fix list. No residual gloss-richer-than-body mismatch found at b125d6659e9f.
Q3 — Status discipline
PASS.

DP-R6-rb still states: "Exceptions stay recorded exceptions until an M0 walk re-executes the repaired procedures — staged drafts are NOT passes (§9 annotation unchanged)."
DP-R6-r2: "Status discipline preserved: drafts, not passes; §10 HARD STOP unchanged … no authorization."
Runbook bodies use "gap fix" / "council corrections applied" as change labels only; they do not claim exception closure or M0 pass.

Gloss-vs-body reconciliation is honest in both directions at this pin: the body was raised to the gloss (seed/volume/cold-session/export-reupload), and the gloss carries an explicit rev-2 note that it was previously ahead of the body.
Q4 — Final verdict
APPROVE-WITH-CHANGES

[major, required before treating R-5 as paper-complete] Replace R-5's POST /v1/cancel with the §6.2b path POST /v1/runs/{id}/kill (Finding 1).
All nine claimed fixes are ACCEPT as stated; the cancel-path label is a new defect introduced by the controlled-exercise wording, not a regression of the original R-5 target fix.

Paper acceptance only. R-4/R-5/R-7 exceptions remain open until M0 re-execution with evidence (T-11-class drills). No deployment authorization.
