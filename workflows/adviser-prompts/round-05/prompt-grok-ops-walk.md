# Council prompt (round-05) — OPERATIONS REVIEWER WALK — for Grok

You are serving as **ops reviewer** for HE-toolstack under the single-human sign-off scheme
(registered 2026-11-24: the project has exactly one human; council members fill the ops
row). Your transcript, archived verbatim, becomes the ops evidence — grade yourself
accordingly: a walk that recites the docs' own claims back is INVALID by the protocol.

Read first (pinned full SHA `e7f261bad8f184a9e43cc965603d0b480a4317ca`, branch dp/round-05-signoff-scheme):

**Status update (re-pinned 2026-11-24):** this walk was re-pinned from `9c578be` to
`e7f261b` after the owner's interactive engineering walk closed 6/6 PASS on the owner
rows (M1/M2/M4/M6/M8/M9). Changes since the old pin: §2b M4 row erratum (phantom
inventory struck, D-08 pattern), D2 gained a spawn-path subgraph + data-flow relabel +
caption addendum, D3 sidecar label gained the root-equivalent caveat. Read
`workflows/adviser-input/round-05/engineering-walk-transcript.md` AFTER you complete
your own M3/M5/M7 walk — your rows must be walked from this pinned tree on your own
evidence, not inherited from the owner transcript.
- Scheme you are operating under: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/e7f261bad8f184a9e43cc965603d0b480a4317ca/workflows/adviser-input/round-05/single-human-scheme.md
- Diagram/prose checklist rows you own (M3, M5, M7): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/e7f261bad8f184a9e43cc965603d0b480a4317ca/docs/HE-TOOLSTACK-DESIGN-REVIEW.md (§2b, lines ~66-74; note which diagram each row names)
- The diagrams themselves: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/e7f261bad8f184a9e43cc965603d0b480a4317ca/docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md (mermaid blocks; D4=M3, D9=M5, D7/D8=M7; §6.9 backup procedure; §6.10 six-step make-down)
- Runbooks you must dry-run: TD §11.8 (https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/e7f261bad8f184a9e43cc965603d0b480a4317ca/docs/HE-TOOLSTACK-TECHNICAL-DESIGN.md lines ~1451-1500, R-1…R-9)

## Q1 — M3 walk (D4 ↔ D-15 rev / zero host publication)
Answer from the diagram text only, then verify against prose: Does D4 show agent→toolserver
over the `he-agent` network with ZERO published host ports, and MinIO bound to host loopback
only? Cite the exact node/edge labels you used as evidence. Then: does the same diagram avoid
re-introducing an exposure path anywhere (sidecar edge, health endpoints, MinIO console)? A
"yes" without quoted edge labels is not a pass.

## Q2 — M5 walk (D9 ↔ NFR-01 six steps, step-for-step)
List the six `make down` steps from the normative source, then map each to a concrete D9
element (message/arrow/label). A step present in prose but absent from D9 (or paraphrased
loosely) is a DEFECT — report it as one; do not smooth it over. Pay attention to
stop-orchestration ordering vs confirm-no-container-created: which happens first in EACH
artifact?

## Q3 — M7 walk (D7/D8 ↔ §8 write-order + §6.9 backup: quiesce-and-wait, OneDrive root, digest verify)
For each of the three named properties, locate it in the diagram(s) AND in prose. Any place
where diagram and prose use DIFFERENT names/paths/sequence is a defect; quote both sides.

## Q4 — Runbook dry-runs (paper only; HARD STOP: no live commands, this is reading + reasoning)
For EACH runbook R-1…R-9: invent one realistic failure scenario (you are the scenario author
for the ops side), then walk symptom → verify → act → verify strictly as written. Verdict
per runbook: EXECUTABLE-BLINDLY (a fresh operator could follow it with no extra knowledge) or
GAP (name the step where you had to supply knowledge the runbook doesn't contain). These
scenario pairs are your gift to the other reviewer — list the 9 scenarios so the owner can
have them re-run independently.

## Output contract
Per question: verdict (PASS / DEFECT / GAP-list), quoted evidence (diagram element labels +
prose section numbers), and — for anything DEFECT/GAP — the minimum fix as a document change.
No file edits; you are read-only. Your reply will be archived verbatim as the ops evidence
record; it carries sign-off weight ONLY through the owner's witness of this transcript.
