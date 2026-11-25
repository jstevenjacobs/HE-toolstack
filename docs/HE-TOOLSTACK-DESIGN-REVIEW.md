# HE-toolstack Architecture Design Review — Checklist & Findings

**Document:** `HE-TOOLSTACK-DESIGN-REVIEW.md` · v1.3 (r12 stale-sync + manual
diagram-to-prose checklist §2b + independent-review findings §10 *written r13*; prior: v1.2 re-gated
against r2 items 1–8) · 2026-11-14
**Purpose:** the review instrument required by DesignStandards §8-D. Reviewers work this
checklist top-to-bottom against `HE-TOOLSTACK-TECHNICAL-DESIGN.md` (TD),
`HE-TOOLSTACK-ADR.md` (ADR), and `HE-TOOLSTACK-REQUIREMENTS.md` (REQ). Each item is
binary: ✅ satisfied / ❌ finding (file it in §5 with a FINDING-nn id) / ➖ not applicable.
A pre-run of this checklist by the document author is recorded inline as **[author
self-review]** — that is a *first pass, not a substitute for independent review*; items
marked 🧑 need a human reviewer.

Reviewed baseline: TD @ commit `4c887f8` (v1.0), REQ @ `0ed664b` (v1.0), ADR @ `f44c294`
(v1.0 incl. OQ-5/OQ-6). **v1.1 re-gate baseline: TD v1.2 + REQ v1.3 (branch
`review/architecture-revisions`, batches 1–2 of the formal-review response).** Phase 1 evidence: `PHASE1-ARCHITECTURE-DISCOVERY.md` @ `141249d`. **r12 re-review baseline:current branch `review/architecture-revisions` @ HEAD (docs REQ v1.10 / TD v1.12 / ADR v1.11 / QA v2.2)** — §2b and §10 apply to the branch, not just the v1.0 reviewee set.

---

## 1. Section completeness (DesignStandards §3)

| # | Required TD section | Present | Author evidence (where) |
|---|---------------------|---------|--------------------------|
| 1 | 1 Executive Summary | ✅ | TD §1 (problem, principles, verdict summary) |
| 2 | 2 System Context (scope, actors, external systems, constraints) | ✅ | TD §2.1–2.8 (assumptions = canonical A-ids) |
| 3 | 3 Logical Architecture (planes, components, responsibilities) | ✅ | TD §3 + Diagram 2 |
| 4 | 4 Component Reuse & Upstream Relationship | ✅ | TD §4 (lineage table, rejected reuse X-ids) |
| 5 | 5 Container Architecture (N-image rule) | ✅ | TD §5 (D-10: 6+1 narrow images, 1 Dockerfile each) |
| 6 | 6 Detailed Component Design (10 reviewability questions each) | ✅ | TD §6 (toolserver, engine, runner, minio, gate, registry, images) |
| 7 | 7 API Design (endpoints, payload schemas, errors, idempotency) | ✅ | TD §7 (contract table + JSON examples app. C) |
| 8 | 8 Workflow & Orchestration (state law, state machine) | ✅ | TD §8 + Diagram 6 |
| 9 | 9 Data Architecture (9 categories × 9 attributes) | ✅ | TD §9 + Diagrams 5 |
| 10 | 10 Security Architecture (trust boundaries, threat model) | ✅ | TD §10 (F-1..F-5 refusals listed) |
| 11 | 11 Infrastructure & Deployment (compose, preflight, runbooks) | ✅ | TD §11.1–11.9 |
| 12 | 12 Reliability / Failure management (13 modes + FMEA) | ✅ | TD §12 (FM-1..FM-13 — r12-synced: FM-11…13 added r2) + Diagram 8 |
| 13 | 13 Performance & Scalability (honest targets, no invented numbers) | ✅ | TD §13 ([U] on every estimate) |
| 14 | 14 Testing & Verification Strategy (10 levels, physics-gate preserved) | ✅ | TD §14 (T-01..T-24 defined in REQ §4 — r12-synced; T-ids grow with findings, TD §14 maps by class) |
| 15 | 15 (cross-cutting: performance above/below line, limits) | ✅ | TD §15 limits & exit criteria |
| 16 | 16 Implementation & Migration Plan (M0–M4, vertical slices) | ✅ | TD §16 (exit gates = T-ids) |
| 17 | 17 Architecture Decisions & Open Issues | ✅ | TD §17 + ADR (**17 D-records** + X/F/OQ — r12-synced; was 12 at v1.0 baseline) |
| 18 | 18 Risk Register | ✅ | TD §17.2/§18 (top-5 w/ owner+mitigation+contingency) |
| 19 | 19 Appendices (glossary, repo tree, API examples, sources) | ✅ | TD app. A–D |
| 20 | Clickable TOC | ✅ | TD top |
| 21 | Revision history | ✅ | TD top table + workflows/ledger.md (per-ticket rows) |
| 22 | Figures numbered, referenced from prose | ✅ | Diagrams 1–9 (D9 added v1.1), each cited in its section — r12-synced |

