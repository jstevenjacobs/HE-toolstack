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
