# Round-07 — Council re-pin prompt: protocol rev-7 (re-pin-5 repair cycle)

Round: Round-07 (M0 interview protocol), sixth repair cycle. Targets: ChatGPT and Grok (voting members); Claude (advisor seat — runner scope, your re-pin-5 required change + 5 non-blocking requests).

## Declared pin

`6c19da3dda22cba681ab69d5ae530e214e56fa49` (branch `dp/round-07-m0-interview`)

## Raw sources at this exact pin

- Protocol **rev-7**: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/workflows/m0-interview-protocol.md
- Broker runner (rev-7): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/scripts/m0-broker-runner.py
- Broker setup script: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/scripts/m0-broker-setup.sh
- Credential-revocation script (rev-7): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/scripts/m0-broker-revoke-keys.sh
- Broker test suite (rev-7, executable evidence, read as text): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/scripts/qa/test_broker_p0.py
- Your re-pin-5 replies, archived verbatim: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/workflows/adviser-input/round-07/reply-chatgpt-protocol-repin5.md, https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/workflows/adviser-input/round-07/reply-grok-protocol-repin5.md, https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/workflows/adviser-input/round-07/reply-claude-protocol-repin5.md
- Ledger (row `DP-R7-rev7`): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/6c19da3/workflows/ledger.md

## Process correction adopted (Grok re-pin-5 Q2)

This prompt implements your proposed hygiene rule verbatim: **every claim below cites `path:symbol` with a line anchor AT THE DECLARED PIN, or a test-id with the exact line of its `check(` call; the claim→evidence table was generated mechanically from `git show 6c19da3:…` output, not from memory.** Where a fix has code but NO dedicated test, the table says so explicitly rather than implying coverage. The three false claims in the re-pin-5 prompt (P0-12b "concurrent readers", P0-11b2 "inventory-less test", "real sshd") are recorded in the rev-7 changelog AND in ledger row DP-R7-rev7, and the test docstrings/claims are corrected at this pin: P0-12b is now claimed only as "atomic + correct completed write", the real inventory-less regression is new P0-11e, and the docstring states plainly there is no sshd anywhere (revoke legs use temporary authorized_keys FILES + real `ssh-keygen`).

## What rev-7 changed (mapped to your re-pin-5 inputs)

Architecture untouched: §3.8 is byte-identical to the wording Grok accepted — verified mechanically (`git show 8509096:workflows/m0-interview-protocol.md` slice `**3.8` → `## 4` vs the same slice at this pin; zero diff). No second machine, no TPM, no attestation — this is ChatGPT's own "targeted reliability repair, not redesign" category: identity, execution certainty, authorization limits.

## Claim → evidence table (anchors at 6c19da3)

Line numbers below were extracted from `git show 6c19da3:` content; `runner` = `scripts/m0-broker-runner.py`, `test` = `scripts/qa/test_broker_p0.py`, `revoke` = `scripts/m0-broker-revoke-keys.sh`.

