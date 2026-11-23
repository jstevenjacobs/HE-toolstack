# DP — Deployment Planning Action Plan (council-assisted, incremental)

**Status:** PROPOSED — first artifact of the planning phase itself; becomes ACCEPTED when merged to main via its own Phase-1 PR.
**Council:** Steven (operator, router) · Hermes main agent (execution, Qwen3.8-Flash-Next, **81 920-token window**) · ChatGPT (adviser) · Grok (adviser) · Gemini (advisor).
**Source of truth:** GitHub `jstevenjacobs/HE-toolstack` @ `main`. A claim has no status until it is pushed; advisers cite permalinks (commit-SHA URLs), never chat summaries.

---

## 0. Hard operating rules (encode PD-toolstack lessons; these bind every round)

**L1 — Incrementalism (Stage-E lesson).**
- One turn = one ticket. One ticket = ≤3 file changes, ≤3-line done-check, cold-session testable.
- Per-turn tool-call budget ≈ 20; per-turn tool-output budget ≈ 8 KB into context. Anything larger goes to a scratch file and is processed with code, never streamed into context.
- Never read a doc > 40 KB whole (TD is 154 KB ≈ 38 k tokens — reads are grep/awk-sliced, ≤300 lines per read, target sections only).
- State lives in files (`workflows/state.json`, `workflows/ledger.md`, ticket files), never in the model's head. A brand-new session must be able to resume from **cold-session contract**: read `state.json` cursor + current ticket + last 10 ledger rows. That is the whole entry ritual.
- If a turn cannot close its done-check inside budget, it commits partial progress with a `WIP:` commit + ledger row and narrows the next ticket. Overreach is a plan defect, not a model defect.

**L2 — External grounding (internal-knowledge lesson).**
- Before any planning decision that depends on external tools/versions (compose semantics, docker API, flock, rclone/MinIO behavior, OS/WSL specifics), the decision record must cite a **retrieved** primary source (fetched this turn, URL + access date recorded). The M0e "≥1 ledger row cites a fetched source" rule is extended to every council round from day one.
- Advisers are information sources, not just judges: prompts ask for specific guidance against named alternatives (§3 format), never open-ended "please review".
- Model-internal knowledge may propose, but may never be the sole basis recorded for a technical claim.

**L3 — Cleanliness (transient-artifact lesson).**
- Any file written outside the repo goes into `/opt/data/cache/scratch/` AND is appended to `workflows/scratch-manifest.txt` the same turn; each round's CLOSE step deletes its registered scratch items. No unregistered orphans.
- Containers/volumes: the planning phase runs none (docs-only rule). When execution starts, cleanup is governed by C3 (orphan teardown), C5 (prune cron), and the six-step `make down` — no ad-hoc `docker rm`.
- The planning branch itself is a transient artifact: every merged round deletes its branch; only tags, main, ledger, and PR history remain.

---

## 1. Branching strategy (visibility for the council)

```
main                          ← frozen source of truth; PR-merge only; protected-ish by convention
dp/round-NN-<slug>            ← one long-lived round branch, pushed on EVERY turn commit
workflows/adviser-input/      ← adviser replies committed verbatim by main agent (version-controlled hearsay)
tags: dp-phase1-frozen, ...   ← milestones on main after each phase merge
```

- Every work turn ends with: commit (message prefixed `dp-rNN:`), **push the round branch**, ledger row with `ref:` to branch + commit.
- A round's review gate = **PR into main** opened at the checkpoint. Advisers read the PR **diff view** and file permalinks — pending changes are visible continuously, not in snapshots.
- Advisers never push. Their words enter the repo only as committed verbatim files (`adviser-input/2026-11-23-grok-r1.md` etc.), so "what the adviser actually said" is auditable and diffable.
- Adopted/rejected adviser advice becomes a numbered decision row in `workflows/decision-log.md` (`CD-nnn`, ADR-style: context / advice / adopted-as-is|modified|rejected / rationale). Rejection requires a written rationale — same law as ADRs.
- No rebase/amend after push; history is the council's memory.
- Steven (router) may approve merges personally; engineering sign-off rows in DR §9 still require the named humans.

## 2. Phase / round map

