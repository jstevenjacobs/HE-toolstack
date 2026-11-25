CHATGPT:
-------------------------------------------------------
Round-07 — ChatGPT independent council review
Paper-only review
Pinned source review

Target pin: cf4a80488dccd0c38de2641e9871050cb2998978

My review position: I am evaluating rev-3 as a new design, not carrying forward the rev-2 verdict automatically. In particular, the broker must demonstrate that it actually constrains execution and independently preserves evidence—not merely that the protocol describes those properties.

I have retrieved the pinned protocol, both broker drafts, both round-2 replies, and the ledger. The setup script and runner are material to this review: accepting the architecture requires examining their actual enforcement behavior, not just the proposed §3 controls.
1. Grok — re-evaluation
Requested statement: ACCEPT stands — I cannot independently endorse that statement on Grok's behalf.

The archived Grok reply is an ACCEPT of rev-2, not rev-3. Its reasoning does support retaining two important conclusions:
- A separate physical machine is not mandatory for the stated single-operator threat model.
- The limitation against a colluding owner must remain explicit.
Rev-3 preserves the latter in §3.8. That is correct. 
GitHub+1

Owner-labor honesty
I agree with the decision to make broker provisioning an owner-controlled operation. It is an appropriate additional responsibility because the owner must establish the boundary that removes Hermes's execution authority.

However, I found an important discrepancy:

The protocol describes one setup-script run (§1, §3.1, §8), but the actual script requires:
1. A provisioning invocation.
2. Manual registration of the broker's GitHub deploy key.
3. Manual service activation and health checks.
4. A second invocation with --confirm-cutover.
The script explicitly exits after phase 1 and requires a second execution for phase 2. 
GitHub+1


Therefore, the owner-labor estimate is not yet accurate.

Required correction: Count the two invocations and intervening manual actions honestly, or redesign the setup workflow to make the claimed one-run process real.

This is not an objection to owner-controlled cutover. It is an objection to understating its operational requirements.
2. ChatGPT — five required properties
Assessment distinguishes protocol intent from implementation evidence.
Required property	Verdict	Assessment
1. No direct execution	PARTIAL	§3.2
2. Capture outside execution boundary	MET — design intent	§3.4
3. No unlogged execution path	PARTIAL	§3.5
4. Remote append-only retention + external checkpoints	NOT MET	§3.7
5. Independent reconciliation	PARTIAL	§3.7

Property 1 — No direct execution
§3.2: PARTIAL.

I accept the functional principle of a dedicated execution account on the same host.

Physical host separation is not inherently necessary to satisfy my original requirement. The important distinction is whether Hermes can execute outside the controlled broker path.

However, there are two implementation concerns:
- The broker belongs to the Docker group. Docker socket access is effectively host-root-equivalent authority, so the broker is a highly privileged execution intermediary.
- The setup script's SSH-key discovery relies on matching textual identifiers (hermes or host_ed25519) in authorized-key entries. It does not establish that every actual Hermes credential is found and revoked.

GitHub+1
The second issue is especially important given the existing SSH access problems recorded in the project history.

Host separation is not my requirement. Effective execution-path isolation is.
Property 2 — Capture outside execution boundary
§3.4: MET as an architectural requirement; NOT YET DEMONSTRATED by the runner.

This is the strongest improvement in rev-3.

The broker has its own account, SSH key, and Git commit identity. It sends evidence directly to the remote repository rather than relying on Hermes to submit its own execution logs.

That addresses the central conflict identified in my rev-2 review. 
GitHub+1


However, the runner does not yet implement all the promised capture fields.

For example, its record contains argv, timestamps, exit status, stdout, and stderr, but does not actually calculate produced-artifact digests or preserve the complete original request as described in §3.4.

This is an implementation defect, not a reason to abandon the architecture.
Property 3 — No unlogged execution path
§3.5: PARTIAL.

I agree with the explicit exclusion rule:

An operation that cannot be observed or routed through the broker is excluded and classified UNPROVEN.

That is the correct treatment.

