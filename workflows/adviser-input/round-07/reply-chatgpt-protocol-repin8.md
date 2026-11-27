CHATGPT:
-------------------------------------------------------
I'll review rev-9 at the exact commit b137ca5dd6a99183aaa392629b73e9b7334039ec, carrying forward the rev-8 blockers. I'll verify the prompt's declared source pin and evidence against the raw files, and I'll keep the review paper-only: no test execution, runtime actions, or gate authorization.

Round-07 Council re-pin review — protocol rev-9
ACCEPT-WITH-CHANGES
Declared source pin reviewed: 0d156d755f9f8f8d99df3088be49ec871b6ac120
Prompt location: b137ca5dd6a99183aaa392629b73e9b7334039ec
Protocol: rev-9
Review scope: Protocol, broker runner, setup script, test suite, committed run artifact, claim-table generator, and ledger.

I reviewed the exact declared source pin. I did not execute tests or scripts. The run artifact is evidence committed in the repository; I treat it as a recorded result, not as an independently reproduced test run.

Q1 — Is the rev-8 post-spawn P0 repaired?
PARTIAL — the specific timeout-cleanup escape is repaired, but the broader post-spawn budget invariant is not yet guaranteed.

What is repaired
The rev-8 defect was real: an exception raised inside the TimeoutExpired handler could escape before budget accounting and durable execution recording.

Rev-9 now:
- Sets the timeout error before attempting cleanup.
- Catches failures from kill() and the subsequent communicate().
- Folds cleanup failures into the timeout error.
- Routes unexpected post-spawn communication failures through a conservative handler.
- Calls bump_usage() before output decoding and writes a durable record with spawn_succeeded=True.
The implementation is visible in the post-spawn section.

The new P0-17e test injects a timeout followed by a failing kill(). P0-17e2 verifies that the same signed command is budget-exhausted under a fresh request ID. The committed log records both checks as passing.

The specific rev-8 timeout-cleanup defect is MET.

Remaining P0 — budget-write failure after a successful spawn
P0 — blocking

The prompt claims:
successful Popen construction implies bump_usage plus a durable spawn_succeeded=True record follow on every path.

The implementation does not guarantee that invariant.

bump_usage() performs a durable write, but it can raise—for example, if the usage file cannot be written, the filesystem becomes unavailable, or an fsync fails.

Critically, the call to bump_usage() is outside the post-spawn exception handler. The handler ends before that call. The durable execution record is written afterward.

That creates this failure sequence:
1. The signed command successfully spawns and executes.
2. bump_usage() fails before the updated budget is durably recorded.
3. The durable execution record is never written.
4. The request remains in started state.
5. On restart, the request may become UNPROVEN, preventing automatic replay of that same ID.
6. A fresh request ID can still pass the budget check if neither the usage counter nor execution-history records show the execution.

The recovery logic only uses a durable execution record to recognize a definite outcome. It does not count a bare started state as a consumed command budget.

This is not merely a missing test for an unlikely exception. It is a gap in the claimed authorization invariant.

Required repair:
- Make failure to durably account for a spawned child stop further command processing until owner recovery, rather than allowing fresh request IDs to obtain another attempt.
- Ensure the broker cannot interpret an execution whose budget write failed as a command that has not consumed its budget.
- Add a test that injects a failure in the usage-counter durable write after successful Popen, then submits the same signed command under a fresh request ID.
- Verify that the fresh request cannot execute.

A durable record failure after a successful budget write is less concerning because the usage counter already protects the budget. The dangerous window is specifically failure of the budget write itself.

Disposition: PARTIAL. The timeout-specific fix is good, but the claimed end-to-end post-spawn invariant is overstated.

Q2 — Do rows 8–14 discharge the rev-8 P1-1 OSError and corruption concerns?
Mostly MET.

Corrupt usage and execution history
The rev-9 HOLD behavior is a meaningful improvement over terminal refusal.

The runner now:
- Holds requests when the usage state is corrupt.
- Holds requests when execution-history records are corrupt.
- Writes no disposition for the held request.
- Allows the owner to repair the underlying file and resubmit the same request ID.
The relevant code is at the usage and history checks.

The tests cover:
- Corrupt usage state followed by same-ID recovery.
- Corrupt execution history followed by same-ID recovery.
- A wiped usage counter with durable execution history still preserving the budget.
- A spawn_succeeded=False record not consuming an execution budget.
The committed log records these as passing.

Disposition: MET.

Ledger state: non-object and unreadable files
Ledger.load() now catches OSError and malformed JSON, and returns a sentinel rather than treating the request as unseen. It also detects valid JSON that is not a object. Ledger.pending() skips corrupt or non-object state files rather than crashing the publication phase.

P0-20g and P0-20h exercise non-object and unreadable state files, respectively. The tests also check that unrelated requests continue to run.

One qualification: the chmod-000 unreadability test is explicitly skipped when running as root. The prompt discloses this limitation; the recorded run claims it was exercised as a non-root user.

Disposition: MET, subject to the stated non-root test precondition.

Invalid UTF-8 plans and artifact paths
The runner catches invalid UTF-8 while verifying the signed plan, and the test confirms the request remains PENDING without crashing the pass.

The artifact-digest code also converts an unreadable artifact path into an explicit UNREADABLE observation rather than allowing the read exception to escape.

Disposition: MET.

