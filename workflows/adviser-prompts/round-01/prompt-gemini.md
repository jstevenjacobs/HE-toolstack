# Council prompt R1b-gemini — HE-toolstack final design review (round 1 of deployment planning)

**STATE.** Repo: https://github.com/jstevenjacobs/HE-toolstack — GitHub is the single source of truth for this council. Design package on `main` at `5c487f4` (DESIGN-v2, DEPLOY-v2, TD v1.13, REQ v1.10, ADR v1.11 incl. D-15 Option D + D-16 Option B ACCEPTED, QA v2.3 claiming 27/27 gates, REVIEW-RESPONSE through r13). PR #12 (open) adds the deployment-planning inputs: residual-risk register R-01..R-12 (`workflows/residual-risks-DP0.md`), 11 candidate tickets (`workflows/tickets/candidates/`), an action plan (`workflows/DEPLOYMENT-PLANNING-PLAN.md`), and a self-contained package (`workflows/for-adviser-review-2026-11-22.md`). Read them at the permalink: https://github.com/jstevenjacobs/HE-toolstack/tree/dp/round-01-dp0 (or after merge, at main <POST-MERGE-SHA>).

**ROLE — **Whole-document coherence adviser.** Your job is the cross-document consistency read the main agent's context window cannot hold: the full TD (~154 KB), REQ §4 T-01..T-24 + §5 traceability, ADR v1.11, QA v2.3, REVIEW-RESPONSE appendices through r13 — all reachable at the permalink.**

**QUESTIONS (answer each, numbered):**
1. Dangling-ID sweep: every T-id, D-id, OQ-id, RC-id, R-id and section cross-reference cited anywhere in workflows/tickets/candidates/ + residual-risks-DP0.md — does the target exist in the referenced document at its claimed meaning? Report misses as (file, line, ID, expected location).
2. Retracted-contract sweep: the package retracted several mechanisms across r1–r13 (rename-as-CAS, O_EXCL-as-sole-arbiter, /health endpoint → /healthz+/readyz+/deps, a sidecar 'reap' op, gateway-URL-success, backup-while-jobs-run). Find any surviving normative use of a retracted mechanism anywhere in docs/ or the candidate tickets. Quote each hit.
3. Ticket↔REQ mapping: for each of T0.1..T0.6, is the 'T-ids exercised' claim consistent with REQ §4 row text (legs vs whole-row claims) and DESIGN-v2 §5 M0a–M0e acceptance bullets? List mismatches.
4. QA v2.3 limits section vs QA gate table: does any PASS claim in the table contradict a limits-section statement (zero runtime claims) or the Q22 truncation (R-10)? 
5. Net coherence verdict on the docs package as a deployment basis: name the top 3 incoherences (if any) an implementer would hit first, with file+section citations.

**REPLY FORMAT (paste back verbatim; it will be committed under `workflows/adviser-input/` unchanged):**
VERDICT: APPROVE | APPROVE-WITH-CHANGES | VETO
FINDINGS: numbered; each = [blocker|major|minor|nit] + one-paragraph argument
ANSWERS: numbered to match the questions above
Quorum rule: 2 of 3 adviser replies required to proceed; a missing reply is recorded as `no-reply`, never treated as consent.
