# CHATGPT — Round-07 re-pin-5 verdict (protocol rev-6)

Adviser: ChatGPT (voting member)
Pin reviewed: 3f3b04a3ea0a83afd4964e1a17287467a0121988
Branch: dp/round-07-m0-interview
Received: 2026-11-26
Verdict: **REJECT** (rev-6; targeted implementation repairs, not architectural)
Note: rendered with the adviser's inline source-link cards stripped ("GitHub", "GitHub+1", "GitHub+2"); text otherwise verbatim.

---

Round-07 — ChatGPT independent council review: rev-6
Paper-only review completed

**REJECT**

Reviewed pin: 3f3b04a3ea0a83afd4964e1a17287467a0121988
Branch: dp/round-07-m0-interview
Review scope: All nine supplied raw sources, including the protocol, runner, setup and revocation scripts, test suite, archived council responses, and ledger.

I inspected the pinned source code and test bodies. I did not execute the test suite or perform runtime operations.

## Executive verdict

Rev-6 is a substantial improvement. Most of the previous repairs are implemented correctly, and Claude's four runner conditions have largely been incorporated.

I also confirm that the architecture remains within the previously accepted scope.

However, I found three remaining implementation problems:

1. Request-ID collision detection does not cover requests already in `started` state.
2. A crash during spawn-failure recording can incorrectly turn a definite failure into UNPROVEN.
3. The use-budget implementation fails open when its durable state is corrupted.

I also found discrepancies between several claims in the re-pin prompt and the actual test bodies.

My vote is REJECT at this pin. These are targeted implementation repairs, not architectural objections.

## Q1 — ChatGPT's four re-pin-4 P0 repairs

### Repair 1 — fsync durability: MET — implementation

`durable_write()` now correctly performs:

1. Temporary-file write.
2. File flush.
3. File `fsync()`.
4. Atomic `os.replace()`.
5. Parent-directory `fsync()`.

The implementation at runner lines 73–89. P0-12a verifies at least two fsync calls occur. P0-12b verifies the resulting file contents and removal of the temporary file.

I accept the implementation.

One qualification: P0-12b does not actually exercise concurrent readers, despite the description in the prompt. It tests the completed write, not concurrent-reader atomicity.

Also, the first creation of nested ledger directories deserves explicit crash-durability consideration: syncing the new directory does not necessarily persist its entry in its own parent directory.

**Disposition: MET** for the original file-and-parent-directory fsync requirement. I recommend hardening directory creation and improving the test.

### Repair 2 — Inventory-wide verification and strict recovery grammar: MET — host-side implementation

The new `verify_inventory()` implementation iterates the pre-cutover fingerprint inventory and determines expected state:

- Revoked credentials: ABSENT.
- Non-revoked credentials: PRESENT.

It checks those states against the live authorized-key files and generates individual OK/FAIL entries. Any unexpected state returns failure.

The recovery grammar is also corrected: `local-console`, `keep:SHA256:...`. Other values are refused. The removed `recovery:<fpr>` form cannot silently become a local-console declaration.

P0-11a exercises selective removal and retained-key verification. P0-11b exercises the consolidated inventory output. P0-11d tests rejection of the removed recovery form.

Important qualification: The prompt claims P0-11b2 tests an inventory-less invocation. The actual P0-11b2 assertion tests a declared-but-absent recovery key. There is no separate inventory-less test body.

The implementation does fail when inventory is absent (revocation script lines 165–170), but that specific behavior lacks the claimed regression test.

The container-side probes are also still an owner-executed checklist, not automated per-fingerprint SSH verification. The protocol explicitly identifies that distinction, which is appropriate.

**Disposition: MET** for the host-side inventory and recovery-grammar repairs. Add the missing inventory-less regression test.

### Repair 3 — Request-ID collision handling: PARTIAL — P0 BLOCKER

The implementation correctly compares the stored request hash with the incoming request hash for requests in these states: executed, dispositioned, published. A changed request with an existing ID produces an ID-COLLISION refusal preserving both hashes. P0-13a and P0-13b exercise this behavior for an already-executed request.

However, the collision check occurs **after** the special handling for `started` requests.

At lines 271–279, a request with an existing `started` state is immediately classified UNPROVEN using the **incoming** request's hash. The stored original hash is not compared with the new hash.

Consequently:

1. Request A starts execution and the process crashes.
2. An incoming request reuses A's ID with different content.
3. The runner enters the started branch.
4. It generates an UNPROVEN refusal against the new request.
5. The original and conflicting hashes are not preserved as an ID collision.

