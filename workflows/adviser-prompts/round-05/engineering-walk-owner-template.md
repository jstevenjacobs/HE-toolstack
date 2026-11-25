# Owner engineering walk — TEMPLATE (fill during the walk, one session, one sitting)

> **[SUPERSEDED 2026-11-24]** Operator reported this fill-in form too complicated to complete
> efficiently/accurately. Use `engineering-walk-interactive.md` (interview protocol v2)
> instead. Retained as manual fallback only.


Protocol: single-human-scheme.md §Walk-protocol (pinned SHA, quote-or-invalid, r12 pre-fill
has zero credit). Execute in a NEW session against a checked-out pinned tree. One row per
M-item; a row passes only with BOTH a prose locus (§ + quoted phrase) and a diagram element
(node/edge label) located. Date + full SHA at top.

Pinned SHA for this walk: ____________________  (must be a merged-round SHA on main)
Walk date/session: ____________________  (may not be a session in which you authored the reviewed artifact)

## Engineering rows (yours per scheme)

### M1 — [row text from DESIGN-REVIEW §2b]
- Prose locus (§ + quote):
- Diagram element (node/edge label):
- Verdict: PASS / DEFECT — [if DEFECT: minimum doc fix]

### M2 — 
- Prose locus:
- Diagram element:
- Verdict:

### M4 —
- Prose locus:
- Diagram element:
- Verdict:

### M6 —
- Prose locus:
- Diagram element:
- Verdict:

### M8 —
- Prose locus:
- Diagram element:
- Verdict:

### M9 —
- Prose locus:
- Diagram element:
- Verdict:

## Runbook scenarios you author (for council re-dry-run per scheme §Sequencing step 2)
Supply 1–3 scenarios (symptom only; no answer) and note which they target:
1.
2.
3.

## At walk end
1. Save filled file to `workflows/adviser-input/round-05/engineering-walk-owner.md` (verbatim, no editing after).
2. Commit + push on the open round branch (or attach to PR if open).
3. Only then does the §9 engineering row get filled (verdict + date + "walk @ SHA …").

Reminder — §9 ops row fills only on the council transcript (Grok walk + ChatGPT cross-check
both archived); owner row you sign outright; every row carries an exception citation to
single-human-scheme.md. HARD STOP §10: this is a paper exercise, nothing executed.
