# HE-toolstack — DP0 package for external adviser review (Grok)

**Date:** 2026-11-22 (CST) · **Prepared by:** Hermes (main agent), packaging turn — no deployment steps, no compose/docker/runtime commands executed this turn; all steps were file reads and markdown writes.
**Repo:** `jstevenjacobs/HE-toolstack` @ HEAD `5c487f4bf40738cc746507caa2734dc8e3653cd4` — commit: *"Merge PR #11: formal architecture review response, rounds 1-13 (docs-only)"* (2026-11-18).

## a) Design-status summary (one sentence + verified facts)

The design package is documentation-integrity-clean but explicitly **not frozen and never executed**: QA v2.3 claims 27/27 automated gates against a scratch (gitignored) harness while its own §3 states "No stack was built; **zero runtime claims** are QA'd here — every T-test is still unexecuted [proposal]", and the freeze grid (DR §9 🧑 rows) is unclaimed.

Verified at HEAD this pass:
- All seven core docs present. Last git-modified: DESIGN-v2.md + DEPLOY-v2.md = 2026-11-14 (`141249d`); TD / REQ / ADR / QA / RR = 2026-11-17 (`68626eb`, merged at `5c487f4`).
- QA-REPORT.md v2.3 (rev r13) still claims the 27-gate PASS set (Q1–Q2, Q4–Q28; Q3 mermaid run separately 9/9) — with the caveat that QA line 38 (Q22 row) is **truncated on disk at 248 bytes**, leaving 26 explicit PASS cells (see DP0 R-10).
- REVIEW-RESPONSE is post-r13: r13 status banner present at line 544; D-15 ACCEPTED (Option D, 2026-11-16), D-16 ACCEPTED (Option B, conflict resolved 2026-11-17), OQ-1 RULED CLOSED, OQ-4 half-open (D-06 wrapper shape unruled).
- `workflows/ledger.md` stale: 11 lines, last row 2026-11-15 (D-14); r4–r13 + merge added no rows (DP0 R-11).

## b) Residual-risk register — full contents of `workflows/residual-risks-DP0.md`


# DP0 — Residual-Risk Register (deployment-planning gate)