## 2. Diagram review (DesignStandards §4)

| # | Check | Status |
|---|-------|--------|
| D1 | 8 required diagram **types** present (context, logical, deployment, network, data-flow, state-machine, e2e sequence, failure sequence) as **9 instances D1–D9** (D7/D8 share the sequence type) — r12 wording sync | ✅ [author self-review] |
| D2 | **Syntactically valid** — `mermaid.parse()` (mermaid 11 + jsdom, node 26.5): 9/9 blocks pass (9 diagrams incl. new D9 lifecycle, re-validated 2026-11-15) | ✅ [V — measured 2026-11-14; the pass found+fixed a real defect: stray `</div>` + unquoted-paren labels in Diagram 1] |
| D3 | Boundaries distinguish container / host / external / storage | ✅ Diagrams 1, 3 (subgraphs = lifecycle boundaries) |
| D4 | Communication direction + protocol shown | ✅ Diagrams 1, 4 (edge labels: HTTP/JSON, docker run, boto3, git) |
| D5 | Consistent naming with prose (§6 component names == diagram node ids) | 🧑 reviewer item |
| D6 | No decorative diagrams (each carries info prose lacks) | 🧑 reviewer item [author: 5,6,8 are the load-bearing ones] |
| D7 | Diagram text matches prose where they overlap (no drift) | 🧑 reviewer item |

## 2b. Manual diagram-to-prose review checklist (r12 — closes the gap Mermaid cannot)

Mermaid parsing proves **syntax only**. These acceptance questions must be answered by a
human reviewer against the current branch; syntax validation (9/9) is *never* evidence of
semantic agreement.

