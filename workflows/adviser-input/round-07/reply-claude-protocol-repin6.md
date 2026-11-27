# Round-07 re-pin-6 reply — CLAUDE (advisor seat, runner scope)
Pin reviewed: 6c19da3 for scripts/m0-broker-runner.py and scripts/qa/test_broker_p0.py, both read as text. The prompt file itself lives at 076c624, but review was of the code at the declared pin. The protocol, setup script, and revoke script were NOT read at this pin; nothing executed. Symbols and behavior in the claim table were spot-checked; line-number anchors not individually verified.

## Required change (unverifiable plan never terminal): DISCHARGED
verify_plan returns unverifiable for absent, unsigned, signature-failed, and structurally broken plans. run_pass writes no disposition for any request that isn't already decided. P0-1, P0-2 and P0-2c exercise this and show a later valid signature runs the same ID. P0-9c covers the empty-argv case.

## Request 1 (per-command budget): DISCHARGED
Key is canonical_sha256([argv, artifacts, max_runs]); a re-sign that only adds commands doesn't reset consumed budgets. Two consequences should be written into §3.3: (a) a change to max_runs or to a pinned artifact hash starts a NEW budget — intended for a changed command but should be stated; (b) the per-command budget also means the owner can reset a budget by re-signing with a new max_runs.

## Request 2 (broadened spawn catch): NOT DISCHARGED — REGRESSION, BLOCKS ACCEPT
except Exception wraps subprocess.run(..., text=True), and that call does more than spawn: it WAITS for the child and decodes captured output strictly. If the command RUNS and prints bytes that aren't valid in the locale encoding, run() raises UnicodeDecodeError AFTER the command has already executed. The except-Exception branch then records spawn_succeeded: false "never executed". bump_usage is skipped and record_history_count excludes that record, so the command's budget is NOT consumed and a fresh request ID can run it again. Under rev-6 the same error escaped the OSError catch, left state as started, and became UNPROVEN on restart — the conservative outcome. Rev-7 broke it.
P0-17c does not catch this: it traps subprocess.run and raises BEFORE calling the real function, so the post-execution path is never exercised.
Required fix: separate spawn from wait. Use Popen; treat only its construction as a definite spawn failure. Once Popen returns, ANY exception is uncertain. Capture output as bytes, or decode with errors="replace", and bump usage immediately after the child exits, BEFORE any decoding.
Required test (P0-17d): a command that writes invalid UTF-8 and increments a side-effect counter. Assert it is recorded as executed (or uncertain), NEVER spawn_succeeded: false; the usage counter IS incremented; the command does not run again under a fresh ID.

## Request 3 (§3.3 residual trust base): NOT VERIFIED
Protocol not read at this pin. The runner's comments state the same limits, so the text should match; will check when reviewing the protocol.

## Request 4 (docstring corrections): PARTLY DONE, one missing body
The module docstring lists P0-16c (bad signature → pending) but the test file has NO P0-16c check. The rev-7 claim table cites P0-2/2b/2c for that behavior, so docstring and bodies are NOT one-to-one — the exact defect this round set out to remove. Either add the test or remove the ID from the docstring.

## Request 5 (queue read as bytes): DISCHARGED
Queue read as bytes, decoded per line; P0-9b shows one bad byte refuses only its own line and the next line still executes.

## Non-blocking
1. Ledger.load calls json.loads without handling corrupt state files — a corrupt state file would stop the pass each time; pending() already handles that case, the two should match.
2. _sync_dir_chain is documented as syncing "untracked" ancestors but syncs EVERY ancestor and stops after 16 levels — the claim "to the filesystem root" is only true for shallow paths.
3. Row 12 (record_history_count) exercised only indirectly, as the table says. A dedicated test should show it counts completed records and skips never-spawned ones — the behavior the spawn bug above depends on.

## Vote: ACCEPT-WITH-CHANGES
Earlier required change discharged; does NOT convert to ACCEPT. Blocking items: (1) the broadened spawn-catch regression with its P0-17d test; (2) the docstring/body mismatch for P0-16c. Once fixed and P0-17d passes, will move to ACCEPT for runner scope.
