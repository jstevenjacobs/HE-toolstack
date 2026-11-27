# CLAUDE — Round-07 re-pin-5 verdict (protocol rev-6, advisor seat)

Adviser: Claude (advisor seat, runner scope)
Pin reviewed: 3f3b04a3ea0a83afd4964e1a17287467a0121988
Scope: scripts/m0-broker-runner.py + scripts/qa/test_broker_p0.py only (no protocol/setup/revoke view)
Received: 2026-11-26
Verdict: **ACCEPT-WITH-CHANGES** (runner-scope; does not convert to ACCEPT)

---

Council position: Claude (advisor, runner scope), rev-6, pin 3f3b04a…

Pin reviewed: 3f3b04a for `scripts/m0-broker-runner.py` and `scripts/qa/test_broker_p0.py`. I read both files and checked the claim-to-test mapping by reading code. I ran nothing. I did not review the protocol text, the setup script, or the revoke script at this pin, so I have no view on P0-11's revocation claims.

## Answers to the re-pin-4 conditions

**Condition 1 (artifacts pinned, verified before spawn) is discharged.** `digest_artifacts` runs before `subprocess.run`, and a mismatch or missing file produces a refusal. The plan digest covers argv, artifacts and max_runs, so the signature protects the pinned scripts. P0-14a and P0-14b exercise a real post-signature swap. Two residuals should be written into §3.3 rather than left implicit. First, only the listed artifacts are pinned: a script that sources another file, or an interpreter resolved from PATH, is outside the signed set. Second, the check reads the worktree at `origin/branch` and the command then runs from that same tree, so the protection depends on nothing else writing to the worktree.

**Condition 2 (use budget) is discharged.** `usage_count` and `bump_usage` key on plan digest plus argv digest, and P0-15 verifies that a fresh request ID cannot reset the budget. One design issue remains. The key includes the whole-plan `plan_digest`, so any re-signed plan with a new command resets every budget, including for commands already used. The owner would have to do that deliberately, but the budget ought to be keyed per command, and §3.3 should say what a re-sign does.

**Condition 3 (absence is pending, not refused) is discharged for a missing plan.** P0-16a and P0-16b cover it. It is **not** discharged for a plan that is present but unverifiable. In `verify_plan`, a plan file with no signature file, or a signature that fails, returns `invalid`, and `run_pass` then writes a permanent refusal for every queued ID it doesn't authorize. Two problems follow. In normal use, if the owner pushes the plan commit before the signature commit, a broker pass in between blacklists the queued IDs. Also, anyone who can push to the branch (the threat model already assumes they can) can push a bad plan to blacklist arbitrary IDs. My condition 3 as I wrote it covered only absence, and I should have said "absent or unverifiable". P0-1 and P0-2 currently lock in the terminal behavior, so they would need to change too.

**Condition 4 (spawn OSError is a definite record) is discharged.** P0-17a and P0-17b cover it, and the code correctly skips `bump_usage` on spawn failure. One gap: an empty argv or a NUL byte raises IndexError or ValueError, which is not caught. The broker would then crash after writing started, and the restart would classify it as UNPROVEN. Catching `Exception` around the spawn, or rejecting empty argv at plan verification, closes this.

## The rev-6 claim-to-test mapping

The P0-12 through P0-17 test bodies exist at this pin and match the docstring. My correction to the record is that P0-11 at this pin has the rev-6 inventory-wide checks, and the test suite uses real `ssh-keygen -Y` signatures and a real rejecting hook. The module docstring still says "no mocks", but P0-12a uses `mock.patch` on `os.fsync`. That's a small inaccuracy and should be corrected.

## Vote: ACCEPT-WITH-CHANGES

My runner-scope vote does not convert to ACCEPT.

### Required before ACCEPT

A plan that is present but unsigned, or has a failing signature, must **not** write terminal refusals. Those requests should stay pending, or be recorded as a non-terminal authorization event that a later valid signature supersedes. Add a test that plants an invalid plan, enqueues an ID, runs the broker, then signs a valid plan with the same ID and expects execution. Update P0-1 and P0-2 to match.

### Requested, not blocking

1. Key the use budget per command (argv, artifacts and max_runs), not per plan, and document what a re-sign does.
2. Catch all exceptions from the spawn call, or reject empty argv at verification.
3. Document the residual trust base in §3.3: unpinned imports, the interpreter, and the worktree.
4. Correct the "no mocks" claim in the test docstring.
5. Consider catching UnicodeDecodeError when reading the queue, so one bad byte doesn't stop the whole pass.
