# Round-05 — Single-human sign-off scheme (operator fact registered 2026-11-24)

**Registered fact:** Steven is the **only human participant** in this project. Every
"distinct human" independence requirement in the doc set (§9 grid, DESIGN-REVIEW §2b
🧑 rows, R-02 accepted claim scheme) can therefore never be satisfied by human headcount.
This file defines the substitute scheme; the §9 exception row cites it.

## Scheme (implements the accepted R-02 claim scheme under the one-human constraint)

| §9 row | Filled by | Independence mechanism |
|---|---|---|
| Owner / decision authority | Steven | — (decision authority is yours by definition) |
| Engineering reviewer (TD §§5–9; walk of M1–M2, M4, M6, M8–M9) | Steven | **Dated walk against a pinned SHA**, executed in a session that did not author the artifacts under review; council records cited. Recorded as the single-human exception — not presented as independent-human review. |
| Ops reviewer (TD §§11–12 + runbook dry-runs; walk of M3, M5, M7) | **Council member** (Grok or ChatGPT) via round-05 prompt | Blind walk at pinned raw-URL SHA; reply archived verbatim; you witness by checking the transcript satisfies the walk questions — the false-confidence rows (M5 shutdown choreography, M7 backup) are the ones the accepted scheme required to be non-author-reviewed, and a non-author council transcript is what substitutes for a second human. |

**Validity limits, stated honestly:** a council member is independent of authorship but is
not a human licensed to accept operational risk; the residual-risk acceptance remains yours
alone (owner row), and §9 records exactly that. No signature in this scheme may be described
in evidence as "independent human review."

## Walk protocol (binding on both rows)

1. Walk executed against a **full-SHA-pinned** tree (`raw.githubusercontent.com/jstevenjacobs/HE-toolstack/<full-sha>/...`).
2. Each M-row answered: the exact prose locus cited, the exact diagram element cited, agreement YES/NO + defect if NO.
3. Output archived verbatim under `workflows/adviser-input/round-05/`; SHA-256 logged.
4. A walk that recites the doc's own claims back without locating diagram elements = INVALID (this is the r12 self-walk failure mode the advisers both named).
5. r12 author pre-fill retains **zero** sign-off credit (unchanged from R-02).

## Runbook dry-runs (ops row, second component per §9 wording)

Each runbook (TD §11.8, R-1…R-9) gets a **table-top dry-run**: the reviewer states symptom →
verify → act → verify from the runbook text for a scenario supplied by the OTHER reviewer,
against a pinned SHA; no live commands (HARD STOP intact — dry-run = paper exercise).
Result row: runbook ID, scenario, reviewer, verdict, defects. Ops row signs only after all
9 dry-runs have result rows (or a named exception per skipped runbook).

## Sequencing (what unblocks what)

1. Council ops-walk (M3/M5/M7) + council runbook dry-runs → ops transcript archive.
2. Your engineering walk (M1–M2, M4, M6, M8–M9) + your scenarios for any runbooks you want the council to re-dry-run — executed via INTERACTIVE PROTOCOL v2 (engineering-walk-interactive.md, DP-R5 amendment 2026-11-24: operator-requested; agent locates evidence under pre-registered predicates + mandatory counter-example search, operator answers yes/no, picks 2 of 6 rows for manual spot-check).
3. §9 filled: owner row (you), engineering row (you, exception-cited), ops row (council, exception-cited) — verdicts "approve w/ exceptions" citing this file.
4. §2b 🧑 rows tick as the corresponding walks land; M3/M5/M7 tick only on the council transcript.

Advisory — HARD STOP §10 unchanged: nothing here executes anything.
