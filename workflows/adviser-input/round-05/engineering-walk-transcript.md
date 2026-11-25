# Engineering walk — owner transcript (interactive protocol v2)

**Date:** 2026-11-24 · **Pinned evidence tree:** `5a24b0c` (diagrams D1–D9 byte-identical
to `main` @ `79beb57`; verified pre-walk). **Predicates:** committed at `93d3cfc` BEFORE
any evidence was displayed (anti-goalpost rule). **Protocol:**
`workflows/adviser-prompts/round-05/engineering-walk-interactive.md`.
**Machine:** single human (owner) judging agent-located evidence pairs.
Head of branch carrying rulings: see ledger row DP-R5-walk.

Operator-side rows: M1, M2, M4, M6, M8, M9 (M3/M5/M7 belong to the council ops walk).

---

## M1 — spawn routing through sidecar only — **PASS**
- Q (§2b): every spawn/kill edge routes through spawn-sidecar (§6.2b 4 ops); no engine→socket edge; no reap op.
- Evidence pair: D1 line 249 `WE -. "4 ops: POST/GET /v1/runs…, POST runs/id kill" .-> SCc`; D3 lines 322–323 (engine "NO Docker socket — D-16", sidecar "sole /var/run/docker.sock holder"); D9 line 903 (`POST /v1/runs/id kill (engine has NO socket, D-16)`); TD §6.2b table = exactly 4 ops.
- Counter-example report: `reap` token → 0 hits anywhere; no fifth sidecar op; no non-sidecar spawn verb in any diagram block.
- Operator answer (verbatim): "Yes" → **PASS**.

## M2 — sole-holder + root-equivalent label — **NO → DEFECT STANDS**
- Evidence pairs: D4 line 343 carries sole-holder + "root-equivalent if compromised" ✅✅; D3 sole-holder ✅ but label lacks the root-equivalent caveat ❌; D2 (lines 262–293) contains **no sidecar node at all** ❌.
- Counter-example report: searched all blocks for the caveat label — present only in D4; D2 has no spawn-sidecar label.
- Agent attempted walk-back; operator overruled: "NO — DEFECT stands."
- **DEFECTS LOGGED (fix deferred to post-transcript commit):** (a) D2 missing spawn-sidecar node; (b) D3 sidecar label missing "root-equivalent if compromised" caveat. This row blocks §9 engineering-sign-off until the diagram fixes land and are re-walked (label-only fix, no re-judgment of semantics required).

## M4 — D3 network/storage inventory — **NO → defect in the §2b row (phantom inventory); D3 PASS under corrected predicate**
- Original row demanded `he-edge / he-agent / he-internal / /var/run/he-runs`. Repo-wide grep: `he-edge` and `/var/run/he-runs` exist ONLY in this §2b row; `git log -S` shows both introduced by `68626eb` (the r12 row-creation commit) — never in any architecture, ADR, requirement, or QA artifact. Documented run workspace is `heat-data/runs/<id>/work`.
- Operator ruling (condensed; full text in predicate-file addendum): defect is in the review row, not D3; do not modify D3 to satisfy an erroneous predicate. Erratum applied to §2b per D-08 pattern; gates 27/0 after erratum; commit `5a73f00`.
- D3 as depicted: he-internal edge (line 323), socket ownership, published ports 9000/9001 @127.0.0.1, binds incl. `heat-data/runs/<id>/work` — all documented; no legacy alt-architecture subgraph. **PASS (corrected predicate).**

## M6 — D5/D6 vs §8.1/§8.8 claim semantics — **YES, downgrade accepted — PASS as-is**
- Evidence pair: D5 line 1036 `open --> in_progress: flock acquired + claimed line under lock (§8.8)`; §8.8 steps 1/4/5–6 (flock is arbiter; kernel release on any exit incl. SIGKILL; supersede = acquire→re-verify→ledger note→write claim; "no rename acts as arbiter"). D6 lines 1068–1070 gate→ledger→MINIO PROMOTE, fail ⇒ no promotion.
- Counter-example report: `supersede` token absent from D5/D6 blocks; no promote-without-gate path; no work-before-lock edge.
- Agent flagged pre-registered FAIL leg (supersede has no diagram counterpart) as ambiguous → DEFECT-by-default; proposed downgrade: supersede is a claim-holder swap in the ledger, not a ticket-state transition; D5 caption's §8.8 pointer is the diagram-level counterpart.
- Operator answer (abridged; opening ruling verbatim): "YES — ACCEPT DOWNGRADE; PASS AS-IS. The D5 claim edge correctly represents the open → in_progress transition as occurring only after flock acquisition and claim recording under the lock. Supersede is not a ticket-state transition. The ticket remains in_progress…" — reasoning adopted in full. **PASS.**

