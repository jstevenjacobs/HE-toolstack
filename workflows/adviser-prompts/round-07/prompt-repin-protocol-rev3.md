# Round-07 — Council re-pin prompt: protocol rev-3 (broker evidence architecture)

Round: Round-07 (M0 interview protocol), second repair cycle. Target: both council members.

## Declared pin

`cf4a80488dccd0c38de2641e9871050cb2998978` (branch `dp/round-07-m0-interview`)

## Raw sources at this exact pin

- Protocol **rev-3**: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/cf4a80488dccd0c38de2641e9871050cb2998978/workflows/m0-interview-protocol.md
- Broker setup script (owner-runs-in-Wave-0; DRAFT for review): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/cf4a80488dccd0c38de2641e9871050cb2998978/scripts/m0-broker-setup.sh
- Broker runner draft: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/cf4a80488dccd0c38de2641e9871050cb2998978/scripts/m0-broker-runner.py
- Grok round-2 reply: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/cf4a80488dccd0c38de2641e9871050cb2998978/workflows/adviser-input/round-07/reply-grok-protocol-repin1.md
- ChatGPT round-2 reply: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/cf4a80488dccd0c38de2641e9871050cb2998978/workflows/adviser-input/round-07/reply-chatgpt-protocol-repin1.md
- Ledger: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/cf4a80488dccd0c38de2641e9871050cb2998978/workflows/ledger.md

## Rules

Paper-only review; fetch raw URLs only; cite by section; first-hand verdicts; Hermes is not a trust root.

## Context for reviewers

Round-2 dispositions: Grok ACCEPT (with §3 residual bounded to the single-operator threat model); ChatGPT ACCEPT-WITH-CHANGES solely on §3 — telemetry + digest-pin proves tamper-evidence, not complete capture. Rev-3 replaces §3 with a broker architecture implemented on existing infrastructure: owner-provisioned `m0broker` account; plan-gated execution (digest-listed argv only, out-of-plan refused with broker-committed refusal records); capture outside the execution boundary (broker pushes full records under its own key to a protected evidence branch; reconciliation is broker-record-minus-committed); coverage definition with unobservable = excluded = UNPROVEN; §3.6 four-part cutover test (revocation verified, out-of-plan blocked+recorded, in-plan captured, capture independent of Hermes host credentials) as the Wave-0 binding gate; §3.8 states the residual honestly (same-host account, no hardware root of trust; protects against adversarial executor, not a colluding owner). Wave 0 now includes the owner's one-time setup-script run (§3.1) — the only increase in owner labor, and it is the act that ends Hermes's host execution authority.

## Questions

1. **Grok:** §3 was rewritten since your ACCEPT. Confirm your round-2 reasoning still holds against rev-3's §3 (§3.8 preserves your limitation statement; the broker strengthens the capture path). Does your ACCEPT stand, and does the owner-runs-setup addition change your view of §8's owner-labor honesty? State explicitly: "ACCEPT stands" or the change you require.
2. **ChatGPT:** For each of your five required properties (no direct execution; capture outside execution boundary; no unlogged path; remote append-only retention + external checkpoints; independent reconciliation), state MET (cite §3.x) or NOT (say what is missing). Judge whether §3.2's deviation from your literal ask — same-host account rather than separate machine — satisfies property 1's *function* (execution-path constraint), or whether you require host separation. Is the §3.6 pre-acceptance test sufficient as your requested bypass-detection demonstration?
3. **Both:** Verdict on rev-3: ACCEPT / ACCEPT-WITH-CHANGES / REJECT. Both ACCEPT at the same pin ⇒ Wave 0 authorized to begin only (§9): owner runs setup script, §3.6 cutover test, C1/C2 host prep via broker, zero destructive ops. ChatGPT's round-2 note that host sshd is currently refusing connections (2222 and 22) is recorded in the ledger as a Wave-0 blocker the owner must restore first.
4. **Both:** The Wave-0 plan file (`workflows/m0-plans/`) referenced in §3.3 does not exist yet — it is written during Wave 0 and council-validated as part of the Wave-0 pack, per §2a. Confirm this sequencing does not weaken rev-3 review.

No authorization is granted or assumed by this prompt beyond what §9 and the HARD STOP (DESIGN-REVIEW §10) already allow.
