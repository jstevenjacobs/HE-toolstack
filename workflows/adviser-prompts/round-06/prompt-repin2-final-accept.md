# Council prompt (round-06, re-pin 2) — FINAL ACCEPT — for ChatGPT and Grok

You are closing round-06. Your re-pin-1 reviews at `b125d665` are archived verbatim IN the
tree at the new pin (URLs below). Both of you ruled APPROVE-WITH-CHANGES with exactly three
residual items between you (Grok F1; ChatGPT F1+F2). All three are claimed fixed at the pin.
This is a final ACCEPT/REOPEN on those three diffs — nothing else opens.

**HARD STOP (DESIGN-REVIEW §10):** paper-only review. (HARD STOP is defined in DESIGN-REVIEW §10, not TD §10 — citation clarified per ChatGPT re-pin-2 note.) No runtime claims, no deployment or
ticket-execution authorization. Quote the pinned tree verbatim.

- **Pin:** `9e382314c4e4ca9238303e852a1fca12e9b07953` (head of `dp/round-06-runbook-repairs`, PR #16)
- **Increment:** `b125d665..9e38231` — three surgical changes only: TD §11.8 R-5 (two), ledger DP-R6-rb gloss (one), plus archived replies + ledger row.

**Raw URLs (no login; all at the pin):**
- TD: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/9e382314c4e4ca9238303e852a1fca12e9b07953/docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md`
- Ledger: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/9e382314c4e4ca9238303e852a1fca12e9b07953/workflows/ledger.md`
- §6.2b contract table: same TD URL, section `6.2b` (ops: `POST /v1/create_run`, `GET /v1/runs/{id}/status`, `POST /v1/runs/{id}/kill`, `GET /v1/runs/{id}/logs`)
- Your re-pin-1 replies (archived): `…/9e382314c4e4ca9238303e852a1fca12e9b07953/workflows/adviser-input/round-06/reply-chatgpt-repin-review.md` and `…/reply-grok-repin-review.md`

**The three claimed fixes:**
- **A (Grok F1, major):** R-5 step-(3) cleanup path — `POST /v1/cancel` replaced by `POST /v1/runs/{id}/kill` (the §6.2b kill op) with a follow-up status check, matching the contract and the §6.10 shutdown path.
- **B (ChatGPT F2):** R-5 symptom sentence now marks the `status`-call failures **pre-restart** and states explicitly that the step-(3) GET is a post-restart liveness probe, not a replay of the symptom.
- **C (ChatGPT F1):** ledger DP-R6-rb gloss rev-3 — narrowed to body-true wording: incomplete trees are *excluded* (no separate quarantine op); the MinIO step is versioned-tier proof (manifest-select + export-reupload + digest-compare), *not* a full MinIO recovery procedure. Rev-2 honesty note retained.

**Q1 — ACCEPT/REOPEN on A, B, C.** Quote the exact text at the pin for each and rule. Confirm against the §6.2b table that no non-contract op name survives anywhere in R-5.

**Q2 — Increment containment.** Confirm the diff `b125d665..9e38231` contains nothing beyond A/B/C plus archive/ledger bookkeeping (no silent content change elsewhere in TD, ADR, or the runbook bodies).

**Q3 — Final round-06 verdict.** If all three ACCEPT: state plainly that round-06 closes as COUNCIL-ACCEPTED PAPER DRAFTS — and restate that R-4/R-5/R-7 remain recorded exceptions closing only at M0 re-execution with T-11-class evidence, §9 annotation unchanged, §10 HARD STOP untouched, no authorization of any kind granted by this review.

**Output rules:** declare your pin; quote exact text for every ruling; if a URL fails, mark the item unverifiable rather than substituting remembered text.
