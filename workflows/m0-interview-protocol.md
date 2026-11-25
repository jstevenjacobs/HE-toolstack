# M0 Interview Protocol (Round-07) — rev-2

**Purpose.** Progress through the M0 gate with the human operator contributing only
judgment, never manual labor. Every mechanical act — typing commands, running drills,
hashing outputs, drafting evidence — is performed by Hermes or verified by the council.
The operator's total contribution across all of M0 is: ~20 sentences of authority
(one per approval/ruling/signature, verbatim), one cold-session paste plus one challenge
response, and one archive fetch. Nothing typed into a shell, nothing manually assembled.

This protocol is a PROCESS design. It changes no ticket, no gate, no §9 row, no D-number,
and grants no authorization. It defines who does what during M0 execution and what counts
as evidence.

**rev-2.** Council round-1 at pin `fd024d8f`: Grok ACCEPT-WITH-CHANGES (amendments 1–4)
and ChatGPT ACCEPT-WITH-CHANGES (amendments 1–5). All adopted here; source replies in
`workflows/adviser-input/round-07/`. Rev-2 awaits council re-pin ACCEPT before Wave 0.

**Precedent.** This is the round-05 interview pattern (engineering walk: one line per
row, transcript pinned, council cross-examined) extended from paper rows to live M0
execution. The council accepted the pattern's discipline at `adca8a4`; nothing here
weakens it — it only removes keystrokes from the human path.

## 1. Roles

- **Owner (the only human):** approvals, risk acceptance, open-decision rulings,
  sign-offs. Answers in one sentence each. Never executes commands, never assembles
  evidence, never types into a shell beyond the single cold-session paste (§4) and
  the single archive fetch (§8).
- **Hermes (executor/scribe, NOT a trust root):** runs every command, writes every
  artifact, commits all evidence, conducts the interview. Hermes's evidence is only as
  good as the independent capture (§3) plus council validation (§6).
- **Council (Grok + ChatGPT, quorum 2/2):** independent review of every wave's evidence
  at pinned SHAs, 2-of-2, same discipline as rounds 01–06. Council validates EVIDENCE
  (was the recorded evidence complete and does it show what is claimed); only the owner
  authorizes.

### 1a. Design Review §9 mapping (explicit; per ChatGPT C1/C4)

Four things stay distinct and are never collapsed into one another:
(i) the owner's authority/signature statements; (ii) the owner's engineering + ops
walk rows under the registered single-human exception; (iii) council 2/2 evidence
validation; (iv) the §9 limitation — a council reviewer is independent of artifact
authorship, **not** an independent human and **not** an authority to accept operational
risk; the owner alone retains residual-risk acceptance. A 2/2 council verdict is a
required review outcome under the registered exception scheme, never a substitute for
the owner's risk acceptance. Owner signatures do not make the owner the engineering or
ops reviewer; the registered council-plus-owner arrangement remains explicit on every
sign-off row.

## 2. The interview: question shapes

Every question Hermes asks is exactly one of these shapes. One question at a time.
Before every authority or risk-acceptance question Hermes presents a short, neutral
decision surface: the alternatives, material consequences, reversibility, and the
rationale for any recommendation (ChatGPT C3.2). The owner's answer must identify the
specific decision being made; silence, ambiguity, or an answer that does not identify
the requested action is never treated as approval.

| Shape | What the owner says | Example prompt |
|---|---|---|
| (a) Destructive-op approval | proceed / no, after seeing the blast radius in the question | "C3 removes the ORIGINAL MinIO volume containing 414 GB of buckets (drill copy already verified). One-word approval?" |
| (b) Risk acceptance | accept / decline, after seeing the neutral risk statement + alternatives | "F-1: sidecar has no auth. Accepted because loopback-only bind + no host port are enforced by CI/compose. Accept residual?" |
| (c) Authority signature / ruling | one verbatim sentence from the fixed vocabulary, citing council verdict + evidence pin | "Say: 'I accept council VERDICT on evidence pin SHA for row-set.'" |

