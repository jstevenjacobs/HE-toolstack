# Round-07 — Council re-pin prompt: protocol rev-8 (re-pin-6 repair cycle)

Round: Round-07 (M0 interview protocol), seventh repair cycle. Targets: ChatGPT and Grok (voting members); Claude (advisor seat — runner scope, your re-pin-6 requirement maps to row 7). Your re-pin-6 replies are archived verbatim at the pin (links below). Rev-7 went 1/2 ACCEPT (Grok ACCEPT; ChatGPT and Claude ACCEPT-WITH-CHANGES); rev-8 is the targeted repair of exactly the items your re-pin-6 replies required. Architecture untouched.

## Declared pin

`a6953989fe74ba256dae90215ac41208d570a32d` (branch `dp/round-07-m0-interview`) — the last commit touching any reviewed file. Gate/tooling commits after it (`d7858fc` onward, gate tooling only) touch only `scripts/qa/gen_claim_table_repin7.py`, never the runner, suite, protocol, or revoke script; `git diff a695398 HEAD -- <reviewed paths>` is empty.

## Raw sources at this exact pin

- Protocol **rev-8**: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/m0-interview-protocol.md
- Broker runner (rev-8): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/scripts/m0-broker-runner.py
- Broker setup script: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/scripts/m0-broker-setup.sh
- Credential-revocation script (unchanged since rev-7; row 21): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/scripts/m0-broker-revoke-keys.sh
- Broker test suite (rev-8, executable evidence, read as text): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/scripts/qa/test_broker_p0.py
- Your re-pin-6 replies, archived verbatim:
  - ChatGPT: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/adviser-input/round-07/reply-chatgpt-protocol-repin6.md
  - Grok: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/adviser-input/round-07/reply-grok-protocol-repin6.md
  - Claude: https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/adviser-input/round-07/reply-claude-protocol-repin6.md
- Ledger (row `DP-R7-rev8`): https://raw.githubusercontent.com/jstevenjacobs/HE-toolstack/a6953989fe74ba256dae90215ac41208d570a32d/workflows/ledger.md

## Process gates adopted (both from your own re-pin-6 instructions)

