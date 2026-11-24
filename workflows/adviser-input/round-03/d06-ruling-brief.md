# R2b — D-06 ruling brief (operator sign-off package)

**Prepared:** 2026-11-23 · DP round-03 · sources: ADR-D-06 + OQ-4 row (`docs/HE-TOOLSTACK-ADR.md` lines 176–189, 371), TD §6.3 (`docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md` lines 579–596), API table line 950, residual-risk R-05 — all read from `main` @ `9db2717` this turn.

## What is unruled (exact scope)

OQ-4 is halved: D-08 (SQLite colocation) was **ACCEPTED by operator ruling 2026-11-16**. The remaining half — **"physics-gate endpoint wrapper (D-06) … stays open for reviewer sign-off"** — is the last OQ blocking **M0 design freeze** (OQ-4 column: "M0 design freeze (D-06 half only)").

The ADR text is already written and stable; the operator is being asked to **rule on the shape as written**, not to redesign it.

## The shape on the table (from ADR-D-06 + TD §6.3, verbatim-grounded)

1. **Methodology is scripts, not a service.** Gate = committed scripts (`gates/*.py` in repo → baked/bound into images) + checklist + negative test — the piece proven end-to-end in attempt-1 D2 [E]. DESIGN-v2's "FastAPI entropy-residual verdicts" framing was retracted (C2).
2. **Primary execution path is the runner step**: `gate` runs `python -m gates <run-dir>` **inside the tool image that owns the physics** (same numeric stack → bit-identity, FR-22).
3. **`POST /gate/run` is a thin convenience wrapper** on toolserver: execs the **identical command** in a spawned container; **adds zero verdict logic**; loopback-only; T-03 requires both entry paths produce **byte-identical reports**.
4. **Fail-closed**: script crash → verdict `error` → run cannot succeed; report absent → registry refuses `succeeded` (enforced at registry write, not convention).
5. **Drift mitigation**: wrapper is 1:1 exec of repo scripts; revisit trigger = gate checks growing beyond scripts (multi-engine/cadence tiers).
6. **FR-20 enforcement point**: no `succeeded` status without a gate report.

## Why sign-off matters now

- R-05 (register) names this the open decision gating M0 build-start alongside D-16/D-17/D-19 — but D-06 is the **only one of those whose text is final**; it is purely a ruling.
- With R2c done (harness now in-repo at `scripts/qa/`), nothing else in the documentation package is undecided except this + the D-16/D-17/D-19 sign-offs (separate ADRs).

## Options for the operator

| Option | Ruling sentence | Consequence |
|---|---|---|
| **A (as-written accept)** — recommended | "D-06 Accepted as written, 2026-11-23; OQ-4 fully closed." | TD §6.3 + API row + T-03 freeze as written; M0 design freeze loses its last doc-side gate. Mirrors the D-08 precedent (status line rewritten by ruling date). |
| B — accept with amendment | Accept + tighten (e.g. pin the wrapper's spawn to the D-16 sidecar path explicitly in §6.3) | One TD sentence needed before freeze; small, but reopens §6.3 for a council pass. |
| C — reject wrapper | Endpoint dropped; runner-step-only gate | FR-20 enforcement still holds (registry write), but the convenience path and its T-03 byte-identity test are dropped; D-06 needs a rewrite. |

**Recommendation: A.** The shape has survived QA r13 Q-coverage, the architecture-review rounds 1–13 (wrapper listed as [P thin], no finding against it), and it is the minimum-surface option consistent with "no new services."

## What the assistant does on ruling

Append the operator ruling note to ADR-D-06's Status line (D-08 precedent format), mark OQ-4 CLOSED in the OQ table, update R-05, and record the ledger row. No other file changes.
