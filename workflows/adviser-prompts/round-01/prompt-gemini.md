# Council prompt R1b-gemini — HE-toolstack final design review (round 1 of deployment planning)

**STATE.** Repo: https://github.com/jstevenjacobs/HE-toolstack — GitHub is the single source of truth for this council. Design package on `main` at `5c487f4` (DESIGN-v2, DEPLOY-v2, TD v1.13, REQ v1.10, ADR v1.11 incl. D-15 Option D + D-16 Option B ACCEPTED, QA v2.3 claiming 27/27 gates, REVIEW-RESPONSE through r13). PR #12 (open: https://github.com/jstevenjacobs/HE-toolstack/pull/12) adds the deployment-planning inputs: residual-risk register R-01..R-12, 11 candidate tickets (C1–C5 Pass-C + T0.1–T0.6 Milestone 0), an action plan, and a self-contained adviser package.

**DOCUMENTS — fetch these raw-file URLs. All are pinned to commit `50e4a62e75f48ee80115c26bc4073e4df1ed3209` (immutable). If PR #12 has since been merged to main, replace the SHA `50e4a62e75f48ee80115c26bc4073e4df1ed3209` with `<POST-MERGE-SHA>` in every URL below:**

Base: `https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/50e4a62e75f48ee80115c26bc4073e4df1ed3209/`

1. `docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md` (~155 KB — normative technical design: §6 lifecycle/queue, §7 health trio /healthz /readyz /deps, §8 claim protocol + submissions inbox)
2. `docs/HE-TOOLSTACK-REQUIREMENTS.md` (~48 KB — §4 = T-01..T-24 test matrix, §5 = traceability)
3. `docs/HE-TOOLSTACK-ADR.md` (~52 KB — decision records D-01..D-16, open questions OQ-1..OQ-9)
4. `docs/HE-TOOLSTACK-QA-REPORT.md` (~17 KB — gate table Q1..Q28 + limits section)
5. `docs/HE-TOOLSTACK-REVIEW-RESPONSE-2026-11-15.md` (~58 KB — review response, appendices through r13)
6. `docs/DESIGN-v2.md` (~15 KB — §5 = Milestone 0 acceptance M0a–M0e, §7 = migration & cleanup)
7. `docs/DEPLOY-v2.md` (~7 KB — Pass C + Pass 0 deployment passes)
8. `docs/HE-TOOLSTACK-DESIGN-REVIEW.md` (~17 KB — the reviewer's own findings doc, FINDING-01..08)
9. `workflows/residual-risks-DP0.md` (~7 KB — register R-01..R-12 with Hard/Soft/Deferred gates)
10. `workflows/for-adviser-review-2026-11-22.md` (~65 KB — self-contained: TOC + full text of all 11 candidate tickets, register inlined; use this in place of fetching each ticket file separately)
11. `workflows/DEPLOYMENT-PLANNING-PLAN.md` (~9 KB — the plan under review)
12. `workflows/ledger.md` (~9 KB — chronological decision ledger)

**ROLE — whole-document coherence adviser.** Your job is the cross-document consistency read the main agent's context window (81 920 tokens) cannot hold: the full TD, REQ §4 + §5, ADR v1.11, QA v2.3, and REVIEW-RESPONSE appendices through r13, all at the raw URLs above.

**QUESTIONS (answer each, numbered):**
1. Dangling-ID sweep: every T-id, D-id, OQ-id, RC-id, R-id and section cross-reference cited anywhere in the 11 candidate tickets + residual-risks-DP0.md (all inlined in URL 10) — does the target exist in the referenced document at its claimed meaning? Report misses as (file, line, ID, expected location).
2. Retracted-contract sweep: the package retracted several mechanisms across r1–r13 (rename-as-CAS, O_EXCL-as-sole-arbiter, `/health` endpoint → `/healthz`+`/readyz`+`/deps`, a sidecar 'reap' op, gateway-URL-success, backup-while-jobs-run). Find any surviving **normative** use of a retracted mechanism anywhere in docs/ (URLs 1–8) or the candidate tickets (URL 10). Quote each hit with its file+section.
3. Ticket↔REQ mapping: for each of T0.1..T0.6, is the 'T-ids exercised' claim consistent with REQ §4 row text (named legs vs whole-row claims) and DESIGN-v2 §5 M0a–M0e acceptance bullets? List mismatches.
4. QA v2.3 limits section vs QA gate table: does any PASS claim in the table contradict a limits-section statement (zero runtime claims) or the Q22 truncation recorded as register row R-10 (URL 9)?
5. Net coherence verdict on the docs package as a deployment basis: name the top 3 incoherences (if any) an implementer would hit first, with file+section citations.

**CITATION RULE.** Every finding must cite the raw URL + file + section (or line) you read. Do not rely on general knowledge of this project — only on the fetched documents.

**REPLY FORMAT (paste back verbatim; it will be committed under `workflows/adviser-input/` unchanged):**
VERDICT: APPROVE | APPROVE-WITH-CHANGES | VETO
FINDINGS: numbered; each = [blocker|major|minor|nit] + one-paragraph argument + citation
ANSWERS: numbered to match the questions above
Quorum rule: 2 of 3 adviser replies required to proceed; a missing reply is recorded as `no-reply`, never treated as consent.