| # | Claim | Code anchor | Test anchor (body present) |
|---|-------|-------------|----------------------------|
| 1 | **ChatGPT blocker 1** — ID/hash collision is evaluated BEFORE every lifecycle branch, `started` included; collision vs a crashed request keeps the original `started` state and answers the conflicting line with `ID-COLLISION` preserving BOTH `request_line_sha256` values | runner: collision block L407–431 ("ID-COLLISION: request id reused…" L418) | test L590 (P0-13a collision refused), L596 (P0-13b colliding argv never executes), L617 (P0-13c collision BEFORE started-branch — never UNPROVEN), L622 (P0-13d original `started` survives untouched), L381 (P0-8c collision under an already-disposed id cites original line-hash in refusal) |
| 2 | **ChatGPT blocker 2** — restart recovery reads the DURABLE RECORD before classifying `started` as UNPROVEN; a record proving `spawn_succeeded: false` recovers as the definite failure it documents; a completed-record + stale `started` recovers the definite outcome | runner: recovery block L432–448 (`rec.get("spawn_succeeded") is False` L442) | test L771 (P0-18a definite completion + `started` → RECOVERED, never UNPROVEN), L773 (P0-18b recovered outcome never re-executes), L710 (P0-17b definite spawn failure never becomes UNPROVEN after restart) |
| 3 | **ChatGPT blocker 3** — corrupted use-budget FAILS CLOSED: missing file = zero uses, valid file = recorded count, corrupt/inconsistent file = `BUDGET-STATE-CORRUPT` refusal + broker-level integrity error, never a fresh allowance | runner: `usage_count` L278, corrupt refuse L505, `bump_usage` corrupt raise L303 | test L790 (P0-19a corrupt budget file → refusal, zero exec), L796 (P0-19b owner removes corrupt file → path executes again — recovery is an explicit owner act) |
| 4 | **Claude required change** — a PRESENT-but-unsigned / signature-FAILED / structurally-unreadable plan is UNVERIFIABLE, never terminal: queued requests stay PENDING, zero dispositions written, a later valid signature runs the SAME ids; P0-1/P0-2 assert the new semantics | runner: `verify_plan` L176; docstring L182 "unverifiable is NEVER terminal"; PENDING path L472 | test L231 (P0-1a unsigned → no exec, PENDING), L237 (P0-1b later signature runs SAME id), L248–258 (P0-2/2b/2c tamper → PENDING zero dispositions; re-sign supersedes and the id still runs) |
| 5 | **Claude req. 1** — budget keyed PER COMMAND to canonical sha256(argv + artifacts + max_runs): a re-sign that adds commands resets no other command's budget; changing argv/artifacts/max_runs starts a genuinely different budget | runner: keying comment + computation L494–499 | test L664 (P0-15 budget survives fresh request ids under per-command keying — check title updated at this pin) |
| 6 | **Claude req. 2** — spawn catch broadened to `except Exception`: ANY spawn exception means never-started → definite `spawn_succeeded: false` record, never `started` pretending uncertainty | runner: L533, definite record L551 | test L737 (P0-17c injected non-OSError at spawn → definite SPAWN-FAILED, never `started`, never executed) |
| 7 | **Claude req. 3** — §3.3 states the residual trust base rather than leaving it implicit (signed set = listed artifacts only; worktree-at-origin assumption) | protocol §3.3 "RESIDUAL TRUST BASE" paragraph | n/a — documentation claim; readable in the §3.3 slice at the pin |
| 8 | **Claude req. 4 / ChatGPT accuracy P1** — test docstring corrected: "Two instrumented exceptions" (P0-12 fsync counter, P0-17c argv-scoped spawn trap); no-sshd stated; "no mocks" overclaim retracted | test docstring L4–11 | n/a — the claims themselves are the subject |
| 9 | **Claude req. 5** — queue read as BYTES, decoded PER LINE: one undecodable byte refuses exactly its own line, the pass continues | runner: L375 `q.read_bytes().split(b"\n")` + per-line decode L377–379 | test L419 (P0-9b bad byte → that line refused, pass continues), L432/L441 (P0-9c empty-argv plan entry → unverifiable → PENDING; corrected signature then executes the same id) |
| 10 | **ChatGPT P1** — explicit inventory-less regression: revoke script now REFUSES at entry when `M0_INVENTORY` is unset (rev-6 WARN+proceed REMOVED), non-zero exit | revoke: L107 `REFUSE: M0_INVENTORY unset …` `exit 1` | test L542 (P0-11e runs the script with `M0_INVENTORY=""` → refuses, no side effects) |
| 11 | **ChatGPT P1** — full new-directory-chain fsync on first nested write (dir entry durability, not just file+parent) | runner: `_sync_dir_chain` L104, used by `durable_write` L127 | test L570 (P0-12c fsync call-set covers file + every newly created dir); L559 (P0-12a file+parent ≥2 fsyncs), L561 (P0-12b — honestly scoped: atomic completed write only) |
| 12 | Code present, **no dedicated test** (honest row): durable-record history participates in the budget via `max(counter, records)` (broker-state wipe cannot reset a budget whose executions are on record); `spawn_succeeded: false` never-spawned records excluded from that history count | runner: `max(used, record_history_count(…))` L511–512; `record_history_count` L308–324 (exclusion L324) | EXERCISED INDIRECTLY on every budget-path check (P0-15, P0-17a/b/c); no check isolates either behavior alone. Not claimed as tested. |

## Test suite status at this pin

`scripts/qa/test_broker_p0.py`: 19 scenarios / 45 checks, **45 PASS / 0 FAIL** (executed on this tree before push; suite runs real `ssh-keygen -Y` signatures, real git remotes with a real rejecting `pre-receive` hook, real subprocess crash/restart simulations — fresh runner PROCESS per pass; no network; `unittest.mock` used ONLY as the docstring's two instrumented exceptions). Docstring scenario list and test bodies one-to-one. Repo gates: 27 PASS / 0 FAIL.

## Questions for this re-pin

**ChatGPT (voting):** Q1 — are your three re-pin-5 P0 blockers each adequately repaired at this pin per the claim→evidence table (verify the anchors, not the prose)? Q2 — row 12 deliberately declares two behaviors without dedicated tests; does that disclosure satisfy you for this pin, or is a dedicated test a blocking requirement? Q3 — do the recorded walk-backs (rev-7 changelog + ledger DP-R7-rev7) plus the mechanically-generated table format satisfy your accuracy standard after three prompt-accuracy failures in this round? Q4 — vote on rev-7 at `6c19da3…`.

**Grok (voting):** §3.8 byte-identical at this pin (slice-diff vs `8509096`, zero diff). Q1 — does your ACCEPT stand? Q2 — is the claim→evidence table, generated from `git show <pin>` and including an explicit no-dedicated-test row, the format you intended by your re-pin-5 process rule? Q3 — vote on rev-7 at `6c19da3…`.

**Claude (advisor, runner scope):** your required change maps to row 4 (P0-1/P0-2 rewritten, PENDING-not-terminal, resign-supersedes) and requests 1–5 to rows 5, 6, 7, 8, 9. Do these discharge ACCEPT-WITH-CHANGES to ACCEPT (advisor advisory)?

## Verdict format

Reply with: pin reviewed (full SHA), per-question answers, vote (ACCEPT / ACCEPT-WITH-CHANGES / REJECT) + blocking items if any. Paper-only review; run nothing.
