Claude:
-------------------------------------------------------
The prompt is now pasted in full, so the raw links at 0d156d7 are in our conversation and I can fetch them. I'll start with the runner.

The runner is readable now. I see one regression in the same OSError fail-closed family the prompt claims is closed, so I need the test file to check it.

The runner and test suite at 0d156d7 are now readable. Before I vote, I'll check the committed run log, since the claim that the suite passed rests on it.

Council position: Claude (advisor, runner scope), rev-9, pin 0d156d755f9f8f8d99df3088be49ec871b6ac120

Scope. I read scripts/m0-broker-runner.py, scripts/qa/test_broker_p0.py, and the committed log scripts/qa/run-artifacts/rev9_test_atpin.log at this pin. The log lists every check as PASS, with FAILS: none, and includes P0-20h as PASS, so that leg ran as non-root. I did not run the suite, did not read the protocol text or the revoke script, and did not check the header or the generator.

Discharged from my earlier requirements

Corrupt budget and history as HOLD (my blocking item from re-pin-7). Confirmed in code: BUDGET-STATE-CORRUPT in both the usage and history paths does continue with no disposition. P0-19a/b and P0-20d and P0-20e/e2 show the same request ID running after repair. The guarantee holds for the owning request.
Spawn, timeout, and post-spawn handling (rows 1–5). The child_ran flag, exit_code pre-bound, err-before-cleanup, the nested kill and communicate guard, the outer kill-and-reap, and bump_usage before the lossy decode all match the claims.
digest_artifacts catches OSError and ValueError and records UNREADABLE.
verify_plan catches UnicodeDecodeError on the plan file (P0-9e).

Blocking: two items

1. Decode errors still crash the pass in ledger reads. Ledger.load, Ledger.pending, the record read in the started branch, and record_history_count catch JSONDecodeError and OSError, but not UnicodeDecodeError, which is a ValueError. A state or record file containing a single non-UTF-8 byte therefore raises out of the pass. pending() scans every state file at the end of every pass, so one bad byte in any file stops publication and dispatch until repair. No execution is unsafe, but it is a liveness failure, and it contradicts the "OSError trio" claim. The tests don't cover it: P0-20h uses chmod 000, and P0-9e covers only the plan file. Fix: catch ValueError in all four places. Add tests that write b"\xff" into one state file and one record file and assert that the pass survives, the held ID does not execute, sibling requests still run, and publication completes.

2. P0-17e2 does not isolate the budget bump. record_history_count counts any record with spawn_succeeded set to true. So after the timeout leg, the same argv would be BUDGET-EXHAUSTED from the durable record alone, even if bump_usage never ran. The any(v >= 1) clause is also satisfied by usage files left by earlier legs, so it adds nothing. P0-17d3 has the same weakness. The invariant that the usage file is bumped on every post-spawn path is therefore not tested. Fix: after the timeout leg, assert that the usage file for canonical_sha256([argv, [], 1]) equals 1. Or delete the record and assert that the refusal comes from the usage file alone.

Non-blocking, but fix in the same pass

1. A corrupt record file holds every command that reaches the history check, not only the owning request. The prompt's "siblings still run" is true for request-state holds, but not for history holds. Document this in §3.3 as a global hold and add a test showing that an unrelated request is held.
2. The module docstring omits P0-9e, P0-17e, and P0-17e2, which the bodies contain. That is the same docstring drift this round was meant to remove.
3. P0-20h prints SKIP under root, which the gate does not count as a failure. The committed run was non-root, so the evidence is valid, but the gate should treat SKIP as failure.
4. The comment in the post-spawn region says "final-ly"; it should read "finally".

Answers to the re-pin-7 questions for Claude

Blocking item (rows 8–10): discharged for the owning request.
NB1 (rows 11–13): the OSError part is discharged. The decode-error part is not, as item 1 above.
NB2 (row 14): discharged.
NB3 (rows 1–7): the code is discharged. The budget-consumption proof is not, as item 2 above.
NB4 (docstring pin): the docstring names no pin, but it still omits three checks, as above.

Vote: ACCEPT-WITH-CHANGES. Blocking: the decode-error gap in ledger reads (item 1) and the P0-17e2 budget-bump test (item 2). Both are small. Once they are fixed and the new tests pass, I'll move to ACCEPT for runner scope.
