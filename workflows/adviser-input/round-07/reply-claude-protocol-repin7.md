# Claude — Round-07 re-pin-7 reply (protocol rev-8, pin `a6953989fe74ba256dae90215ac41208d570a32d`)

Advisor (runner scope). Read scripts/m0-broker-runner.py and scripts/qa/test_broker_p0.py at this pin; checked rows 1–14 by reading code and test bodies. Did not run the suite, read protocol text (§3.3, rev-8 wording), or the revoke script (row 21 unverified by this seat). Line-number anchors not checked one by one — symbols and behavior only.

## Re-pin-6 blocking items: discharged

**Spawn and decode (rows 1–6).** Popen construction is now the only definite never-started path (except Exception around Popen writes spawn_succeeded: false). After the child exists, communicate() runs, bump_usage runs before any decoding, output decoded with errors="replace". The rev-7 regression is fixed. P0-17d/d2/d3 cover it: test script prints \377\376, record spawn_succeeded: true, budget consumed under fresh ID.

**Phantom P0-16c (rows 7–8).** Docstring no longer lists P0-16c, body gone. P0-9c2 present.

**Confirmed rows.** Rows 9–10 (corrupt usage and history fail closed), rows 11–12 (Ledger.load returns unreadable-corrupt, run_pass holds the request; P0-20f), rows 13–14 (verify_plan shape checks; P0-9d) — implemented with test bodies.

## New blocking item — corrupt budget/history refusal is TERMINAL, inconsistent with corrupt request-state handling

`refuse()` writes a dispositioned state. Once the owner repairs or removes the corrupt file, the same request ID is **skipped forever**. The tests hide this: P0-19b and P0-20e both re-queue under a fresh ID (r19b2; the P0-20e recovery step), so neither checks whether the ORIGINAL ID can run after repair. This matches the "unverifiable is never terminal" principle from re-pin-4 condition 3.

Two acceptable fixes:
1. (Better) Hold these requests the way corrupt request state is held: no disposition, no execution — an owner repair lets the same ID run exactly once.
2. Or state explicitly in §3.3 that such requests must be re-issued under new IDs.

Either way: add a test that repairs the file and re-queues the original ID.

## Non-blocking (fix before ACCEPT)

1. `verify_plan` catches JSONDecodeError and OSError, but `read_text()` on a signed plan with invalid UTF-8 raises UnicodeDecodeError (a ValueError) which escapes. Owner-only file, but the pass would crash every cycle instead of going PENDING. Catch ValueError.
2. `digest_artifacts` calls `read_bytes()` without handling a directory/unreadable file — a signed artifact path that isn't a regular file crashes the pass. Treat as artifact mismatch.
3. In the post-spawn `except Exception` around communicate(), the child is not killed or reaped. Kill and reap it there.
4. Test docstring says the suite passed at b134df3, different from the declared pin. Either rerun and cite the pin, or state that the log is from an earlier commit. Claude has not seen `rev8_test_final.log` and cannot confirm 57/57.

## Vote: ACCEPT-WITH-CHANGES

Rows 1–14 discharge the re-pin-6 requirement and earlier blocking items. Holding ACCEPT for the corrupt-budget/history refusals becoming terminal, blocking same-ID recovery. Non-blocking items should be cleared in the same pass. Once the same-ID repair test passes, moves to ACCEPT for runner scope.
