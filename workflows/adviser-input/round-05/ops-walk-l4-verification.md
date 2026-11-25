# Round-05 ops-walk — L4 verification notes (Hermes, 2026-11-24)

Pinned tree: `bc73dfce1b714a333ce4e53d4226f6dcf7c9741e`. Every claim in both replies
checked against this tree. Paste sha256 recorded in each reply file header.

## Sequence-integrity finding (disclosed, not hidden)

Both replies arrived in ONE operator paste. The prompt-ordering rule (ChatGPT walks
blind before reading Grok's transcript) is satisfied on ChatGPT's own attestation and
its independent Q1 table (it produced three counter-examples Grok did not, and one
"first material counterexample" it then retracted after reading full §6.10 — a real
blind-pass signature). BUT: Grok's ops-walk transcript was NOT archived at the pinned
tree when ChatGPT ran, so ChatGPT's requested Q2 transcript-to-transcript comparison
could not be performed and was substituted (ChatGPT says so explicitly and refuses to
claim the comparison). Residual risk: possible prompt-channel co-delivery or ChatGPT
self-consolidation from conversation context cannot be fully excluded by the archive
alone. This is recorded as the ops row's known limitation; it does not contaminate the
Q1 independent findings, which match pinned-tree evidence ChatGPT could not have copied
from any archived artifact (none existed at the pin).

## M3 counter-example — UPHELD

- §2b M3 predicate: "…and MinIO on host loopback only?" — loopback IS in the row.
- D4 block contains `9001` but zero `127.0.0.1` occurrences (verified programmatically).
- §5.3 line 311: `MINIO_CONSOLE_BIND=127.0.0.1` exists but is marked proposal (§11.6 table:
  `[proposal]`, "operator UI posture"); D3 line 332 carries the loopback claim, D4 does not.
- ChatGPT's fix options (label the D4 console edge loopback-bound, or mark the binding as
  proposed-configuration) are both minimal. NOT a D4 topology error: the agent/toolserver
  half of M3 passes on Grok's and ChatGPT's independent reads.

## M5 counter-example — UPHELD, and the §2b row itself is stale (Grok's fix (a) confirmed)

- §6.10 lines 883–884: step 2 = SIGTERM kill, "waits ≤ TS_SHUTDOWN_GRACE_SECONDS=60 [P],
  then re-issues kill." NFR-01 restates "(SIGTERM within TS_SHUTDOWN_GRACE_SECONDS, then kill)".
- D9 carries kill + SIGTERM + grace tokens but NO wait/re-issue/SIGKILL/60 depiction —
  escalation half of step 2 absent from the diagram (verified programmatically).
- Six-step ORDER confirmed correct by both reviewers; this is a completeness gap, not ordering.
- §2b M5 row on disk still carries the pre-v1.13 parenthetical ("…core-5 → down
  --remove-orphans…") that matches neither §6.10 nor D9 — same phantom-adjacent pattern as
  the M4 row. Grok's minimum fix (replace parenthetical with the six §6.10 steps) verified
  as necessary.

## M7 counter-example — UPHELD against the row's own predicate

- Row predicate: quiesce-and-wait ✓(D8 line 1800), `$ROOT` OneDrive root — D8 uses role
  label only, no canonical path/§-pointer; digest verify ✓.
- D8 lacks: §6.9.2 step 3 source-snapshot validation (integrity_check/quick_check/manifest.src
  — all absent from D8, verified programmatically); step 8 interrupted-transfer
  detection/resume/quarantine (quarantine/resume/interrupted absent).
- Step 8 is normative text. Two genuine coverage omissions under the counterpart test.

## Runbook GAP findings — both reviewers, with one correction

- R-4, R-5, R-7 GAPs: Grok and ChatGPT independently (ChatGPT also R-2, R-6, R-9 stalls).
- **R-5 finding is the sharpest and is corroborated in source:** line 1471 says restart via
  "make up workflow-engine scoped" while the service to restart is `spawn-sidecar` — a
  concrete service-target mismatch, not just vagueness. ChatGPT caught it independently.
- ChatGPT's substitute dry-run (its own scenarios, no Grok transcript available to it)
  stands as independent runbook evidence: 3 FOLLOWED / 6 STALL vs Grok's 6 EXECUTABLE / 3 GAP.
  The union of stalls is {R-2, R-4, R-5, R-6, R-7, R-9}; the intersection {R-4, R-5, R-7}
  is the hard core both agree on.
- The requested Grok-vs-ChatGPT same-scenario comparison remains not-performed (see
  sequence-integrity finding). Recorded as such.

## Line-cite spot-check of ChatGPT's quotes

Lines 243–244 (D1 4-op edge), 282–284 (D2 SC node), 336–337 (D3 edges), 351–352 (D4 edges),
577 (§6.2b root-equivalent): all match the pinned tree verbatim. M2 "CONFIRM … all three
diagrams" independently reproduces the owner re-walk result plus a D4 datum the owner walk
did not require. Locator caveat (owner transcript's 5a24b0c-era line numbers ≠ pinned-tree
locators) accepted — SHA distinction already preserved in transcript §Status.

## Verdict inputs

- Owner rows M1–M9: 6 CONFIRM by ChatGPT blind pass; zero surviving counter-examples;
  six owner judgments stand.
- Council rows: M3 PASS-with-label-finding / M5 finding upheld / M7 finding upheld.
- Runbooks: paper-executable core exists; union 6 stalls incl. one concrete R-5 service
  mismatch.
- Neither reviewer's summary claims deployment approval; both disclaim independent-human
  risk acceptance. Scheme validity limit preserved.

## Ruling + fixes (2026-11-24, operator: "I agree with your recommendations")

- M3: D4 :9001 console edge relabeled `(loopback bind 127.0.0.1 [proposal], §11.6)`. D3 LB
  left unqualified (finding named D4 only; D3's 127.0.0.1 mirrors §11.6 proposal row).
- M5: D9 step-2 label extended `SIGTERM → wait ≤ TS_SHUTDOWN_GRACE_SECONDS=60 [P] →
  re-issue kill (§6.10 step 2)` (annotation, no new interaction); §2b M5 parenthetical
  replaced with the six §6.10 steps (erratum marker).
- M7: D8 gains validate-source-snapshot (§6.9.2 step 3) and interrupted-transfer
  resume/quarantine (§6.9.2 step 8) messages; participant relabeled `OneDrive root $ROOT
  (§6.9)` — §-pointer form, literal user path not embedded.
All fixes label/additive-message level; no prose semantics, API, or security changes.
Gates 27/0, 9 mermaid blocks. Re-walk + re-pin to follow; then batched ChatGPT follow-up
(Q2 Grok-scenario comparison + fix verification at new pin).
