# Ticket C5 — Container scratch prune + hygiene cron

**Goal:** close Pass C item C5 (`DEPLOY-v2.md` §Pass C, `DESIGN-v2.md` §7 item 5): remove
`stageE`, `e2bfix`, stray snapshot scripts from container scratch
(`/opt/data/cache/scratch/`), keep `pd-analysis` (design not yet signed off — DR §9 grid
empty) as a single tarball, and register the 24 h scratch prune explicitly.

**Runtime-exception whitelist (not "invented", observed at HEAD-claim):** live agent
runtime entries the prune must never touch — `hermes_kernel_*`, `*.sock`,
`node-compile-cache/`, and any active session working dir (e.g. `HE-toolstack-review/`
while a review is in flight). The done-check set-equality is asserted over the *archival*
contents of scratch, whitelist excluded.

**Done-check (≤3 lines):**
- [ ] `ls /opt/data/cache/scratch` (whitelist above excluded) == `pd-analysis.tar.gz` and nothing else; `tar -tzf pd-analysis.tar.gz | head` lists the old `pd-analysis/` contents; `pd-analysis/`, `stageE/`, `e2bfix/` dirs gone.
- [ ] Prune cron entry listed by `crontab -l` (24 h idle prune over scratch with the whitelist as exclusions), and a probe confirms it targets scratch only.
- [ ] Space freed recorded (before/after `du -sh` scratch) in the ledger row + Result.

**Preconditions:**
- C2 closed — anything worth keeping from these dirs (run scripts, evidence) is already archived; C5 deletes, C2 only copied.
- Confirm `pd-analysis` is still needed live: DESIGN-v2 §7 item 5 keeps it "until this design is signed off" — DR §9 sign-off grid is empty, so directory→tarball happens NOW and the *tarball* is the thing that persists (this is the DEPLOY-v2 done-check state).
- The scratch dir is agent-owned (`/opt/data/cache/scratch`) — D-05: agent scratch is non-authoritative by definition, deletable without asking; nothing host-side is touched by this ticket.

**Steps:**
1. Inventory: `du -sh /opt/data/cache/scratch/*` sorted, plus `ls`. *Check: inventory captured in Result; `stageE`, `e2bfix`, `pd-analysis`, and `hermes-snap-*.sh` present (drift from these names → re-derive deletions from §7 item 5 wording, never from memory).*
2. Verify C2's manifest already covers anything from these dirs the archive claims (grep MANIFEST for `stageE`/`e2bfix` evidence paths). *Check: manifest hits or a recorded note "C2 archive did not depend on stageE/e2bfix" (whichever is true).*
3. Tarball `pd-analysis` → `pd-analysis.tar.gz` in scratch; `tar -tzf` verify; remove the directory only after tar verify. *Check: tar listing count == dir file count; dir gone.*
4. Remove `stageE/`, `e2bfix/`, stray snapshot scripts (`hermes-snap-*.sh`) and the dated one-off review/probe artifacts from prior rounds (`r*.py`, `pr-*.md`, `new*.md`, `diff_*.txt`, `revlog.txt`, `q16_block.py`, `r2probe*.sh`, `issues.sh`, `mmcheck*/`, `review/`, `he-seed/`). *Check: each removed name listed in Result; whitelist entries untouched.*
5. Register/verify the prune cron explicitly (`crontab -e`-safe: `crontab -l` round-trip) — 24 h idle prune of `/opt/data/cache/scratch` excluding the whitelist. *Check: `crontab -l` prints the entry; a `touch`ed sentinel file older than 24 h would match the prune expression (dry-run `find -mmin +1440` listing, no execution needed).*
6. Final state: `du -sh scratch` + whitelist-excluded `ls`. *Check: matches done-check line 1 exactly.*
7. Append ledger row with `ref:` to §7 item 5 + D-05 scratch-deletability clause. *Check: `tail -1 workflows/ledger.md`.*

**Evidence to commit:** before/after inventory + freed-space delta, tar verify line,
`crontab -l` output, final `ls` — as `evidence/pd-archive/c5-scratch-prune.md` + ledger row.

**Rollback / failure recording:** `pd-analysis` is protected by its tarball (step 3
ordering); stageE/e2bfix are expendable by D-05 definition — if C2's manifest check (step 2)
shows any needed artifact lived only there, STOP before step 4, archive it via C2's path
first, record in **Result**. Cron mis-entry: `crontab -r` of only the added line (restore
prior crontab captured in step 5), ledger note.

**Estimated sessions:** 1

**Result:** _(fill on close)_