The colliding command does not execute, but the evidence no longer correctly identifies the relationship between the original request and the conflicting request.

**Required correction:** Perform request-ID/hash comparison **before all status-specific recovery handling, including started.** The collision must preserve both hashes regardless of the original lifecycle state. The original uncertain execution must remain separately identifiable as UNPROVEN.

Add a regression test using a started request with a different incoming line.

**Disposition: PARTIAL — P0 blocker.**

### Repair 4 — Claude's additional conditions: MOSTLY MET — one additional blocker identified

| Claude condition | Verdict | Evidence |
|---|---|---|
| Signed-plan artifact pinning | MET | P0-14a/b |
| Plan+argv use budget | PARTIAL | P0-15 |
| Missing plan means PENDING | MET | P0-16a/b |
| Spawn OSError means definite failure | PARTIAL | P0-17a/b |

Artifact pinning: the runner verifies the pinned artifact digest before spawning. P0-14 simulates a post-signature artifact swap and checks that execution is refused.

Missing plan: the runner distinguishes an absent plan from an invalid signature. P0-16a/b verifies that the same request remains pending and can execute after the owner signs the plan.

Spawn failure: the normal OSError path now creates a definite failure record with `spawn_succeeded: false`. P0-17a/b checks the completed failure and a subsequent restart.

There is, however, a crash window:

- The runner writes `started`.
- `subprocess.run()` raises OSError.
- The runner writes the definite failure record.
- Before it saves the executed state, the host crashes.

On restart, the runner checks `started` before inspecting the existing record. It therefore generates an UNPROVEN refusal, even though the durable record proves the process never spawned.

**Required correction:** Recovery must inspect an existing durable record **before** classifying `started` as uncertain. A record with `spawn_succeeded: false` must recover as a definite spawn failure.

P0-17b currently tests restart after the entire failure-handling sequence, not this intermediate crash window.

## Q1 continued — Use-budget fail-closed behavior

There is one additional issue in Claude's second condition.

The `usage_count()` function returns zero if its JSON state file cannot be parsed:

```python
except (json.JSONDecodeError, ValueError):
    return 0
```

That is **fail-open** behavior. If the durable usage ledger is corrupted, the broker can treat a previously exhausted authorization as unused and execute the command again under a fresh request ID. This contradicts the purpose of the signed `max_runs` budget.

**Required correction:**
- Missing usage file: zero uses, if genuinely never initialized.
- Valid usage file: use its recorded count.
- Corrupt or inconsistent usage file: refuse execution and record an authorization-state integrity failure.
- Recovery from corrupted budget state requires explicit owner intervention.

P0-15 demonstrates the ordinary fresh-ID budget case, but not corrupted-state handling.

**This is another P0 blocker.**

## Q2 — Prompt-accuracy incidents and process remedy

Process improvement required.

The two earlier corrections were appropriate:
- Rev-4 prompt incorrectly claimed `--once` existed.
- Rev-5 prompt incorrectly claimed P0-12 through P0-17 had test bodies and that P0-11 covered the new inventory-wide verification.

I agree with recording both incidents in the changelog and ledger. They should not automatically invalidate otherwise correct engineering work.

However, I found **additional inaccuracies in the current prompt**:

| Current prompt assertion | Actual source |
|---|---|
| P0-12b tests concurrent readers seeing old-or-new content | P0-12b checks final file contents and temp-file removal only. |
| P0-11b2 tests inventory-less failure | P0-11b2 tests a declared-but-absent recovery key. |
| Revocation tests use a real sshd | No sshd reference exists in the test suite. P0-11 operates on temporary authorized_keys files and uses ssh-keygen. |

These are independently verifiable discrepancies.

### My recommended council process rule

I recommend adopting a **mandatory claim-to-source verification rule** for every future re-pin prompt. Every material assertion about implementation or tests should have:

1. Exact pinned source file.
2. Function, symbol, or test ID.
3. Relevant line range.
4. The specific behavior that the evidence establishes.
5. A distinction between source inspection, test execution, and claimed test results.

For example:

| Claim | Required evidence |
|---|---|
| `--once` performs exactly one cycle | Runner argument/dispatch lines + P0-10 body |
| Inventory-wide verification fails closed | Revocation function + explicit missing-inventory test |
| Spawn failure survives restart | OSError handler + intermediate-state recovery test |
| No duplicate execution | State machine + restart/replay regression test |

