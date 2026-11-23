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
