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