I would also require a final mechanical review of the claim-to-source matrix against the exact commit before the prompt is issued.

**My position:** The repeated inaccuracies warrant a process correction, not a penalty against the engineering design. However, the current prompt itself should not be treated as authoritative evidence when its assertions conflict with the committed test bodies.

## Q3 — Architecture and scope: ACCEPTED

I confirm that rev-6 stays within the architectural boundaries previously established.

- No second machine.
- No TPM.
- No hardware root of trust.
- No remote attestation.
- No new evidence-collection architecture.
- No change to the single-operator threat model.
- No change to §3.8.

The broker remains a dedicated account, execution identity, and evidence identity on the existing host.

The artifact-pinning addition is a particularly useful improvement: it addresses the possibility that someone with evidence-repository push access changes an executable script after the owner signs the plan.

The use-budget addition is also appropriate: it limits the authority of a signed plan independently of request IDs.

The absent-plan rule is correct: an absent plan is not evidence of a verified authorization denial.

These changes strengthen the existing design without expanding its trust assumptions.

## Claude — advisor-seat conditions

The archived Claude reply is the rev-5 runner-scope ACCEPT-WITH-CHANGES, not a new rev-6 verdict.

| Condition | ChatGPT assessment |
|---|---|
| Pre-spawn artifact verification | Satisfied |
| Durable plan+argv use budget | Implemented, but corruption handling is fail-open |
| Missing plan remains pending | Satisfied |
| Spawn OSError produces definite failure | Normal path satisfied; intermediate crash window remains |

I would not yet convert the runner-scope assessment to an unconditional ACCEPT. The remaining issues are narrow and testable.

## Final disposition

**REJECT — rev-6.** The previous repairs are substantially complete, but I cannot accept the broker implementation while its recovery and authorization-state handling still contain fail-open or misleading-evidence paths.

### Blocking items for rev-7

| Priority | Required repair | Acceptance evidence |
|---|---|---|
| P0 | Check request hashes before handling every lifecycle state, including started | Collision test against started request |
| P0 | Recover definite spawn failures from their durable records before generating UNPROVEN | Crash-between-record-and-state test |
| P0 | Make corrupted use-budget state fail closed | Corrupted-ledger regression test |
| P1 | Add explicit inventory-less verification test | P0-11 regression |
| P1 | Strengthen P0-12b's atomicity test if concurrent-reader behavior is claimed | Concurrent-reader test |
| P1 | Correct test-suite description concerning sshd | Accurate test inventory |
| P1 | Adopt claim-to-source verification for future council prompts | Verified evidence matrix |

## Voting summary

| Question | ChatGPT answer |
|---|---|
| Q1: Four previous P0 repairs | 2 MET, 1 PARTIAL, 1 MET with additional Claude-related blockers |
| Q2: Prompt-accuracy corrections | Recorded corrections accepted; mandatory verification process recommended |
| Q3: Architecture and scope | ACCEPT |
| Q3: Overall rev-6 | REJECT |
| Q4: Wave-0 authorization | NOT GRANTED |

## Authorization

**NO WAVE-0 AUTHORIZATION.** The required 2/2 voting-member acceptance has not been established.

Consequently: no owner cutover execution authorization; no C1/C2 host preparation authorization; no destructive operations; no deployment authorization; no ticket-execution authorization.

The following remain unchanged: §3.8 threat-model limitation; R-4/R-5/R-7 exceptions until Wave-3 live evidence; Wave-0 evidence pack requires its own 2/2 validation; DESIGN-REVIEW §10 HARD STOP.

## Recommendation

I would make rev-7 the **final targeted reliability repair**, not another architecture review. The broker architecture is acceptable. The remaining work concerns three specific guarantees:

1. **Identity:** a request ID must always identify the same exact request content.
2. **Execution certainty:** a known failure must never become an uncertain execution merely because the process crashed between two durable writes.
3. **Authorization limits:** corrupted authorization-use state must never grant additional executions.

These are fundamental properties of the execution boundary, not optional hardening.

I also recommend adopting the claim-to-source verification rule immediately. The council should not have to discover whether a test actually exists after a prompt asserts that it does.

**Final ChatGPT vote: REJECT rev-6 at 3f3b04a3ea0a83afd4964e1a17287467a0121988.**

I remain prepared to accept the existing architecture without requesting a second machine, TPM, or remote-attestation infrastructure once these targeted implementation defects are closed.