| Q | Acceptance question | Reviewer answer |
|---|---------------------|-----------------|
| M1 | Does every spawn edge (D1/D3/D4) route **only** through the spawn-sidecar's 4 HTTP ops (TD §6.2b), with no engine/sidecar socket mount and no fifth `reap` edge? | 🧑 |
| M2 | Do D2/D3/D4 name the sidecar as **sole docker.sock holder** *and* carry the root-equivalent-if-compromised label (D-16 ACCEPTED caveat)? | 🧑 |
| M3 | Does D4 show agent→toolserver over the `he-agent` network with **zero published host ports** (D-15 rev), and MinIO on host loopback only? | 🧑 |
| M4 | Does D3's network inventory enumerate exactly `he-edge / he-agent / he-internal / /var/run/he-runs` with no legacy alt-architecture subgraph? **[DP-R5-walk erratum 2026-11-24 — operator ruling on walk row M4: `he-edge` and `/var/run/he-runs` are phantom tokens — repo-wide they occur nowhere but this row, introduced with it in `68626eb` (r12); no architecture, ADR, requirement, or QA artifact defines them; the documented run workspace is `heat-data/runs/<id>/work`. Operative predicate now: D3's inventory names the documented deployment-scope network/storage elements it actually depicts — `he-internal` (4-op spawn edge), sole `/var/run/docker.sock` holder, published ports 9000/9001 minio-only behind `127.0.0.1` (toolserver publishes nothing), `heat-data` bind mounts (`runs/<id>/work` included) — while `he-agent` membership is a D1/D4 edge-label + §5.3/§5.4b prose scope item, not a D3 element; the no-legacy-alt-architecture-subgraph leg is retained unchanged. D3 itself was verified conformant — do NOT add `he-edge`/`he-runs` to any diagram.]** | 🧑 |
| M5 | Does D9 match NFR-01 step-for-step per §6.10 six steps (erratum 2026-11-24: former parenthetical was stale pre-v1.13 text): ① compose stop -t grace → engine stops claiming; ② engine→sidecar SIGTERM, wait ≤ grace, re-issue kill; ③ record interrupted/killed write-ahead BEFORE engine exits; ④ compose down (class C only); ⑤ host-side janitor sweep of he-stack=1 remnants; ⑥ verify zero containers (docker ps -a label filter + compose ps -a; class X excluded)? | 🧑 |
| M6 | Do D5/D6 ticket-state edges match §8.1/§8.8 claim semantics (flock at execution time; supersede after kernel-released lock)? | 🧑 |
| M7 | Do D7/D8 match §8 write-order and §6.9 backup procedure (quiesce-and-wait, `$ROOT` OneDrive root, digest verify)? | 🧑 |
| M8 | Do diagram node names equal §6 component names (no drift in either direction)? | 🧑 |
| M9 | Does every health/readiness label agree with the canonical trio `/healthz` `/readyz` `/deps` (no `/health`)? | 🧑 |

**Author pre-fill (self-review, NOT a substitute):** M1–M9 walked once by the author at r12,
no mismatches found; 🧑 independent confirmation still required per DesignStandards §8-D.

## 3. Reviewability — the 10 questions per major subsystem (DesignStandards §7)

Reviewer runs this grid against TD §6; ✅ = the section answers all 10 (problem, necessity,
responsibilities, interfaces, data owned, dependencies, failure behavior, testing,
deployment/maintenance, limits/risks).

| Subsystem | Grid complete | Notes |
|-----------|---------------|-------|
| toolserver | ✅ | limits incl. no-authN refusal F-1 stated |
| workflow-engine (queue/admission/loop) | ✅ | |
| job runner + spawn channel | ⚠️ OQ-5 | spawn channel explicitly unresolved — surfaced as OQ-5 (M0 blocker), not hidden [ref §6.2, §17.1] |
| per-job tool images | ✅ | per-image: build, pin, smoke, digest rule (D-10) |
| MinIO evidence tier | ✅ | OR-05 posture flagged |
| physics-gate | ✅ | methodology preserved from attempt 1 [E] |
| candidate registry | ✅ | colocation decision = OQ-4 |

## 4. Decision quality (DesignStandards §3.17 / §8-B)

| # | Check | Status |
|---|-------|--------|
| A1 | Every D-nn ADR has: ID, title, status, context, alternatives, evaluation criteria, decision, rationale, consequences, risks, revisit conditions, references | ✅ [author self-review — 17 ADR records, D-01…D-12 + D-14…D-18 (no D-13 record was ever filed — see register numbering note, ADR register); r12 corrected an '18 records' overcount] |
| A2 | Alternatives genuinely evaluated (not strawmen); rejections visible (X-nn section) | ✅ 8 rejected alternatives recorded (r12 recount verified) |
| A3 | Uncertainty separated from fact: evidence tags [V]/[E]/[P]/[U] used; no untagged performance number | ✅ grep-verified (TD §19 self-check) |
| A4 | Decisions from *the user* (D-04=B, D-05=1, D-10=separate) represented verbatim-ruled, not silently reinterpreted | 🧑 reviewer to confirm against Phase 1 register |
| A5 | Proposed-but-not-accepted decisions clearly "Proposed" (D-02 posture → OQ-1) | ✅ |
| A6 | Open issues never buried in prose — all in OQ table (**OQ-1..OQ-9** — r12-synced) w/ needed-by dates | ✅ |
| A7 | ID hygiene: single namespace across TD/REQ/ADR (assumption A-ids = Phase 1 canonical; no collisions) | ✅ [V — cross-doc grep 0 dangling; collision found+fixed in QA pass @f44c294] |

