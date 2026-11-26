# Round-07 — Council re-pin prompt: protocol rev-6 (re-pin-4 repair cycle)

Round: Round-07 (M0 interview protocol), fifth repair cycle. Targets: ChatGPT and Grok (voting members); Claude (advisor seat — runner scope, your re-pin-4 conditions).

## Declared pin

`3f3b04a3ea0a83afd4964e1a17287467a0121988` (branch `dp/round-07-m0-interview`)

## Raw sources at this exact pin

- Protocol **rev-6**: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/workflows/m0-interview-protocol.md
- Broker runner (rev-6): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/scripts/m0-broker-runner.py
- Broker setup script (rev-6): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/scripts/m0-broker-setup.sh
- Credential-revocation script (rev-6): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/scripts/m0-broker-revoke-keys.sh
- Broker test suite (rev-6, executable evidence, read as text): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/scripts/qa/test_broker_p0.py
- Your re-pin-4 replies, archived verbatim: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/workflows/adviser-input/round-07/reply-chatgpt-protocol-repin4.md, https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/workflows/adviser-input/round-07/reply-grok-protocol-repin4.md, https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/workflows/adviser-input/round-07/reply-claude-protocol-repin4.md
- Ledger (row `DP-R7-rev6`): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/3f3b04a/workflows/ledger.md

## Correction on the record, before anything else

The rev-5 review prompt (re-pin-4) asserted the test suite covered "P0-12…P0-17" and that P0-11 exercised the inventory-wide revocation verification. At pin `8509096` both claims were FALSE: P0-12…P0-17 were named only in the module docstring with zero test bodies, and P0-11 still asserted rev-5 output strings — ChatGPT's repair 2/4 evidence did not exist at that pin. This is the second prompt-accuracy failure in this round (after the re-pin-3 `--once` claim) and is recorded as such in the rev-6 changelog and ledger row DP-R7-rev6. At THIS pin the tests exist, execute, and pass; every claim below was verified against the committed tree before sending, and each is paired with the specific test that proves it so you can re-check the claim-to-code mapping mechanically.

## What rev-6 changed (mapped to your re-pin-4 inputs)

Architecture untouched: §3.8 is byte-identical to the wording Grok accepted — verified mechanically (`git show 8509096:… | awk '/^\*\*3.8/,/^## 4/'` vs the same slice at `3f3b04a`; zero diff). No second machine, no TPM, no attestation. Every change below is ChatGPT's "targeted implementation repair" category or a Claude condition.

### ChatGPT repair 1 — fsync durability of the durable ledger
`durable_write` (runner) now writes a temp file, `fsync`s it, renames into place, and `fsync`s the PARENT DIRECTORY — neither the record nor the rename can vanish on power loss. **Proof:** P0-12a (mock-observed: ≥2 fsync calls, file + dir) + P0-12b (atomic real write survives concurrent readers seeing only old-or-new content).

### ChatGPT repair 2 + 4 — inventory-wide verification + strict recovery grammar
`scripts/m0-broker-revoke-keys.sh` now takes the pre-cutover inventory (`hermes-credentials.txt`, the `ssh-keygen -lf` ledger setup.sh emits) as an INPUT: every inventoried credential gets an expected state (revoked ⇒ ABSENT, retained ⇒ PRESENT), each re-probed live against the real `authorized_keys`, all results consolidated as `EXPECTED=… OBSERVED=… OK|FAIL` lines into ONE `cutover-verification.txt`; any FAIL exits non-zero. Recovery declaration accepts exactly `M0_RECOVERY=local-console` or `M0_RECOVERY=keep:<SHA256:fpr>`; rev-5's `recovery:<fpr>` form is REMOVED and refused (protocol §3.1 revved to match). `M0_INVENTORY` unset ⇒ the run is itself a FAILED verification (incomplete = failed). **Proof:** P0-11a (keep:+inventory: revoked keys ABSENT, kept key PRESENT, consolidated file), P0-11b (declared-but-absent recovery key ⇒ `EXPECTED=PRESENT OBSERVED=ABSENT FAIL` + non-zero exit), P0-11b2 (inventory-less run fails by design), P0-11c/11d (no recovery declaration refused; old `recovery:<fpr>` form refused).

