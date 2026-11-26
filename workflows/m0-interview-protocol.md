# M0 Interview Protocol (Round-07) — rev-5

**Purpose.** Progress through the M0 gate with the human operator contributing only judgment (plus the bounded owner-run cutover sequence, §3.1), never mechanical labor. Every mechanical act — typing commands, running drills, hashing outputs, drafting evidence — runs through the plan-gated broker (§3) or is verified by the council. This protocol is a PROCESS design: it changes no ticket, no gate, no §9 row, no D-number, grants no authorization, and changes no council standard (evidence rules, 2/2 verdicts, three-state discipline, §9 exceptions, DESIGN-REVIEW §10 HARD STOP all unchanged). It defines who does what during M0 execution and what counts as evidence. The operator's total contribution across all of M0 is: ~20 sentences of authority (one per approval/ruling/signature, verbatim), one cold-session paste plus one challenge response, one archive fetch, and the bounded owner-run cutover sequence with the owner's own hands (§3.1, counted honestly in §8). Nothing else typed into a shell, nothing manually assembled.

**rev-2.** Council round-1 at pin `fd024d8f`: Grok ACCEPT-WITH-CHANGES (amendments 1–4) and ChatGPT ACCEPT-WITH-CHANGES (amendments 1–5). All adopted; source replies in `workflows/adviser-input/round-07/`.
**rev-3.** Council round-2 at pin `2951d35`: Grok ACCEPT (amendments 1–4 verified adopted; §3 residual accepted as bounded to the single-operator threat model) + ChatGPT ACCEPT-WITH-CHANGES (Q3: §3 must specify an execution broker + independently controlled capture so Hermes cannot control the evidence boundary, plus a bypass-detection test). Rev-3 implements that design on existing infrastructure: a dedicated m0broker account, plan-gated execution, evidence-repo write separation, §3.6 cutover test — and keeps Grok's limitation statement as §3.8. Nothing else in the protocol changes. Rev-3 goes to council re-verification; both members must ACCEPT the same pin.
**rev-4.** Council re-pin-2 at pin `cf4a804`: Grok **ACCEPT** (§3.8 limitation preserved; §8 labor honesty accepted; Q4 sequencing confirmed) + ChatGPT **REJECT** — architecture accepted, implementation rejected: plan authorization was a recomputed digest rather than a verified owner signature, runner failure paths unchecked, evidence could fail to publish silently, setup labor understated, credential revocation unproven. Rev-4 is that narrow implementation repair, per ChatGPT's own instruction ("no architectural redesign… no second machine, TPM, or remote-attestation infrastructure"). All seven required repairs are implemented and exercised by `scripts/qa/test_broker_p0.py` (8/8 green, real `ssh-keygen -Y` signatures + real git remotes, no mocks). Source replies archived in `workflows/adviser-input/round-07/`. Rev-4 goes to re-pin-3; both members must ACCEPT the same pin.
**rev-5.** Council re-pin-3 at pin `1ce2b3c`: Grok **ACCEPT — stands at this pin** (§3.8 substance unchanged; every rev-4 delta assessed as implementation repair inside the accepted architecture; no change required) + ChatGPT **REJECT — narrower** (architecture, §3.8, plan authorization, capture fields all ACCEPTED items; five implementation P0s block: in-memory processed-set ⇒ replay after restart; no uncertain-execution recovery; blanket authorized_keys emptying could strand owner access; per-fingerprint re-probe promised not implemented; malformed queue lines vanish silently; plus P1s: §6 labor-count inconsistency, `--once` claimed but absent — a false claim in the re-pin-3 prompt, recorded honestly — public retention repo unprotected). Rev-5 is the targeted reliability repair ChatGPT recommended: durable execution-state lifecycle (`started`/`executed`/`published`, UNPROVEN on uncertain outcomes, never automatic re-execution), disposition-for-every-line, selective by-fingerprint revocation with declared owner recovery + per-credential verification record, real `--once`, public-repo protection contract, §6 count fixed. Test suite expanded to 11 scenarios / 18 assertions, all green. Source replies archived in `workflows/adviser-input/round-07/`. Rev-5 goes to re-pin-4; both members must ACCEPT the same pin.

