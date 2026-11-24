# Round-04 — Hermes suggestions on R-03 / R-02 / R-04a / R-12

**Assembled:** 2026-11-24 · **Repo HEAD:** `79beb57967eaee97d4772747483b8f4879201af8` (main, dp-phase3-harness-in-repo) · **Evidence basis:** live register rows, REQ §4 T-rows, DESIGN-REVIEW §2b/§9, TD §11.8/§4, QA §3.1/§5, all read from main at HEAD this pass.
**Status:** Hermes position for operator decision + adviser review. Advisers: evaluate independently; disagreement preferred over consent.

## R-03 — T-01…T-24 execution mandate

**Proposal: three execution classes, one witnessing protocol.**

- **(a) Agent-executed, operator-witnessed:** T-01, T-02, T-07, T-12, T-15, T-17, T-20, T-21, T-23, T-24. All scriptable inside the stack or via existing host-ssh; none destroys host state.
- **(b) Operator-executed (or operator-triggered with agent recording):** T-05c + T-13c (host-reboot legs — the agent runs *inside* WSL; a WSL restart kills the tester mid-test, so the tester cannot be the witness), T-19 (host dockerd restart — disruptive to unrelated containers), T-11 + T-18 (touch OneDrive root, long-running, irreversible-path adjacent), T-13 bring-up itself (first `make up` is the ritual event; operator presses the button per P3).
- **(c) Scope-reduced at M0:** T-06 runs its **flag-off-refusal leg only** (GPU admission is disabled at M0 by constraint; VRAM-simulation and floor-math legs belong to C6/GPU-class enablement, consistent with OQ-2). T-22 runs but its OQ-8 premise (deployed rclone/MinIO version history) is itself an acceptance finding, not a blocker.

**Anti-false-pass control (the load-bearing part):** for every agent-executed leg, the pass predicate must be **pre-registered in the ticket file before execution** — an assertion list citing the design section it tests (e.g. "T-20: ≥2 independent OS processes claim same ticket; exactly one wins → REQ §4 T-20, TD §8.8"), plus the raw command transcript, exit codes, and sha256 of each log in `workflows/evidence/T-XX/`. The operator witnesses by reading the *predicate* and checking the transcript satisfies it — never by reading the agent's narration. The predicate is pinned at a SHA before the run, so it cannot be retrofitted. This is the only control that survives the harness-author-writes-own-test problem; T-02 is neutralized differently — by its own definition the tester is a zero-context fresh session (M0 ticket constraint, verbatim: "Cold-session test (T0.5) must succeed with zero conversation context").

## R-02 — M1–M10 diagram↔prose checklist + §9 grid

**Reframe: do not staff three humans; sequence the signatures.**

1. **M1–M10 are not a staffing problem — they are M0 evidence.** The register itself says "closed by T-11 during M0" and R-03 converts the same diagrams' claims to [V] by execution. Recommendation: leave M1–M10 open now; each row is claimed as its corresponding T-test passes, operator ticks it against the evidence packet. No signatures needed before `make up`.
2. **§9 grid:** Owner row = Steven, signed when the two open-exception lists (this + QA §5) are dispositioned. Engineering row: in a one-human project, honest substance = the council rounds (R1–R3, quorum records) backing each row — sign owner+engineering as one human with the council rounds cited as the review basis, rather than invent a phantom reviewer whose signature would be theater. Ops row: earned, not declared — sign only after ops dry-runs of runbooks R-1…R-8 (TD §11.8), which is a concrete pre-`make up` activity.
3. **r12 author self-walk (M1–M9):** counts as completeness evidence (shows rows are answerable), explicitly "NOT a substitute" per §2b — keep it recorded, give it zero sign-off weight.

## R-04a — OneDrive L4/L5 durability (A: execute drills vs B: accept fallback)

**Proposal: A — execute. B is not actually cheaper, and the choice is partly illusory.**

T-11 and T-18 are REQ §4 T-matrix rows; M0 acceptance already requires them green (R-03). Choosing B only removes a gate QA §5 would otherwise record — it does not remove the work and it does not make R-04b safe. The genuinely load-bearing, non-optional step is already correctly separated in the register: **before C3 removes the MinIO volume**, either one successful manual web read-back of `pd-minio-orphan/` logged to `drills/onedrive-readback.log`, or an explicit operator purge-approval row in the ledger (irreversible-loss path — this is the one place where written acceptance is legitimate, because *this* decision is inherently the owner's risk call). Sequence: read-back (cheap, ~minutes) → C3 volume removal → T-11/T-18 executed normally during M0 → OQ-9 closes on drill evidence, not acceptance.
**Disk sample:** re-sample before `make up` (one command), not a watermark policy — 81.5% full with ~66 GB free is adequate for CPU-class M0; if sustained monitoring is ever wanted, it belongs as a monitoring item in TD §11.7, not a new artifact now.

## R-12 — FINDING-06 reuse-claim debt

**Proposal: tiered smoke checks, cost calibrated to failure consequence.**

- **Tier 1 (all claimed-unchanged scripts):** entry-point invocation against one fixed minimal fixture — proves import + wiring, not just `python -c import`.
- **Tier 2 (numeric paths — mesh/solver/pre-post scripts):** frozen-grid digest A/B via the **T-04 bit-identity harness that the design already provides** — reuse our own regression harness rather than inventing a smoke format. A silently wrong digest is the failure mode that matters; an ImportError is trivially visible.
- **Tier 3 (one-off migration/ops scripts):** `--check`/dry-run invocation.
Evidence per script: transcript + digest recorded in a QA §5 import table row; FINDING-06 closes when the table is full. Highest-risk class to audit first: scripts whose wrongness produces **silently wrong physics** (unit parsing, mesh conversion) — Tier 2 mandatory there; scripts that fail loudly can sit at Tier 1.
