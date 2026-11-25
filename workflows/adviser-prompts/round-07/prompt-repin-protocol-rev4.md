# Round-07 — Council re-pin prompt: protocol rev-4 (broker implementation repair)

Round: Round-07 (M0 interview protocol), third repair cycle. Target: both council members.

## Declared pin

`1ce2b3cdb7717fe35428d1fdfd20a4e99a736693` (branch `dp/round-07-m0-interview`)

## Raw sources at this exact pin

- Protocol **rev-4**: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/1ce2b3cdb7717fe35428d1fdfd20a4e99a736693/workflows/m0-interview-protocol.md
- Broker runner (rev-4, fail-closed): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/1ce2b3cdb7717fe35428d1fdfd20a4e99a736693/scripts/m0-broker-runner.py
- Broker setup script (rev-4, two-phase): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/1ce2b3cdb7717fe35428d1fdfd20a4e99a736693/scripts/m0-broker-setup.sh
- Broker P0 test suite (executable evidence, read as text): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/1ce2b3cdb7717fe35428d1fdfd20a4e99a736693/scripts/qa/test_broker_p0.py
- Grok re-pin-2 reply (ACCEPT): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/1ce2b3cdb7717fe35428d1fdfd20a4e99a736693/workflows/adviser-input/round-07/reply-grok-protocol-repin2.md
- ChatGPT re-pin-2 reply (REJECT + 7-row repair table): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/1ce2b3cdb7717fe35428d1fdfd20a4e99a736693/workflows/adviser-input/round-07/reply-chatgpt-protocol-repin2.md
- Ledger: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/1ce2b3cdb7717fe35428d1fdfd20a4e99a736693/workflows/ledger.md

## Rules

Paper-only review; fetch raw URLs only; cite by section; first-hand verdicts; Hermes is not a trust root.

## Context for reviewers

Re-pin-2 at `cf4a804`: Grok **ACCEPT** (§3.8 limitation preserved; §8 labor honesty accepted; Q4 sequencing confirmed). ChatGPT **REJECT** — architecture accepted in principle, implementation rejected, with an explicit instruction: narrow implementation repair, no architectural redesign, no second machine, no TPM, no remote-attestation. Rev-4 does exactly that. The §3 architecture and §3.8 limitation statement (Grok's accepted wording) are UNCHANGED. What changed:

1. **§3.3 — authorization is now cryptographic.** `workflows/m0-plans/open.json` must carry an OpenSSH detached signature (`open.json.sig`) verifying via `ssh-keygen -Y verify` against an owner-pinned `allowed_signers` file. Empty owner-key list ⇒ nothing executes. Digest proves consistency; signature proves authorization. Request digests are recomputed from the argv the broker itself will execute; caller-supplied digests are recorded, never trusted.
2. **Runner failure paths checked.** Every git step (fetch/reset/write/commit/push) exit-checked; `published` set only from a confirmed push; repeated push failure exits non-zero so systemd restarts with backoff — a stalled evidence pipeline is loud, not silent. Self-identity guard: non-broker committers ⇒ refuse, don't crash.
3. **§3.4 — capture fields complete**: request, argv, timestamps, exit code, full stdout/stderr, artifact digests, matched authenticated plan digest.
4. **§3.1 + §8 — labor honestly counted**: two-phase setup (provision+start / inventory+confirm-remove), deploy-key registration, `M0_CUTOVER_CONFIRMED=yes` gate; ~4 short interactions stated, not "one run".
5. **Revocation verified, not assumed**: setup lists EVERY host authorized_keys entry by fingerprint (no name-substring matching); §3.6 now has a fifth leg — the council fetches `open.json`+`open.json.sig` raw and runs `ssh-keygen -Y verify` itself; (a) re-probes every listed fingerprint post-cutover.
6. **§3.5/§3.7 — no anchoring overclaim**: broker commits are plain commits (their authentication is push-rights + plan signature + council-side verify, stated as such); public permanence via small per-wave retention packs in the public repo; Rekor optional with the pack as fallback.
7. **Single-pass mode implemented** (`--once`) so the §3.6 cutover test can run under controlled one-pass semantics; systemd uses the daemon unit (flag mismatch fixed).

Executable evidence: `scripts/qa/test_broker_p0.py` — 8 checks, all green, using real `ssh-keygen -Y` signatures and real git remotes (no mocks): unsigned plan ⇒ zero execution + refusal (P0-1a/b); tampered-after-signature plan ⇒ refused citing signature (P0-2/2b — the reproducible sim of §3.6(e)); signed in-plan command executes with full capture fields (P0-3); out-of-plan argv refused (P0-4); records+refusals reach the remote branch (P0-5/5b). Gate harness: 27 PASS / 0 FAIL, unchanged.

## Questions

1. **Grok:** §3.8 is unchanged from your ACCEPT, word for word. The changes since your pin are §3.1 (two-phase + fingerprint inventory + proven revocation + explicit docker-group=root honesty), §3.3 signature-authorization, §3.5 retention packs, §3.6 five legs, §8 honest cutover count. Does your ACCEPT stand at `1ce2b3c…`? State explicitly: "ACCEPT stands at this pin" or the change you require.
2. **ChatGPT:** For each row of your re-pin-2 repair table, state MET (cite the § / code location / test ID) or NOT MET (say precisely what is missing). Specifically judge: §3.3 signature gate vs your "plan authorization must be cryptographic" demand; runner checked-failure + loud-stall vs "subprocess errors unchecked"; §8 count vs your labor-honesty demand; §3.6(e) + fingerprint re-probe vs "revocation must be verified post-cutover"; §3.7 honest commit model vs rev-3's "signed commits" overclaim. Confirm rev-4 stayed inside your scope instruction (no architecture redesign, no second machine/TPM/attestation).
3. **Both:** Verdict on rev-4: ACCEPT / ACCEPT-WITH-CHANGES / REJECT. 2/2 ACCEPT at this pin ⇒ Wave 0 authorized to begin only (§9): owner runs the two-phase cutover, §3.6 five-leg test, C1/C2 host prep via broker, zero destructive ops. The re-pin-2 sshd blocker is cleared (host reachable on 2222; recorded in ledger).
4. **ChatGPT:** Your P1 items — single-pass mode and mandatory external checkpoints. `--once` is implemented (runner). External checkpoints: §3.7 makes Rekor optional with the public retention pack as the standing mechanism; is that acceptable, or does Wave 0 block until you name a mandatory public log you will accept on this infrastructure?

No authorization is granted or assumed by this prompt beyond what §9 and the HARD STOP (DESIGN-REVIEW §10) already allow.