## M8 — diagram node names == §6 component names — **YES, ACCEPT — PASS**
- Evidence pair: both-direction label extraction (script over D1–D9 blocks vs §6.1–6.9 headings). Every §6 component appears under its §6 name (toolserver, workflow-engine, spawn-sidecar, physics-gate, gpu-admission fn, minio, he client, backup steps in D8); every diagram node maps to a §6 component, documented infrastructure (host/plane groupings), external service (Ollama/sglang, both "NOT compute"), D-10 image names, or operational actor (GitHub, operator ssh :2222).
- Counter-example report: zero alias/drift pairs (no "scheduler"/"artifact-store"/"gatekeeper" phantoms); no node invents a component.
- Operator answer (abridged): "YES — ACCEPT. All §6 components are represented in at least one diagram under their documented component names… No component-name drift, undocumented aliases, or phantom components were identified in either direction. No remediation required." **PASS.**

## M9 — canonical health trio only — **YES — PASS**
- Evidence pair: canonical trio `/healthz` `/readyz` `/deps` in TD §7/§7.5 (e.g. `http://toolserver:8100/healthz`), REQ NFR-23, ADR D-15/D-16; QA gate Q28 asserts `/health` retired. D1–D9 blocks: **zero** health-endpoint tokens (no `/health`, no trio) — diagrams carry topology/lifecycle, health contract is prose-plane (§7) + host-side `make health`/`make down`.
- Counter-example report: exact token `/health` (word-boundary, excl. healthz) across TD+REQ+ADR+all blocks → 0 hits outside retirement statements. `make health` flagged as a make-target name, not an HTTP endpoint.
- Operator answer (verbatim): "YES — PASS".

---

## Row scorecard
| Row | Result |
|---|---|
| M1 | PASS |
| M2 | **DEFECT stands** — fixes committed (D2 sidecar subgraph, D3 caveat label, label-level); **re-walk owed** against fix commit; row blocks §9 sign-off until re-walked |
| M4 | PASS under operator-corrected predicate (§2b row erratum `5a73f00`, D-08 pattern) |
| M6 | PASS (downgrade accepted) |
| M8 | PASS |
| M9 | PASS |

## Spot-check phase — rules (executed below)
Operator picks **2 of the 6 rows**; verifies each quoted locator in the pinned tree
(`https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/5a24b0c…/<path>` — line
anchors above) and reports MATCH/MISMATCH. MISMATCH reopens that row. Then the operator
signs the transcript-approval line and this file is committed as the §9 engineering-walk
record (with M2's exception noted).

## Spot-check phase — COMPLETE
Operator picked rows **M2** and **M9**; verified both quote-locators against pinned tree
`5a24b0c` personally. Reported: M2 — MATCH (D2 contains no spawn-sidecar node; upheld
defect substantiated; D2 correction warranted). M9 — MATCH (canonical endpoints
/healthz, /readyz, /deps; exact /health references limited to retirement statements;
make health is a host-side probe, not an HTTP endpoint). No row reopened.

## Transcript approval (operator, verbatim)
> Transcript approval: I approve the recorded judgments subject to the separately
> committed, label-level M2/D3 diagram corrections and subsequent re-walk. This approval
> does not constitute approval of deployment readiness.

## M2 remediation (label-level, per approval condition)
Separate commit on `dp/round-05-signoff-scheme`: D2 gains `Spawn path (D-16, §6.2b)`
subgraph — `spawn-sidecar / sole docker.sock holder / root-equivalent if compromised`,
edges `runner ->(spawn/kill: 4-op HTTP (§6.2b)) sidecar` and
`sidecar ->(Docker API via sole socket) Execution plane`; D3 SCc label gains
`root-equivalent if compromised` (matching D4). No semantic/architecture change —
labels + edges only, exactly the two logged defects. Gates 27/0 after fix; 9 Mermaid
blocks intact. **M2 re-walk owed** against the new commit (label-level judgment: does
each fix carry the required claim — sole-holder + root-equiv in both diagrams).
