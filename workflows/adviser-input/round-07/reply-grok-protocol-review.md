GROK:
---------------------------------
Pin: fd024d8fbdcd3cab22b45a973834593fce5a6a79

Sources: workflows/m0-interview-protocol.md, workflows/m0-interview-transcript.md, workflows/ledger.md (DP-R7-ip). Paper-only.

Q1 — §9 invariants, T0.5 cold-session, owner-answer separation
§9 invariants — largely preserved, with one binding ambiguity.
Protocol Hard rule 6 and the wave-close clause state the discipline explicitly:
“Status discipline unchanged: executed ≠ passed ≠ authorized; drafts ≠ passes.”
“Every wave closes with: evidence committed → council prompt issued → verdicts recorded in the ledger → next wave.”
Ledger DP-R7-ip matches:
“NOT self-accepted: council verdict required before wave 0 rulings bind.”
Council remains 2/2 on evidence rows from pinned SHAs (Roles; Hard rule 6). Drafts are not treated as passes. That is the same shape that survived rounds 05–06.
T0.5 cold-session — structurally protected against Hermes faking the session, not against Hermes faking the content.
Hard rule 4:
“the cold-session answer must be produced in a fresh session with zero carried context — structurally impossible for Hermes to fake. Owner contribution: open a new session and paste ONE line that Hermes prepares.”
The fresh-session constraint is real: Hermes cannot open the owner’s new session. The residual risk is that Hermes prepares the single paste line and the owner pastes it uncritically. That is acceptable for a T0.5 existence check (a cold operator can follow the runbook from paper) only if the prepared line is the input to the drill, not the claim that the drill passed. The protocol should state that the paste is the cold-session trigger/input, and pass/fail still comes only from committed command-output evidence under council review. As written, “paste ONE line that Hermes prepares” is one step short of that.
Owner-answer separation — sufficient in design, under-specified at the boundary.
Hard rule 2–3 correctly bar the owner from technical pass/fail:
“Owner answers give authority and preference only — never technical claims. Pass/fail of any T-test comes from command output evidence committed to git…”
Exactly three answer classes: (a) destructive/irreversible approvals one-by-one, (b) risk acceptance, (c) authority signatures / open-decision rulings.
That is the right cut. The residual hazard is class (c) wording that could sound like a technical pass (“I confirm T-13 passed”) instead of pure authority (“I accept the council’s PASS on the Wave-3 evidence pack”). The protocol should require signature sentences to cite the council verdict + evidence pin, not the test result itself. Without that sentence-shape constraint, a casual owner answer can re-introduce human-as-measurement.
Verdict on Q1: invariants hold in principle; T0.5 and signature sentence-shape need the minimum amendments in Q3.

Q2 — Destructive-op gating; live vs pre-collected confirmation
Protocol Hard rule 5:
“each wave’s approvals are collected in the interview, but execution is gated: nothing irreversible runs until the council ACCEPTs this protocol (PR #17) and the specific op’s blast radius has been presented in the question itself.”
Hard rule 3(a): individual approvals only; “blanket approvals not accepted.”
Wave 1 scopes the known destructive set (C3/C4/C5 teardowns/archives) to three one-word-class approvals after blast-radius presentation.
Ops that should still require LIVE confirmation at execution time (not only the pre-collected interview answer):

Any irreversible volume/data purge on the authoritative heat-data path (C3-class volume removal, R-4 restore onto a non-drill path, real-disk wipe). Pre-collected “yes” hours earlier is not enough once the live df/mount/label state is known; the operator should re-confirm against the live blast-radius line Hermes presents immediately before the command.
Host-destructive actions outside the compose project (e.g. systemctl stop/disable of docker, disk repartition, deletion under /home/steven/backups that is not a pure move into a verified archive). These are class-X / host-prerequisite territory; a live “proceed” after Hermes prints the exact command and target is the right bar.
Any op whose blast radius changed since the interview answer (path resolved differently, unexpected running containers, different free space). If Hermes’s pre-exec probe disagrees with the question that collected the approval, the old approval is void and a new live answer is required.

Interview-collected approvals remain appropriate for non-irreversible stack lifecycle (scoped compose up/down of class-C services, sidecar restart, synthetic job kill) once the protocol itself is council-ACCEPTed.

Q3 — Concrete failure mode + minimum amendment
Failure mode: executor cherry-picking + rubber-stamped signatures.
Hermes runs Wave 3 drills, commits only the clean log tails, and frames the council prompt around those artifacts. Council, reviewing only what is linked, returns PASS. Owner then signs M0 CLOSED with a sentence that restates the result (“T-13 passed; M0 closed”) rather than accepting a council verdict on a pinned pack. Chain: selective evidence → council PASS on incomplete pack → owner authority signature that looks technical → §9 “authorized” without a full evidence surface.
A secondary form of the same mode: T0.5 paste is a Hermes-prepared “PASS” claim rather than a cold trigger, so the cold-session row never actually exercises the runbook from a zero-context human session.
Minimum amendments:

Evidence-completeness clause (Hard rule 6 extension): every wave’s council prompt must link (a) the full command log dir, (b) the pass and fail/skip rows, (c) the transcript rows for that wave, and (d) an explicit “what was not run” list. Council REJECT is mandatory if any of (a)–(d) is missing. Hermes is not a trust root for omission.
Signature sentence-shape (Hard rule 3(c)): owner authority signatures must be of the form “I accept council verdict <VERDICT> on evidence pin <SHA> for <row-set>” — never a first-person technical pass/fail claim.
T0.5 paste role (Hard rule 4): the owner-pasted line is defined as the cold-session input/trigger only; pass/fail is solely from committed drill output under council review. Hermes-prepared text must not contain the words PASS/FAIL/CLOSED.
Live re-confirm for irreversible data/host ops (Hard rule 5 extension): after protocol ACCEPT, any volume-purge / non-drill restore-to-live / host-destructive command requires a fresh owner answer against the live blast-radius line printed immediately before execution; a prior interview “yes” is insufficient if the live probe differs or the op is irreversible.

Q4 — Verdict
ACCEPT-WITH-CHANGES
Adopt amendments 1–4 from Q3 (evidence-completeness, signature sentence-shape, T0.5 paste role, live re-confirm for irreversible ops). With those in the protocol text, the design matches the operator directive (interview, not manual labor) without weakening the round-05/06 discipline.
Binding questions (asked explicitly):

Do protocol ACCEPT + owner answers bind Wave-0 rulings? No — not until council 2/2 ACCEPTs this protocol (PR #17) and the Wave-0 evidence/answer pack is itself council-validated. Ledger DP-R7-ip already states “council verdict required before wave 0 rulings bind”; that must stay. Protocol ACCEPT alone is necessary but not sufficient for Wave-0 rulings to bind.
Is council validation still required per wave? Yes. Hard rule 6 already requires it; do not collapse multi-wave evidence into a single end-loaded review.

Status restatement: this review is paper-only. It does not authorize Wave-0 execution, destructive ops, or M0 closure. R-4/R-5/R-7 remain recorded exceptions until M0 re-execution with T-11-class evidence. §9 annotation meaning unchanged. §10 HARD STOP untouched.
