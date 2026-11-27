# Round-07 re-pin-6 reply — CHATGPT (voting member)
Pin reviewed: 6c19da3dda22cba681ab69d5ae530e214e56fa49
Branch: dp/round-07-m0-interview · Protocol: rev-7 · Review mode: Paper-only (pinned source and test bodies inspected; nothing executed).
Pin clarification: the prompt lives at commit 076c6246d7f8e805860712e565443af6856d1104; review was of the DECLARED source pin 6c19da3dda22cba681ab69d5ae530e214e56fa49.

## Q1 — Are the three re-pin-5 blockers adequately repaired?
Overall: the first two fixes are present in the implementation; the third is substantially repaired but does not fully meet the stated fail-closed contract. There is also a missing regression test for the precise crash window in blocker 2.

### 1. Request-ID collision before every lifecycle branch — MET
The rev-7 runner performs the request-hash comparison before the started-recovery branch. At runner lines 387–408 it: loads the existing request state; compares stored hash with incoming line hash; creates a separate collision disposition; preserves both hashes and the original status; leaves the original request state untouched. Tests appropriately targeted: P0-13c (collision detection against an existing started state), P0-13d (original state and hash survive unchanged).

### 2. Recovery of definite outcomes before UNPROVEN — implementation MET; test evidence incomplete
The runner inspects the durable record before classing started as UNPROVEN (runner lines 415–442): spawn_succeeded false recovers as definite spawn failure; spawn_succeeded true with exit field recovers as completed execution; only inconclusive outcomes become UNPROVEN.
However the test evidence does not exercise the exact failure window:
- P0-17b runs a spawn failure through the NORMAL handler (record + state→executed written, then restart). It does not simulate a crash BETWEEN the two writes.
- P0-18a manually seeds started + durable record, but the record has spawn_succeeded TRUE — it tests completed-execution recovery, not the definite spawn-failure case.
Required test: P0-18c — seed/produce (1) started state with original request hash, (2) matching durable record with spawn_succeeded false, (3) restart before state transitions to executed. Verify recovery produces the definite spawn-failure outcome, never writes UNPROVEN, never re-executes.

### 3. Corrupted use-budget state fails closed — PARTIAL
Primary repair present: missing file → zero; valid count returned; invalid counts/malformed JSON → CORRUPT result; caller writes BUDGET-STATE-CORRUPT refusal (usage_count at runner 265–284, refusal path 480–491). P0-19a/P0-19b cover malformed JSON + owner-removal recovery.
Two remaining weaknesses:
A. Structurally invalid but syntactically valid JSON (e.g. [] or "unexpected") parses; body.get("count") raises AttributeError, which the JSONDecodeError/ValueError catches do not cover. It will not silently grant a run, but it also will not produce the promised BUDGET-STATE-CORRUPT refusal.
B. Corrupt execution-history records are SILENTLY SKIPPED by record_history_count (catches JSONDecodeError, continues) — weakens the history-based protection if the counter is also absent/reset. The protocol describes corrupt usage state as a broker-level integrity failure, not a condition that may silently reduce the historical count.
Required: treat non-object usage JSON / unreadable usage files / invalid count structures as explicit corruption; do not silently skip corrupt execution-history records (fail closed or require explicit owner recovery); add regression coverage.

## Q2 — Row-12 disclosure sufficient, or dedicated tests required?
A dedicated test is required before unconditional ACCEPT. Disclosure is a meaningful accuracy improvement, but record_history_count exists specifically to prevent broker-state loss resetting a consumed max_runs budget. Required focused checks:
1. Execute a command with max_runs: 1.
2. Remove its usage-counter file, preserving its durable execution record.
3. Submit the same command under a fresh request ID.
4. Verify refusal as BUDGET-EXHAUSTED.
Also test that a spawn_succeeded false record does NOT consume budget, and that a corrupt execution-history record cannot silently reduce the count. Not a redesign request — a regression requirement for a newly introduced authorization invariant.

## Q3 — Do the walk-backs + mechanical table satisfy the accuracy standard?
Mostly, not completely. Genuine progress: three false re-pin-5 claims recorded; docstring corrected re sshd/mocks; code-present vs dedicated-test distinguished; pinned anchors replace narrative. P0-11e present; P0-12b honestly scoped; P0-12c added.
Remaining gaps:
- Row-2's test mapping still OVERSTATES evidence for the precise spawn-failure crash window (P0-17b is the normal-handler path; P0-18 tests spawn_succeeded TRUE recovery).
- verify_plan() does not first validate the decoded plan is an object with a valid commands collection — a syntactically valid JSON list/scalar escapes the intended unverifiable path via an uncaught structural exception. Fail-stop, not an execution bypass, but it does not fully demonstrate the prompt's claim that structurally unreadable plans are handled as explicit PENDING.
Process ruling: the matrix is the right required format; it still needs independent verification against exact source, and a test ID must prove the PARTICULAR behavior claimed — not a nearby or normal-path behavior. Walk-backs are genuine progress; the accuracy issue is not completely closed at this pin.

## Q4 — Vote: ACCEPT-WITH-CHANGES
Architecture accepted; no request for second machine/TPM/hardware root of trust/remote attestation; §3.8 limitation remains consistent.
Required changes before unconditional ACCEPT:
| Priority | Required change |
| P0 | Regression test for started + durable spawn_succeeded:false record + restart before the state transition. |
| P1 | Dedicated test proving durable-record history preserves max_runs after the usage counter is removed. |
| P1 | Make corrupt or structurally invalid usage state AND corrupt execution-history records fail closed explicitly. |
| P1 | Validate the decoded plan's top-level structure and commands collection; add malformed-structure PENDING tests. |
Targeted reliability and evidence repairs; no architecture change required.
Authorization status: Architecture Accepted; rev-7 ACCEPT-WITH-CHANGES; Wave 0 NOT authorized by this verdict; owner cutover / C1-C2 prep / destructive ops / deployment NOT authorized; DESIGN-REVIEW §10 HARD STOP unchanged; R-4/R-5/R-7 open until live evidence. Wave 0 requires 2/2 council acceptance at the SAME pin; acceptance authorizes Wave 0 only.
Final vote: ACCEPT-WITH-CHANGES at 6c19da3dda22cba681ab69d5ae530e214e56fa49. Prepared to review a narrowly scoped rev-8.
