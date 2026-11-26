CHATGPT:
-------------------------------------------------------
Round-07 — ChatGPT independent council review
Paper-only review
REJECT — current pin

Target: 1ce2b3cdb7717fe35428d1fdfd20a4e99a736693

Scope: Protocol rev-4, broker runner, setup script, P0 test suite, prior council replies, and ledger. All source inspection was against the exact pinned raw URLs.
Executive verdict
Rev-4 makes substantial progress. In particular, it corrects the most important defects I identified in rev-3:
- Cryptographic owner authorization replaces digest-only authorization.
- The runner checks Git operations and does not mark requests processed before publication.
- Full request and artifact-digest capture is implemented.
- Owner cutover labor is itemized more honestly.
- Credential inventory replaces unreliable key-name matching.
- The protocol no longer overclaims signed broker commits.
- The same-host architecture and §3.8 limitation remain unchanged.
However, I found a new P0 defect in request processing that prevents acceptance.

The runner maintains its processed-request set only in memory. It does not durably acknowledge or remove processed requests from the queue. Consequently, restarting the systemd service can cause previously executed operations to execute again.

There are also discrepancies between the stated single-pass behavior and the actual runner, and the credential-revocation procedure needs another correction.

These are implementation problems, not architectural objections.

1. Grok — previous ACCEPT
Grok's archived re-pin-2 reply explicitly accepted rev-3, including its §3.8 limitation and owner-controlled cutover. 
GitHub


I cannot issue a new verdict on Grok's behalf.

My assessment is that the changes in rev-4 do not undermine the architecture or the limitation statement Grok previously accepted.

Requested Grok disposition: ACCEPT stands at this pin remains a reasonable position for Grok to consider, subject to his independent inspection of the implementation defects identified below.

In particular, the owner-labor honesty improvement is genuine in §8, although there is still a conflicting count in §6.
2. ChatGPT — seven-row repair assessment
These are the seven required repairs from my re-pin-2 response.
#	Required repair	Rev-4 verdict	Evidence
1	Cryptographically authenticated plans	MET	§3.3; runner 47–76; P0-1, P0-2
2	Runner failure handling and publication	PARTIAL	Runner 127–226
3	Honest owner-labor accounting	PARTIAL	§8; §6
4	Verified Hermes credential revocation	PARTIAL	§3.1; setup 31–53
5	Remote append-only retention and external checkpoints	PARTIAL	§3.5, §3.7
6	Full request and artifact capture	MET	§3.4; runner 178–198; P0-3
7	Expanded bypass-detection validation	PARTIAL	§3.6; P0-1 through P0-5

Repair 1 — Cryptographic plan authorization
MET
This is a proper repair.

The runner now:
- Requires the plan, detached signature, and allowed-signers file.
- Uses ssh-keygen -Y verify.
- Recomputes the digest from the actual argv.
- Uses the signed plan's argv for execution.
- Refuses execution when signature verification fails.
- Checks the plan's internal digest for consistency.
The distinction between authorization and integrity is now correctly expressed: the signature authorizes; the digest establishes consistency.

GitHub+2
P0-1 and P0-2 exercise unsigned and tampered-plan rejection, respectively. P0-3 exercises execution under a valid signature. 
GitHub+1


One small documentation discrepancy remains: §3.3 says the owner principal is declared in the plan, whereas the runner obtains it from broker configuration (--owner-principal). This should be made consistent, but it does not negate the cryptographic authorization improvement.
Repair 2 — Runner failure handling and publication
PARTIAL
The improvements are real.

git_checked() now checks return codes. Fetch, reset, commit, and push failures are surfaced. Requests are added to the in-memory processed set only after a successful push. Repeated push failure terminates the runner non-zero. 
GitHub+1


However, there is a serious new problem.

P0 finding: request replay after restart.

At runner initialization:
processed: set[str] = set()



This set exists only in memory.

The queue is read from workflows/m0-evidence/requests.jsonl. Successfully processed requests are never durably acknowledged, removed, or moved to a completed queue.

The systemd unit uses Restart=on-failure. On restart, the processed set is empty again. The runner fetches the remote branch, reads the same historical requests, and can execute them again.

