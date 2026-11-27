# Round-07 — Council re-pin prompt: protocol rev-9 (re-pin-7 repair cycle)

Round: Round-07 (M0 interview protocol), eighth repair cycle. Targets: ChatGPT and Grok (voting members); Claude (advisor seat — runner scope). Your re-pin-7 replies are archived verbatim at the pin (links below). Re-pin-7 went 1/2 ACCEPT (Grok ACCEPT; ChatGPT ACCEPT-WITH-CHANGES 1 P0 + 3 P1; Claude ACCEPT-WITH-CHANGES 1 blocking + 4 non-blocking). Rev-9 is the targeted repair of exactly those items. Architecture untouched; §3.8 byte-identical to the slice you already accepted (row 20).

## Declared pin

`0d156d755f9f8f8d99df3088be49ec871b6ac120` (branch `dp/round-07-m0-interview`) — the last commit touching any reviewed file. Later commits `ca5583e`/`e10cb6c` touch only `scripts/qa/gen_claim_table_repin8.py` and the generated claim-table file under `workflows/adviser-prompts/`; `git diff 0d156d7 HEAD -- <reviewed paths>` is empty (verified).

## Raw sources at this exact pin

- Protocol **rev-9**: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/workflows/m0-interview-protocol.md
- Broker runner (rev-9): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/scripts/m0-broker-runner.py
- Broker setup script: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/scripts/m0-broker-setup.sh
- Credential-revocation script (byte-identical since re-pin-7; row 21): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/scripts/m0-broker-revoke-keys.sh
- Broker test suite (rev-9, executable evidence, read as text): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/scripts/qa/test_broker_p0.py
- Committed run artifact (suite log + header pinning the code commit it ran): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/scripts/qa/run-artifacts/rev9_test_atpin.log and https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/scripts/qa/run-artifacts/rev9_test_atpin.header
- Your re-pin-7 replies, archived verbatim:
  - ChatGPT: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/adviser-input/round-07/reply-chatgpt-protocol-repin7.md
  - Grok: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/adviser-input/round-07/reply-grok-protocol-repin7.md
  - Claude: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/adviser-input/round-07/reply-claude-protocol-repin7.md
- Ledger (row `DP-R7-rev9`): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/0d156d755f9f8f8d99df3088be49ec871b6ac120/workflows/ledger.md

## What rev-9 changed (mapped to your re-pin-7 inputs)

