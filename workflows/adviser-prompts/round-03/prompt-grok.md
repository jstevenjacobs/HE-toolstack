# Adviser prompt — PR #14 round-03 (Grok) — raw files pinned to `d5523d65ce04893c7897589a8b720b337325cd7e`

Repo: jstevenjacobs/HE-toolstack · PR #14 (`dp/round-03-harness`, base `main` @ `9db2717`).

Verify (raw pins):
1. **Harness port claim-completeness.** Fetch `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/d5523d65ce04893c7897589a8b720b337325cd7e/scripts/qa/gates_v13.py`. Confirm the docstring's claim: ONLY the `base=` docs path and the `git -C` path were made repo-relative — no gate logic altered vs the predicate expectations you verified in round 2 (Q22 = T-20..T-23 both in matrix and REQ rows; Q12 checks cited SHAs; Q13 OneDrive root). List any behavioral difference you find.
2. **Hardcode sweep.** Grep the file for absolute paths outside the `_root` derivation — should be zero.
3. **Self-verifiability.** From your side, clone the repo and run `python3 scripts/qa/gates_v13.py` (or reason precisely about what would fail without a clone); report whether the suite is now stranger-runnable. If you run it, paste the TOTAL line.
4. **Round-2 carry-over.** Does this close the CD-R2-013 verification limitation (gate results not independently reproducible) going forward? Historical round-2 logs remain recorded-not-reproduced; confirm that framing.
5. **D-06 brief quality** (advisory): `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/d5523d65ce04893c7897589a8b720b337325cd7e/workflows/adviser-input/round-03/d06-ruling-brief.md` — does it fairly represent ADR-D-06 / OQ-4 / TD §6.3 at the pinned SHA? Any mischaracterization of the as-written shape? (This is a ruling-prep check, not a request for you to make the ruling.)

Output: verdict + numbered findings with line anchors.