GitHub+2
This creates an at-least-once execution model without an explicit idempotency contract.

That is unacceptable for a broker whose plans may contain state-changing operations.

Consider:
1. A broker executes a planned operation successfully.
2. The evidence push succeeds.
3. The runner subsequently fails or is restarted.
4. Its in-memory processed set disappears.
5. The old request is read again.
6. The operation executes a second time.
Even worse, an operation can execute successfully but its evidence push fail. The runner retries from the remote queue and may execute that operation again before publication succeeds.

Required correction:

Implement durable request-state tracking with a stable request ID and execution lifecycle.

At minimum:
- Persist an execution-started record before invoking the command.
- Persist the execution result and publication state.
- On restart, recognize previously executed requests.
- Never automatically repeat an operation whose execution outcome is uncertain.
- Require an explicit, separately authorized recovery decision for uncertain executions.
The correct behavior for an uncertain execution is UNPROVEN, not automatic re-execution.

This is my principal reason for rejecting rev-4.
Repair 3 — Owner-labor honesty
PARTIAL
Section 8 is substantially better.

It explicitly identifies:
- Phase-1 provisioning.
- GitHub deploy-key registration.
- Phase-2 fingerprint inventory.
- Confirmation and removal.
- Additional verification activities.
It no longer presents the entire operation as one trivial script invocation. 
GitHub


However, §6 still says:
1 setup-script run (§3.1)

The actual process includes phase 1, a phase-2 inventory invocation, and a subsequent phase-2 confirmation invocation.

The detailed §8 count is the authoritative description, but §6 should be corrected.

Required correction: Make the Wave-0 table consistent with §8. Describe the complete owner-run cutover sequence rather than calling it one script run.

This is a documentation correction, not an architectural blocker.
Repair 4 — Verified credential revocation
PARTIAL
The fingerprint inventory is an improvement over rev-3's substring-based identification.

The setup script enumerates authorized-key files and uses ssh-keygen -lf to list their fingerprints. It then empties the authorized-key files. 
GitHub


However, I found two problems.

Problem A — The removal is broader than Hermes's credentials.