Q3 — Does the committed run artifact, generator, and declared-pin discipline discharge the claim-hygiene concerns?
PARTIAL — the committed artifact is a substantial improvement, but the generator does not establish all the provenance claims it makes.

What is now good
The run artifact is committed at the declared pin. Its header records:
- Review pin: e78f1c2df102a0ef59fafd6b15aa6980d55f58e1
- Suite exit: 0
- PASS count: 63
- FAIL count: 0
The log contains the individual PASS entries and ends with FAILS: none.

The successor generator at e10cb6c now uses the declared review pin 0d156d7, reads the committed artifact, recounts PASS and FAIL lines, compares those totals with the header, and checks the log ending.

This addresses the earlier problem of hardcoded test counts and an uncommitted scratch log.

Remaining P1 — the generator does not verify the run pin against the review pin
The generator's code-identity check compares:
- Runner at d1c0e09 against the review pin.
- Test-file changes at d1c0e09 against the review pin, checking that the changed hunks are within the module docstring.
But the artifact header identifies e78f1c2 as the commit actually tested.

The generator does not perform the equivalent runner and test-file comparisons directly between e78f1c2 and 0d156d7. Instead, its generated claim states that the intervening difference is nil.

That is an important distinction. The table's claim that the tested code is the reviewed code needs a direct comparison between the artifact's full run SHA and the declared review SHA. The current check does not establish that.

Required repair: Compare the runner and test-file content directly between e78f1c2df102a0ef59fafd6b15aa6980d55f58e1 and 0d156d755f9f8f8d99df3088be49ec871b6ac120. The test-file comparison should explicitly allow only the documented module-docstring delta, if any. Generate the row from those actual comparisons.

Remaining P1 — claim-table line anchors are not accurate
The generated claim table reports runner anchors such as:
- child_ran = False at line 671.
- Timeout error assignment at line 678.
- Generic cleanup condition at line 696.
- bump_usage() at line 704.
But the pinned runner places those corresponding statements at approximately lines 653, 659, 677, and 685, respectively.

The discrepancy is systematic, not a single typo. The generated table's anchors are therefore not reliable references to the exact pinned source.

The generator's anchor() function uses the first substring occurrence and returns its line number. It does not verify that the line it returns is the actual implementation location described by the claim.

Required repair: Correct the table and improve the generator so that its output is checked against the exact implementation location. A substring-presence check is not sufficient when the table is intended to provide auditable source anchors.

Remaining P1 — generic post-spawn cleanup lacks a dedicated regression test
The runner's generic post-spawn handler attempts to kill and reap the child after an unexpected communication exception.

P0-17e exercises a failure inside the timeout handler. It does not exercise the generic handler's separate path. The committed log has no distinct test result demonstrating that an unexpected non-timeout communication exception triggers kill/reap and still records the outcome.

This is a narrower evidence gap than the budget-write failure, but it matters because the prompt specifically maps Claude's generic kill/reap requirement to rows 1–7.

Required test: Add a separate test where the initial communicate(timeout=...) raises an unexpected exception, then verify the generic handler attempts cleanup, records a post-spawn uncertain outcome, and consumes the budget.

Q4 — Remaining blocking items and vote
ACCEPT-WITH-CHANGES
Rev-9 is a meaningful improvement. The previous timeout-cleanup defect is repaired, corrupt-state HOLD semantics are substantially better, and the committed run artifact is a step forward.

However, I cannot accept the claim that the post-spawn budget invariant is now guaranteed. A failure in bump_usage() after successful process creation can still leave a spawned command without durable budget consumption or a durable execution record. That is a direct authorization/accounting gap.

Required changes
Priority | Required change
P0 | Make post-spawn budget-write failure fail closed for subsequent requests. Add a regression test proving a fresh request ID cannot obtain another run after the budget write fails.
P1 | Compare the artifact's actual run SHA (e78f1c2…) directly with the review pin (0d156d7…) in the generator.
P1 | Correct generated source line anchors and make the generator verify implementation locations, not just substring presence.
P1 | Add a dedicated regression test for the generic post-spawn exception handler's kill/reap path.

Architecture and authorization
The architecture remains accepted. I am not requesting a second machine, TPM, hardware root of trust, or remote attestation.

The protocol's §3.8 limitation remains the accepted one: separate broker identity and credentials on the same physical host, with the owner remaining the ultimate trust authority. The rev-9 prompt reports §3.8 byte-identical to the earlier accepted slice; I found no basis in this review to reopen that architectural decision.

- Architecture: ACCEPTED.
- Protocol rev-9: ACCEPT-WITH-CHANGES.
- Wave 0: Not authorized by this verdict.
- Owner cutover: Not authorized.
- C1/C2 preparation: Not authorized.
- Destructive operations: Not authorized.
- Deployment or ticket execution: Not authorized.
- DESIGN-REVIEW §10 HARD STOP: Unchanged.
- R-4/R-5/R-7 exceptions: Remain open until their required live evidence exists.
The protocol's 2/2 same-pin acceptance requirement remains in force. A council ACCEPT-WITH-CHANGES is not an ACCEPT and does not authorize Wave 0.

Final vote: ACCEPT-WITH-CHANGES at 0d156d755f9f8f8d99df3088be49ec871b6ac120.

I would keep the next repair cycle narrowly scoped. Rev-9 has resolved most of the previous findings; the remaining P0 is the durability boundary between a successful spawn and durable budget accounting. That boundary must fail closed before I can give an unconditional ACCEPT.
