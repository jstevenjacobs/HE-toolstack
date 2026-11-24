# Round-04 — Final synthesis: R-02, R-03, R-04a, R-12 (Hermes, after council analysis)

Inputs: Hermes suggestions (`hermes-suggestions-r4.md`), Grok reply (`reply-grok-r4.md`),
ChatGPT reply (`reply-chatgpt-r4.md`). Every checkable adviser claim about OUR docs was
re-verified against the files at `79beb57` before acceptance (L4); results noted inline.

---

## R-03 — FINAL: three-class execution split + unified witnessing protocol (adopt council)

**Split (final):**
- **(a) Agent-executed, operator witnesses:** T-01, T-02, T-07, T-12, T-15, T-17, T-20, T-21, T-23, T-24.
- **(b) Operator-executed:** T-19 (dockerd restart — Grok+ChatGPT both flagged; my draft left it in (a): WRONG), all host/WSL-restart legs (verified in REQ: T-05 queue-restart and T-13 inbox-restart rows include restart-WSL/WSL-shutdown legs; agent cannot execute-then-witness its own resurrection), T-11/T-18 (destructive-adjacent, OneDrive root), first `make up`.
- **(c) Scope-reduced:** T-06 flag-off-refusal leg only at M0 (both advisers ACCEPT; full VRAM/floor-math to C6/GPU-class per OQ-2).

**Witnessing protocol — adopt the union of ChatGPT's 5 rules + Grok's per-leg oracles:**
1. **Pre-register** scenario, inputs, pass predicate, failure conditions, cleanup — in the ticket file, pinned SHA, BEFORE execution.
2. **Independent read-only verifier** — must not import the implementation's success predicate; checks externally observable state only. For T-20/T-21: operator inspects `/proc/<pid>/fd` / `lslocks` before accepting PASS (Grok). For T-07/T-23: operator-side sqlite3 integrity + re-hash of digests (Grok); complete enumerated crash-point list + raw pre/post snapshots (ChatGPT). T-02: a genuinely fresh session executes; the scenario author cannot grade its own recovery; recovery must succeed with zero conversation context (M0 T0.5 precedent).
3. **Raw evidence** to `workflows/evidence/T-<id>/` (transcripts, snapshots, PIDs, digests) — never a bare PASS line.
4. **Witness row** per test: who/when/commit/artifact path/deviations.
5. **PASS/FAIL/BLOCKED only** — missing evidence or verifier error is never PASS (ChatGPT).
6. Highest-risk legs (T-01, T-07, T-19, T-20, T-23): operator reads the verifier's inputs + acceptance logic before trusting results (ChatGPT).

**Register framing (Grok Q5, ACCEPT):** the matrix is not one Hard gate — contract/docs legs
(T-08, T-12, T-24) execute and claim EARLY; acceptance-question is "which legs green before
which claim," not "everything before anything." Annotated in register.

## R-02 — FINAL: council-minimal claim scheme (both advisers REVISED my 3-humans draft; they concur with each other)

Verified: **M1–M9** (9 rows; register said M1–M10 — erratum applied). Scheme:
- **Owner row:** you — residual-risk acceptance + operator decisions + sign §9. Not also the sole engineering/ops reviewer (ChatGPT).
- **Engineering walker:** M1–M2, M4, M6, M8–M9 + §9 engineering row. May be one person, must not be the diagram-writing session; recorded with date+SHA.
- **Ops reviewer:** M3, M5, M7 + §9 ops row. **Must be a person distinct from the engineering walker** (Grok: M5 shutdown-choreography and M7 backup are the false-confidence rows). Council members are candidate ops reviewers on request.
- **r12 author self-walk = pre-fill only, zero sign-off credit** (both advisers; the doc says so itself).
- Errata applied: T-11 does NOT close diagram rows (different claims); sign-offs live DR §2b + §9, not QA §5.
- **Honest caveat:** engineering row may be you + dated walk, but §9 engineering+ops need TWO humans. If M0 must close before a second human exists, record an exception row — not a silent self-sign.

## R-04a — FINAL: ChatGPT's 4-step sequence with live disk data (my draft REVISED; live re-sample run 2026-11-24)

