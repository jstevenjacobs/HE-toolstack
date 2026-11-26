Claude:
-------------------------------------------------------

Council position: Claude (advisor seat), Round-07 rev-5, pin 8509096

Scope of this review. I reviewed scripts/m0-broker-runner.py and scripts/qa/test_broker_p0.py at that pin. I did not review the protocol (workflows/m0-interview-protocol.md), the setup script, the revoke script, the ledger, or the re-pin-3 replies from Grok and ChatGPT. I did not execute the test suite. So this vote covers the runner only. It does not address the protocol as a whole, the five P0 dispositions, or the Wave 0 authorization.

Vote on the runner: ACCEPT-WITH-CHANGES.

The durable request lifecycle, the UNPROVEN rule for uncertain executions, and retry-without-re-execution are implemented and have real tests behind them. The changes below are conditions for an ACCEPT, not optional improvements.

Pin artifacts in the signed plan. Each plan command should carry a SHA-256 for every artifact it depends on. The runner should verify those hashes before spawning and refuse on mismatch. Currently every test plan has an empty artifact list, and the digests are recorded only after execution. Required evidence: a test that modifies a referenced script after signing and confirms nothing runs.
Bound each authorization to a use count. A signed command should authorize a limited number of executions, recorded in durable state keyed by plan digest and argv digest, not by request ID. Required evidence: a test that submits an already-executed argv under a fresh request ID and confirms the second run is refused.
Decide and document the rule for unverifiable plans. I recommend that a missing or unverifiable plan leave requests pending, and that only a verified plan lacking the command produce a refusal. Refusing permanently while the plan is absent means a later valid signature cannot authorize earlier IDs. Required evidence: a test covering the refuse-then-sign sequence, with the outcome matching the rule written into §3.3.
Handle spawn failures. Wrap the subprocess call so that OSError (for example, a missing binary) is recorded as a failed spawn, not left as started and classified as UNPROVEN. Required evidence: a test with a nonexistent binary.

Non-blocking. P0-10 should assert the exact expected exit code, not accept 0 or 3. P0-9 should check for exactly four invalid-request records, not at least four.

Open question that affects condition 1. The broker executes scripts from the same branch that carries the queue and plans. Whoever can push to that branch can change those scripts, so the signature does not protect them unless their hashes are pinned. Please confirm where the executable code lives, and whether the council and the broker share write access to it.

What this vote does and does not do. My vote does not authorize Wave 0. The prompt requires 2/2 acceptance from the named members, and I am not one of those members. I'd also ask the owner to record this vote in the ledger against the pin, since I can't write to the repo or carry state between sessions. I'd want to review the protocol §3.3 text and the revoke script before voting on the protocol as a whole.