---

## 5. Source integrity & honesty (DesignStandards §2 — the non-negotiables)

| # | Check | Status |
|---|-------|--------|
| S1 | No proposed functionality presented as implemented — every compose service, endpoint, CLI is marked as design; "not yet built" stated in TD §1 | ✅ |
| S2 | No invented API endpoints / config params / perf metrics / test results — config keys all map to a named consumer (§11.6); perf numbers all [U] + have a measurement plan | ✅ |
| S3 | Unverifiable info explicitly identified (e.g. pinned-version freshness [U], T-12 numbers pending) | ✅ |
| S4 | Historical evidence preserved w/ citations (Phase 1 §6 D1–D14 lessons linked from TD §4 lineage table) | ✅ |
| S5 | No test claims without evidence: every T-id is *to-be-executed*; the only [V] claims are Phase 1 measurements w/ commands | ✅ |
| S6 | The three stale-ref sweeps from Phase 1 still hold in v2 docs (gpu-broker/toolserver/broker-pool refs = ruling context only) | ✅ [V — re-grepped; TD contains gpu-broker only as rejected legacy X-3] |

## 6. Traceability (REQ ↔ TD ↔ tests)

| # | Check | Status |
|---|-------|--------|
| TR1 | Every FR/NFR (66 ids: 42 FR + 24 NFR rows; 40 FR in the initial-release matrix — FR-41/42 [M3+]) has verification method + acceptance criteria | ✅ [V — script check @P2.1 + r2 re-gate: all rows complete] |
| TR2 | REQ §5 matrix: every requirement → ≥1 T-test; every T-ref resolves | ✅ [V — 0 dangling both directions] |
| TR3 | TD cites REQ ids where requirements are satisfied (component/section level) | ✅ |
| TR4 | TD references ADR ids for structural choices; ADR ↔ TD bidirectional (OQ-5/OQ-6 present in both) | ✅ [V — grep @f44c294] |
| TR5 | M0–M4 exit gates expressed as T-ids (not prose adjectives) | ✅ |
| TR6 | Assumption ids used in TD all resolve (Phase 1 canonical + A13–A15) | ✅ [V — collision fixed @f44c294] |

## 7. Operations & migration reviewability

| # | Check | Status |
|---|-------|--------|
| O1 | Single compose project; `make down` zero-orphan is an *acceptance test* (T-13), not a hope | ✅ |
| O2 | External dependencies explicitly listed (§11.9: docker engine, WSL2, Ollama, sglang host, GitHub, host disk) despite self-containment principle | ✅ |
| O3 | Runbooks exist w/ symptom→verify→act→verify (**R-1..R-9** — r12-synced) | ✅ (drill = T-07; never yet executed — honestly [proposal]) |
| O4 | Migration: PD-toolstack artifacts frozen as evidence source; D-ledger import = triaged (OQ-3), no silent re-adoption | ✅ |
| O5 | Rollback plan real: append-frozen images + git revert + make up | ✅ |
| O6 | Disk/watermark/backups addressed w/ numbers (80/95%, canonical backup root D-14, R-8 stale-backup guard) | ✅ |

---

## 8. Findings register

Findings filed *by the author's self-review pass* (inputs to the review, not suppressed).
Reviewers append FINDING-nn rows.

