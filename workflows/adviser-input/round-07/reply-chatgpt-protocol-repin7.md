# CHATGPT — Round-07 re-pin-7 reply (protocol rev-8, pin `a6953989fe74ba256dae90215ac41208d570a32d`)

Executed independently against the pinned protocol, implementation, and tests. Paper-only — no test execution or operational authorization.

## Executive verdict

ACCEPT-WITH-CHANGES at the declared source pin: `a6953989fe74ba256dae90215ac41208d570a32d`

Rev-8 repairs the principal rev-7 defects: the spawn/decode budget bypass, malformed plan handling, structurally invalid usage files, corrupt execution-history records, and the missing request-state corruption handling. The new tests cover the previously missing started + spawn_succeeded: false recovery case.

Not an unconditional ACCEPT. Remaining: (a) a request-state corruption path the new P0-20f test does not cover, (b) a post-spawn timeout-cleanup path that can escape the new budget-accounting handler, (c) a mismatch in the prompt's claim that the 57-check run was performed against the declared pin.

## Q1 — Are the re-pin-6 items repaired?

| Item | Verdict | Review |
|---|---|---|
| Spawn/decode budget bypass | PARTIAL — remaining blocker | Popen split, byte capture, lossy decoding, pre-decode budget increment fix the original invalid-UTF-8 bypass. P0-17d/d2/d3 exercise the executed-invalid-output case. But the timeout-cleanup path has an unhandled exception window. |
| Non-object plan / invalid commands structure | MET | verify_plan() checks plan object + commands list-of-objects before accessing. P0-9d tests top-level list plan → PENDING not crash. |
| Structurally invalid usage JSON | MET | Non-object JSON, invalid counts, read errors return corruption sentinel; caller refuses dispatch. P0-20d tests valid JSON wrong shape. |
| Corrupt execution-history records | MET | Unparseable/non-object records return CORRUPT; dispatch refuses rather than silently reducing budget. P0-20e covers malformed history. |
| Corrupt request-state handling | PARTIAL | Malformed JSON is held, but non-object state and read-error paths are not fully handled through the publication phase. P0-20f tests malformed JSON only. |
| Plan-shape and docstring/body repairs | Implementation MET; claim mapping inaccurate | Behaviors exist, but the generated evidence table misidentifies one test and its location. |

### Remaining blocker 1 — timeout cleanup can bypass budget accounting (P0 — blocking)

Post-spawn structure:

```
try:
    raw_out, raw_err = proc.communicate(timeout=3600)
    exit_code = proc.returncode
except subprocess.TimeoutExpired:
    proc.kill()
    raw_out, raw_err = proc.communicate()
    exit_code, err = None, "TIMEOUT exceeded 3600s"
except Exception as e:
    raw_out, raw_err = b"", b""
    exit_code, err = None, f"POST-SPAWN-UNCERTAIN ..."
bump_usage(L, use_key)
```

The generic `except Exception` does not catch exceptions raised inside the `TimeoutExpired` handler. If `proc.kill()` or the second `proc.communicate()` raises, control exits before `bump_usage()` and before the durable execution record is written — request left `started` with no record. Restart conservatively marks UNPROVEN, but the per-command budget was not consumed: a fresh request ID can get another attempt.

Required repair:
- Every path after successful Popen construction must converge on durable budget consumption, including timeout-cleanup failures.
- Record a post-spawn uncertain outcome rather than letting a cleanup exception escape as if no execution occurred.
- Add P0-17e: simulate TimeoutExpired, then inject an exception from kill() or the second communicate(). Verify budget consumed, durable post-spawn outcome recorded, fresh request ID cannot re-execute the same command.

### Remaining issue 2 — corrupt request-state handling incomplete (P1)

1. `Ledger.load()` catches JSONDecodeError, not OSError. A state file that exists but cannot be read does not produce the claimed sentinel.
2. `Ledger.pending()` independently parses state files and calls `st.get("status")` without checking `st` is a dict. A state file containing valid JSON such as `[]` raises AttributeError during publication. `run_pass()` calls `L.pending()` after processing the queue.