Owner answers give **authority and preference only** — never technical claims, never
verbatim technical measurements (round-05 discipline: no byte counts or digests typed
by hand). Pass/fail of any T-test comes from command-output evidence committed to git
and reviewed by the council — never from an owner answer.

### 2a. Signature sentence-shape (Grok amendment 2)

Authority signatures must take the form
**"I accept council <VERDICT> on evidence pin <SHA> for <row-set>."**
Never a first-person technical pass/fail claim (not "T-13 passed"; the owner accepts the
council's verdict on a pinned pack). This keeps human-as-authority and never lets the
answer become human-as-measurement.

**Wave-0 binding (divergence resolved conservatively).** Council round-1 split: Grok —
protocol ACCEPT is necessary but not sufficient; the Wave-0 rulings pack needs its own
council validation; ChatGPT — protocol ACCEPT + owner answers bind Wave-0 rulings. The
protocol adopts Grok's stricter reading: protocol ACCEPT alone binds nothing; every
wave's answer/evidence pack, including Wave 0's rulings, is itself council-validated
before it binds.

## 3. Independent, complete evidence capture (ChatGPT C1 + Grok amendment 3)

Hermes is executor AND scribe, so completeness is never taken on trust:

1. **Independent append-only capture.** Every interview session runs under shell
   telemetry that writes each command + arguments, timestamps, exit status, stdout,
   stderr — directly, including failed attempts — to a capture file Hermes cannot
   silently rewrite or selectively omit. Before any wave's evidence is committed, the
   capture log's digests are pinned with an external signed checkpoint (a transparency
   log such as `cosign attach hashedrekor`, or an equivalent external hash anchor) so
   omission is detectable after the fact.
2. **Per-wave manifest.** Each wave commits: the full capture log, the pass AND
   fail/skip rows, the transcript rows for that wave, and an explicit **"what was not
   run"** list.
3. **Delta duty.** Hermes's council prompt must report the capture delta: every
   destructive or unexpected command observed in the raw capture, including ones that
   bear on no claimed test. If independent capture or external pinning cannot be
   established for a wave, the council treats completeness as UNPROVEN and must not
   infer it from Hermes's summary.
4. **Council REJECT is mandatory** if any manifest item is missing. Hermes is not a
   trust root for omission.

## 4. T0.5 cold-session row (challenge/response; limits stated)

Rev-1's claim that faking is "structurally impossible" is **withdrawn** (ChatGPT T0.5).
What is true and what is required:

- Hermes cannot open the owner's fresh session (a fresh session carries zero prior
  context by the platform's session semantics). That isolates session state; it does
  not by itself prove the exchange is what it claims to be.
- The owner-pasted line is the cold-session **trigger/input only** — Hermes prepares it
  in advance and it MUST NOT contain the words PASS, FAIL, or CLOSED.
- The fresh session must then produce a response to a follow-up **challenge** that was
  not contained in the prepared paste, and the owner **attests** that the session was
  newly opened with no carried conversation context.
- The cold-session exchange log (with the §3 capture telemetry) is committed and
  pinned, and the **council inspects the resulting exchange at its pinned source**.
- Pass/fail comes solely from committed command-output evidence under council review —
  never from the paste, the attestation alone, or Hermes.
- Limits stated accurately: this makes silent fabrication by Hermes detectable and
  requires a real human keystroke in a fresh session; it does not constitute
  cryptographic proof of the operator's cognitive state.

## 5. Destructive-op gating (interview approval + live re-confirm)

