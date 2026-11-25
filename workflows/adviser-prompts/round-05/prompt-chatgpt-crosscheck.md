# Council prompt (round-05) — INDEPENDENT CROSS-CHECK + BLIND RUNBOOK RE-RUN — for ChatGPT

You are the **second pair of eyes** in the single-human sign-off scheme (registered 2026-11-24:
exactly one human; council fills ops independence). Grok walks M3/M5/M7 + runbook dry-runs
first; your job is to catch what a single reviewer — human or agent — structurally cannot:
their own blind spots. Order of operations: (1) walk independently BEFORE reading Grok's
transcript, (2) then diff against it. Your reply is archived verbatim; it must show both
passes separately or it is invalid for this purpose.

Pinned full SHA `bc73dfce1b714a333ce4e53d4226f6dcf7c9741e` (branch dp/round-05-signoff-scheme).

**Status update (re-pinned 2026-11-24):** re-pinned from `9c578be` to `bc73dfc` after
the owner walk closed 6/6 PASS. Your blind-falsify pass on the owner rows should
attempt to break those recorded judgments from this pinned tree — transcript is at
`workflows/adviser-input/round-05/engineering-walk-transcript.md`; report any locator
mismatch or counter-example that survives, but do NOT read it before forming your own
M5/M7 independent pass.
Doc roots: scheme `workflows/adviser-input/round-05/single-human-scheme.md`; docs under `docs/`
— DESIGN-REVIEW (§2b rows M1–M9, §9), TECHNICAL-DESIGN (mermaid D1–D9; §6.9 backup; §6.10
six-step down; §11.8 runbooks R-1…R-9; §8 write-order). Raw-URL base:
https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/bc73dfce1b714a333ce4e53d4226f6dcf7c9741e/

## Q1 — Independent adversarial pass on M5 and M7 (the two false-confidence rows named in R-02)

**Amendment 2026-11-24 (operator-requested):** the owner's engineering walk (M1, M2, M4, M6, M8, M9) is now executed INTERACTIVELY — the agent pre-locates evidence, the operator answers yes/no. Your Q1 duty therefore EXTENDS to all six engineering rows: for each, search the pinned tree for a counter-example the interactive walk would likely miss (a quote pair that technically matches but conflicts elsewhere; a second location that contradicts). Report per row: CONFIRM or COUNTER-EXAMPLE FOUND (with locators). Do not read the operator's walk transcript — your falsification pass is blind to it, exactly as for M5/M7.
Do this from the pinned tree WITHOUT previewing Grok's answer. For M5: is any of the six
`make down` steps reordered, merged, or dropped in D9 vs NFR-01/§6.10 — quote both artifacts.
For M7: does any backup-path or digest-verify step in §6.9 have no diagram counterpart (or
vice versa)? Your adversarial stance is the point: assume Grok's walk will be plausible and
wrong somewhere; hunt for the specific place.

## Q2 — Blind runbook re-run (paper only; HARD STOP: no live commands)
After Q1 is written, read Grok's 9 scenarios (from their archived transcript, provided in
this chat) and dry-run each strictly as written, as if you were a fresh operator with zero
project context. Verdict per scenario: followed / stalled-at-step-N (name what you had to
invent). Any stall Grok's own walk did not flag = the finding that justifies dual review.

## Q3 — Scheme critique (meta, 5 items max)
The scheme (single-human-scheme.md) delegates the ops row to council transcripts. Attack it:
name the ways this scheme could still produce a FALSE sign-off despite the protocol (e.g.
both reviewers sharing a model family's blind spot; scenario author grading own pair; digest
claims rest on the very tool being verified). For each: one-line strengthening that does NOT
require a second human. Do not propose adding humans — that option is registered as
unavailable; propose the best available substitute.

## Output contract
Q1 with quoted evidence from BOTH artifacts per claim; Q2 scenario-by-scenario verdicts
clearly separated from Q1 (proof you walked blind first); Q3 numbered strengthenings.
Read-only. Sign-off weight flows only through owner witness of this transcript + the scheme's
validity limits, which you should restate in one sentence at the top of your reply.
