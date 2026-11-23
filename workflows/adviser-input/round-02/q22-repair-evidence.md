# R2a evidence — Q22 row repair (2026-11-23)

## Damage
QA-REPORT line 38 (Q22) ends mid-sentence at "crash matrix) are" — 248 bytes on
main @ 4b0838c. Present in every commit touching the file from the r3 filing through
r13 (68626eb): authoring-time truncation, not transport damage. Both advisers flagged
this (ChatGPT finding 3; Grok verified it from live GitHub — CD-007).

## Repair sources (in-repo, verifiable)
1. Intact predecessor row at 3feb698 (r2-era, 310 bytes, ends complete):
   tail = "defined in REQ §4 **and** rowed in the §5 matrix | **PASS** | defined +
   matrixed; network reachability proof remains T-17 (from-container probe) |"
2. Harness predicate gates_v13.py line 146: Q22 passes iff T-21/T-22/T-23 appear in
   the REQ §5 matrix AND rows "| T-21 |"/"| T-22 |"/"| T-23 |" appear in REQ §4.

## Reconstruction rule
Keep the truncated r3 header verbatim (through "...crash matrix) are"), append the
r2-era completion (the sentence is the same construction "are defined in REQ §4 and
rowed in the §5 matrix"), keep the PASS + evidence tail, and add a bracketed
DP-R2a repair annotation in-place so the reconstruction is self-documenting.

## Verification (2026-11-23, this branch)
- Prefix check: main row is NOT a byte-prefix of the r2 row (r3 reworded T-20/T-21
  after the O_EXCL→flock replacement) — so only the sentence construction and tail
  are reused, never the r2 T-20 wording. Confirmed by diff.
- Harness re-run on this branch after repair: 27 PASS / 0 FAIL
  (gate-run-postfix.txt, this directory). Pre-repair baseline on main: 27/0 —
  the truncation was invisible to the predicate (header alone satisfied it); the
  repair makes the TEXT verifiable without changing any gate result.
- r16-era header versions unchanged (REQ v1.10 / TD v1.13 / ADR v1.11) — Q16 pins
  them; this errata deliberately avoids a version bump, errata annotated in-row.
