# Owner engineering walk — INTERACTIVE PROTOCOL v2 (supersedes the fill-in template)

**Why v2:** the fill-in template (round-05 v1) made the only human do locator work — hunting
quotes through 3,478-line and 1,997-line documents — which is exactly the work an agent does
reliably and a human does slowly and inaccurately. v2 moves locator work to the agent and
keeps every judgment that needs a human with the human. Operator requested this change
2026-11-24.

## Guarantees preserved from the scheme (single-human-scheme.md)
Predicates-before-evidence · quote-or-invalid (the agent does the quoting) · walk session ≠
authoring session · verbatim transcript is the evidence record.

## What changed, disclosed to council
Quote-hunting was previously the human's act; now the agent surfaces candidate evidence.
Mitigations, all structural: ① counter-example search is mandatory (the agent must report
what it searched against, not just what matched); ② a row with missing prose-or-diagram
evidence is **DEFECT by default** — the human may only downgrade with a one-line reason;
③ spot-checks are chosen by the operator AFTER answering, from a blind list; ④ ChatGPT
cross-check blind-falsifies every engineering row (Q1) without seeing the operator's answers;
⑤ the whole transcript is committed — a wrong quote is discoverable post-hoc and the walk is
re-runnable at the same SHA.

## Procedure — one chat session, ~10 minutes total

**Phase 0 — pre-registration (agent, before the session; committed + pushed).**
File `workflows/adviser-input/round-05/walk-predicates-<sha8>.md` at the pinned SHA: per
engineering row (M1, M2, M4, M6, M8, M9) — the §2b question verbatim, the mechanically
derived FAIL tokens (e.g. M9: any health label in D1–D9 outside {`/healthz`,`/readyz`,`/deps`}
⇒ FAIL; M1: any spawn edge not routed via a §6.2b sidecar op ⇒ FAIL), and the required
counter-example greps. **No candidate answers in this file.** Committed before phase 1
starts — the predicate cannot move after the evidence is seen.

**Phase 1 — the interview (agent asks, operator answers, one row per message).**
Per row the agent shows: (a) the question; (b) prose evidence: § locator + verbatim quote;
(c) diagram evidence: diagram ID + exact node/edge label; (d) counter-example result: token
list searched, matches found beyond the quote pair. Operator answers **yes / no / show more**
("show more" ⇒ agent expands surrounding context until answerable; never argues). Agent
records answers verbatim.

**Phase 2 — operator spot-checks (the human-verification duty, kept human).**
After all rows answered, agent lists the six quote-locators blind (section numbers only, not
their content claims). **Operator picks 2 rows**, opens the documents at the pinned tree,
confirms the quoted text exists in real context, reports confirmed / mismatch. A mismatch
re-opens that row as a DEFECT investigation. (Design intent: the human could still have found
a wrong quote — on 2 of 6 rows, chosen by the human, not pre-selected by the agent.)

**Phase 3 — verdict + commit.**
Agent writes the filled walk file (row, evidence pair, counter-example note, operator answer,
spot-check outcome per row) and pastes it in-chat; operator replies "approve walk transcript"
— that message is recorded verbatim inside the committed file. §9 engineering row cites:
walk transcript + predicate-file SHA + spot-check results.

## What the operator must actually supply
Six yes/no answers + "show more" where needed + two spot-check verdicts + one approve line.
No typing into forms, no document searching except the two deliberate spot-checks.

## Fallback
`engineering-walk-owner-template.md` (v1 fill-in) remains for use if the agent doing the
interview is ever unavailable; same rows, same pass standard, just manual.