**Assembled:** 2026-11-22 (CST) · **Repo HEAD:** `5c487f4` (merge of PR #11, rounds 1–13, docs-only) · **Docs at HEAD:** TD v1.13 / REQ v1.10 / ADR v1.11 (r11) / QA v2.3 (r13) / RR post-r13 (status banner r13).
**Sources:** (a) residual-risk register R-01…R-08 from the documentation-package review (this session series); (b) QA-REPORT §3 "Known limits" + §3.3/r5 retraction notes; (c) ADR §OQ register open rows + DESIGN-REVIEW findings register.
**Evidence classes:** [V] verified by execution · [E] on-disk artifact inspected this pass · [P] proposal/design-record only · [U] unmeasured/uncertain.

| ID | Statement | Evidence class ([V]/[E]/[P]/[U]) | Gate type (Hard/Soft/Deferred) | Owner action required | Blocks Pass-C? (yes/no) |
|----|-----------|----------------------------------|-------------------------------|----------------------|------------------------|
| R-01 | Design-freeze sign-off grid is unclaimed: DESIGN-REVIEW §9 has all three 🧑 rows empty (owner / engineering / ops) and QA §5 diagram sign-offs unclaimed — freeze cannot be declared, and the package itself says so ("the 🧑 rows still block design freeze"). | [P] | Hard (for freeze; interim record required before first `make up`) | Steven signs owner row; engineering + ops reviewers sign; ops dry-runs runbooks R-1…R-8 (esp. R-7). Before first `make up` without full grid: an initialed ledger row authorizing M0 build while freeze stays blocked. | no |
| R-02 | DESIGN-REVIEW §2b diagram↔prose checklist rows M1–M10 are human-only and unclaimed; closed by T-11 during M0. | [P] | Soft | Human reviewers claim rows during M0. | no |
| R-03 | All tests T-01…T-24 are specified-only, **zero executed** (QA §3.1: "No stack was built; zero runtime claims are QA'd here — every T-test is still unexecuted [proposal]"); the QA harness itself is scratch/gitignored (`.hermes-tmp/gates_v13.py`), so "27/27" is author-reproducible only (RR App. J §J.5). | [E] | Hard (for M0 acceptance; execution is the M0 deliverable itself) | Execute T-matrix per runbook; record in QA §5. | no |
| R-04 | OneDrive off-host durability has no L4/L5 upload-completion proof (OQ-9 open: "no credential-free automated signal reaches L4/L5"); T-11/T-18 drills unexecuted; disk headroom sampled only once during ticket work (~66 GB free, 81.5% full — a dated sample, [U]). | [U] | Deferred (drill before M0 close or formal D-05 fallback acceptance) | Run T-11/T-18/NFR-22 drill before M0 close, or formally accept D-05 secondary-disk fallback; re-sample disk at check time. | no |
| R-05 | OQ-4's remaining half — D-06 physics-gate endpoint-wrapper shape — is **unruled** (ADR OQ-4 row: D-08 half CLOSED by operator, D-06 half open), and DESIGN-REVIEW §9 conditions *M0 build start* on it ("OQ-1/OQ-4 ruled before M0 build starts"; OQ-1 RULED CLOSED). | [E] | **Hard for any build (`make up` / T0.x); not for Pass-C cleanup** | Operator ruling on D-06 recorded in ADR (OQ-4 row + D-06 section) before any T0.x build starts. | no |
| R-06 | ADR-D-07 (solver state hand-off) and ADR-D-11 (MinIO artifact retention) remain **Proposed** — must not drift into assumed-accepted during M0 (RR §10 lesson). | [E] | Soft | Rule in ADR before the affected components are built. | no |
| R-07 | F-1: no authN/Z beyond `he-agent` group membership; a compromised spawn-sidecar is root-equivalent (deferred by operator; D-12 trigger reopens). | [P] | Deferred | Rule authN/Z posture at D-12 trigger / before any fleet. | no |
| R-08 | ADR open questions still open: OQ-2 (D-04 GPU numbers need C6 data — FINDING-04: 8 GiB ceiling / 5.5 GiB floor rest on one measurement chain, driver floor claim unconfirmed), OQ-7 (fleet/WSL bind topology), OQ-8 (MinIO version-history fallback, T-22 unexecuted). M2+ scope. | [P] | Deferred | Proposers file ADRs / re-measure ticket after C6. | no |
| R-09 | QA-harness location decision is unmade: FINDING-08 (QA-report numbering — promotion of the gate script into repo `scripts/qa/`) is explicitly due **at M0 start**; today the 27-gate result is reproducible only by the author. | [E] | Hard (at M0 start — before freeze re-gate is claimed) | Operator decision recorded in ledger: promote to `scripts/qa/` (recommended: yes, CI-style rerun by a stranger) or accept author-reproducible with rationale. | no |
| R-10 | Freeze-integrity repairs outstanding (found by this review's own grep): (1) QA-REPORT line 38 **Q22 row truncated on disk at 248 bytes** → only 26 explicit PASS cells, "27/27" rests on the header + §5 narrative; (2) RR Appendix I §I.3 row 4 stale ("OQ-4 … both halves unruled" contradicts ADR r11 D-08-half-CLOSED); (3) QA footer says "results above are the r12 tree" while header claims r13 re-gate. All cosmetic-grade, none a design defect — but each re-introduces exactly the stale-coherence failure class rounds r12/r13 killed. | [E] | Hard (before freeze can be claimed / before first `make up` package handoff) | Repair Q22 row + RR App. I row + QA footer; re-gate Q1–Q27 against the r13 tree; commit with gate output. | no |
| R-11 | `workflows/ledger.md` is stale (11 lines; last row 2026-11-15 D-14): rounds r4–r13 and the PR #11 merge appended no rows despite the DEPLOY-v2 state law requiring one per ticket/decision. State-machine debt, not a design defect. | [E] | Soft (hard at M0 close) | Restart the ledger with this DP0 row; one row per ticket/claim from here on, `ref:` enforced. | no |
| R-12 | FINDING-06: TD §4 reuse list claims several Phase-1 scripts reusable "unchanged" on reading only — each owes an import-time smoke check at M0 import. FINDING-05 (make-down/runbooks unexecuted) is open by nature and converts to [V] at M0. | [P] | Deferred | M0 execution activity with evidence per script. | no |

## Go/no-go recommendation — Pass C

**GO for Pass C.** No open item in this register blocks C1–C5: every open question (R-05's D-06 ruling, R-06's Proposed ADRs, R-08's M2+ items) gates *build* decisions that Pass-C cleanup never touches, and Pass-C's own risks (orphan teardown, archive, prune) are mechanical, reversible-by-evidence, and gated by their own per-ticket done-checks. The two review conditions that do bind are sequencing conditions, not Pass-C conditions: (1) before any `make up`/T0.x build, R-05 and R-10 and R-09 must close and R-01 must at least carry an initialed interim authorization row; (2) before any M0-acceptance or freeze claim, R-01–R-03 close fully. Recommended claim order remains C1→C2→C3→C4→C5 (risk-ranked; C3's object-count and Cognee-untouched assertions are the highest-consequence and must run only after C2's evidence archive exists).


## c) Candidate-ticket table of contents

| Filename | Title | Done-check (first 3 lines, condensed) |
|---|---|---|
| `workflows/tickets/candidates/C1-seed-repo.md` | Ticket C1 — Seed repo completion (re-baselined to HEAD reality) | - [ ] `make help` runs at repo root, exit 0, and lists at least `help`. | - [ ] `he/` client stub exists in the repo tree (placeholder for the `he` HTTP/JSON client, ADR-D-09 shape — no MCP, no implementation). | - [ ] Both committed to `main`; ledger row appended with `ref:` to DESIGN-v2 §7 C1. |
| `workflows/tickets/candidates/C2-evidence-archive.md` | Ticket C2 — PD-toolstack evidence archive | - [ ] `make verify-archive` exits 0: committed file count under `evidence/pd-archive/` equals the committed manifest count. | - [ ] A fresh-context delegate, given only the repo, answers "what was E2b's gate result" with a file path inside `evidence/pd-archive/` (paste Q+A in Result). | - [ ] Issue #41/#42 text (or a recorded discrepancy note if the numbers do not resolve) committed under `evidence/pd-archive/issues/`; ledger row appended. |
| `workflows/tickets/candidates/C3-orphan-minio-teardown.md` | Ticket C3 — Host orphan MinIO teardown (copy-first; Cognee untouched) | - [ ] Recursively-counted object count + total bytes staged == source counts captured before removal (per-bucket `mc ls --recursive` counts, both sides, in committed evidence). | - [ ] `docker ps -a | grep -c minio` == 0 on host afterwards (zero count includes the `infra` container AND its volume gone via `docker volume ls`); the D-14 root staging dir holds the copy. | - [ ] Cognee green after teardown: `cognee_api`, `cognee_postgres`, `cognee_ui` all `Up (healthy)` — same three containers, same compose project `cognee`, before and after. |
| `workflows/tickets/candidates/C4-working-copy-archival.md` | Ticket C4 — PD-toolstack working-copy archival | - [ ] Three tarballs exist in the archive dir (host PD-toolstack, container PD-toolstack, PD-toolstack-ops); each passes `tar -tzf` and its sha256 + file count is in the committed manifest. | - [ ] `du -sh ~/PD-toolstack ~/PD-toolstack-ops` on host and `du -sh /opt/data/PD-toolstack*` in container all report "No such file" afterwards (working copies gone only after step-2 verify passes). | - [ ] Runbooks from `PD-toolstack-ops` committed under `he/docs/runbooks/`; `ls he/docs/runbooks/` non-empty. |
| `workflows/tickets/candidates/C5-scratch-prune-cron.md` | Ticket C5 — Container scratch prune + hygiene cron | - [ ] `ls /opt/data/cache/scratch` (whitelist above excluded) == `pd-analysis.tar.gz` and nothing else; `tar -tzf pd-analysis.tar.gz | head` lists the old `pd-analysis/` contents; `pd-analysis/`, `stageE/`, `e2bfix/` dirs gone. | - [ ] Prune cron entry listed by `crontab -l` (24 h idle prune over scratch with the whitelist as exclusions), and a probe confirms it targets scratch only. | - [ ] Space freed recorded (before/after `du -sh` scratch) in the ledger row + Result. |
| `workflows/tickets/candidates/T0.1-compose-skeleton.md` | Ticket T0.1 — Compose skeleton (single project, zero host publication, functional sidecar) | make up && make doctor          # exit 0; exactly 1 compose project; all services healthy; no gpu profile | ss -ltn | grep -c ':8100'       # 0 — zero host publication for toolserver, any form (D-15 Option D; :8100 listener = preflight failure) | docker exec he-toolstack-workflow-engine-1 sh -c 'test ! -e /var/run/docker.sock && echo NOSOCK'   # NOSOCK |
| `workflows/tickets/candidates/T0.2-queue-wired.md` | Ticket T0.2 — Serialized queue wired (engine SQLite FIFO → sidecar execution → run capture) | bash workflows/t02_queue_matrix.sh   # exit 0: 3 no-op jobs FIFO; kill -9 engine mid-run and mid-write => zero job loss, resume correct | docker exec he-toolstack-workflow-engine-1 sh -c 'test ! -e /var/run/docker.sock && echo NOSOCK'  # NOSOCK | ss -ltn | grep -c ':8100'            # 0 (still zero host publication after wiring) |
| `workflows/tickets/candidates/T0.3-tasmet-trivial-solve.md` | Ticket T0.3 — TaSMET trivial solve through the queue (minimal closed sCO2 loop, CPU class) | bash workflows/t03_solve.sh            # submits closed-loop config via POST /v1/jobs, polls to succeeded, exit 0 | ls runs/<job>/ | grep -c 'solution\|entropy' # >=2: solution files + entropy-residual readout present | grep -c 'sha256:' stacks/tasmet/PIN.md       # >=1, value == docker images --digests row for ta-solver-runtime |
| `workflows/tickets/candidates/T0.4-physics-gate.md` | Ticket T0.4 — Physics-gate carry-forward + M0 verdict (5 checks, fail-closed) | make gate RUN=<t03_job_id>   # exit 0; gate_report.json with checks[5] all computed (verdict may be warn, not error) | make test-gate               # exit 0: E1/E2b regression unit tests green, N/N | diff <(engine-path report) <(endpoint-path report)   # byte-identical reports, two entry paths |
| `workflows/tickets/candidates/T0.5-registry-state-cold-session.md` | Ticket T0.5 — Registry + state-machine files + claim protocol + cold-session test | make test-state                 # exit 0: ledger refuses ref-less append; state.json cursor advances only on committed checkpoint | python3 workflows/t05_claim_race.py   # >=2 procs race 1 fresh ticket, 10x: exactly 1 claim, kill -9 mid-claim recovers, hung holder NOT superseded | bash workflows/t05_cold_session.sh    # zero-context delegate's done/next answer == t05_expected.txt (diff empty) |
| `workflows/tickets/candidates/T0.6-m0-acceptance.md` | Ticket T0.6 — M0 acceptance run (`make verify` chains M0a–M0e; full-stack drills; evidence + ledger close) | make verify                 # exit 0: M0a→M0b→M0c→M0d→M0e green in one chain, evidence/ artifacts written | bash workflows/t06_drills.sh  # T-13 (down during active job -> interrupted rows), T-15 six legs, T-16 CI, T-19 RC-3, host-reboot leg of T-05 | git log --oneline --  evidence/m0/ | head -1   # evidence dir committed; ledger final row: M0 CLOSED |

## d) Full text of every candidate ticket


---

## File: `workflows/tickets/candidates/C1-seed-repo.md`

# Ticket C1 — Seed repo completion (re-baselined to HEAD reality)

**Goal:** close out Pass C item C1 (`DEPLOY-v2.md` §Pass C, `DESIGN-v2.md` §7 item 1).
The repo seed already exists at HEAD (`docs/` + `workflows/` state machine are committed,
PR #11 merged), so the original "first commit" wording is satisfied except for two named
artifacts that are **absent at HEAD**: root `Makefile` (with `make help`) and the `he/`
client stub (`DESIGN-v2.md` §7: "this doc + `he/` scaffold + `Makefile` targets"). This
ticket adds exactly those — no services, no physics, no GPU, no new directories beyond
the two named.

**Done-check (≤3 lines):**
- [ ] `make help` runs at repo root, exit 0, and lists at least `help`.
- [ ] `he/` client stub exists in the repo tree (placeholder for the `he` HTTP/JSON client, ADR-D-09 shape — no MCP, no implementation).
- [ ] Both committed to `main`; ledger row appended with `ref:` to DESIGN-v2 §7 C1.

**Preconditions:**
- Push access to `jstevenjacobs/HE-toolstack` `main` (container push path per repo convention).
- No running stack required — this ticket touches only the git repo.

**Steps:**
1. Record the baseline: `git rev-parse HEAD` and `ls` at repo root (confirms `Makefile`/`he/` absent at claim time). *Check: baseline captured in this ticket file.*
2. Add root `Makefile` with a `help` target that lists available targets; no service targets (compose shape is frozen only after M0 — T0.1 owns `up/verify/down`). *Check: `make help` exits 0 and prints the target list.*
3. Add `he/` stub: package skeleton only (entry placeholder + README line pointing at ADR-D-09); no HTTP code. *Check: `test -d he && ls he` non-empty; `grep -l -i "no MCP\|D-09" he/README*` (or equivalent stub comment) hits.*
4. Commit and push to `main`; append the ledger row (`workflows/ledger.md`, state law). *Check: `git log origin/main -1` shows the commit; `tail -1 workflows/ledger.md` is the C1 row with a `ref:`.*

**Evidence to commit:** the `Makefile`, the `he/` stub, the ledger row, and the baseline +
`make help` output pasted into this ticket's **Result** section.

**Rollback / failure recording:** plain `git revert` of the seed commit restores HEAD state;
no external side effects exist. If blocked (e.g. push refused), record the blocker in
**Result** + a ledger row marked `blocked` and stop — do not work around by force-push.

**Estimated sessions:** 1

**Result:** _(fill on close)_


---

## File: `workflows/tickets/candidates/C2-evidence-archive.md`

# Ticket C2 — PD-toolstack evidence archive

**Goal:** close Pass C item C2 (`DEPLOY-v2.md` §Pass C, `DESIGN-v2.md` §7 item 2): copy
PD-toolstack run scripts (`scripts/verify_e1.py`, `scripts/verify_e2.py`, `scripts/e2b_*`
per §7), the E1/E2b evidence dirs, and open issues #41/#42 text into
`evidence/pd-archive/` in HE-toolstack. PD-toolstack stays **frozen** — no commits to it
under any circumstance (§7 item 2: "until then PD-toolstack receives nothing").

**Done-check (≤3 lines):**
- [ ] `make verify-archive` exits 0: committed file count under `evidence/pd-archive/` equals the committed manifest count.
- [ ] A fresh-context delegate, given only the repo, answers "what was E2b's gate result" with a file path inside `evidence/pd-archive/` (paste Q+A in Result).
- [ ] Issue #41/#42 text (or a recorded discrepancy note if the numbers do not resolve) committed under `evidence/pd-archive/issues/`; ledger row appended.

**Preconditions:**
- Root `Makefile` present (if C1 not yet claimed, C2 adds the `verify-archive` target itself — still independent).
- Host tree `/home/steven/PD-toolstack` reachable via the host-ssh path (repo convention).
- Host `gh` CLI available for the issue dump.

**Steps:**
1. Locate the named artifacts at their §7 paths on host `~/PD-toolstack` (`scripts/verify_e1.py`, `scripts/verify_e2.py`, `scripts/e2b_*`, E1/E2b evidence dirs). *Check: `ls` output per path captured in Result; any path absent at claim time is recorded as a discrepancy line — no substitute files invented.*
2. `find` the same name patterns across the host working copy to catch relocated scripts. *Check: find output appended to the discrepancy line (found / not-found).*
3. Copy (never move) everything found into `evidence/pd-archive/` preserving names; write `evidence/pd-archive/MANIFEST` (one relative path per line, sha256 per file). *Check: `sha256sum -c` against MANIFEST exits 0.*
4. Dump open issues: `gh issue view 41`/`42` (repo per §7) into `evidence/pd-archive/issues/`. *Check: two files exist, or a `DISCREPANCY.md` records the exact `gh` error verbatim (probe at ticket-writing time: GraphQL "could not resolve" — expected until reconciled).*
5. Add `make verify-archive` (Makefile from C1): counts files under `evidence/pd-archive/` against MANIFEST, exits non-zero on mismatch. *Check: `make verify-archive` exits 0; deliberately removing one file makes it exit non-zero (then restore).*
6. Commit, push, append ledger row with `ref:` to DESIGN-v2 §7 item 2. *Check: `git log origin/main -1` + `tail -1 workflows/ledger.md`.*

**Evidence to commit:** the whole `evidence/pd-archive/` tree + MANIFEST + `verify-archive`
target + ledger row; Result section carries the locate/find output, delegate Q+A, and issue
dump status.

**Rollback / failure recording:** pure additive commit — `git revert` restores prior tree;
no host state is mutated by this ticket (copy-only). Blocker (missing evidence paths, issue
numbers unresolved): record verbatim output in **Result**, ledger row `blocked`, stop.

**Estimated sessions:** 1

**Result:** _(fill on close)_


---

## File: `workflows/tickets/candidates/C3-orphan-minio-teardown.md`

# Ticket C3 — Host orphan MinIO teardown (copy-first; Cognee untouched)

**Goal:** close Pass C item C3 (`DEPLOY-v2.md` §Pass C, `DESIGN-v2.md` §7 item 3; ADR-D-01
"teardown must copy bucket contents before host-orphan removal"): copy (not move) the
orphan `infra-minio-1` bucket contents out, then stop/remove compose project `infra`
(config `/home/steven/PD-toolstack/infra/minio-compose.yml`) and its volume, leaving the
Cognee stack untouched.

**Deviation note (recorded, not silent):** DEPLOY-v2's done-check assumes the M0 app-MinIO
service exists as the copy target. Pass C forbids new services — the `minio` compose
service only arrives with T0.1. Copy destination is therefore a staging directory under
the D-14-ruled backup root: `/mnt/c/Users/steven/OneDrive/Backup/HE-toolstack/` (layout
`heat-data/` `repo/` `drills/` per D-14; add `pd-minio-orphan/` as a sibling staging dir).
Import into the app bucket is a **T0.x follow-up**, recorded in the ledger row.

**Done-check (≤3 lines):**
- [ ] Recursively-counted object count + total bytes staged == source counts captured before removal (per-bucket `mc ls --recursive` counts, both sides, in committed evidence).
- [ ] `docker ps -a | grep -c minio` == 0 on host afterwards (zero count includes the `infra` container AND its volume gone via `docker volume ls`); the D-14 root staging dir holds the copy.
- [ ] Cognee green after teardown: `cognee_api`, `cognee_postgres`, `cognee_ui` all `Up (healthy)` — same three containers, same compose project `cognee`, before and after.

**Preconditions:**
- Operator approval to remove the orphan (this ticket deletes containers/volumes — one-time destructive step, pre-ruled in DEPLOY-v2 §7 item 3 but re-confirm at claim).
- `mc` (or the MinIO container's own client) available on host; credentials readable from `/home/steven/PD-toolstack/infra/minio-compose.yml`.
- Cognee state snapshot baseline captured (`docker ps` + healthcheck output) BEFORE any infra action.

**Steps:**
1. Baseline probe, no mutation: `docker inspect infra-minio-1` compose labels (project/config path — must match the §7 config path), `docker volume ls` for the `infra` volume, per-bucket recursive object count + bytes via `mc ls --recursive`/`du`. *Check: probe output committed as `evidence` below; config path in labels == `/home/steven/PD-toolstack/infra/minio-compose.yml` or STOP (wrong orphan).*
2. Cognee baseline: names/status/health of the three `cognee`-project containers. *Check: all healthy; captured for later diff.*
3. Copy bucket contents to `/mnt/c/Users/steven/OneDrive/Backup/HE-toolstack/pd-minio-orphan/` (copy, never move — D-01 consequence wording). *Check: re-count staged objects + bytes; equals step-1 counts exactly.*
4. `docker compose -f /home/steven/PD-toolstack/infra/minio-compose.yml down` (project `infra` only; never a name-matched `docker rm`). *Check: `docker ps -a --filter label=com.docker.compose.project=infra -q` empty.*
5. Remove the orphan volume (`docker volume rm infra_<volume>` as named in step 1) + the config file path stays on disk (it is PD-toolstack-frozen content; C4's tarball captures it). *Check: `docker volume ls | grep -c infra` == 0.*
6. Cognee diff + final gate: re-list the three cognee containers, compare to step-2 baseline; run `docker ps -a | grep -c minio`. *Check: identical container set + all healthy; grep count == 0.*
7. Append ledger row with `ref:` to D-01 A1 consequences + §7 item 3 and the T0.x import follow-up. *Check: `tail -1 workflows/ledger.md`.*

**Evidence to commit:** step-1 probe + per-bucket count/bytes table, step-3 staged-vs-source
count table, before/after Cognee `docker ps` outputs, final grep-0 output — as
`evidence/pd-archive/c3-orphan-teardown.md` (commit text only; **no credentials**, no
bucket data) + ledger row.

**Rollback / failure recording:** until step 4 the host is unmutated (steps 1–3 are pure
read/copy). If counts mismatch at step 3, do NOT proceed to step 4 — record the delta,
ledger `blocked`. After step 4, rollback = `docker compose -f <config> up -d` restores the
orphan from its existing volume (volume removal is the last, point-of-no-return step and
only runs after counts verified); record any restore in **Result** + ledger.

**Estimated sessions:** 1

**Result:** _(fill on close)_


---

## File: `workflows/tickets/candidates/C4-working-copy-archival.md`

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


---

## File: `workflows/tickets/candidates/C5-scratch-prune-cron.md`

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


---

## File: `workflows/tickets/candidates/T0.1-compose-skeleton.md`

# Ticket T0.1 — Compose skeleton (single project, zero host publication, functional sidecar)

**Goal:** DEPLOY-v2 Pass-0 item T0.1: `compose.yaml`, ONE project `he-toolstack`, all
services stub-minimal with healthchecks. Class-C canonical five (TD §6.10): `toolserver`,
`workflow-engine`, `minio` (+bucket env), `spawn-sidecar`, `he-scratch-keeper`;
`postgres` optional-off profile. Deviation recorded (DEPLOY-v2 bullet is older than the
TD): `physics-gate` is **not** a compose service — it runs as a one-shot through the
sidecar (T0.4); the fifth core service is `spawn-sidecar`/`he-scratch-keeper` per TD
§6.10, and "host is the sole worker, D-11" is superseded by D-16 Option B (ACCEPTED;
D-11 stays Proposed). The sidecar lands **functional** here (sole `docker.sock` holder,
four §6.2b ops `create_run`/`status`/`kill`/`logs`, digest allow-list, `network:"none"`
enforced, `cap_drop: ALL`, non-root) because the spawn boundary is a compose skeleton
property; T0.4 exercises and hardens the full matrix. Engine never sees a socket.

**Done-check (≤3 lines; cold session with repo at root + host access):**
```
make up && make doctor          # exit 0; exactly 1 compose project; all services healthy; no gpu profile
ss -ltn | grep -c ':8100'       # 0 — zero host publication for toolserver, any form (D-15 Option D; :8100 listener = preflight failure)
docker exec he-toolstack-workflow-engine-1 sh -c 'test ! -e /var/run/docker.sock && echo NOSOCK'   # NOSOCK
```

**Preconditions:** Pass-C **C1** green (seed repo + root Makefile exist) and **C3** green
(orphan `infra-minio-1` gone — the zero-orphan assertion is only meaningful on a clean
host). R-05/D-06 endpoint-wrapper ruling recorded in the ADR (DESIGN-REVIEW hard gate for
any T0.x build).

**Steps:**
1. `compose.yaml` root: project `he-toolstack`; five core services; profiles `gpu` (inert,
   never activated in M0), `postgres` (off); every service `he-stack=1` label +
   healthcheck + `restart: unless-stopped` + digest-pinned images (T-16 seed); minio with
   bucket env + `pull_policy: never`. ✓ `docker compose config --quiet` exit 0.
2. Networks: `he-agent` (internal; toolserver attached) + `he-internal` (internal;
   sidecar + engine + toolserver); toolserver has **no `ports:` key**; sidecar publishes
   nothing; `TS_BIND=0.0.0.0` inside-container. ✓ `docker network inspect` both
   `Internal: true`; zero published ports in `docker compose ps`.
3. Data root bind-mounts per D-01 (heat-data / minio / Backup under one host root declared
   in `infra/ENVIRONMENT.md`); queue DB on the bind, not a named volume. ✓ `docker volume
   ls` gains nothing new.
4. Sidecar per TD §6.2b verbatim: socket at sidecar path only, `he-internal` reach only,
   shared-secret bearer from sidecar-only tmpfs file; 403/404/413/422/429 shapes;
   `sidecar_audit` one row per call. ✓ contract smoke: create_run of an allow-listed
   `busybox` digest with `network:"none"` → 201 → status → kill → logs; deny legs (a)–(d)
   at least one probe each; non-member reach → no route.
5. `make up|down|health|logs|test` + `make doctor` (project set, zero `:8100` listener any
   form, zero `he-stack=1` containers when down, CPU-only flags) + `make health` as the
   operator path (`docker run --rm --network <project>_he-agent … /healthz` — TD §7.1). ✓
   doctor exit 0 up and down (up relaxes only the zero-container rule).
6. `make down` = the full six-step §6.10/D9 recipe (1 `compose stop -t grace` engine →
   2 engine kills class-J via sidecar `kill` — no-op with zero jobs → 3 write-ahead
   `interrupted/killed` → 4 `compose down` → 5 host-side janitor sweep of `he-stack=1`
   remnants, works with engine AND sidecar dead → 6 assert). ✓ step 6 prints 0;
   `docker compose ps -a` empty.
7. Stub HTTP on toolserver: health trio `/healthz`+`/readyz`+`/deps` (`/health` → 404,
   r12 canonical) + `POST /v1/jobs` stub returning `201 {job_id, queue_pos}` (exact shape,
   no `state`). ✓ trio answers from **inside an agent-like container** over
   `http://toolserver:8100` (host-side curl does not count, F1); stub 201 shape verbatim.

**Evidence to commit:** `compose.yaml`; `Makefile` targets diff; `workflows/t01_doctor.txt`
(up+down); `workflows/t01_ss_output.txt`; `workflows/t01_makedown_transcript.txt` (six
steps + step-6 zero); `workflows/t01_sidecar_smoke.txt` (4 ops + ≥1 refusal per leg +
audit row count == call count); ledger row.

**T-tests exercised:** **T-13** partially (zero-orphan at rest + six-step recipe executed
empty-stack; running-job variant is T0.6), **T-15** partially (legs 1–4 skeleton:
agent-member reach leg from inside a container, non-member unresolvable/refused, host
`127.0.0.1:8100` refused; full six-leg matrix in T0.6), **T-16** partially (all images
digest-pinned in compose; MANIFEST CI lands T0.6), **T-08** partially (health trio + 201
stub shape fixtures seeded). Not exercised: T-01/T-03/T-04/T-05/T-07.

**Failure recording (write-ahead):** before any re-attempt, append `FAILURE T0.1 <what>
<observed>` to this ticket + ledger row, with the failing output kept as
`t01_*.fail<N>.txt`. A `:8100` host listener found, or any path by which the engine
container can reach a Docker socket, is a **stop-the-ticket event**: freeze (`make down`),
record verbatim, escalate — never mitigate silently.

**Estimated sessions:** 1.


---

## File: `workflows/tickets/candidates/T0.2-queue-wired.md`

# Ticket T0.2 — Serialized queue wired (engine SQLite FIFO → sidecar execution → run capture)

**Goal:** DEPLOY-v2 Pass-0 item T0.2: job JSON → `workflow-engine` SQLite FIFO queue
(D-03/D-04: no broker daemon; CPU class) → execution **only through the D-16 sidecar**
(worker seam calls the §6.2b four-op API; engine never sees a socket) → log/run capture,
client via `he` HTTP only. State machines per TD §8.2 with §8.4b per-table write owners;
write-ahead ordering per D-05 (state row fsynced before effect). Executor for this ticket
= allow-listed `busybox`-class no-op digest (T0.1 smoke image); the real solver arrives in
T0.3 behind the same seam.

**Done-check (≤3 lines; cold session with repo + running stack from T0.1):**
```
bash workflows/t02_queue_matrix.sh   # exit 0: 3 no-op jobs FIFO; kill -9 engine mid-run and mid-write => zero job loss, resume correct
docker exec he-toolstack-workflow-engine-1 sh -c 'test ! -e /var/run/docker.sock && echo NOSOCK'  # NOSOCK
ss -ltn | grep -c ':8100'            # 0 (still zero host publication after wiring)
```

**Preconditions:** Pass-C **C1** green; T0.1 green (stack up, sidecar functional, 201 stub
to replace with real enqueue). C2 green recommended (PD queue-behavior logs as
comparator), not blocking. GPU class: `gpu` profile stays inert; any GPU-class submission
must refuse/never-leave-queued (FR-18).

**Steps:**
1. Engine service reads job JSON from the toolserver's `submissions` inbox (toolserver =
   INSERT only, §7.5/§8.4b) and owns queue rows; SQLite WAL on the D-01 bind path (no
   named volume). ✓ two-process ownership probe: toolserver never UPDATEs queue table;
   engine never INSERTs submissions.
2. FIFO dequeue + spawn via sidecar `create_run` ONLY (digest from allow-list,
   `network:"none"`, run-dir bind under heat-data prefix, labels `he-stack=1/he-run/
   he-job-id`, cpuset/mem_limit CPU-class); poll `status`, tail `logs`, exit code recorded.
   ✓ one no-op job: submitted via `POST /v1/jobs` → `201 {job_id, queue_pos}` → run dir
   with log capture → state `succeeded`; sidecar audit rows == engine API calls.
3. Write-ahead law (D-05/§8.2): every transition row fsynced **before** the effect it
   authorizes; ledger append by engine only. ✓ kill -9 engine at each of {before-spawn,
   after-spawn-before-exit, after-exit-before-report} → restart → no lost/duplicated job,
   orphan class-J handled by six-step/step-5 janitor path, `make down` remains the only
   stop path.
4. Crash-boundary subset: kill harness for artifact↔state↔ledger windows on fake steps
   (T-07 partial; physics windows complete in T0.3/T0.4). ✓ each window: restart →
   reconciliation → no double-run (no second sidecar create for same job).
5. Concurrency legs (T-23 a–d): N≥4 distinct-key POSTs → N queue rows exactly; same
   `Idempotency-Key` raced 4× → one row, dedup at consume; kill between submission-insert
   and consume → after restart the row is consumed exactly once; two engines forbidden
   (single-writer flock on DB file, second instance refuses to start). ✓
   `t02_queue_matrix.sh` output committed.
6. GPU-class refusal: submit with `class:"gpu"` → `409`/never-dequeued per flag-off
   contract; audit shows no `create_run`. ✓ verbatim refusal committed.
7. Stop cleanly with `make down` (six-step §6.10/D9). ✓ step-6 zero `he-stack=1`.

**Evidence to commit:** `he/engine/*` (queue, worker seam module), `tests/t02/*`;
`workflows/t02_queue_matrix_output.txt` (kill matrix + T-23 legs);
`workflows/t02_gpu_refusal.txt`; `workflows/t02_audit_count.txt` (calls == audit rows);
ledger rows (engine-appended, `ref:` where design decisions taken).

**T-tests exercised:** **T-05** substantially (queue persistence + kill -9 engine matrix;
host-reboot leg stays in T0.6), **T-23** substantially (a–d on the real inbox/consume
path), **T-07** partially (artifact↔state↔ledger crash windows on no-op steps), **T-06**
partially (flag-off GPU refusal; VRAM floor math out of M0), **T-14** partially (worker
seam exists and is the single execution path), **T-01** partially (loop exists except real
physics). Not exercised: T-03/T-04 (T0.3–T0.4), T-02/T-08-contract-full/T-20/T-21 (T0.5).

**Failure recording (write-ahead):** `FAILURE T0.2 <what> <observed>` appended to this
ticket + ledger row **before** any re-attempt; failing harness output kept as
`t02_*.fail<N>.txt`. Any discovered path where the engine reaches Docker other than the
sidecar API, or a lost/duplicated job after clean restart, is a stop-the-ticket event
(`make down`, verbatim capture, escalate).

**Estimated sessions:** 1.


---

## File: `workflows/tickets/candidates/T0.3-tasmet-trivial-solve.md`

# Ticket T0.3 — TaSMET trivial solve through the queue (minimal closed sCO2 loop, CPU class)

**Goal:** DEPLOY-v2 Pass-0 item T0.3 (largest M0 risk — sized first): minimal **closed
sCO2 loop** config (DESIGN-v2 §5) run by the TaSMET fork on the `ta-solver-runtime`
image, digest-pinned, executed as a class-J container **through the D-16 sidecar via the
queue** (TD supersedes the older "host worker" phrasing — spawn path is the sidecar,
same as T0.2). Fork source pin + patches 0001–0003 recorded under `stacks/` at repo
root (exact path DEPLOY-v2 names). CPU wheels only; no GPU.

**Done-check (≤3 lines; cold session with stack up + this ticket + run dir):**
```
bash workflows/t03_solve.sh            # submits closed-loop config via POST /v1/jobs, polls to succeeded, exit 0
ls runs/<job>/ | grep -c 'solution\|entropy' # >=2: solution files + entropy-residual readout present
grep -c 'sha256:' stacks/tasmet/PIN.md       # >=1, value == docker images --digests row for ta-solver-runtime
```

**Preconditions:** Pass-C **C1** green (seed paths) and **C2** green (PD-toolstack run
scripts/logs archived — the E1/E2b regression baselines and solver invocation patterns are
this ticket's working reference; C2's `verify-archive` manifest proves they're on disk).
T0.2 green (queue + sidecar execution path under test). Operator ruling **R-05/D-06**
already recorded (T0.1 precondition; re-checked). Host pin: fork source + patches
0001–0003 present at the location `infra/ENVIRONMENT.md` names for build inputs.

**Steps:**
1. Pin: record fork origin commit, patches 0001–0003 (replayed, `git apply --check`
   clean), and the `ta-solver-runtime` image digest in `stacks/tasmet/PIN.md`; append the
   digest to `deploy/allowed_images.txt` (sidecar allow-list gains the real solver). ✓
   `git apply --check` exit 0 for all three patches; digest file committed.
2. Build the minimal closed sCO2 loop config under `stacks/tasmet/m0_closed_loop/`
   (components + topology only — smallest loop that closes mass/energy; all physics
   decisions carry fetched-source `ref:` in the ledger row before the step is called
   done, internet-first rule M0e). ✓ config parses in-container (`--check` mode) exit 0.
3. Register solver profile: `run.sh` entrypoint (config path + run-dir bind semantics),
   CPU limits via sidecar request fields (cpuset/mem_limit), `network:"none"`, run-dir RW
   bind under the heat-data prefix. ✓ sidecar `create_run` 201 for a `--check`-only job;
   no-socket-engine assertion still `NOSOCK`.
4. Solve via the queue: `POST /v1/jobs` (solver class, CPU) → engine spawns → poll
   `status` → capture `logs`. ✓ terminal state `succeeded`; sidecar audit row == the one
   create_run; zero containers left (reap per class-J lifecycle).
5. Outputs: run dir carries solution files + **entropy-residual readout** (the §5 slice
   requirement); digests of inputs + outputs recorded in run state per §8.2. ✓ done-check
   line 2 counts them; residual value is finite + within the config's stated tolerance
   table (record the number; verdict semantics are T0.4's job, not this ticket's).
6. Timing evidence: wall time 3 runs at CPU limits, median + spread into
   `workflows/t03_cpu_wall.md`, labeled "M0 canonical, CPU class" — feeds the §5 CPU-only
   acceptance re-baseline; makes no GPU claim (D-09 ON HOLD). ✓ file committed.
7. `make down` (six-step §6.10) with the solved run complete; restart `make up`; engine
   reconciliation re-reads the run's final state without re-running. ✓ step-6 zero; no
   duplicate `create_run` in audit after restart.

**Evidence to commit:** `stacks/tasmet/PIN.md` + `m0_closed_loop/` config;
`deploy/allowed_images.txt` diff; run dir pointer + `run_state` snapshot under
`workflows/t03_run/` (solution files themselves live in heat-data — pointer + digests
committed); entropy-residual readout copy; `workflows/t03_cpu_wall.md`; solve transcript
`workflows/t03_solve_transcript.txt`; ledger row(s) with `ref:` fields.

**T-tests exercised:** **T-01** partially (real physics leg of the vertical slice — the
e2e close-out incl. gate verdict + registry is T0.4/T0.5/T0.6), **T-04** partially
(digest checks + frozen config established for the bit-identity A/B harness; frozen-grid
harness completes at M1 with E2b), **T-09** partially (solver smoke leg: run succeeds,
deterministic on rerun within recorded spread), **T-16** partially (real solver digest in
allow-list), **T-05** partially (solve survives engine restart reconciliation without
re-run). Not exercised: T-02/T-03 (T0.4/T0.5), T-06/T-07 full, T-20/T-21.

**Failure recording (write-ahead):** `FAILURE T0.3 <what> <observed>` here + ledger row
before any re-attempt; solver stderr/log tail kept as `t03_*.fail<N>.log`; a non-converged
or non-finite-residual solve is recorded **with the run dir pointer** (the failure is
evidence, not something to delete and retry silently). If patches fail to replay or the
digest is unbuildable from `stacks/` inputs, stop-the-ticket: the pin is wrong, record
verbatim and escalate (this is the M0 risk item; a wrong pin poisons T-04 downstream).
Wall-time blowout = record-and-escalate to the §5 CPU-only re-baseline, not a re-run
until green.

**Estimated sessions:** 1–2 (largest M0 risk — sized first per DEPLOY-v2; the 2nd session
is budgeted for pin/convergence iteration, not scope).


---

## File: `workflows/tickets/candidates/T0.4-physics-gate.md`

# Ticket T0.4 — Physics-gate carry-forward + M0 verdict (5 checks, fail-closed)

**Goal:** DEPLOY-v2 Pass-0 item T0.4: physics-gate carried from PD-toolstack code
(`scripts/verify_e1.py`, `scripts/verify_e2b.py` + D2 gate methodology, archived by C2),
shipped **as-is** per D-06 ("scripts unchanged; wrapper adds no verdict logic") — wrapper
shape per the recorded R-05/D-06 ruling. E1/E2b regressions become unit tests in-repo.
Gate runs as `python -m gates <run-dir>` inside the physics-owning tool image
(`ta-solver-runtime`, same numeric stack — FR-22) as a one-shot class-J spawn **through
the sidecar** (physics-gate is NOT a compose service — TD §6.10 canonical five; DEPLOY-v2
bullet is older). Both entry paths (engine runner step, thin endpoint) execute the
**identical command** and produce byte-identical reports (T-03). This ticket closes M0c:
verdict JSON with all 5 checks computed on the T0.3 M0 run.

**Done-check (≤3 lines; cold session with stack up + T0.3 run dir present):**
```
make gate RUN=<t03_job_id>   # exit 0; gate_report.json with checks[5] all computed (verdict may be warn, not error)
make test-gate               # exit 0: E1/E2b regression unit tests green, N/N
diff <(engine-path report) <(endpoint-path report)   # byte-identical reports, two entry paths
```

**Preconditions:** Pass-C **C1 + C2** green (C2 is hard here: the gate scripts and D2
tolerance-table evidence ARE the archived PD-toolstack assets C2 puts on disk with a
verified manifest). T0.3 green (a real M0 run dir to gate). R-05/D-06 wrapper-shape ruling
recorded (endpoint shape below must match it verbatim). GPU/CPU: unchanged posture,
CPU-only.

**Steps:**
1. Vendor gate scripts into `gates/` (byte-for-byte copy of the C2-archived
   `verify_e1.py`/`verify_e2b.py` + D2 methodology files; provenance header comments
   record source path + digest from the C2 manifest). ✓ `sha256` of each vendored file ==
   C2 manifest value (scripts unchanged — D-06).
2. Bake/bind into the solver image path so `python -m gates <run-dir>` runs in-container
   on the same numeric stack; tolerance tables dataset-derived from D2 evidence [E],
   committed under `gates/tolerances/`. ✓ in-container `--list-checks` prints exactly the
   5 check IDs.
3. Engine runner step `gate` (post-solve, fail-closed): engine spawns the gate one-shot
   via sidecar; report absent or script crash ⇒ verdict `error` ⇒ registry refuses
   `succeeded`. ✓ kill-the-gate probe: spawned gate container SIGKILLed → run terminal
   state cannot be `succeeded`, `gate_verdict=error` in state row.
4. Thin endpoint `POST /gate/run` per the R-05/D-06 ruling execs the identical command;
   response = pointer to `gate_report.json` in heat-data (not inline bytes, §7.4). ✓
   two-path diff of reports byte-identical (done-check line 3); envelope errors per §7.3.
5. Negative test (carried D2 discipline): corruption injection on a copy of the M0 run
   (perturb one solution value past tolerance) → gate verdict correctly fails the affected
   check, overall not pass. ✓ negative-case report committed; check that failed is the
   named one.
6. Regression units: E1 + E2b fixtures from C2 run in-repo as unit tests against vendored
   scripts (frozen inputs from the archive). ✓ `make test-gate` N/N green; fixtures carry
   source-archive digests.
7. Tolerance-table integrity: any future change requires an ADR row — encode as CI/gate
   test that edits under `gates/tolerances/` without an ADR reference fail. ✓ deliberate
   no-ADR edit in a scratch branch fails the check (output committed).

**Evidence to commit:** `gates/*` + `gates/tolerances/*`; `workflows/t04_gate_report_m0.json`
(5 checks computed); `workflows/t04_negative.txt` (corruption case);
`workflows/t04_two_path_diff.txt` (byte-identical); `tests/gate/*` (E1/E2b regression
units); tolerance-guard CI output; ledger row with `ref:` to D-06/R-05 ruling.

**T-tests exercised:** **T-03** substantially (gate suite incl. the carried corruption
negative test, both entry paths byte-identical), **T-01** partially (M0c leg of the
vertical slice closes), **T-08** partially (`POST /gate/run` contract fixtures per the
R-05 shape; full trio+suite is T0.5), **T-04** partially (gate digests-covered field wired
for the A/B harness). Not exercised: T-02/T-05/T-06/T-07/T-09–T-24.

**Failure recording (write-ahead):** `FAILURE T0.4 <what> <observed>` here + ledger row
before re-attempt; failing reports as `t04_*.fail<N>.json`. A gate that returns `pass` on
the corruption-injected copy is a **stop-the-ticket safety event** (fail-open gate
= M0 cannot freeze): `make down`, verbatim capture, escalate — the whole point of the
carried methodology is the negative test catching corruption. Vendored-script drift from
C2 digests = stop-the-ticket too (D-06 "unchanged" is the design).

**Estimated sessions:** 1.


---

## File: `workflows/tickets/candidates/T0.5-registry-state-cold-session.md`

# Ticket T0.5 — Registry + state-machine files + claim protocol + cold-session test

**Goal:** DEPLOY-v2 Pass-0 item T0.5: `registry/` JSONL + `workflows/` state files
(`state.json` cursor, per-ticket state, handoff-note template) + ledger with `ref:` field
enforced (FR-33; missing ref → append refused, machine-checked). Plus the §8.8 r3 flock
claim protocol realized for these files (`he ticket claim`: `flock(LOCK_EX|LOCK_NB)` on
`workflows/tickets/.locks/<ticket>.lock` → classify fresh/live/stale/done **under the held
lock** → write→fsync `claimed:` line → ledger claim event → release on exit; stale =
heartbeat older than `HE_CLAIM_STALE_MIN` [P 30 min] **and** kernel-released lock; loser
never reads the ticket). Closes M0d: a fresh session answers "what is done / what's next"
from `workflows/` **only** — verified by a `delegate_task` child with no other context.

**Done-check (≤3 lines; cold session reading ONLY `workflows/` + this repo checkout):**
```
make test-state                 # exit 0: ledger refuses ref-less append; state.json cursor advances only on committed checkpoint
python3 workflows/t05_claim_race.py   # >=2 procs race 1 fresh ticket, 10x: exactly 1 claim, kill -9 mid-claim recovers, hung holder NOT superseded
bash workflows/t05_cold_session.sh    # zero-context delegate's done/next answer == t05_expected.txt (diff empty)
```

**Preconditions:** Pass-C **C1** green (the existing `workflows/tickets/` + `ledger.md`
convention files are the schema this ticket formalizes — read them first; do not fork a
second convention). T0.2 green (queue state rows exist to mirror into run-state files;
ledger writer = engine, sole-appender rule §8.4b). T0.4 green not required; cold-session
state can be exercised on T0.2 no-op runs.

**Steps:**
1. `registry/` JSONL: one append-only file; entry per run `{job_id, run_dir, state,
   gate_verdict, digests, ledger_ref}`; registry write refuses `succeeded` when
   `gate_report.json` absent/`error` (constraint at write, not convention — TD §6.3). ✓
   probe: hand-append `succeeded` without a gate pointer → refused + logged.
2. `workflows/state.json` cursor + per-run state files + `handoff-note-template.md`
   (fields: done / in-flight / next / known-failures / resume-point), all matching the
   existing repo convention (`ledger.md` columns, ticket front-matter) — extend, don't
   reinvent. ✓ existing `ledger.md` rows still parse under the new schema (migration
   check in `make test-state`).
3. Ledger `ref:` enforcement: engine writer rejects appends missing `ref:` (or `ref:`
   pointing at nothing resolvable); internet-first decision rows carry a fetched-source
   ref. ✓ harness kills a ref-less append → rejected with machine-readable error.
4. Claim protocol implementation + race harness `t05_claim_race.py` (T-20/T-21): ≥2
   independent OS processes, independent `flock()` calls (harness must not serialize);
   scenarios: fresh race (one winner, losers bounded-wait → `already_claimed`, never read
   the ticket), claimant `kill -9` mid-critical-section (kernel releases lock → fresh
   claimant completes coherently), stale-supersede (heartbeat-stale + lock-free → exactly
   one superseder proceeds, ledger notes `superseded:`), hung-but-alive holder NOT
   supersedeable. 10× each, zero double-claims. ✓ harness output committed.
5. Ticket-file writer audit hook (T-24 class): any write path to `workflows/tickets/*.md`
   that bypasses the claim lock is flagged by `make test-state`'s static check + the live
   demo from step 4. ✓ audit output committed.
6. Cold-session test (M0d, hard requirement): state left in a deliberate mixed condition
   (runs succeeded/failed, one ticket claimed-stale, next = named ticket);
   `t05_cold_session.sh` spawns a `delegate_task` child whose ONLY inputs are
   `workflows/` + run dirs (script asserts no conversation context, no env, no memory —
   zero conversation context, constraint honored), asks "what is done / what's next",
   diffs against `t05_expected.txt`. ✓ diff empty; child transcript committed.

**Evidence to commit:** `registry/` schema + first real entries; `workflows/state.json`,
`workflows/handoff-note-template.md`; `he/cli/ticket.py` (flock claim);
`workflows/t05_claim_race_output.txt`; `workflows/t05_cold_session_transcript.txt` +
`t05_expected.txt`; ref-rejection harness log; ledger migration check output; ledger row.

**T-tests exercised:** **T-02** substantially (the cold-session resume harness IS done-
check line 3 — M0d; re-run under full load in T0.6), **T-20** substantially (claim mutual
exclusion incl. claimant-crash), **T-21** substantially (stale-supersede + expiry + hung-
holder assertion), **T-10** partially (registry lifecycle rows, ledger↔registry links;
legacy-D2 digest probe deferred M1), **T-12** partially (done-check attestation discipline
auditable via state files), **T-24** partially (writer-audit leg; complements T-12, does
not replace it). Not exercised: T-01/T-03/T-04/T-05/T-06/T-07/T-08/T-09/T-13–T-19/T-22/
T-23.

**Failure recording (write-ahead):** `FAILURE T0.5 <what> <observed>` here + ledger row
before re-attempt. A cold-session MISMATCH is never cosmetic: commit the delegate's exact
answer + a tarball of the `workflows/` snapshot it saw under `evidence/` — the state-law
defect must be reproducible by the next session without the author present. Any
double-claim in the race harness = stop-the-ticket (state law broken at the root).

**Estimated sessions:** 1.


---

## File: `workflows/tickets/candidates/T0.6-m0-acceptance.md`

# Ticket T0.6 — M0 acceptance run (`make verify` chains M0a–M0e; full-stack drills; evidence + ledger close)

**Goal:** DEPLOY-v2 Pass-0 item T0.6 / DESIGN-v2 §5: one cold `make verify` run that
chains **M0a** (compose up all-healthy, single project, down → zero containers), **M0b**
(one real solve job through the serialized queue, HTTP only, CPU class), **M0c**
(physics-gate verdict JSON, 5 checks computed on the M0 run), **M0d** (registry + ledger
rows; fresh-session cold answer from `workflows/` only), **M0e** (internet-first exercised:
≥1 design decision in the run's ledger rows cites a fetched source). Completes the
full-lifecycle legs the build tickets deferred: T-13 full incl. `make down` **during an
active job**, T-15 six-leg isolation matrix, T-16 MANIFEST CI, T-19 daemon-restart
reconciliation (RC-3). No new scope — only chaining, drilling, and closing.

**Done-check (≤3 lines; cold session with repo + host access, nothing else carried):**
```
make verify                 # exit 0: M0a→M0b→M0c→M0d→M0e green in one chain, evidence/ artifacts written
bash workflows/t06_drills.sh  # T-13 (down during active job -> interrupted rows), T-15 six legs, T-16 CI, T-19 RC-3, host-reboot leg of T-05
git log --oneline --  evidence/m0/ | head -1   # evidence dir committed; ledger final row: M0 CLOSED
```

**Preconditions:** Pass-C **C1–C5** green (acceptance runs on the cleaned host state C3–C5
establish; C5's cron must be verified not to touch `he-toolstack` labeled paths or heat-
data during this run). T0.1–T0.5 **all green** — this ticket is strictly sequential.
R-05/D-06 ruling still on record (verify asserts the wrapper shape matches it). GPU:
`gpu` profile inert throughout; T-06 floor math explicitly out of scope (C6 is M2).

**Steps:**
1. `make verify` recipe: ordered chain M0a–M0e, each leg = the owning ticket's done-check
   re-run fresh (no state carried between legs; a leg failure aborts with that leg's
   evidence committed). ✓ chain green from a cold `make down` start.
2. M0a full lifecycle (T-13 full): cold bring-up; then submit a real solve job and run
   `make down` **during** it → six-step sequence: engine stops claiming, kills class-J via
   sidecar `kill`, records `interrupted` write-ahead, compose down, janitor sweep, step-6
   `docker ps -a --filter label=he-stack=1 -q | wc -l` == 0 (classes C∪J; class X host
   timer excluded) **and** `docker compose ps -a` empty (bare `compose down` alone is
   never an acceptance target). ✓ interrupted rows in registry + ledger reference the
   killed run; zero orphans. gitleaks CI leg green.
3. T-15 six-leg isolation matrix executed per the REQ row from **inside** the named source
   containers (host-side curl never counts, F1): agent-member reach 200; default-bridge
   peer gaierror/refused; compose-net non-member same; host-local refused; LAN side
   refused; fresh-bridge every-gateway refused. `he doctor` re-runs legs 1–3 after agent
   recreation. ✓ six-leg transcript committed; NFR-07 claim rests on this, not on T0.1's
   partial.
4. T-16 MANIFEST CI leg + digest drift check: every image referenced by compose or
   allow-list resolves to the MANIFEST digest; CI check fails on drift. ✓ deliberate
   tag-bump scratch attempt fails CI (output committed).
5. T-19 RC-3 drill: `systemctl restart docker` (daemon) mid-job → boot reconciliation
   re-adopts/re-queues per §8.6, ledger gapless (interrupted-or-completed, never blank).
   Plus the T-05 host-reboot leg once (WSL `docker restart` cadence documented first —
   host reboot is operator-scheduled; if scheduling is impossible within the session,
   record `DEFERRED-DRILL` with the exact command sequence, NOT a silent pass). ✓ drill
   log committed.
6. M0d re-run at full fidelity: cold-session delegate after ALL the above chaos (mixed
   succeeded/interrupted/error history in `workflows/`), answer still correct. ✓ diff
   empty against regenerated expected file.
7. Close: evidence/ tree (one file per leg, named `m0a_*…m0e_*`), ledger closing row
   `M0 CLOSED` with ref fields to every leg's evidence, handoff note per T0.5 template. ✓
   done-check line 3.

**Evidence to commit:** `evidence/m0/` full tree (per-leg artifacts incl. six-leg T-15
transcript, mid-job `make down` six-step capture, RC-3 drill log, MANIFEST CI outputs);
`Makefile` verify recipe; cold-session transcript at full fidelity; ledger rows through
`M0 CLOSED`; handoff note.

**T-tests exercised:** **T-01** fully (the vertical slice end-to-end in one verify chain),
**T-13** fully (cold bring-up + six-step zero-orphan incl. class-J + down-during-active-job
+ gitleaks), **T-15** fully (six legs from inside), **T-16** fully (MANIFEST CI leg
completes), **T-19** fully (RC-3), **T-05** fully (host-reboot leg completes the matrix),
**T-02** fully (cold session at full fidelity), **T-12** partially (cleanup pass §6 of the
DESIGN-v2 checklist is part of acceptance). Stays unexercised at M0 (by design): T-04
frozen-grid A/B (M1), T-06 VRAM math (M2/C6), T-09 per-tool full matrix (M1), T-11/T-18
backup drills (drill-specified, never implied-pass), T-10 legacy-D2 probe, T-22 version
export, T-24 live-demo leg rides on T-20 harness already green.

**Failure recording (write-ahead):** `FAILURE T0.6 <leg> <observed>` here + ledger row
before re-attempt; the verify chain commits failing-leg evidence automatically on abort
(by design of step 1 — aborts are also evidence). A step-6 non-zero orphan count, any T-15
leg returning anything but its expected result, or a blank/lost ledger gap under RC-3 is
**stop-the-ticket**: M0 cannot be declared CLOSED; escalate with verbatim captures. A
drill that cannot be executed in-session is recorded `DEFERRED-DRILL`, never assumed.

**Estimated sessions:** 1.


---
*End of DP0 package. Nothing in this file is a claim of execution: every T-id cited is specified-only. Pass-C tickets C1–C5 and M0 tickets T0.1–T0.6 are original artifacts of the five-prompt review series (not reconstructions). Adviser decision requested: may deployment planning (Pass C) begin, and under which register items must close first.*
