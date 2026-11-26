# Round-07 — Council re-pin prompt: protocol rev-5 (broker reliability repair)

Round: Round-07 (M0 interview protocol), fourth repair cycle. Target: both council members.

## Declared pin

`85090961562649a16885c382b5be5e9520810d97` (branch `dp/round-07-m0-interview`)

## Raw sources at this exact pin

- Protocol **rev-5**: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/workflows/m0-interview-protocol.md
- Broker runner (rev-5, durable execution state): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/scripts/m0-broker-runner.py
- Broker setup script (rev-5, two-phase + selective cutover): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/scripts/m0-broker-setup.sh
- Credential-revocation script (rev-5, NEW — selective by fingerprint): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/scripts/m0-broker-revoke-keys.sh
- Broker test suite (rev-5, executable evidence, read as text): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/scripts/qa/test_broker_p0.py
- Your re-pin-3 replies, archived verbatim: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/workflows/adviser-input/round-07/reply-grok-protocol-repin3.md and https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/workflows/adviser-input/round-07/reply-chatgpt-protocol-repin3.md
- Ledger: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/8509096/workflows/ledger.md

## Correction on the record, before anything else

The rev-4 review prompt (re-pin-3) asserted "`--once` is implemented (runner)". That claim was FALSE at pin `1ce2b3c…`: the rev-4 runner had no `--once` flag and its non-daemon mode ran up to two passes. ChatGPT caught it. The error was in the prompt, not the code, but a prompt assertion is a project assertion — it is recorded as such in the rev-5 changelog and ledger row DP-R7-rev5. At this pin the flag exists and is proven by regression test P0-10 (exactly one cycle, exit 0, second invocation makes no further passes). No other rev-4 prompt claim is walked back; re-verify any you doubt against the raw sources above.

## What rev-5 changed (mapped to ChatGPT re-pin-3 §7)

Architecture untouched: §3.8 byte-identical to the wording Grok accepted (`git diff 1ce2b3c..8509096` shows zero §3.8 changes); no second machine, no TPM, no attestation. All changes are ChatGPT's recommended "targeted broker reliability repair".

**P0-1 (replay after restart) — durable request-state machine.** The in-memory `processed` set is gone. `Ledger` (runner, `class Ledger`) persists one JSON file per request id under a state dir (`ReadWritePaths=/opt/m0-broker`), fsynced (`durable_write`), with statuses `started` → `executed`/`dispositioned` → `published`. Every pass skips any id whose state exists: a decided request can NEVER re-execute on restart (test P0-6: two full runner cycles, side-effect counter stays 1).

**P0-2 (uncertain outcomes) — UNPROVEN discipline.** `started` is written durably BEFORE the subprocess spawns. A restart that finds `started` treats the outcome as uncertain: the runner writes an UNPROVEN refusal record and refuses to re-execute; resumption requires a separate explicit owner recovery decision (§3.3 rev-5 text). Nothing is auto-repeated (test P0-8a/8b). Executed-but-unpublished evidence retries the PUBLISH only, never the command (P0-7a/7b, exercised against a real rejecting `pre-receive` hook).

**P0-3 (owner recovery access) — SELECTIVE revocation.** Blanket `authorized_keys` emptying is removed from the codebase. New `scripts/m0-broker-revoke-keys.sh` removes credentials BY FINGERPRINT from an owner-supplied list (`M0_REVOKE_FPR`), and REFUSES to run unless the owner declares a recovery path (`M0_RECOVERY=keep:<fpr>` — that key must remain present and usable — or `recovery:<fpr>` removed-but-announced, or `local-console`). Non-matching keys are untouched (test P0-11a: Hermes keys gone, owner key kept; P0-11c: no declaration ⇒ abort).

**P0-4 (per-fingerprint verification).** The revoke script re-probes EVERY inventoried fingerprint after removal and writes `cutover-verification.txt` with one line per credential (PRESENT/ABSENT vs declared state); any wrong-state entry exits non-zero ⇒ automatic cutover failure (§3.1, §3.6(a)). §3.6(a) then re-attempts each revoked key from the container, each result recorded separately (test P0-11b).

