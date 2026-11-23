# Adviser prompt — R2a freeze-repair review (carry verbatim to Grok)

Repo: https://github.com/jstevenjacobs/HE-toolstack · **PR #13** (base `main`, head `4acfb7c29de5576fa52ec76b7f6c84782d873727`). You have live GitHub access — verify from the hosting service itself, not just raw files.

**Verify (you previously confirmed the Q22 truncation from live GitHub at main — CD-007 in round-1 log):**
1. Pre-repair baseline: at tag `dp-phase1-frozen` (main `4b0838c`), `docs/HE-TOOLSTACK-QA-REPORT.md` line 38 ends mid-sentence ("…crash matrix) are"). Confirm or refute from live GitHub.
2. Post-repair: on branch `dp/round-02-freeze` @ `4acfb7c`, the same line is complete, annotated `[DP-R2a …]`, and consistent with REQ §4 T-20…T-23 definitions + §5 matrix rows (check those two REQ tables too — raw: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/4acfb7c29de5576fa52ec76b7f6c84782d873727/docs/HE-TOOLSTACK-REQUIREMENTS.md`).
3. Reconstruction integrity: evidence file `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/4acfb7c29de5576fa52ec76b7f6c84782d873727/workflows/adviser-input/round-02/q22-repair-evidence.md` claims the r2-era row at commit `3feb698` was the completion source and that the r3 header was kept verbatim. Check `3feb698`'s QA file on GitHub; confirm the r2 row's tail matches what was appended, and that no r2-only claims (O_EXCL-era wording) leaked into the repaired row.
4. TD §8.8: SIGKILL/container-kill fd-close clause (CD-008 follow-up you raised) — is the committed wording fully faithful to the kernel semantics you cited? Any edge case worth a further half-line (e.g. fd leaked to a child process via fork+exec inheriting the fd)?
5. Gate logs: `gate-run-postfix.txt` in the same directory claims 27 PASS / 0 FAIL. The harness itself is NOT in the repo (known open item R-09) — state plainly whether you can or cannot verify the log without it, and do not treat absence as refutation.

**Reply format:** `APPROVE` / `APPROVE-WITH-CHANGES` / `REJECT` + numbered findings labeled blocker/major/minor, each citing the URL/commit you actually loaded. Silence = no-reply, never consent.