**Precedent.** This is the round-05 interview pattern (engineering walk: one line per
row, transcript pinned, council cross-examined) extended from paper rows to live M0
execution. The council accepted the pattern's discipline at `adca8a4`; nothing here
weakens it — it only removes keystrokes from the human path.

## 1. Roles

- **Owner (the only human):** approvals, risk acceptance, open-decision rulings,
  sign-offs. Answers in one sentence each. Runs the one-time broker setup script with
  own hands (§3.1 — the only owned execution act, and the act that removes Hermes's
  host authority). Otherwise never executes commands, never assembles evidence, never
  types into a shell beyond the single cold-session paste (§4) and the single archive
  fetch (§8).
- **Broker (m0broker — the only execution path after cutover):** a dedicated host
  account that Hermes has no credentials for. Executes only plan-listed commands and
  pushes capture records to the evidence repo under its own key (§3). This is what
  moves the evidence boundary out of the executor's hands.
- **Hermes (interviewer/scribe, NOT a trust root and NOT an executor after cutover):**
  prepares command blocks, drafts plans + evidence packs, commits manifests and
  transcript rows. After cutover it holds no host credentials (§3.1) and cannot write
  the broker's evidence commits (§3.4); its own commits are audited against the
  broker's record (§3.7).
- **Council (Grok + ChatGPT, quorum 2/2):** independent review of every wave's evidence
  at pinned SHAs, 2-of-2, same discipline as rounds 01–06, fetching the broker's raw
  record URLs directly (§3.7). Council validates EVIDENCE (was the recorded evidence
  complete and does it show what is claimed); only the owner authorizes.

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

## 3. Evidence capture: broker architecture (rev-5; ChatGPT re-pin-3 reliability repair at `1ce2b3c…`)

Round-2 finding adopted: shell telemetry plus an externally pinned digest makes
submitted records tamper-evident but does NOT prove complete capture — an executor that
controls the shell also controls the evidence boundary, and Hermes is both executor and
scribe. Rev-3 moved execution and capture out of Hermes's control. Rev-4 makes the
implementation match that architecture, exactly as ChatGPT's re-pin-2 recommended: no
design change, no second machine, no TPM, no remote attestation. The §3.8 limitation
statement is unchanged from rev-3.

