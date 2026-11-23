# Ticket C4 — PD-toolstack working-copy archival

**Goal:** close Pass C item C4 (`DEPLOY-v2.md` §Pass C, `DESIGN-v2.md` §7 item 4): one
tarball each for host `~/PD-toolstack`, container `~/PD-toolstack`, and `PD-toolstack-ops`
into the archive location, then remove the working copies; runbooks extracted to
`he/docs/runbooks/` in the new repo (per DEPLOY-v2 C4 wording).

**Archive location (no new path invented):** existing frozen archive dir
`/mnt/c/Users/steven/OneDrive/Backup/PD-toolstack/` — already present beside
`HE-toolstack/` (D-14 context names it "the frozen `Backup/PD-toolstack/` archive"),
WSL-visible from host and container.

**Done-check (≤3 lines):**
- [ ] Three tarballs exist in the archive dir (host PD-toolstack, container PD-toolstack, PD-toolstack-ops); each passes `tar -tzf` and its sha256 + file count is in the committed manifest.
- [ ] `du -sh ~/PD-toolstack ~/PD-toolstack-ops` on host and `du -sh /opt/data/PD-toolstack*` in container all report "No such file" afterwards (working copies gone only after step-2 verify passes).
- [ ] Runbooks from `PD-toolstack-ops` committed under `he/docs/runbooks/`; `ls he/docs/runbooks/` non-empty.

**Preconditions:**
- C3 closed (orphan MinIO already retired; PD-toolstack no longer referenced by a live service).
- Free space on `/mnt/c` ≥ 2× total payload (D-14 A1 preflight rule).
- The tarball contains no live secrets in plaintext beyond what already exists at rest; if the tree holds credential files, they are recorded in the manifest as redacted-by-name, and any actively-rotating secret is rotated, not shipped (note in Result).

**Steps:**
1. Measured-size baseline: `du -sh` each of the three trees (host + container paths above). *Check: sizes captured (DESIGN-v2 §7's 160 MB/6.8 MB estimates are drift-checked against measured values; deltas recorded, no gating on the estimate).*
2. For each tree: `tar -czf <archive-dir>/<name>-<date>.tar.gz` from a quiesced state (nothing running against PD-toolstack — confirmed by C3 + `docker ps` having no PD-toolstack consumers). *Check: `tar -tzf` lists entries; `sha256sum` + entry count appended to manifest.*
3. Extract-to-temp spot check per tarball: one named runbook + one run script present. *Check: both files readable from the temp extract; temp dir removed.*
4. Copy runbooks into `he/docs/runbooks/` in the repo (only the runbook docs, not scripts/state). *Check: `ls he/docs/runbooks/` shows the expected runbook set; count matches manifest line.*
5. Commit repo changes (runbooks + manifest), push, ledger row. *Check: `git log origin/main -1` shows it.*
6. Remove working copies ONLY after steps 2–5 pass: host `rm -rf ~/PD-toolstack ~/PD-toolstack-ops`; container `rm -rf /opt/data/PD-toolstack /opt/data/PD-toolstack-ops`. *Check: `du -sh` on each path returns "No such file or directory".*
7. Append ledger row with `ref:` to §7 item 4. *Check: `tail -1 workflows/ledger.md`.*

**Evidence to commit:** manifest (tarball names, sha256, entry counts, sizes), step-3 spot
check output, before/after `du` outputs, runbook listing + ledger row.

**Rollback / failure recording:** removal (step 6) runs strictly after verified tarballs, so
rollback before step 6 is nothing-to-undo; after step 6, restore = `tar -xzf` the matching
archive back to its original path — record any restore in **Result** + ledger. Any step 2–3
failure: stop, keep working copies, ledger `blocked` with the failing checksum listing.

**Estimated sessions:** 1

**Result:** _(fill on close)_