However, the broker runner currently accepts commands through a JSON request queue and executes the supplied argv. The implementation does not independently establish that every operation is constrained to the intended host-operation boundary.

There is also a plan-integrity problem:

The runner checks a SHA-256 digest over the plan's argv entries, but does not authenticate an owner signature or independently verify the signed transcript approval described in §3.3.

A matching digest establishes consistency, not authorization.

GitHub+2
Property 4 — Remote append-only retention and external checkpoints
§3.7: NOT MET.

This is a material gap.

Rev-3 substitutes Git history and push permissions for the originally requested remote append-only collector and external checkpoint mechanism.

GitHub-hosted evidence is useful, but the protocol does not establish:
- Enforced append-only retention against repository administrators.
- A mandatory signed broker commit.
- Mandatory external checkpoint publication.
- An independently verifiable checkpoint for every wave.
In particular, Rekor publication is conditional: it happens when reachable.

That is not equivalent to a required external checkpoint. 
GitHub


I would accept a properly configured protected evidence repository as a retention mechanism if its controls were specified and verified. But the current text does not establish that standard.
Property 5 — Independent reconciliation
§3.7: MET as a review requirement; PARTIAL as an implemented mechanism.

The protocol correctly requires council members to retrieve broker evidence independently and reconcile it against:
- The wave manifest.
- Transcript entries.
- Pass/fail/skip rows.
- Declared operations.
- Missing or unexplained records.
Mandatory REJECT for unexplained gaps is appropriate.

GitHub
However, reconciliation depends on trustworthy and complete broker records. The current runner's incomplete record fields and missing authentication of the plan mean this property cannot yet be considered operationally established.

3. Additional implementation defects
These findings materially affect whether the proposed broker can safely be installed.
A. The runner is not ready for execution
I found several specific defects in m0-broker-runner.py.
Finding	Consequence
No cryptographic plan-signature verification	A digest is not proof of owner authorization.
No independent request-digest calculation	The runner relies on the supplied digest rather than authenticating the request.
Broker commit and push errors are not checked	Evidence can fail to reach GitHub without the runner reliably stopping.
Requests are marked processed before successful execution and evidence publication	Failed operations can disappear from subsequent processing.
Git fetch/reset errors are not checked	The runner can operate on stale or unexpected repository state.
Artifact digests are not generated	The implementation does not fulfill §3.4's full capture specification.

These are visible directly in the runner's request-processing and commit/push logic. 
GitHub+1


The most consequential issue is the missing authentication of the plan. The protocol calls it a signed plan, but the implementation only checks a recomputed hash.

Required: The runner must fail closed unless it can verify the plan's authorization, integrity, wave identity, and validity.
B. The setup script needs additional hardening
Beyond the two-invocation discrepancy:
- An existing m0broker account is not guaranteed to receive the Docker group membership.
- The script does not itself start the service, despite creating its systemd unit.
- The SSH revocation procedure depends on a manually verified fingerprint list.
- The script does not independently verify that all alternate Hermes execution credentials have been removed.
- The evidence key registration and branch protection requirements are not fully automated or verified.

GitHub+2
These are fixable, but they should be corrected before the owner executes the setup.
C. The broker's trust boundary needs a more precise definition
The architecture says Hermes cannot execute outside the broker.

That is only true if all relevant execution channels are actually disabled or controlled.

The setup script currently focuses on SSH authorized keys. It does not establish that other possible channels, such as existing service credentials, alternative SSH identities, or other host-management interfaces, have been eliminated.

The §3.6 tests should verify the actual configured environment, not simply the expected behavior of four selected probes.
4. Is §3.6 sufficient?
NOT SUFFICIENT AS WRITTEN
The four-part test is a good cutover acceptance test:
1. Hermes SSH access denied.
2. Hermes Docker socket access denied.
3. Out-of-plan request refused and recorded.
4. Broker-authored evidence commit independently verified.
I would retain all four.

However, these tests establish selected properties at one point in time. They do not establish that the broker's plan authorization is trustworthy, that evidence publication cannot silently fail, or that alternative execution paths do not exist.