**P0-5 (silent disappearance).** Every queue line receives a disposition: valid+authorized ⇒ execute; valid+unauthorized ⇒ refusal; malformed JSON ⇒ `invalid-request` refusal; missing/invalid id ⇒ `invalid-request` refusal under a synthetic `noid-<hash>` id (runner `run_pass`; test P0-9: both malformed kinds produce refusal records, nothing dropped).

**P1 (owner labor §6 vs §8).** §6 wave table and §8 item 1 now carry the SAME sequence: phase-1 run, GitHub deploy-key registration, phase-2 inventory run, fingerprint-list + recovery declaration, confirm run — 3 script invocations + 1 web act + 1 supply in both sections. §3.1's principal wording now matches the runner (principal pinned in broker config, not declared by the plan — repair 1's documentation nit fixed).

**P1 (`--once`).** Explicit single-pass mode implemented and regression-tested (P0-10); systemd uses `--daemon` (unit unchanged: `Restart=on-failure`, `ExecStart=… --daemon` — the durability contract now makes restarts safe, which is §3.6(f)'s new leg).

**P1 (public retention repo).** §3.5 rev-5: the public repo carries the SAME protection contract as the private one — force-push + deletion disabled, each wave's pack commit pinned by digest in that wave's evidence pack, council independently retrieves pack and verifies pack digest + evidence-branch HEAD at every wave close; a test pack is published and council-fetched during Wave 0 (ChatGPT re-pin-3 §6 five steps adopted verbatim as Wave-0 exit criteria). Rekor remains optional and its absence is never classified as a failure when the pack mechanism verifies.

Executable evidence: `scripts/qa/test_broker_p0.py` — 11 scenarios / 18 assertions, all green, real `ssh-keygen -Y`, real git remotes, real rejecting hook, real filesystem state, no mocks: P0-1a/b, P0-2/2b, P0-3, P0-4, P0-5/5b carried over unchanged; P0-6, P0-7a/7b, P0-8a/8b, P0-9, P0-10, P0-11a/b/c new. Gates 27 PASS / 0 FAIL.

## Questions

1. **Grok:** your ACCEPT stood at `1ce2b3c…`. Rev-5 is another implementation-only cycle inside the architecture you accepted: §3.8 byte-identical (verifiable: diff the two pins — the protocol hunk touches every other section and not §3.8), labor count moved from ~4 to ~4–5 interactions (revocation became selective + per-credential-verified), §3.6 grew a sixth leg (durability contract: unit file + P0-6/7/8). Does your ACCEPT stand at `8509096…`? State explicitly: "ACCEPT stands at this pin" or the change you require.
2. **ChatGPT:** for each of your five re-pin-3 P0 blockers and three acceptance-relevant P1s, state MET (cite § / runner symbol / test ID) or NOT MET (precisely what is missing). Judge specifically: the started/executed/published ledger + UNPROVEN rule vs your three post-restart questions ("authorized? executed-or-uncertain? published?"); P0-7's rejecting-hook scenario vs your "executes successfully but evidence push fails" case; the revoke script's recovery declaration + P0-11a vs "must not inadvertently remove the owner's recovery access"; per-fingerprint `cutover-verification.txt` vs repair 4; P0-9 disposition-for-every-line vs finding 5. Also confirm your §7 note "The first five are acceptance blockers. The remaining three…" is satisfied, and whether the false `--once` claim in the rev-4 prompt (corrected above, recorded in the changelog) changes your acceptance conditions in any way beyond what you've already required.
3. **Both:** verdict on rev-5: ACCEPT / ACCEPT-WITH-CHANGES / REJECT. 2/2 ACCEPT at this pin ⇒ Wave 0 authorized to begin only (§9): owner runs the cutover sequence, §3.6 six-leg test (including the public test-pack fetch + digest verification), C1/C2 host prep via broker, zero destructive ops. Wave-0 rulings still need their own evidence pack and 2/2 validation before they bind (§2a). R-4/R-5/R-7 stay recorded exceptions until Wave-3 live evidence. DESIGN-REVIEW §10 HARD STOP untouched.
4. **ChatGPT:** you wrote you expect to "reconsider acceptance without requesting any architectural changes" once these repairs land with regression tests. If your five blockers read MET at this pin, is rev-5 accepted as-is, or does anything in rev-5 — including the prompt-accuracy incident above — still block a clean ACCEPT?

No authorization is granted or assumed by this prompt beyond what §9 and the HARD STOP (DESIGN-REVIEW §10) already allow.
