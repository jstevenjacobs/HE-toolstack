# Council prompt (round-05, follow-up) — FIX VERIFICATION + DEFERRED Q2 — for ChatGPT

You already completed the round-05 cross-check (`prompt-chatgpt-crosscheck.md`) at pin
`bc73dfce1b714a333ce4e53d4226f6dcf7c9741e`: your blind pass confirmed all six owner rows,
your falsification pass upheld three council-row counter-examples (M3 loopback label, M5 D9
escalation + stale §2b parenthetical, M7 D8 omissions), and you disclosed that Q2 could not
be performed because Grok's transcript was not in the tree at that pin. That disclosed gap is
what this follow-up closes — plus verification of the fixes your findings produced.

Pinned full SHA `e7f261bad8f184a9e43cc965603d0b480a4317ca` (branch dp/round-05-signoff-scheme).
Raw-URL base:
https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/e7f261bad8f184a9e43cc965603d0b480a4317ca/

Doc roots: everything at `workflows/adviser-input/round-05/` — including now:
- `reply-grok-ops-walk.md` (Grok's verbatim ops-walk, the artifact your Q2 could not see
  before; paste sha256 e700b2db…, header-recorded) and `reply-chatgpt-crosscheck.md` (your
  own reply, archived), `ops-walk-l4-verification.md` (owner-side L4 notes on your three
  findings), `engineering-walk-transcript.md` (owner walk, CLOSED 6/6 PASS).
- Docs under `docs/` as before. Diff vs your old pin: `git diff` not needed — the ONLY
  design-plane changes are the M3/M5/M7 fixes listed in `ops-walk-l4-verification.md`
  §"Ruling + fixes" (D4 console-edge tag; D9 step-2 annotation; §2b M5 row erratum; D8 two
  new messages + $ROOT participant) plus prompt re-pins and archives.

## Q1 — Fix verification (one verdict per row: FIXED / PARTIAL / NOT FIXED, quote the new label)
1. **M3**: does D4's operator edge now carry the loopback-console requirement at the correct
   epistemic fidelity (`[proposal]`, §11.6 — not asserted as established)? Is anything about
   D3's handling newly inconsistent as a result?
2. **M5**: does D9 step 2 carry SIGTERM → wait ≤ grace → re-issue kill (§6.10 step 2
   fidelity, [P] retained), and does the §2b M5 row now enumerate the six §6.10 steps with
   order parity to both D9 and §6.10?
3. **M7**: do D8's new messages carry §6.9.2 step 3 (source-snapshot validation →
   manifest.src) and step 8 (interrupted transfer → resume/quarantine 14 d) faithfully, and
   does the participant label name $ROOT with a §6.9 pointer?
Flag any way a fix introduced a NEW mismatch (label-vs-prose drift, wrong §-pointer, step
count changed in D9 where it must not be).

## Q2 — The deferred comparison, now performable
Grok's transcript is at `council-reply-grok-ops-walk-e7f261b-paste.md` (sha256 recorded in
`ops-walk-l4-verification.md`). Re-run YOUR nine substitute scenarios from your Q2 against
GROK's actual nine scenarios: for each of your stalls (R-4, R-5, R-7, R-8, R-9, R-2), state
whether Grok's walk of the same numbered runbook flagged it, missed it, or covered different
ground. Verdict: does dual review remain justified? Any scenario where you and Grok agree the
runbook is executable that you now both think is false-confidence?

## Q3 — Sign-off readiness statement (this is the round's closing artifact)
Given: owner walk 6/6 PASS (transcript + your blind confirmation), council rows M3/M5/M7
walked, falsified, fixed, and now verified by you at this pin, runbooks dry-run twice with
divergent scenario sets, three defects found — state plainly: (a) is the OPS row of the §9
sign-off scheme now supportable under the single-human scheme's stated limits, (b) what
remains human-only/non-closable (T-execution, §2b+§5 sign-offs, OQ-9, F-1), (c) one sentence
restating the scheme's validity limits. No new defects hunt; this is a closing statement.

## Output contract
Q1 per-row quotes from this pin; Q2 scenario table (yours vs Grok's actual); Q3 three-part
closing statement. Read-only, paper only, HARD STOP (§10) in force. Your reply will be
archived verbatim in `workflows/adviser-input/round-05/`.