| Phase | Rounds | Content | Exit gate |
|---|---|---|---|
| **P1 — Council final design review + commit pending** | R1a, R1b | see §4 | PR merged to main; tag `dp-phase1-frozen`; DP0 committed |
| **P2 — Freeze repairs + build-readiness rulings** | R2a repairs (Q22 row, RR App. I OQ-4 row, QA footer); R2b D-06 wrapper-shape decision (adviser prompts + operator ruling); R2c QA-harness promotion decision | DP0 R-05/R-09/R-10 closed on main |
| **P3 — Pass-C execution plan** | R3a adviser review of C1–C5 (already drafted); R3b incorporate + host-state preflight facts refreshed; R3c commit to main as `tickets/` (not candidates) | Pass-C tickets normative; execution claimable |
| **P4 — Pass-0/M0 plan** | R4a T0.1–T0.6 adviser review; R4b make-verify chain + T-test matrix (already extracted) review; R4c revisions + commit | M0 plan normative; `make up` authorized per DP0 hard-gate table |
| **P5 — Pass A/B + drills scheduling** | R5a Pass-A/B scope review; R5b drill calendar (T-11/T-18/T-22, OneDrive L4/L5, host-reboot); R5c commit | Full roadmap on main, every future execution ticket has a home |

Each round = its own branch + PR + adviser cycle + merge. No round starts until the previous merge is on main. This is the "iterative enough for the context window" guarantee: the largest single object any turn ever touches is one ticket or one PR diff.

## 3. Checkpoint protocol (adviser prompts)

Every checkpoint emits a **self-contained prompt file** (written under `workflows/adviser-input/prompts/`, pushed, and given to Steven to paste):

```
[dp-rNN checkpoint prompt → ChatGPT / Grok / Gemini (role)]
STATE: repo permalink @ SHA, PR diff URL, round goal (≤2 lines)
DELTA: exact diff or file permalink under review (never a narrative summary of it)
QUESTIONS (numbered, ≤5, each answerable independently)
ALTERNATIVES (where a choice is asked: list options A/B/C with trade-offs — advisers pick and justify)
ANSWER FORMAT: per question APPROVE | CHANGES: <specific> | VETO: <reason>; plus one "what we did not ask but should have" line
```

- Role defaults (flexible; operator may reassign): **ChatGPT** — reasoning, option analysis, decision-shape critique; **Grok** — adversarial review + external verification (asks it to check claims against live sources — feeds L2); **Gemini** — long-context cross-document coherence (it can hold whole TD/REQ in its window where my 81 k cannot — this turns my hardest constraint into the council's complementarity).
- A checkpoint passes only on **written replies collected by the router**; main commits them verbatim, then produces a response-diff round addressing every CHANGES/VETO (disagreement that survives one full round escalates to the operator, not to silent main-agent override).
- Quorum rule: 2 of 3 adviser replies required; a missing reply is recorded as `no-reply`, never assumed consent.

## 4. Phase 1 — detail (the user's proposed first phase, as amended)

**R1a (no adviser review needed):** commit DP0 as-is — register, 11 candidate tickets, adviser package, planning plan (this file) — as `dp/round-01-dp0` → PR → main. These are *inputs to review*, not design changes; committing them makes the council's Phase-1 review target stable and permalinked. No design content touched.

**R1b (the council's final design review):** advisers receive the PR + `for-adviser-review-2026-11-22.md` + the four core docs (as permalinks; Gemini gets whole-doc review, ChatGPT/Grok get the DP0 register + targeted sections). Charter: final coherence sweep, flag anything the thirteen automated rounds missed, per-question format of §3. Findings land as `adviser-input/` files → response commits on the branch → merge → tag `dp-phase1-frozen`.

Two amendments to the operator's framing:
1. **Split, don't mix:** pending DP0 artifacts (R1a) and final design review (R1b) are separate PRs — design review must run against a fixed SHA, and mixing "commit our drafts" with "review the design" gives advisers two moving targets.
2. **Council ≠ freeze sign-off:** the 🧑 rows of DR §9 (owner/engineering/ops) remain human-only. Council review is recorded as evidence feeding those rows, not as a substitute for them.

## 5. Turn rhythm (every turn, without exception)

1. Cold-session entry: `state.json` cursor + current ticket + ledger tail.
2. Work inside ticket budget.
3. Commit `dp-rNN: …`, push round branch.
4. Ledger row with `ref:`; update cursor.
5. Register/clean scratch per L3; update `state.json` `tickets_open`.
6. If checkpoint turn: emit the prompt file (§3), hand to router, **stop and wait** — no speculative work while advisers deliberate.

## 6. Metrics that prove the plan is working (checked at every phase close)

- Turns-per-ticket (target ≈1; >3 means the ticket must be split).
- Zero tickets closed by reading a >40 KB doc whole.
- Every technical claim's source field non-empty (L2 audit, one grep).
- Scratch manifest → empty set at each round close (L3 audit).
- Adviser-reply files exist for every checkpoint question (no-assumed-consent audit).