1. **Claim→evidence table, generated not asserted** (Grok re-pin-5 Q2, adopted as standing pre-send gate per your re-pin-6 suggestion): every row below was emitted by `scripts/qa/gen_claim_table_repin7.py` (committed at the pin's successor), which anchors each claim by substring-searching `git show a695398:<file>` and **fails loudly if any anchor is absent** — the gate caught three of my claims as literally false before send (wrong trap-function name, wrong variable name, a docstring line posing as a code site) and those rows were rewritten against the real code. Where a row says "live git-diff", the generator itself ran the diff (rows 20–21).
2. **Accuracy audit recorded honestly** (ChatGPT re-pin-6 P1-1): during that gate work I discovered that my earlier rev-7 §3.8 check (`awk '/^### 3.8/…'`) was **vacuous** — §3.8 is a bold marker (`**3.8 —`), not a heading, so the awk range matched nothing and any two vacuous extractions "compare equal". §3.8 **is** genuinely unchanged: re-verified with a corrected extractor (full text `**3.8 —` → next `## `, sha256) across `8509096` → `6c19da3` → `a695398`, all `c91a5b83e83c4235…` (row 20 is the live in-generator check). The over-claim was in my *verification method*, not the fact; disclosed because your P1-1 is precisely about audit-method precision.

## What rev-8 changed (mapped to your re-pin-6 inputs)

- **Shared blocker (ChatGPT P0-1 / Claude blocking 1)** — executed-but-undecodable commands used to be recorded `spawn_succeeded: false` and exempted from budget. Fixed: spawn is separated into `Popen` construction (the ONLY definite never-started path) vs post-construction failure; output captured as bytes and decoded **lossily** (`errors='replace'`) so decoding can never fail post-execution; a post-spawn uncertainty except writes an executed-with-error record and the budget bump happens the moment the child ran, pre-decode. Proven by P0-17d/d2/d3 (rows 4–5).
- **Claude blocking 2** — phantom `P0-16c` (docstring-only scenario) removed; its behavior is covered by the real P0-9c/P0-9c2 bodies (rows 7–8).
- **ChatGPT P1-3A (silent zero on corrupt usage)** — a usage file that parses but isn't a JSON object now yields a `CORRUPT:` sentinel; both the usage and history counters refuse dispatch (`BUDGET-STATE-CORRUPT`) instead of resetting to zero (rows 9–10).
- **ChatGPT P1-3B / Claude non-blocking 1 (corrupt request-state re-execution hole)** — `Ledger.load` returns an explicit `unreadable-corrupt` sentinel for unparseable state files; `run_pass` HOLDs such requests (`LEDGER-STATE-CORRUPT` log), never re-executes, while unaffected requests still run (rows 11–12).
- **ChatGPT P1-2 (non-object plan crashed the pass)** — `verify_plan` shape-checks plan and commands; malformed plan = UNVERIFIABLE → requests stay PENDING (rows 13–14).
- **§3.3 protocol text** updated to match the code exactly (spawn-construction scoping + the corrupt-state fail-closed trio), rows 18–19.
- Docstring over-claim about untracked ancestor chains fixed (16-level cap stated honestly, row 15). Revoke script untouched since rev-7 ACCEPT (row 21).

## Claim → evidence table (at pin a695398, mechanically generated)

Every line anchor below was extracted by the gate script from `git show a695398:<path>` content; a needle absent at the pin aborts the generator. Shorthand: runner = `scripts/m0-broker-runner.py`, test = `scripts/qa/test_broker_p0.py`.

| # | Claim (rev-8, at pin `a695398`) | Evidence (mechanically extracted) |
|---|---|---|
| 1 | Spawn construction (Popen) is the ONLY definite never-started path; no bump_usage on it | `scripts/m0-broker-runner.py:599` |
| 2 | Post-construction failure (communicate timeout / POST-SPAWN-UNCERTAIN except) still consumes budget — bump_usage runs immediately after the child ran, before decode | `scripts/m0-broker-runner.py:636 + :648` |
| 3 | Output captured as bytes, decoded lossily (errors='replace') so decode cannot fail | `scripts/m0-broker-runner.py:651` |
| 4 | P0-17d: invalid-UTF8 executed command consumes budget (never-spawned claim impossible) | `scripts/qa/test_broker_p0.py:801` |
| 5 | P0-17d2/d3: budget-exhausted after the executed-but-undecodable run; restart does not re-execute | `scripts/qa/test_broker_p0.py:808 + :815` |
| 6 | P0-17c traps Popen CONSTRUCTION (matches rev-8 code shape, not subprocess.run) | `scripts/qa/test_broker_p0.py:762` |
| 7 | Phantom P0-16c is GONE from the test docstring; docstring names P0-9c2 for that behavior | `P0-16c occurs 0 times in test@a695398; P0-9c2 named at test:457` |
| 8 | P0-9c2 body present (bad-signature plan -> PENDING -> later valid signature executes) | `scripts/qa/test_broker_p0.py:457` |
| 9 | usage_count: structurally-invalid-but-parsable JSON -> 'CORRUPT:' sentinel (silent zero impossible) | `scripts/m0-broker-runner.py:323` |
| 10 | record_history_count: corrupt history record -> CORRUPT:<file>; dispatch refuses BUDGET-STATE-CORRUPT (both usage + history refuse sites cited) | `scripts/m0-broker-runner.py:373 + :577` |
| 11 | Ledger.load corrupt state -> unreadable-corrupt sentinel; run_pass HOLDs, never re-executes | `scripts/m0-broker-runner.py:172 + :481 + :171` |
| 12 | P0-20a-f: usage non-object / history corrupt / state corrupt + sibling still runs, each proven | `scripts/qa/test_broker_p0.py:925…:1007` |
| 13 | verify_plan: non-object plan or non-list commands -> UNVERIFIABLE -> PENDING, no crash | `scripts/m0-broker-runner.py:253 + :258` |
| 14 | P0-9d: list-plan and non-list-commands both -> PENDING for every queued request | `scripts/qa/test_broker_p0.py:475` |
| 15 | _sync_dir_chain docstring states the 16-ancestor-level cap (no untracked-chain over-claim) | `scripts/m0-broker-runner.py:111` |
| 16 | Test suite: 22 scenarios / 57 checks; run on the exact pinned tree: 57 PASS / 0 FAIL (`FAILS: none`, exit 0) | `test:13 (docstring count) + executed log (0 lines matching '^FAIL ')` |
| 17 | Protocol title is rev-8; changelog records all three re-pin-6 verdicts | `workflows/m0-interview-protocol.md:1` |
| 18 | §3.3 scoped at rev-8: spawn CONSTRUCTION = definite never-executed; post-construction failure consumes budget | `workflows/m0-interview-protocol.md:223` |
| 19 | §3.3 rev-8 fail-closed trio: usage CORRUPT / history CORRUPT:<file> / state unreadable-corrupt hold | `workflows/m0-interview-protocol.md:209` |
| 20 | §3.8 limitation byte-identical 8509096 = 6c19da3 = a695398 (corrected extractor; sha256 prefix `c91a5b83e83c4235`) | `in-generator live diff — 'live git-diff at pin: … sha256-equal'` |
| 21 | Revoke script byte-identical since rev-7 (no new claims about it) | `git diff --quiet 6c19da3 a695398 -- scripts/m0-broker-revoke-keys.sh => clean` |

## Test suite status at this pin

`scripts/qa/test_broker_p0.py`: **22 scenarios / 57 checks — 57 PASS / 0 FAIL / exit 0** (`FAILS: none`), executed after the final reviewed-file commit on the exact pinned tree. The suite runs real `ssh-keygen -Y` signatures, a real local bare git remote with a rejecting pre-receive hook, real `ssh-keygen -lf` inventories, real subprocess crash/restart simulations. Two declared instrumented exceptions (P0-12 fsync counter, P0-17c argv-scoped Popen trap) are documented in the suite docstring; the docstring previously overclaimed "no mocks" — corrected at rev-7 and tracked as such.

## Questions for this re-pin

**ChatGPT (voting):** Q1 — are your re-pin-6 items each repaired at this pin per the table: the P0 spawn/decode budget bypass (rows 1–6) and P1-2 plan shapes (13–14), P1-3A usage corrupt (9–10), P1-3B corrupt-state hold (11–12), and the P1-1 audit-accuracy disclosure above? Q2 — does the vacuous-awk disclosure + corrected §3.8 verification (row 20) discharge P1-1, or do you require a different audit method stated in §3.6/§9? Q3 — any remaining blocking item at this pin, yes/no with anchor.

**Grok (voting):** §3.8 limitation statement byte-identical at this pin (in-generator diff, row 20 — and note the honest disclosure in gate section 2 about my earlier vacuous check). Q1 — does your ACCEPT stand at `a695398`? Q2 — with the table now emitted by a fail-loud generator committed in-tree, does the standing pre-send gate meet your Q2 bar?

**Claude (advisor, runner scope):** your two blocking items map to rows 1–6 (spawn/decode separation, lossy decode, budget bump pre-decode) and rows 7–8 (P0-16c phantom removed, P0-9c2 body present); non-blocking corrupt-state hole to rows 11–12. Confirm or re-open with anchors.

## Verdict format

Reply with: pin reviewed (full SHA `a6953989fe74ba256dae90215ac41208d570a32d`), per-question answers, vote (ACCEPT / ACCEPT-WITH-CHANGES / REJECT) + blocking items if any. Paper-only review; run nothing. Per §9, Wave 0 may BEGIN only on 2/2 voting ACCEPT at the same pin; Wave-0 rulings still need their own evidence + 2/2 validation (§2a), and DESIGN-REVIEW §10 HARD STOP is untouched.
