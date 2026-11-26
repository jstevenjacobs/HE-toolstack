GROK:
---------------------------------
Pin: 1ce2b3cdb7717fe35428d1fdfd20a4e99a736693

Sources: protocol rev-4 §3.1–§3.8, §8; scripts/m0-broker-runner.py; scripts/qa/test_broker_p0.py. Paper-only.

Q1 — Does ACCEPT stand at this pin?
ACCEPT stands at this pin.
§3.8 is unchanged in substance from the wording I accepted at cf4a804 / rev-3:
“The broker is a separate account, key, and commit identity on the same physical host — not a second machine and not a hardware root of trust. A colluding owner can alter the broker; the owner is the single point of ultimate authority in this project by design (§9). Rev-4 claims exactly what rev-3 claimed (Grok's accepted wording, unchanged): completeness of capture against Hermes as adversarial executor (no host credentials post-cutover, plan-gated execution, refusal records, council-fetched evidence). Rev-4 does not claim: cryptographic proof of honesty against the owner.”
The delta since that pin is implementation repair inside the architecture I already accepted, not a design change:





































ChangeAssessment vs prior ACCEPT§3.3 cryptographic plan auth (open.json + open.json.sig, ssh-keygen -Y verify, empty signers ⇒ nothing runs; runner recomputes digest from argv)Strengthens plan gate; does not expand claimsRunner fail-closed (checked git/push; published only after confirmed push; push-fail exits non-zero)Matches the residual I accepted (detectable stall, not silent omission)§3.4 full capture fieldsCompleteness of record, not a new trust root§3.1 + §8 honest cutover count (~4 short interactions)Corrects understatement; labor honesty improves§3.6 five legs + fingerprint inventory / re-probeMakes revocation proven, which §3.2’s load-bearing claim required§3.7 plain commits + retention pack; Rekor optionalRemoves overclaim; still fits single-operator bounddocker-group = root-equivalent stated in §3.1 and pointed at §3.8Honest; already inside the accepted limitation
P0 suite (P0-1a/b, P0-2/2b, P0-3, P0-4, P0-5/5b) exercises the fail-closed paths with real ssh-keygen -Y and real git remotes. That is executable evidence of the implementation repair, not a substitute for §3.6 live cutover on the host.
No change required. Residual remains exactly as §3.8 states.

Q3 — Verdict on rev-4
ACCEPT
2/2 ACCEPT at this pin ⇒ Wave 0 authorized to begin only (§9 / protocol §9): owner runs the two-phase cutover, §3.6 five-leg test, C1/C2 host prep via broker, zero destructive ops. sshd blocker recorded cleared on 2222.
Wave-0 rulings still need their own evidence pack and 2/2 validation before they bind (§2a). R-4/R-5/R-7 remain recorded exceptions until Wave-3 live execution with T-11-class evidence. DESIGN-REVIEW §10 HARD STOP untouched.
No authorization beyond Wave 0 start.