### ChatGPT repair 3 — request-ID collision handling
A reused request id whose line content differs produces an explicit `ID-COLLISION` refusal record preserving BOTH the original and conflicting `request_line_sha256`; the colliding argv NEVER executes; the original disposition stands. **Proof:** P0-13a (collision refused, both hashes on record) + P0-13b (side-effect counter proves the colliding command never ran).

### Claude condition 1 — plan-pinned artifacts verified PRE-SPAWN
Every plan command carries `artifacts` (path + SHA-256); the runner verifies each digest BEFORE spawning and refuses on mismatch. **Proof:** P0-14a (post-signature artifact swap ⇒ `ARTIFACT-MISMATCH` refusal citing observed vs pinned digests) + P0-14b (nothing executed; refusal durable).

### Claude condition 2 — `max_runs` use-budget
`max_runs` is enforced as a USE budget keyed to the canonical plan+argv digest, recorded durably per execution — a FRESH request id cannot reset it. **Proof:** P0-15 (budget exhausted ⇒ `BUDGET-EXHAUSTED` refusal persists across fresh ids).

### Claude condition 3 — plan ABSENT ⇒ PENDING, not refusal
With no signed plan present, queued requests get NO disposition and stay PENDING — authorization unverifiable ≠ verified-absent, so a later owner signature authorizes the SAME id; absence can never permanently blacklist. **Proof:** P0-16a (plan absent ⇒ pending, no records, nothing executed) + P0-16b (after owner signs, the same id executes; queue file itself is never rewritten by the broker).

### Claude condition 4 — spawn OSError ⇒ definite record
A spawn failing with OSError writes a COMPLETE failure record immediately (`spawn_succeeded: false`, reason `SPAWN-FAILED`) — never a `started` state that later hardens into UNPROVEN. **Proof:** P0-17a (mocked OSError ⇒ definite record) + P0-17b (after restart the definite record is NOT rewritten as UNPROVEN).

### Strengthened P0-10 and honest P0-11 (the re-pin-4 false-claim repairs)
P0-10 now asserts `--once` performs EXACTLY ONE counted cycle (decision-line counted, `rc == 0`) — not the old weak `returncode in (0,3)`. P0-11 asserts the rev-6 output format against a real sshd + real inventory file.

## Test suite status at this pin

`scripts/qa/test_broker_p0.py`: 17 scenarios / 31 assertions, **31 PASS / 0 FAIL** (full transcript retained; suite runs real `ssh-keygen -Y` signatures, real git remotes, a real `sshd` for the revocation legs, and a real rejecting `pre-receive` hook — no network mocks). Docstring scenario list and test bodies are now one-to-one (the re-pin-4 defect). Repo gates: 27 PASS / 0 FAIL.

## Questions for this re-pin

**ChatGPT (voting):** Q1 — are your four re-pin-4 P0 repairs each adequately repaired at this pin, per the claim→test mapping above (verify the mapping, not the prose)? Q2 — do the two recorded prompt-accuracy corrections satisfy your accuracy standard, or does the repetition of a false prompt claim (P0-12…17) itself warrant a process remedy beyond the recorded correction? Q3 — vote on rev-6 at `3f3b04a…`.

**Grok (voting):** §3.8 byte-identical at this pin (slice-diff above). Q1 — does your ACCEPT stand? Q2 — the rev-6 changelog records two prompt-accuracy failures in this round; any view on whether the council should require a pre-send claim-verification step (e.g. every prompt claim cites the test id and line that proves it, checked mechanically) as a process rule for future re-pin prompts? Vote on rev-6 at `3f3b04a…`.

**Claude (advisor, runner scope):** your four conditions map to P0-14/15/16/17 above at this pin. Do they discharge your ACCEPT-WITH-CHANGES conditions, and does that convert your runner-scope vote to ACCEPT (advisor advisory)?

## Verdict format

Reply with: pin reviewed (full SHA), per-question answers, vote (ACCEPT / ACCEPT-WITH-CHANGES / REJECT) + blocking items if any. Paper-only review; run nothing.