Hard rule: nothing irreversible runs until (i) this protocol is council-ACCEPTED
(PR #17), (ii) the specific op's blast radius was presented in the approval question,
and (iii) for the class below, a fresh live confirmation is given immediately before
execution.

**Live re-confirm class** (Grok amendment 4 + ChatGPT C2): irreversible destruction or
removal of an authoritative or recovery copy of real data — e.g. C3 original-volume
removal/purge, any restore onto a non-drill path, deletion of a source volume/backup/
archive that is part of the only remaining recovery path, host-destructive actions
outside the compose project. Immediately before execution Hermes prints the exact
command, the resolved target, the live probe (mount/label/free-space/running-state),
and the consequence if any verified copy is unusable; the owner confirms against THAT
line. **If the live probe disagrees with the state described in the interview question
that collected the approval, the prior approval is void** and a fresh live answer is
required.

Interview-collected approvals remain sufficient for reversible in-project lifecycle
(scoped compose up/down of class-C services, sidecar restart, synthetic-job kill) once
the protocol is accepted.

## 6. Wave structure

Five waves. Each wave ends with: evidence committed → council prompt issued → both
verdicts recorded in the ledger → next wave. Council validation is per-wave; multi-wave
evidence is never collapsed into one end-loaded review (both members, Q4).

| Wave | Hermes executes | Owner says (total sentences) |
|---|---|---|
| 0 | (after protocol ACCEPT) C1/C2 host prep; readiness re-check | rulings for execution-blocking open decisions (D-06/07/11/17/18, OQ-9 as needed) — shape (c). Wave-0 pack gets its own council validation (§2a). |
| 1 | C3/C4/C5 prep: archive + copy + drill (writes only, zero destructive) | 3 approvals (shape a) + 1 risk acceptance (F-1, shape b) + read-back (§6a) |
| 2 | Build chain: compose up, pin digests, sidecar smoke, archive fetch (§8), **then the cold-session row (§4)** | 1 fetch + 1 paste + 1 challenge answer (§4) + read-back |
| 3 | Verification chain: T-13, T-16, T-15, T-19, T-05, solve attempt, R-4/R-5/R-7 live walk with T-11 evidence (first live execution closes the three exceptions) | 0 unless a live re-confirm (§5) or an irreversible fork appears; + read-back |
| 4 | Evidence pack + prompts | 8 signatures via shape (c): DR §2b (2 rows) + QA §5 (3 rows) + ops §2d + D-18 + M0 CLOSED (one owner transcript; council 2/2 on evidence per §1a) + final read-back |

**Irreversible fork rule.** The moment live execution reaches something irreversible
that wasn't anticipated, Hermes stops, presents the fork as a shape (a)/(b) question,
and waits. No proceeding on inference.

### 6a. Wave read-back (ChatGPT C3.3)

After each wave, Hermes presents the exact transcript entries and their wave-level
hash; the owner confirms. The confirmation is recorded as a separate authority row.
Original entries are never silently rewritten — corrections are appended. A hash chain
proves tamper-evidence of committed entries, not speaker identity; the read-back rows
are what authenticate the record with the owner.

**Total expected owner labor: ~20 sentences + 1 fetch + 1 paste + 1 challenge answer +
5 read-back confirmations. No typing of commands, no assembly, no transcription work.**

## 7. Transcript

`workflows/m0-interview-transcript.md` — one row per question/answer, sha256-chained
(§6a), owner text verbatim, never edited; corrections appended as new rows, never
rewritten. Wave-level hashes for the read-back. This file is itself evidence in every
council pack.

## 8. The human keyboard moments (complete list)

1. Wave 2: fetch the archive once (`curl` the pinned-branch archive to `~/he-build/`
   — no git clone; build box has no repo access) + open the fresh session + paste the
   prepared trigger + answer the follow-up challenge (§4).
2. Authority sentences + per-wave read-back confirmations (spoken/typed as chat
   messages, executed by Hermes as transcript rows).

Everything else — every `make`, every drill, every hash — is Hermes's keyboard.

## 9. What this protocol does NOT do

- Does not make R-4/R-5/R-7 papers executable; they close on first live execution with
  T-11-class evidence, produced under this protocol in Wave 3.
- Does not re-admit the round-05 council ops-walk as §9 ops sign-off (unregistered
  hybrid stays closed).
- Does not weaken §9, D-15/D-16, or any HARD STOP. The owner's authority sentences
  remain the only source of authorization.
- Does not establish runtime behavior until waves actually run; council ACCEPT of this
  protocol authorizes Wave 0 to begin, nothing more.
