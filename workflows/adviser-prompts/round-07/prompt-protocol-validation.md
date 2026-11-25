# Council prompt — Round-07: M0 interview protocol validation

**Protocol under review:** workflows/m0-interview-protocol.md at PR #17 head b615c184febd873456d42aade2e41276427da1e9

Raw:
- https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/b615c184febd873456d42aade2e41276427da1e9/workflows/m0-interview-protocol.md
- https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/b615c184febd873456d42aade2e41276427da1e9/workflows/m0-interview-transcript.md
- https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/b615c184febd873456d42aade2e41276427da1e9/workflows/ledger.md

Context: operator directive (verbatim): "Assigning large amounts of manual work to human participants is not appropriate. Use an interview style process to progress passed the M0 gate." The project is single-human; round-05 §9 scheme already has the owner answering one-line interview questions for paper walks. This protocol extends that pattern to live M0 execution: Hermes executes everything mechanical, the owner supplies only authority answers (~20 sentences + 1 cold-session paste), the council validates all evidence from pinned SHAs.

Rules: no local files; raw URLs at the pinned SHA; cite by section; verdicts first-hand, do not anchor on the other member; Hermes must not be treated as a trust root; paper-only review.

**Q1 — Does the protocol preserve every §9 state-discipline invariant?** Check specifically: executed ≠ passed ≠ authorized; drafts ≠ passes; cold-session integrity (H4) — can the T0.5 fresh-session row still not be faked by Hermes? Council 2/2 role intact? What the owner answers (authority/preference only) vs never answers (technical pass/fail claims) — sufficient separation?

**Q2 — Destructive-op gating (H5).** Wave-1 approvals are collected in interview form but executed only after protocol ACCEPT + per-op blast-radius presentation. Name any class of operation you would additionally require a LIVE (not pre-collected) confirmation for, if any.

**Q3 — Where does this fail?** Give at least one concrete failure mode (e.g. owner rubber-stamping, evidence cherry-picking by the executor, transcript chain breakage) and the minimum protocol amendment that closes it.

**Q4 — Verdict:** ACCEPT / ACCEPT-WITH-CHANGES (list required changes) / REJECT. If ACCEPT: does protocol ACCEPT bind Wave-0 rulings when the owner gives them (yes/no), and is council validation still required per wave (yes/no)?
