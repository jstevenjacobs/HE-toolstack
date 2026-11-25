# Council prompt — Round-07 re-pin: M0 interview protocol rev-2

**Pin (branch tip):** 2951d35fac8890c0f86a21929bf8643182058f35

Raw:
- Protocol rev-2: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/2951d35fac8890c0f86a21929bf8643182058f35/workflows/m0-interview-protocol.md
- Grok round-1 reply: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/2951d35fac8890c0f86a21929bf8643182058f35/workflows/adviser-input/round-07/reply-grok-protocol-review.md
- ChatGPT round-1 reply: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/2951d35fac8890c0f86a21929bf8643182058f35/workflows/adviser-input/round-07/reply-chatgpt-protocol-review.md
- Ledger: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/2951d35fac8890c0f86a21929bf8643182058f35/workflows/ledger.md
- Transcript: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/2951d35fac8890c0f86a21929bf8643182058f35/workflows/m0-interview-transcript.md

Rules: paper-only review; fetch raw URLs only; cite by section; first-hand verdicts; Hermes is not a trust root.

Context: both members returned ACCEPT-WITH-CHANGES at fd024d8f. Protocol rev-2 adopts Grok amendments 1-4 and ChatGPT amendments 1-5. The one divergence (does protocol ACCEPT + owner answers bind Wave-0 rulings — Grok: no, ChatGPT: yes) is resolved CONSERVATIVELY in §2a: Wave-0 rulings get their own evidence pack and their own 2/2 wave validation.

Q1 — Item-by-item: for EACH amendment you required in round 1, state ADOPTED (cite the rev-2 section) or NOT (say what is still missing).
Q2 — Is the §2a conservative resolution of the Wave-0 binding divergence acceptable? If your round-1 reading was the looser one, state whether you accept being bound by the stricter rule.
Q3 — §3 independent capture: mechanism = shell telemetry writing append-only logs + external transparency-log pin of capture digests before commit. If you judge this insufficient against an adversarial executor, name the mechanism you would accept. Do not accept the clause by default.
Q4 — Final verdict on protocol rev-2: ACCEPT / ACCEPT-WITH-CHANGES / REJECT. If both members ACCEPT, Wave 0 (host prep, zero destructive ops) is authorized to begin per §9's last line — nothing more.

No authorization is granted or assumed by this prompt beyond what §9 and the HARD STOP (DESIGN-REVIEW §10) already allow.
