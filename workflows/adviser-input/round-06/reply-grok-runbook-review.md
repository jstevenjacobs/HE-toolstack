<!-- received 2026-11-25 via owner paste; paste sha256 3ed34ad4adbabe09e132bc75147d3ab86b8a425ae224bf8521e3ffaa8538b4e2; pinned review SHA 5315c372cc0774427e54a69bc30199232f3831b4; verbatim, owner-delimited split Grok/ChatGPT -->

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