In particular, test (d) proves broker commit authorship, not completeness of execution capture.

My requirement: Keep §3.6 as a mandatory Wave-0 gate, but supplement it with implementation-level validation of the runner, credential revocation, and remote evidence-retention controls.

The test must remain a prerequisite to any evidence row claiming capture completeness. The current UNPROVEN rule is correct. 
GitHub+1

5. Verdict on rev-3
REJECT — current pin
This is not a rejection of the broker architecture.

It is a rejection of the current implementation and its claim that the five required properties have been established.

The central improvement is sound:
- Separate execution identity.
- Plan-gated operations.
- Broker-controlled evidence commits.
- Explicit treatment of unobservable operations.
- Independent council reconciliation.
- Honest residual-risk statement.
But the implementation does not yet substantiate the guarantees the protocol attributes to it.

I would not authorize the owner to execute this setup script at the current pin.
Required repairs for the next revision
Priority	Required repair
P0	Implement cryptographically authenticated, owner-approved execution plans.
P0	Fix runner failure handling, request processing, and evidence publication.
P0	Make the setup workflow's actual owner labor and cutover sequence accurate.
P0	Establish and verify complete Hermes credential revocation.
P1	Specify enforced remote append-only retention and mandatory external checkpoints.
P1	Complete the broker's artifact-digest and full-request capture implementation.
P1	Expand §3.6 validation to cover the actual execution and evidence boundaries.

I do not require a second physical host as a prerequisite. The same-host design remains acceptable in principle, provided its isolation and residual limitations are demonstrated honestly.
6. Wave-0 plan sequencing
Q4: ACCEPT the proposed sequencing, with one important condition.

The absence of workflows/m0-plans/ at the review pin does not invalidate a paper review of the architecture.

It is reasonable to create the operational plan during Wave 0 rather than prematurely inventing commands and execution details.

However, there is a dependency that must be resolved:

The broker runner requires workflows/m0-plans/open.json before it can execute anything. Therefore:
1. The initial Wave-0 plan must be drafted.
2. Its exact commands and digest must be established.
3. The owner must confirm its authority and scope.
4. The broker must authenticate that approval before executing the listed commands.
5. The completed Wave-0 evidence pack must receive council validation before its rulings bind or progression occurs.
Do not allow the absence of a finalized plan to become an exception to plan-gated execution.

This sequencing is compatible with §2a and §3.3. 
GitHub+1

7. Authorization and final disposition
Question	ChatGPT disposition
Grok's previous ACCEPT	Cannot independently renew; archived ACCEPT was for rev-2
Owner-labor honesty	Correction required
Same-host broker	Acceptable in principle
Five required properties	Not all established
§3.6 cutover test	Retain, supplement
Missing Wave-0 plan	Acceptable sequencing
Rev-3 verdict	REJECT

Authorization: NONE.

I do not authorize Wave 0 at this pin.

Even if Grok independently renews ACCEPT, the required 2/2 acceptance at the identical pin has not been achieved.

The existing SSH blocker also remains relevant: the ledger records that both ports 2222 and 22 were refusing connections and that the owner must restore access before Wave 0. 
GitHub


The following restrictions remain unchanged:
- No destructive operations.
- No deployment authorization.
- No ticket-execution authorization.
- No bypass of DESIGN-REVIEW §10 HARD STOP.
- No assumption that protocol acceptance establishes runtime readiness.
8. Recommended next step
I recommend a rev-4 repair focused narrowly on the broker implementation rather than another architectural redesign.

The key decision is already made: a same-host, independently credentialed execution broker is an acceptable architecture for this project's stated threat model.

The next revision needs to make the implementation match that architecture.

I would specifically avoid adding a second machine, TPM, or remote-attestation infrastructure unless the repaired implementation demonstrates that those controls are necessary.

The objective should be to close the actual enforcement gaps without expanding the system's complexity unnecessarily.

Final ChatGPT position: REJECT rev-3 at cf4a80488dccd0c38de2641e9871050cb2998978. No Wave-0 authorization.