P0-20f only plants malformed JSON (`{broken`), which pending() silently skips; neither failure above is covered.

Required repair: make `Ledger.load()` and `Ledger.pending()` consistently handle malformed, non-object, and unreadable state files. Add tests for list-shaped and unreadable state files; verify the affected request is held, unrelated requests can still be published, no request treated as unseen.

Not the same severity as the timeout bypass: principally a fail-closed reliability and evidence-publication defect. But the current broad protocol claim is not yet demonstrated.

## Q2 — Does the corrected §3.8 verification discharge the audit-method concern?

Yes, for the specific §3.8 verification defect. The prior check was vacuous (searched for a nonexistent Markdown heading). Rev-8 discloses rather than conceals. The new extractor correctly searches the bold marker `**3.8 —`, ends at the next `##`, hashes and compares rev-8 vs rev-7. Independently inspected §3.8 at both pins — limitation unchanged (same physical host, separate broker account/key/commit identity, owner remains ultimate trust authority, no cryptographic proof against colluding owner claimed). **Disposition: MET.** No new audit method required in §3.6/§9 for this. That does not make every other table claim accurate.

## Q3 — Does the generated claim→evidence table satisfy the accuracy standard?

No — meaningful improvement, but it fails its own accuracy standard.

**A. P0-9c2 misattributed.** Prompt says P0-9c2 is named in the docstring with body = bad-signature plan → PENDING → valid signature, anchor line 457. Actual pinned file: docstring describes P0-9c as empty-argv entry and does NOT name P0-9c2; P0-9c2 is the body assertion that a corrected plan executes the same request ID; its assertion is at line 434; line 457 is argv10 setup for --once. The bad-signature behavior IS tested (P0-1 unsigned→signed, P0-2 tampered→signed) — the table's attribution and anchor are wrong. More importantly `anchor()` searches the entire file for the first substring occurrence, never restricting to the docstring despite labeling it a docstring anchor — the docstring claim is not actually checked.

**B. The test-result row is not mechanically verified.** Row 16 says 57 PASS/0 FAIL executed; the generator does not read any log — it emits `executed log grep: 57 '^PASS', 0 '^FAIL'` as a hardcoded string. Provenance mismatch: the test file at the declared pin cites its run at b134df3, and the b134df3 version cites 4ee1302. ChatGPT did not execute the suite (paper-only) and does not certify 57/57 at a695398.

Required process repair:
1. Generator validates docstring claims against the docstring region, not the whole file.
2. Count/assert absent test IDs rather than hardcoding "P0-16c occurs 0 times".
3. Test-result row must read a specific, committed run artifact containing the exact source SHA and PASS/FAIL totals — never print a hardcoded claim that a log was checked.
4. Correct P0-9c2 description and line anchor.
5. Regenerate and independently inspect emitted output against raw pinned source.

The table proves substring presence — not that the cited location is the right kind of evidence or that the described behavior is what the test exercises.

## Q4 — Final vote: ACCEPT-WITH-CHANGES

| Priority | Required change |
|---|---|
| P0 | Close timeout-cleanup exception path: every successful Popen construction consumes budget + durable post-spawn outcome. Add P0-17e. |
| P1 | Complete request-state corruption handling in Ledger.load() and Ledger.pending() for non-object and unreadable files; targeted regression tests. |
| P1 | Correct generated evidence table: P0-9c2 docstring claim/anchor, hardcoded test-result row, non-verified absent-ID assertion. |
| P1 | Provide a run artifact identifying the exact full source SHA against which the 57 checks executed. |

Architecture: ACCEPTED (no second machine / TPM / attestation requested; §3.8 intact). Protocol rev-8: ACCEPT-WITH-CHANGES. Wave 0 / owner cutover / C1-C2 prep / destructive ops / deployment: NOT authorized by this verdict. DESIGN-REVIEW §10 HARD STOP unchanged. R-4/R-5/R-7 remain open until Wave-3 live evidence.

"Rev-8 is close, and the remaining implementation work is narrow. But the timeout-cleanup path is a real budget-accounting hole, and the claim-to-evidence process has repeated an accuracy failure in the very table intended to prevent one. I would not waive either issue for this gate."