**My "formal acceptance can close OQ-9" option B is withdrawn** — ChatGPT correctly separates
what my draft collapsed:
1. **D-05 ≠ backup fallback** (fixed: local state dir + write-ahead ordering).
2. **OQ-9 Option A accepted = procedure chosen**, not copy proven.
3. **T-11 drill** proves restore works in a disposable copy — it does NOT prove the C3-staged copy is on OneDrive.
4. Only **read-back of the actual `pd-minio-orphan/` copy** (logged) or an **explicit exception-logged purge approval** authorizes C3's irreversible volume removal. Keep decision/test-evidence/destructive-authorization as three non-implicating states.

**Disk — RESOLVED WITH LIVE DATA [V 2026-11-24]:** `/dev/sdf` = 1007G total, 144G used,
**813G free, 16% used** — matches ADR-D-05/TD figures; the register's ~66 GB / 81.5% sample is
stale-or-wrong-volume (its [U] flag already said unreliable; ChatGPT right to distrust). No
warning threshold crossed. Standing policy stands as designed (TD §11.6: `DISK_WARN_PCT=80` /
`DISK_HARD_PCT=95` [proposal] — engine warn/refuse; ChatGPT right that policy, not my one-shot
re-sample, is the durable control). Re-measure + record (timestamp/device/%) immediately before
first `make up` AND before C3 volume removal.

**Milestone conflict — CONFIRMED [V]:** NFR-22 is **P0** (REQ) but T-11 is **M2 acceptance**
(TD §16 line ~1662). R-04 wants it at M0. DECIDE: move T-11/T-18 into M0-close (conservative;
recommended given C3 removal + P0) or record the deferral explicitly. Do not let it move silently.

## R-12 — FINAL: ChatGPT's class table governs; risk-tiers map as T1/T2/T3

Both advisers REVISE my tiering: **import-only is never sufficient for a trust-bearing script.**
- **T3 — behavioral/digest** (ChatGPT highest-risk 4): physics gates (need known-good fixture
  AND deliberately-corrupted fixture that MUST FAIL — a silently-passing gate is the platform's
  worst failure); resolve.py/MANIFEST (digest fixtures + mismatch/refusal cases); backup/restore
  (fixture backup→restore→integrity, via T-11, never a file-exists check); solver
  generators/CPU loop (frozen input → deck comparison via T-04 bit-identity path; benchmark
  tolerances where bit-identity is invalid).
- **T2 — fixture invocation:** containerized tools (image digest + minimal representative run —
  an image can boot while its capability is broken), path/manifest utilities (temp-dir fixtures).
- **T1 — import + deps + CLI help:** pure utilities only.
- **Inventory first** (both advisers; confirmed: TD §4 is a narrative retained-assets list, not a
  file inventory): enumerate exact Phase-1 script paths + owner + tier; an unenumerated script
  does NOT inherit "unchanged."

## Register/QA integrity fixes applied this pass [all DP-R4, original text preserved]

- QA report (3 sites): stale `.hermes-tmp/gates_v13.py` pointer → `scripts/qa/gates_v13.py` +
  reproducible-YES annotation (ChatGPT's doc-integrity finding; CONFIRMED — a reviewer following
  QA §5 would have looked for the wrong harness).
- R-02: M1–M10 → **M1–M9** ✓verified; T-11≠diagram-close.
- R-01: sign-off location DR §2b/§9, not QA §5 ✓verified.
- R-03: harness-scratch framing superseded by DP-R3c; zero-runtime-executed remains true.
- R-04: D-05≠backup-fallback; OQ-9-A = procedure not proof.
- R-09: stale status cross-ref noted.
- R-12: tiered acceptance + inventory-first.
- Gates re-run after edits: **27 PASS / 0 FAIL** ✓.
- Runbook R-9: ChatGPT's "R-1…R-9 in TD §11.8" claim did **not** reproduce (11.8 enumerates R-1…R-8;
  R-9 dockerd-restart drill exists in TD §11.8/§9.4 region; my R-01 annotation records the location
  as found, not as claimed — L4 discipline applies to adviser corrections too).

## The operator's decision list that survives this round

1. T-11/T-18 at M0 vs deferred-to-M2 exception (explicit, because P0 vs TD §16 conflict).
2. Who fills §9 engineering + ops rows (two humans, ops ≠ engineering walker).
3. The C3 read-back/purge-approval checkpoint (hard, before volume removal).
4. Whether council members may serve as the ops reviewer (they can, on your request).

Advisory only — HARD STOP §10 unchanged: nothing here authorizes execution.
