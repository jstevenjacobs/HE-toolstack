# Council prompt R1b-chatgpt — HE-toolstack final design review (round 1 of deployment planning)

**STATE.** Repo: https://github.com/jstevenjacobs/HE-toolstack — GitHub is the single source of truth for this council. Design package on `main` at `5c487f4` (DESIGN-v2, DEPLOY-v2, TD v1.13, REQ v1.10, ADR v1.11 incl. D-15 Option D + D-16 Option B ACCEPTED, QA v2.3 claiming 27/27 gates, REVIEW-RESPONSE through r13). PR #12 (open) adds the deployment-planning inputs: residual-risk register R-01..R-12 (`workflows/residual-risks-DP0.md`), 11 candidate tickets (`workflows/tickets/candidates/`), an action plan (`workflows/DEPLOYMENT-PLANNING-PLAN.md`), and a self-contained package (`workflows/for-adviser-review-2026-11-22.md`). Read them at the permalink: https://github.com/jstevenjacobs/HE-toolstack/tree/dp/round-01-dp0 (or after merge, at main <POST-MERGE-SHA>).

**ROLE — **Sequencing & risk adviser.** You are not asked to re-verify external facts; you are asked to attack the plan's ordering, dependencies, and risk classifications.**

**QUESTIONS (answer each, numbered):**
1. DP0's go/no-go paragraph says GO for Pass C while R-05 (D-06/OQ-4 ruling), R-09 (QA harness promotion, due at M0 start) and R-10 (freeze repairs: Q22 truncation, OQ-4 appendix row, re-gate vs r13) stay open. Is that separation (cleanup now, build later) defensible, or does any of R-05/R-09/R-10 actually gate Pass C in your reading?
2. Pass-C claim order C1→C2→C3→C4→C5 and M0 dependency chain T0.1→{T0.2,T0.5}→{T0.3,T0.4}→T0.6 — any inversion or missing edge that would strand a ticket mid-round?
3. The main agent has an 81,920-token context window and the TD alone is ~38k tokens. The plan's mitigation is 1 turn = 1 ticket, no >40 KB doc read whole, state rebuilt from ledger+ticket each turn. What is the single largest remaining execution risk under that regime, and what one rule would you add?
4. Any residual-risk row mis-gated (Hard↔Soft↔Deferred)? Answer by ID with one-line justification each; 'none' is acceptable.
5. Which decision currently deferred to the operator (D-06 wrapper shape, harness location, OneDrive L4/L5, sign-off grid) has the largest hidden cost if it slips past M0, and why?

**REPLY FORMAT (paste back verbatim; it will be committed under `workflows/adviser-input/` unchanged):**
VERDICT: APPROVE | APPROVE-WITH-CHANGES | VETO
FINDINGS: numbered; each = [blocker|major|minor|nit] + one-paragraph argument
ANSWERS: numbered to match the questions above
Quorum rule: 2 of 3 adviser replies required to proceed; a missing reply is recorded as `no-reply`, never treated as consent.