| ID | Sev | Finding | Disposition |
|----|-----|---------|-------------|
| FINDING-01 | medium | Spawn-channel security decision was at risk of being hand-waved in early drafts; leaving it open inside prose would violate DesignStandards §6.4 | RESOLVED (surfaced): OQ-5 is now an explicit M0 blocker in TD §6.2/§17 + ADR, with 3 enumerated options (socket mount / sidecar / host unit) |
| FINDING-02 | medium | TD draft created a private A-id namespace colliding with Phase 1 canonical assumptions | FIXED @f44c294 (unified to Phase 1 register + A13–A15) |
| FINDING-03 | low | Diagram 1 contained invalid mermaid (stray `</div>`, unquoted-paren labels) — would have failed review rendering | FIXED @4c887f8 (v1.0); re-validated on v1.2 tree; validated 9/9 blocks with real parser (mermaid 11 + jsdom, node 26.5) [V] |
| FINDING-04 | open | GPU-class numbers (8 GiB ceiling / 5.5 GiB floor) rest on one C6 measurement chain; driver floor ≥591.59 claim unconfirmed (nvidia-smi over SSH returned no rows) | OPEN — re-measure ticket owed (OQ-2 is the gate); FR-19 insulates M0–M2 from GPU |
| FINDING-05 | open | `make down`/preflight/runbooks/MANIFEST exist only as *design*; none executed against a built stack (stack not built — per Phase 1 law) | OPEN by nature — M0 acceptance converts them to [V]; reviewers must NOT accept M0 claims today |
| FINDING-06 | open | Attempt-1 reuse list (TD §4) claims several scripts reusable "unchanged" based on Phase 1 reading; each needs an import-time smoke check at M0 import | OPEN — tracked as M0 activity with evidence requirement |
| FINDING-07 | low | Toolserver availability tied to one uvicorn process; restart semantics stated once — spell out if reviewer asks | OPEN (low) — FM-9 covers crash behavior |
| FINDING-08 | low | **Stale-documentation class defect (r12):** QA-REPORT + DESIGN-REVIEW + TD appendices carried counts/version/terminology that lagged nine revision rounds (e.g. "8 required views" over 9 diagrams, "REQUIREMENTS v1.4"/"ADR v1.2" in TD App. C, "12 D"/"Diagrams 1–8"/"R-1..R-7" here, RR §5.4 mis-citing T-12 for claim races). Root cause: Q16 checked only numeric tokens, not concept coherence. | FIXED r12: every listed statement corrected + Q16 hardened to concept-level checks (QA §10 reproducibility scope); new §2b manual diagram-to-prose checklist |

## 9. Reviewer sign-off grid

| Reviewer | Role | Date | Verdict (approve / approve w/ exceptions / reject) | Exceptions |
|----------|------|------|----------------------------------------------------|------------|
| Steven | owner / decision authority (OQ-1…9 register, ADR §4) | | | |
| (TBD) | engineering reviewer — TD §§5–9 | | | |
| (TBD) | ops reviewer — TD §§11–12 + runbook dry-run | | | |

**Author recommendation (pre-review, not a verdict):** *approve with exceptions* —
conditions: OQ-5 resolved and OQ-1/OQ-4 ruled before M0 build starts; FINDING-04..06
accepted as M0 evidence work, not document defects. *(r13 note: OQ-1 RULED CLOSED and
OQ-5 CLOSED since written; OQ-4 D-06-half remains reviewer-side before M0.)*

### §9 exception annotation — single-human ops-reviewer scheme (2026-11-24)

**Registered structural exception (owner ruling 2026-11-24):** the project has exactly one
human participant; the §9 engineering-reviewer and ops-reviewer rows cannot be filled by
independent humans. Under the registered single-human scheme
(`workflows/adviser-input/round-05/single-human-scheme.md`), these rows are filled by
**council transcripts** (Grok blind ops-walk + ChatGPT blind falsification/cross-check,
quorum 2-of-2, verbatim archives under `workflows/adviser-input/round-05/`) plus the
**owner's interactive walk** (`engineering-walk-transcript.md`, CLOSED 6/6 PASS, re-walks
MATCH at every pin). This annotation is the disposition of R-02's §9 finding.