The script empties every matching authorized-key file:
for hk in /home/*/.ssh/authorized_keys /root/.ssh/authorized_keys; do
  [[ -f $hk ]] && : > "$hk"
done


This is not selective Hermes credential revocation. It removes all authorized SSH keys for all matching accounts, potentially including legitimate owner and administrative access.

The protocol must explain how owner access is preserved or restored before this operation is permitted.

Problem B — The promised per-fingerprint verification is not implemented.

Section 3.6 says every credential in the inventory is re-probed after removal.

The script's actual instruction is to attempt SSH using <hermes-key> from the container. It does not implement an iteration over every inventoried fingerprint.

GitHub+1
Required correction:
- Preserve an explicitly identified owner recovery credential or provide a verified local recovery mechanism.
- Re-probe every inventoried credential, not just one representative Hermes identity.
- Record each result separately.
- Make any unverified credential an automatic cutover failure.
I accept the underlying design: removing Hermes's host authority is the right objective. The implementation must not inadvertently remove the owner's recovery access.

Repair 5 — Remote retention and external checkpoints
PARTIAL
I accept the architectural change in §3.7.

The protocol now distinguishes three things:
1. Private evidence repository: full records and stdout/stderr.
2. Public retention pack: per-wave manifest, record digests, artifact digests, and evidence-branch HEAD.
3. Optional Rekor publication: additional transparency evidence when reachable.
It also correctly describes broker commits as plain commits, authenticated through push rights, the owner-signed plan, and council-side verification—not embedded commit signatures. 
GitHub+1


I do not require Rekor to be mandatory.

A public retention pack is an acceptable alternative for this infrastructure. I do not want to introduce another external service merely to satisfy a theoretical preference.

However, one control is missing: the protocol specifies branch protection for the private evidence repository but does not establish equivalent protection for the public retention-pack repository.

The assertion that public packs survive private-repository deletion is useful, but it does not establish protection against deletion or history rewriting of the public repository itself.

Required correction:

Specify and verify that:
- Each wave's retention pack is published to the public repository.
- Its commit is pinned in the wave evidence pack.
- The public repository's relevant branch has force-push and deletion protection.
- Council independently verifies the pack digest and corresponding evidence-branch HEAD.
This can be a Wave-0 configuration and verification requirement.

I will accept the public retention pack as the standing checkpoint mechanism. Rekor remains optional.
Repair 6 — Full request and artifact capture
MET
The implementation now includes:
- Original request line.
- Exact executed argv.
- Request and command digests.
- Start and end timestamps.
- Exit code.
- Standard output and standard error.
- Execution error information.
- Artifact SHA-256 digests.
- Authenticated plan digest and signer identity.
The implementation is visible in runner lines 178–198. 
GitHub


P0-3 checks the presence of the principal capture fields. 
GitHub


I accept this repair.

The request replay defect identified under repair 2 still affects the reliability of these records, but does not negate the fact that the capture fields themselves are now implemented.
Repair 7 — Expanded bypass-detection validation
PARTIAL
The five-leg §3.6 test is a meaningful improvement.

The most important addition is (e): council independently verifies the actual signed plan and confirms that a tampered variant is rejected.

The setup-script fingerprint inventory also improves the revocation evidence. 
GitHub


The P0 test suite contains eight assertions covering:
Test	Purpose
P0-1a	Unsigned plan cannot execute
P0-1b	Unsigned plan generates refusal
P0-2	Tampered plan cannot execute
P0-2b	Tampering is identified as signature failure
P0-3	Signed in-plan execution and capture
P0-4	Out-of-plan execution refused
P0-5	Broker records reach remote branch
P0-5b	Remote branch contains actual record files


GitHub+1
These are appropriate tests. They use real signature and Git mechanisms rather than mocks, according to the test source.

However, I have inspected the test source, not executed the suite. I am not independently certifying the claimed 8/8 runtime result.

More importantly, the suite does not test:
- Restart and replay of previously executed requests.
- A command that executes successfully followed by a failed evidence push.
- Recovery after an uncertain execution outcome.
- The complete per-fingerprint revocation process.
- Preservation of owner SSH recovery access.
- Public retention-pack protection and independent verification.
- The claimed single-pass execution mode.
The tests establish important properties, but not the complete operational behavior.

Required correction: Add regression tests for these cases before the broker is accepted.

3. Specific additional finding: --once is not implemented
The prompt says single-pass mode has been implemented.

I cannot verify that claim in the pinned runner.

The argument parser defines:
- --daemon
- --verify
There is no --once argument.

Instead, the runner contains:
max_passes = 2 if not a.daemon else 10**9



Consequently, the non-daemon runner executes up to two passes, not one. 
GitHub+1


The P0 test harness also invokes the runner without --once. 
GitHub


This is a direct mismatch between the stated repair and the implementation.

Required correction: Implement an explicit --once mode that performs exactly one fetch/process/publish cycle and exits. Add a test proving it performs one cycle.

The systemd daemon can continue using its separate daemon mode.

4. Is the rev-4 architecture still within scope?
YES
I confirm that rev-4 stayed within my previous architectural instruction.

It did not introduce:
- A second physical machine.
- TPM.
- Hardware root of trust.
- Remote attestation.
- A new external evidence-collection architecture.
The broker remains a dedicated account and identity on the existing host.

The §3.8 limitation is unchanged and remains acceptable.

I specifically accept the explicit acknowledgment that Docker-group membership is host-root-equivalent authority, and that the broker's security therefore depends on its plan gate and fail-closed behavior. 
GitHub+1


I am not requesting an architectural redesign.

The required changes are confined to execution-state correctness, recovery, cutover safety, and validation.

5. Additional P0 finding: malformed requests disappear silently
There is another issue relevant to the no-unlogged-path requirement.

In runner lines 147–151:
try:    req = json.loads(line)except json.JSONDecodeError:    continue



Malformed queue entries are silently skipped.

Requests without an ID are also skipped by the subsequent filtering logic.

This contradicts §3.3's requirement that queued requests receive broker-committed refusal records when they cannot be authorized. 
GitHub+1


Required correction:

Every queue line must receive a disposition:
- Valid and authorized: execute.
- Valid but unauthorized: refusal record.
- Malformed: invalid-request refusal record.
- Missing or invalid request ID: invalid-request refusal record.
No input should disappear silently.

6. Q4 — External checkpoints and Wave-0 sequencing
Decision: Rekor is optional. Public retention packs are acceptable.

I do not require another public transparency service.

I do require the public retention repository to have explicitly defined protection against force-push and deletion, with independently verifiable per-wave pack hashes.

This is a bounded infrastructure requirement, not an architectural redesign.

The actual verification can be incorporated into Wave 0, provided that:
1. The public repository protection is configured.
2. A test retention pack is published.
3. The council independently retrieves it.
4. The pack digest and evidence-branch HEAD match.
5. The result is included in the Wave-0 evidence pack.
The absence of Rekor must never be classified as a failure if the required public retention mechanism works.

GitHub+1

7. Consolidated repair requirements for rev-5
I recommend keeping this repair cycle narrowly scoped.
Priority	Required change	Acceptance evidence
P0	Durable request-state tracking	Restart/replay regression tests
P0	Prevent automatic re-execution after uncertain outcomes	Failed-push and recovery tests
P0	Preserve owner SSH recovery access during cutover	Setup test and post-cutover access verification
P0	Re-probe every inventoried credential	Per-fingerprint verification records
P0	Record malformed and unidentified requests	Refusal-record tests
P1	Correct §6 owner-labor description	Cross-section consistency
P1	Implement actual --once mode	Single-cycle regression test
P1	Protect public retention repository	Branch-protection evidence
P1	Verify public retention packs independently	Pack digest and HEAD verification

The first five are acceptance blockers. The remaining three can be resolved through the Wave-0 preparation and validation process, but must be explicitly closed before their respective guarantees are claimed.
8. Final verdict
REJECT — rev-4
This is a narrower rejection than rev-3.

I accept the architecture and most of the implementation repairs. I am not asking for another architecture cycle.

The remaining blockers are concrete:
1. Request replay after systemd restart.
2. Uncertain execution recovery.
3. Potential loss of owner SSH recovery access.
4. Incomplete credential-by-credential revocation verification.
5. Silent disappearance of malformed requests.
These defects undermine the exact properties the broker is supposed to guarantee.
Authorization decision
Question	ChatGPT
Cryptographic plan authorization	ACCEPT
Broker capture implementation	ACCEPT
Same-host architecture	ACCEPT
§3.8 threat-model limitation	ACCEPT
Honest §8 labor accounting	ACCEPT, with §6 correction
§3.6 five-leg test	ACCEPT, with additional tests
Optional Rekor/public retention alternative	ACCEPT, subject to repository protection
Runner implementation	REJECT
Rev-4 overall	REJECT

Wave-0 authorization: NOT GRANTED.

Grok's new verdict is not yet available to me. Regardless, ChatGPT's verdict is REJECT, so the required 2/2 ACCEPT condition has not been satisfied.

The cleared SSH connectivity blocker is welcome, but it does not resolve these implementation defects.

The following restrictions remain:
- No Wave-0 execution authorization.
- No destructive operations.
- No deployment authorization.
- No ticket-execution authorization.
- DESIGN-REVIEW §10 HARD STOP remains unchanged.
- No assumption that staged code or passing tests establish runtime readiness.
9. Recommendation
I recommend rev-5 be a targeted broker reliability repair, not another redesign.

The most important engineering change is to make request execution recoverable across process failures without silently repeating operations.

That requires treating execution and evidence publication as separate durable states, rather than treating an in-memory processed set as the source of truth.

The broker must be able to answer three questions after any restart:
1. Was this operation authorized?
2. Did it execute, or is its outcome uncertain?
3. Was its evidence successfully published?
If it cannot answer those questions, the operation must remain UNPROVEN and must not execute again automatically.

Once these issues are repaired and demonstrated with regression tests, I expect to be able to reconsider acceptance without requesting any architectural changes.

Final ChatGPT disposition: REJECT rev-4 at 1ce2b3cdb7717fe35428d1fdfd20a4e99a736693. No Wave-0 authorization.