- **ChatGPT P0 (blocking) / Claude NB3 — post-spawn escape paths.** The entire post-`Popen` region is now guarded end-to-end: a `child_ran` flag set before the first post-spawn call; `exit_code` bound pre-try (no UnboundLocalError window); the TIMEOUT path sets the recorded error BEFORE kill/reap, and a kill/communicate failure is folded INTO that recorded error at the site (`cleanup failed (Type)`), so no exception can escape past the budget bump; the generic post-spawn handler additionally kills + reaps the child on any uncertain outcome. Proven by P0-17e (timeout whose `kill()` itself raises, in-process argv-scoped Popen trap — recorded TIMEOUT+cleanup-failure, `spawn_succeeded` true) and P0-17e2 (same signed command BUDGET-EXHAUSTED for a fresh id afterwards; no silent re-execution). Rows 1–7.
- **Claude blocking (and ChatGPT P1's sibling) — corrupt-state terminal refusals retyped to HOLD.** Corrupt durable usage and corrupt execution history no longer terminalize the pass: `BUDGET-STATE-CORRUPT` is now a HOLD — nothing is written (no disposition, no state file), the owning request is skipped, siblings run, and after the owner repairs the file the SAME request id executes (repair-then-rerun-same-ID legs P0-19a/b, P0-20d/e/e2). Rows 8–10.
- **ChatGPT P1-1 / Claude NB1 (OSError fail-closed)** — `Ledger.load` and `Ledger.pending` catch `OSError` (valid-JSON-non-object and unreadable files both yield the held-never-re-executed sentinel; exercised for real via chmod-000 as non-root); `verify_plan` catches `UnicodeDecodeError` (invalid-UTF-8 plan → UNVERIFIABLE → PENDING, P0-9e); `record_history_count` fail-closes on unreadable/non-object history files. P0-20g (non-object state) / P0-20h (unreadable state) prove the owning request holds while siblings still run. Rows 11–13.
- **ChatGPT P1 (also Claude NB2) (`digest_artifacts`)** — directory or unreadable artifact path yields `observed = f"UNREADABLE ({type(e).__name__})"`, never an uncaught OSError. Row 14.
- **ChatGPT P1-2 / Claude NB4 (claim hygiene)** — your required evidence form adopted as standing structure: the suite result is now backed by a run log COMMITTED IN THE REPO (`scripts/qa/run-artifacts/rev9_test_atpin.log`, header `rev9_test_atpin.header` naming the full code-commit SHA it ran from a clean `git archive` of it). The suite docstring no longer hardcodes any pin and no longer asserts counts — counts are mechanically re-counted from the committed log by the claim-table generator (row 16 proves the citation, row 17 the code identity). During this work our own cross-check (check-call-sites vs committed log IDs) caught a **phantom `P0-21` docstring bullet** — a scenario advertised by the docstring that never existed as a check; real coverage is P0-20f–h (LEDGER-STATE-CORRUPT family). The docstring now names P0-20f–h and nothing else; also the stale "26 scenarios" count (wrong — the artifact re-counts 20 scenario bases / 63 checks) was corrected in docstring, protocol changelog, and ledger. Disclosed proactively because P1-2 is precisely about docstring-vs-reality drift.
- **§3.3 protocol text** updated to state the post-spawn invariant and the HOLD retype with same-ID repair (row 19). §3.8 untouched (row 20).

## Claim → evidence table (at pin 0d156d7, mechanically generated)

Every row was emitted by `scripts/qa/gen_claim_table_repin8.py` (committed at `e10cb6c`), which anchors each claim by substring-searching `git show 0d156d7:<file>` and **fails loudly if any anchor is absent** — during this cycle it aborted twice on my own wrong needles (wrong TIMEOUT line text; wrong f-string text for the UNREADABLE fold), and both rows were rewritten against the real code before send. Rows 15–17 and 20–21 are live in-generator git-diff/re-count checks, not assertions. Full table verbatim at `workflows/adviser-prompts/round-07/claim-table-repin8.md` (pin successor `e10cb6c`). Shorthand: runner = `scripts/m0-broker-runner.py`, test = `scripts/qa/test_broker_p0.py`.

<!--BEGIN GENERATED TABLE — emitted by scripts/qa/gen_claim_table_repin8.py, do not hand-edit-->

| # | Claim (rev-9, at pin `0d156d7`) | Evidence (mechanically extracted) |
|---|---|---|
| 1 | Post-spawn region enters a guard flag before the first post-Popen call; exit_code bound pre-try | `scripts/m0-broker-runner.py:671` |
| 2 | TIMEOUT path sets err BEFORE kill/reap, and kill+communicate failure is folded INTO the recorded error at the site (cannot escape to the generic handler or past bump_usage) | `scripts/m0-broker-runner.py:678 + scripts/m0-broker-runner.py:688` |
| 3 | Generic post-spawn handler kills + reaps the child (no orphan on uncertain outcome; Claude NB3) | `scripts/m0-broker-runner.py:696` |
| 4 | Invariant documented at the site: successful Popen construction => bump_usage + durable spawn_succeeded=True on EVERY post-spawn path | `scripts/m0-broker-runner.py:668` |
| 5 | bump_usage runs the moment the child was run (pre-decode) | `scripts/m0-broker-runner.py:704` |
| 6 | P0-17e: timeout whose kill() ITSELF raises (in-process Popen trap, argv-scoped) -> TIMEOUT-with-cleanup-failure recorded, budget consumed | `scripts/qa/test_broker_p0.py:1131` |
| 7 | P0-17e2: the SAME signed command is BUDGET-EXHAUSTED for a FRESH id afterwards (no re-execution) | `scripts/qa/test_broker_p0.py:1151` |
| 8 | Corrupt durable usage is a HOLD now: logs BUDGET-STATE-CORRUPT, executes nothing, writes NO disposition | `scripts/m0-broker-runner.py:593` |
| 9 | Corrupt execution history is a HOLD (same retype at the history site) | `scripts/m0-broker-runner.py:603` |
| 10 | P0-19a/b + P0-20d/e/e2 rewritten to hold semantics: after the owner repairs the file the SAME request id runs again (repair-then-rerun-same-ID legs) | `scripts/qa/test_broker_p0.py:916 … scripts/qa/test_broker_p0.py:1012` |
| 11 | Ledger.load: valid-JSON-non-object -> unreadable-corrupt HOLD sentinel, 'held, never re-executed' (OSError caught too — chmod-000 exercised for real as non-root) | `scripts/m0-broker-runner.py:177` |
| 12 | verify_plan catches UnicodeDecodeError: invalid-UTF-8 signed plan -> UNVERIFIABLE -> PENDING, every pass survives (P0-9e) | `scripts/qa/test_broker_p0.py:1095` |
| 13 | P0-20g/20h: non-object state + unreadable state file both HOLD the owning request while siblings still run | `scripts/qa/test_broker_p0.py:1052 + scripts/qa/test_broker_p0.py:1070` |
| 14 | digest_artifacts: directory or unreadable artifact path -> observed='UNREADABLE' (never an uncaught OSError crashing the pass; ChatGPT re-pin-7 P1 / Claude NB2) | `scripts/m0-broker-runner.py:333` |
| 15 | Test suite green AT THIS PIN per the COMMITTED artifact (mechanically re-counted here from the committed log, not from the header alone): 63 PASS / 0 FAIL / tail 'FAILS: none'; artifact header pins the code commit e78f1c2df102a0ef59fafd6b15aa6980d55f58e1 (run from a clean git archive of it — no scratch-dir log, no hardcoded count in any docstring) | `git show 0d156d7:scripts/qa/run-artifacts/rev9_test_atpin.header re-counted against git show 0d156d7:scripts/qa/run-artifacts/rev9_test_atpin.log` |
| 16 | Test docstring cites the committed artifact path (not b134df3, not /tmp) | `scripts/qa/test_broker_p0.py:15; b134df3 occurs 0 times in scripts/qa/test_broker_p0.py@0d156d7` |
| 17 | Code executed by the suite at the pinned commit (e78f1c2, run from clean `git archive`, artifact header cites its full SHA) is the code AT THIS REVIEW PIN: runner byte-identical d1c0e09→0d156d7 (git diff --quiet, 0 lines) and the only test-file delta d1c0e09→0d156d7 is inside the module docstring — every `git diff -U0` hunk of the test file falls within the docstring line span at BOTH endpoints (verified here programmatically; between e78f1c2 and 0d156d7 even that delta is nil, the artifact commit adds only the run log, its header, and this generator) | `git diff --quiet d1c0e09 0d156d7 -- runner => clean; test hunks [('13', '3', '13', '3'), ('18', '', '18', '3'), ('77', '', '79', '2'), ('79', '', '82', '')] ⊂ docstring spans (2, 80)/(2, 83)` |
| 18 | Protocol title is rev-9; changelog records all three re-pin-7 verdicts (Grok ACCEPT, ChatGPT AWC, Claude AWC) | `workflows/m0-interview-protocol.md:1 + workflows/m0-interview-protocol.md:12` |
| 19 | §3.3 states the rev-9 post-spawn invariant (guard end-to-end; kill/reap+bump+record on every path) and the corrupt-state HOLD retype with same-ID repair | `workflows/m0-interview-protocol.md:12 + workflows/m0-interview-protocol.md:206` |
| 20 | §3.8 architecture limitation byte-identical to the ORIGINAL accepted slice (rev-5) AND to the last reviewed pin | `sha256 at 0d156d7 = c91a5b83e83c4235 == 8509096 (c91a5b83e83c4235) == a695398 (c91a5b83e83c4235)` |
| 21 | Revoke script byte-identical since re-pin-7 pin (no new claims about it) | `git diff --quiet a695398 0d156d7 -- scripts/m0-broker-revoke-keys.sh => clean` |

<!--END GENERATED TABLE-->

## Test suite status at this pin

`scripts/qa/test_broker_p0.py`: **20 scenario bases / 63 checks — 63 PASS / 0 FAIL / exit 0** (`FAILS: none`), run from a clean `git archive` of `e78f1c2df102a0ef59fafd6b15aa6980d55f58e1` (runner byte-identical to this pin; test delta docstring-only — row 17), log committed at this pin (row 15 re-counts it here). The suite runs real `ssh-keygen -Y` signatures, a real local bare git remote with a rejecting pre-receive hook, real `ssh-keygen -lf` inventories, real subprocess crash/restart simulations, and chmod-000 unreadable-file paths exercised for real as a non-root user. Declared instrumented exceptions (fsync counter P0-12; argv-scoped Popen traps P0-17c/17e) are documented in the suite docstring.

## Questions for this re-pin

**ChatGPT (voting):** Q1 — is your re-pin-7 P0 repaired at this pin per rows 1–7 (guard end-to-end, err-before-cleanup, fold-at-site, kill+reap, P0-17e/17e2 proof)? Q2 — do rows 8–14 discharge your P1-1 (OSError trio incl. non-object/non-UTF8/unreadable)? Q3 — does the committed run artifact + header + in-generator re-count + docstring-hygiene fix + the disclosed phantom-P0-21 catch discharge P1-2, and is the declared-pin discipline (reviewed files unchanged to HEAD) acceptable for P1-3? Q4 — any remaining blocking item at this pin, yes/no with anchor.

**Grok (voting):** §3.8 byte-identical at this pin (in-generator triple-pin diff, row 20); architecture untouched; all changes are the repair items your seat already saw. Q1 — does your ACCEPT stand at `0d156d7`? Q2 — the claim table is again emitted by the fail-loud committed generator (it aborted on me twice this cycle; disclosures above); does the pre-send gate meet your bar?

**Claude (advisor, runner scope):** your blocking item maps to rows 8–10 (HOLD retype + repair-then-rerun-same-ID legs P0-19a/b, P0-20d/e/e2); NB1 → rows 11–13; NB2 → row 14; NB3 → rows 1–7 (generic handler kill+reap); NB4 (docstring pin) → row 16 (docstring names no pin at all now; counts deferred to the committed artifact). Confirm or re-open with anchors.

## Verdict format

Reply with: pin reviewed (full SHA `0d156d755f9f8f8d99df3088be49ec871b6ac120`), per-question answers, vote (ACCEPT / ACCEPT-WITH-CHANGES / REJECT) + blocking items if any. Paper-only review; run nothing. Per §9, Wave 0 may BEGIN only on 2/2 voting ACCEPT at the same pin; Wave-0 rulings still need their own evidence + 2/2 validation (§2a), and DESIGN-REVIEW §10 HARD STOP is untouched.