**3.1 — Broker setup (owner-run; honestly counted).** Before Wave 0 consumes any command whose
truth depends on capture completeness, the owner provisions a dedicated Unix account
(`m0broker`) on the host by running one committed script — `scripts/m0-broker-setup.sh`
— with the owner's own hands, after reading it. The script is two-phase and its labor is
counted exactly in §8: phase 1 provisions (creates m0broker with no sudo and no
privileged group beyond docker, asserted by an `id -nG` gate; installs the broker runner
as a systemd unit under that account and starts it — active service is a hard gate for
phase 2; generates the broker-only GitHub deploy key, which the owner registers with
write access to the evidence repo's broker branch and proves with `git ls-remote`).
Phase 2 (`--confirm-cutover`) lists EVERY authorized_keys entry on the host by
fingerprint with its source file — no name-substring matching — and, only after the
owner re-runs it with `M0_CUTOVER_CONFIRMED=yes`, performs SELECTIVE revocation via
`scripts/m0-broker-revoke-keys.sh` (rev-5; ChatGPT re-pin-3 finding 4): credentials are
removed BY FINGERPRINT from an owner-supplied revocation list — never blanket file
emptying, which could strand owner/admin access — and the script REFUSES to run unless
the owner declares a recovery path (`M0_RECOVERY=keep:<fpr>`, a retained owner key
verified present after revocation, or `recovery:<fpr>` removed-but-announced). It then
RE-PROBES EVERY inventoried fingerprint individually and writes
`cutover-verification.txt`: every revoked key must read ABSENT, the recovery key's state
must be as declared; any wrong-state entry exits non-zero and is an automatic cutover
failure. Revocation is then PROVEN, not assumed: §3.6 re-attempts every inventoried
Hermes credential from the container and the broker records each result. Abort between
phases is
recoverable and non-destructive (Hermes keeps working, broker idle). The script's
terminal output is committed as a Wave-0 evidence row — owner-run acts are owner
records — and the council verifies the POST-cutover state from the broker side per
§3.6, not from the script's promises. The broker account holds docker-group access,
which is host-root-equivalent: that is a known, stated property of the design (§3.8),
acceptable because the broker enforces §3.3's plan gate before it uses that privilege,
and it is why the runner's fail-closed behavior is tested, not assumed.

**3.2 — No direct execution after cutover.** Every M0 host operation runs only through
the broker. Hermes holds no host credentials, no docker socket access, and no key to the
evidence repo's protected branches — so it cannot bypass, disable, or alter broker
capture. (The container→host SSH channel is the single point of execution authority
today, which makes §3.1's revocation step the load-bearing one.)

**3.3 — Plan-gated execution with authenticated authorization.** Each wave carries a plan
file — the exact commands with full argv — listed in the interview and owner-confirmed
in the §6a read-back. The plan is CRYPTOGRAPHICALLY authorized, not merely hashed: before
the broker may execute anything, `workflows/m0-plans/open.json` must carry an OpenSSH
detached signature (`open.json.sig`) that verifies via `ssh-keygen -Y verify` against an
owner-pinned `allowed_signers` file (namespace `file`; the owner principal is pinned in
the broker's own config — `allowed_signers` + `owner_principal` — which lives on the
broker account and is not writable by the host; a plan signed by any key not in that
file authorizes nothing — rev-5 wording fix per ChatGPT re-pin-3 §2 repair 1). A matching digest
proves consistency; only the signature proves authorization — rev-4's central repair
(ChatGPT re-pin-2, property 3). The broker recomputes every request digest from the argv
it itself would execute and matches it against the signed plan; a caller-supplied digest
is recorded but never trusted. An unverifiable, unsigned, or internally inconsistent plan
means NOTHING executes, and every queued request gets a broker-committed refusal record
citing the reason. EVERY queue line receives a disposition (rev-5; ChatGPT re-pin-3
finding 5): valid+authorized ⇒ execute; valid+unauthorized ⇒ refusal record; malformed
JSON or non-object line ⇒ `invalid-<hash>` refusal record; missing or invalid request id
⇒ `noid-<hash>` / `invalid-<hash>` refusal record. No input disappears silently; silent
skip is itself the bypass this section forbids. Execution is a DURABLE LIFECYCLE
(rev-5's central repair, ChatGPT re-pin-3 principal finding): before any subprocess the
broker writes a `started` state to its private durable ledger (outside the evidence
repo, outside Hermes); after the subprocess it writes `executed` with the full record;
after a CONFIRMED push it writes `published`. On restart the broker answers three
questions per request from durable state alone — authorized? outcome certain? evidence
published? — and an interrupted request whose state is stuck `started` is answered
**UNPROVEN**: a refusal record with `unproven: true`, NEVER automatic re-execution;
re-running an uncertain operation requires a separate explicit owner recovery decision.
Executed-but-unpublished evidence is replayed by content re-publish (never re-execution),
so at-least-once execution is structurally impossible. A refusal record is a detected bypass attempt — visible to the
council, never silently dropped. The initial Wave-0 plan is drafted, digest-established,
owner-confirmed, and broker-authenticated in exactly that order (ChatGPT re-pin-2 §6);
an absent plan is a refusal state, never an exception to plan-gating.

**3.4 — Capture outside the execution boundary.** The broker pushes the full record of
every operation — request, exact argv, start/end timestamps, exit code, complete
stdout/stderr including failures, digests of produced artifacts, and the authenticated
plan digest the request matched — directly to the evidence repo under its own key, as
commits Hermes neither authors nor relays. Hermes may cite URLs; it cannot author, edit,
or reorder those bytes. Publication is not silent: every git step (fetch, write, commit,
push) is exit-checked, each request's durable state reaches `published` only from a
CONFIRMED push, evidence left unpushed is re-published on the next cycle WITHOUT
re-executing the command (the durable ledger proves the outcome), and repeated push
failure exits the runner non-zero so systemd restarts it with backoff and a stalled
evidence pipeline becomes loud rather than quiet (§3.5). The runner's `--once` mode
performs exactly one fetch/process/publish cycle and exits — the mode the test harness
and any manual verification use; `--daemon` is the systemd loop (rev-5: `--once` is
implemented, not merely claimed — proven by regression test P0-10).

**3.5 — No-unlogged-path rule + per-wave manifest.** Any M0-relevant operation class
that cannot be routed through or observed by the broker is excluded from the wave and
recorded in the explicit "what was not run" list, treated as unproven — never silently
assumed captured. Each wave commits: the broker's full wave record, the pass AND
fail/skip rows, the wave's transcript rows, and the not-run list. Any planned operation
missing from the broker record is a delta row with a stated reason (delta duty).
Because capture is full, retention is bounded: raw evidence lives in the private
evidence repo under branch protection for the project's duration; at each wave close the
broker additionally publishes a retention pack — the wave manifest, every record's
request/argv/timestamps/exit-code/plan-digest, full record and artifact SHA-256s, and
the evidence-branch HEAD at close — committed to the PUBLIC toolstack repo
(`workflows/m0-retention/`). Public-record permanence therefore rests on small digests
plus pack hashes that survive any private-repo deletion, while bulk stdout/stderr stays
private without pretending months-to-years of private history is a public anchor
(ChatGPT re-pin-2, repair 6). The PUBLIC retention repository carries the SAME protection
contract as the private one (rev-5; ChatGPT re-pin-3 repair 5): force-push and branch
deletion disabled, each wave's pack commit pinned by digest in that wave's evidence pack,
and the council independently retrieves the pack and verifies pack digest +
evidence-branch HEAD at every wave close — a Wave-0 configuration and verification
requirement, with a test pack published and council-fetched during Wave 0 itself. Absence
of Rekor is never classified as a failure when this mechanism verifies (ChatGPT re-pin-3 §6).

**3.6 — Cutover bypass-detection test (Wave-0 gate; ChatGPT's required test).**
Immediately after cutover, before any later wave consumes a command whose truth depends
on capture completeness, all six of the following are executed and committed:
(a) the Hermes identity attempts host SSH — must be refused, host-side log line
captured; (b) the Hermes identity probes the docker socket — must be permission-denied;
(c) an out-of-plan request to the broker — must produce a refusal record; (d) a
broker-authored evidence commit — the council fetches the evidence repo raw URL and
verifies the commit author and payload directly; (e) the broker's signed-plan gate — the
council fetches `workflows/m0-plans/open.json` + `open.json.sig` raw, runs
`ssh-keygen -Y verify` itself against the owner's pinned key, and confirms a tampered
variant is refused (the test suite's P0-2 is the reproducible sim of this); (f) the
durability contract — the council verifies from the broker's unit file and the test
suite (P0-6/7/8) that restart cannot re-execute a decided request and an uncertain
execution surfaces as UNPROVEN. Together,
(a) + the setup script's pre-cutover fingerprint inventory VERIFY revocation — every
credential the inventory listed is re-probed for refusal, each result recorded
separately in `cutover-verification.txt` (rev-5; per-fingerprint, not one representative
key) — rather than assuming the
removal step succeeded. Until all six are verified, capture
completeness is UNPROVEN and no evidence row binds. A failure here is never repaired by
weakening the test: it returns the project to pre-cutover state and a protocol rev.

**3.7 — Anchoring + independent reconciliation.** The anchor is the evidence repo's git
history — server-side chronology, append-only enforced by push rights (Hermes holds
none; force-push disabled via branch protection; the broker's records are never
rewritten). Broker commits are plain commits under the broker's identity; their
authentication comes from the deploy key's push rights plus the §3.3 plan signature and
the §3.6(e) council-side verify, not from embedded commit signatures. When public
transparency logging is reachable (Sigstore Rekor), the broker additionally publishes a
per-wave checkpoint digest there; where unreachable, the §3.5 public retention pack is
the anchoring mechanism and the council checks the pack digest at every wave close. The
council receives
the broker's complete wave record, fetches it directly from pinned raw URLs — never from
a Hermes summary — and reconciles it against the manifest, transcript, pass/fail/skip
rows, and declared operations. Missing records or unexplained gaps ⇒ council REJECT is
mandatory. Hermes is not a trust root for omission.

**3.8 — Limitation statement (required; do not overclaim).** The broker is a separate
account, key, and commit identity on the same physical host — not a second machine and
not a hardware root of trust. A colluding owner can alter the broker; the owner is the
single point of ultimate authority in this project by design (§9). Rev-4 claims exactly
what rev-3 claimed (Grok's accepted wording, unchanged):
completeness of capture against Hermes as adversarial executor (no host credentials
post-cutover, plan-gated execution, refusal records, council-fetched evidence). Rev-4
does not claim: cryptographic proof of honesty against the owner.

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
- The cold-session exchange runs as a broker request under the open wave's signed plan,
  so the exchange log lives in the broker's §3.4 record — the same capture path as every
  other command. It is committed and pinned, and the council inspects the exchange at
  its pinned source.
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
| 0 | (after protocol ACCEPT) broker setup + §3.6 cutover test (owner runs the full §3.1 sequence: phase-1 script, GitHub deploy key, phase-2 inventory, revocation fingerprint list + confirm run); C1/C2 host prep via broker; readiness re-check | the full §3.1 cutover sequence (§8 rows 1–4, not "one script run" — see §8 for the itemized count) + rulings for execution-blocking open decisions (D-06/07/11/17/18, OQ-9 as needed) — shape (c). Wave-0 pack gets its own council validation (§2a). |
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
the full §3.1 cutover sequence (per §8: phase-1 script run, GitHub deploy-key
registration, phase-2 inventory run, revocation fingerprint list + confirm run, ≈4–5
short interactions with verification checks) + 5 read-back confirmations. No typing of
commands, no assembly, no transcription work.**

## 7. Transcript

`workflows/m0-interview-transcript.md` — one row per question/answer, sha256-chained
(§6a), owner text verbatim, never edited; corrections appended as new rows, never
rewritten. Wave-level hashes for the read-back. This file is itself evidence in every
council pack, reconciled per §3.7 against the broker's record.

## 8. The human keyboard moments (complete list)

1. Wave 0: the broker cutover (§3.1), with own hands — the act that ends Hermes's host
   execution authority. Honestly counted, this is: read the setup + revoke scripts once;
   run phase 1 (provision + service start); register the broker deploy key on GitHub
   (web); run phase 2 `--confirm-cutover` once to read the fingerprint inventory, supply
   the revocation fingerprint list + declared recovery key, then re-run with
   `M0_CUTOVER_CONFIRMED=yes` to execute selective revocation and read
   `cutover-verification.txt`. That is 3 script invocations + 1 web interaction + 1
   fingerprint-list supply — one reading, ~4–5 short interactions total, not the "one
   run" rev-3 understated (ChatGPT re-pin-2 repair 4; re-pin-3 repair 3 §6 consistency).
2. Wave 2: fetch the archive once (`curl` the pinned-branch archive to `~/he-build/`
   — no git clone; build box has no repo access) + open the fresh session + paste the
   prepared trigger + answer the follow-up challenge (§4).
3. Authority sentences + per-wave read-back confirmations (spoken/typed as chat
   messages, executed by Hermes as transcript rows).

Everything else — every `make`, every drill, every hash — runs through the broker (§3).

## 9. What this protocol does NOT do

- Does not make R-4/R-5/R-7 papers executable; they close on first live execution with
  T-11-class evidence, produced under this protocol in Wave 3.
- Does not re-admit the round-05 council ops-walk as §9 ops sign-off (unregistered
  hybrid stays closed).
- Does not weaken §9, D-15/D-16, or any HARD STOP. The owner's authority sentences
  remain the only source of authorization.
- Does not establish runtime behavior until waves actually run; council ACCEPT of this
  protocol authorizes Wave 0 to begin, nothing more.
