# Council prompt (round-06) — M0 RUNBOOK REPAIR REVIEW — for ChatGPT and Grok

This is the repair round your own findings produced. In round-05 both of you independently
identified the same three runbook gaps — R-4 (no concrete restore procedure), R-5 (wrong
service target: `make up workflow-engine` where the broken service is `spawn-sidecar`), and
R-7 (undefined archive destination) — and the owner ruled them recorded exceptions, not
fixes. This branch converts those exceptions into staged paper repairs. Your job: verify the
staged repairs faithfully close each gap you described, and stress the new text for the same
class of label-versus-prose defects you found in round-05.

Pinned full SHA `5315c372cc0774427e54a69bc30199232f3831b4` (branch dp/round-06-runbook-repairs).
Raw-URL base:
https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/5315c372cc0774427e54a69bc30199232f3831b4/

Read (all from the pinned tree):
- `docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md` §11.8 (runbooks R-1…R-9 — the changed rows R-4,
  R-5, R-7), §12.4 FM-13 row, §12.5 RC-4/RC-5 rows, §9.2 layout, §9.4 retention,
  §6.2b (sidecar contract), §6.9 + §6.9.2/§6.9.3 (backup + export), §11.5, §11.6.
- `workflows/adviser-input/round-05/reply-grok-ops-walk.md` and
  `reply-chatgpt-followup.md` (your own R-4/5/7 findings, the yardstick).
- `workflows/ledger.md` row `DP-R6-rb` (what was staged and what was found during staging).
- The increment under review is ONLY commits `adca8a4..5315c372` (2 files: TD + ledger).
  Everything else on the branch is the already-closed round-05 record.

Tasks:
1. **Q1 — Gap closure, per runbook.** For each of R-4, R-5, R-7: does the staged text
   actually contain the concrete content your round-05 finding demanded (restore: source
   selection, validation, fresh-volume rebuild, verification; R-5: correct service target +
   direct sidecar verification; R-7: a defined destination + safety rules)? Verdict per
   runbook: CLOSED / PARTIAL (name the residual) / NOT CLOSED (quote the gap).
2. **Q2 — New-defect hunt.** The new text is ~35 lines of operational prose with commands.
   Hunt for: commands that contradict invariants (D-16 socket rule, §10 class boundaries,
   six-step shutdown §6.10, backup-root-is-not-archive), epistemic tags presented as facts
   (`make disk-report` is [P] — anything else that should be [P] but reads as existing?),
   and internal contradictions with §6.9/§9.4/§11.5. Quote line text for every finding.
3. **Q3 — Legacy erratum check.** During staging the owner found three older mis-pointings
   (FM-13, RC-4, RC-5 cited R-5 for restore/reboot drills; R-5 has always been the
   spawn-channel runbook). Corrections applied: FM-13 → R-4; RC-5 → R-4 drill + T-11;
   RC-4 → R-9 drill. Verify each correction against §11.8's actual runbook texts, and check
   whether any FOURTH mis-pointing of the same family survives anywhere in the tree
   (grep-style sweep: every `R-[0-9]` citation outside §11.8 — does the cited runbook
   actually carry the cited procedure?).
4. **Q4 — Status discipline.** Confirm the staged repairs are recorded as staged drafts,
   not passes: the R-4/5/7 exceptions must remain recorded exceptions until M0 re-execution,
   §9's annotation unchanged in meaning. Flag any wording that could be read as closing an
   exception on paper alone.

Rules: read-only; pinned SHA only; no deployment approval; nothing in this review
constitutes M0 authorization (§10 HARD STOP in force). Report format: Q1–Q4 with verdicts
and quoted evidence; end with an overall verdict line: APPROVE / APPROVE-WITH-CHANGES
(numbered findings) / REJECT.