**Verdicts as filled under this scheme:** engineering row — owner walk 6/6 PASS +
ChatGPT blind confirmation (zero surviving counter-examples to the six owner rows).
Ops row — **approve with exceptions** at final pin (see below); not an independent-human
approval and never representable as one.

**Ops-row exceptions (carried, not converted to passes):**
1. Runbook gaps R-4 (no concrete restore procedure), R-5 (wrong/undefined service target —
   `make up workflow-engine` where the restarted service is `spawn-sidecar`), R-7
   (archive destination undefined) — found independently by both council reviewers;
   owner ruling 2026-11-24: accept as recorded exceptions; repair is M0-gated work
   (HARD STOP §10), not a document fix.
2. Scenario-supply protocol deviation (self-disclosed by ChatGPT): reviewers authored
   their own dry-run scenarios; comparison was post-hoc divergent-set analysis, not
   literal cross-supplied re-runs. Owner ruling: accepted exception; coverage is
   documented as divergent (3 shared stalls R-4/5/7 + 3 divergent R-2/6/9).
3. Council validity limit (restated verbatim from ChatGPT Q3): a council reviewer is
   independent of artifact authorship, not an independent human or an authority to accept
   operational risk; the owner alone retains residual-risk acceptance.

**Not closable by any review (unchanged human/M0 gates):** T-01…T-24 execution (runtime
evidence), §2b + QA §5 sign-offs as *human* acts, OQ-9 off-host L4/L5 durability (manual
web read-back is the only evidence), F-1 authN/Z beyond network membership (compromised-
sidecar root-equivalence stands). Nothing in this annotation or the council record
constitutes deployment approval.


## 10. Independent review record (rounds 12–13, r13)

A **read-only delegated independent reviewer** (not the authoring agent) audited the r12
working tree against a 12-item checklist (counts, versions, status claims, T-ID integrity,
issue reconciliation, diff scope). Verdict: **APPROVE WITH EXCEPTIONS**.

- Items 1–3: **PASS**. Items 4–12: EXCEPTIONS.
- Documentation-fixable exceptions found by the reviewer were **closed r13**: TD §14
  "18 records" → 17 with numbering note; TD §18 filing-time self-assessment reframed as
  v1.2 snapshot (FINDING-08 recurrence); TD §8.2 stale "A1 pending" → ACCEPTED/CLOSED;
  RR status banner + T-01…23 inline note; QA v2.3 sync. Re-gated **27/27 PASS**.
- **Open exceptions (not doc-fixable — carried into M0):** M1–M10 diagram↔prose checklist [DP-R4 erratum 2026-11-24: checklist is M1–M9 — M10 never existed; register R-02 corrected same date; original preserved]
  (§2b) and QA §5 diagram sign-offs unclaimed (human-only); T-01…T-24 specified-only,
  zero executed (design freeze gated on M0 evidence); OneDrive off-host durability has no
  L4/L5 proof (OQ-9 contingent); no authN/Z beyond `he-agent` group membership (F-1
  deferred; compromised spawn-sidecar = root-equivalent); D-07/D-11/D-17/D-18 remain
  **Proposed** — must not drift into assumed-accepted during M0 (D-06 CLOSED by
  operator ruling 2026-11-23 [DP-R3b], Option A as written); QA harness is now
  tracked at `scripts/qa/gates_v13.py` (R3c), so 27/27 is independently
  reproducible from a full-history clone — round-2 logs remain recorded evidence.

This section records an **independent automated reviewer**, not the human sign-offs the §9
grid requires; the 🧑 rows still block design freeze.

---
*Checklist instrument authored under DesignStandards §8-D. Author self-review items are
marked; 🧑 items require an independent human reviewer and block design freeze.*
