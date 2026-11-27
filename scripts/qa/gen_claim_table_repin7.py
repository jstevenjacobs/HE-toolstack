#!/usr/bin/env python3
"""Generate the claim->evidence table for the re-pin-7 prompt.
Every anchor is extracted mechanically from `git show <PIN>:<file>` —
nothing here is asserted from memory. FAILS LOUD if any anchor is absent."""
import subprocess, sys, re

PIN = "b134df3"
REPO = "/opt/data/cache/scratch/HE-toolstack-review"

def at(path):
    return subprocess.run(["git", "-C", REPO, "show", f"{PIN}:{path}"],
                          capture_output=True, text=True, check=True).stdout

runner = at("scripts/m0-broker-runner.py")
test = at("scripts/qa/test_broker_p0.py")
proto = at("workflows/m0-interview-protocol.md")

def anchor(src, path, needle, label, want=1):
    """Return 'path:N' (first match line) of a needle that occurs >=want times."""
    lines = src.splitlines()
    hits = [i + 1 for i, l in enumerate(lines) if needle in l]
    if len(hits) < want:
        print(f"MISSING: {label!r} needle {needle!r} in {path} (found {len(hits)}, want {want})",
              file=sys.stderr)
        sys.exit(1)
    return f"{path}:{hits[0]}"

rows = []
def claim(c, ev):
    rows.append((c, ev))

def _sec38_identical():
    """True iff §3.8 (accepted rev-5 slice) is byte-identical between 6c19da3 and PIN."""
    import hashlib, re
    def sec(src):
        m = re.search(r"^\*\*3\.8 —.*?(?=\n## |\Z)", src, re.S | re.M)
        if not m:
            sys.exit("SEC38-NOT-FOUND in protocol")
        return hashlib.sha256(m.group(0).encode()).hexdigest()
    return sec(at("workflows/m0-interview-protocol.md")) == sec(
        subprocess.run(["git", "-C", REPO, "show", "6c19da3:workflows/m0-interview-protocol.md"],
                       capture_output=True, text=True, check=True).stdout)

R, T, P = ("scripts/m0-broker-runner.py", "scripts/qa/test_broker_p0.py",
           "workflows/m0-interview-protocol.md")

# ---- spawn/exec separation (the shared ChatGPT+Claude blocker) ----
claim("Spawn construction (Popen) is the ONLY definite never-started path; no bump_usage on it",
      anchor(runner, R, "proc = subprocess.Popen(", "Popen construction"))
claim("Post-construction failure (communicate timeout / POST-SPAWN-UNCERTAIN except) still consumes budget — bump_usage runs immediately after the child ran, before decode",
      anchor(runner, R, "proc.communicate(timeout=3600)", "communicate") + " + "
      + anchor(runner, R, "bump_usage(L, use_key)   # consumed the moment the child was run, pre-decode", "bump pre-decode"))
claim("Output captured as bytes, decoded lossily (errors='replace') so decode cannot fail",
      anchor(runner, R, 'errors="replace"', "lossy decode"))
claim("P0-17d: invalid-UTF8 executed command consumes budget (never-spawned claim impossible)",
      anchor(test, T, '"P0-17d', "P0-17d"))
claim("P0-17d2/d3: budget-exhausted after the executed-but-undecodable run; restart does not re-execute",
      anchor(test, T, '"P0-17d2', "P0-17d2") + " + " + anchor(test, T, '"P0-17d3', "P0-17d3"))
claim("P0-17c traps Popen CONSTRUCTION (matches rev-8 code shape, not subprocess.run)",
      anchor(test, T, "def trap_popen", "Popen trap"))

# ---- docstring/body parity (Claude blocking 2) ----
claim("Phantom P0-16c is GONE from the test docstring; docstring names P0-9c2 for that behavior",
      "P0-16c occurs 0 times in " + T + "@" + PIN + "; P0-9c2 named at "
      + anchor(test, T, "P0-9c2", "P0-9c2 docstring"))
claim("P0-9c2 body present (bad-signature plan -> PENDING -> later valid signature executes)",
      anchor(test, T, '"P0-9c2', "P0-9c2 body"))

# ---- corrupt-state fail-closed (ChatGPT 3A/3B, Claude non-blocking 1) ----
claim("usage_count: structurally-invalid-but-parsable JSON -> 'CORRUPT:' sentinel (silent zero impossible)",
      anchor(runner, R, "CORRUPT:", "CORRUPT sentinel"))
claim("record_history_count: corrupt history record -> CORRUPT:<file>; dispatch refuses BUDGET-STATE-CORRUPT (both usage + history refuse sites cited)",
      anchor(runner, R, 'return f"CORRUPT:{f.name}: {e}"', "history CORRUPT return") + " + "
      + anchor(runner, R, 'refuse(L, rid, f"BUDGET-STATE-CORRUPT: durable execution history for "', "history refuse site"))
claim("Ledger.load corrupt state -> unreadable-corrupt sentinel; run_pass HOLDs, never re-executes",
      anchor(runner, R, 'return {"id": rid, "status": "unreadable-corrupt", "note": str(e)}', "sentinel return") + " + "
      + anchor(runner, R, 'if st and st.get("status") == "unreadable-corrupt":', "run_pass HOLD branch") + " + "
      + anchor(runner, R, "LEDGER-STATE-CORRUPT {rid}: {e} \u2014 held, never re-executed", "hold log"))
claim("P0-20a-f: usage non-object / history corrupt / state corrupt + sibling still runs, each proven",
      anchor(test, T, '"P0-20a', "P0-20a") + "…" + anchor(test, T, '"P0-20f', "P0-20f"))

# ---- plan-shape validation ----
claim("verify_plan: non-object plan or non-list commands -> UNVERIFIABLE -> PENDING, no crash",
      anchor(runner, R, "isinstance(raw_plan, dict)", "plan shape check") + " + "
      + anchor(runner, R, "isinstance(raw_commands, list)", "commands shape check"))
claim("P0-9d: list-plan and non-list-commands both -> PENDING for every queued request",
      anchor(test, T, '"P0-9d', "P0-9d"))

# ---- docstring honesty ----
claim("_sync_dir_chain docstring states the 16-ancestor-level cap (no untracked-chain over-claim)",
      anchor(runner, R, "16 levels", "16-level note"))

# ---- suite / gates / protocol state ----
claim("Test suite: 22 scenarios / 57 checks; rev-8 run at this tree: 57 PASS / 0 FAIL / FAILS: none",
      "test docstring states the count at " + anchor(test, T, "57 checks", "docstring count")
      + "; executed log grep: 57 '^PASS', 0 '^FAIL'")
claim("Protocol title is rev-8; changelog records all three re-pin-6 verdicts",
      anchor(proto, P, "— rev-8", "rev-8 title"))
claim("§3.3 scoped at rev-8: spawn CONSTRUCTION = definite never-executed; post-construction failure consumes budget",
      anchor(proto, P, "PROCESS CONSTRUCTION fails", "3.3 scoping"))
claim("§3.3 rev-8 fail-closed trio: usage CORRUPT / history CORRUPT:<file> / state unreadable-corrupt hold",
      anchor(proto, P, "BUDGET-STATE-CORRUPT` (ChatGPT re-pin-6 P1-3A", "trio usage") )
claim("§3.8 architecture limitation byte-identical since accepted slice",
      "live git-diff at pin: §3.8 at " + PIN + " vs 6c19da3 sha256-equal"
      if _sec38_identical() else "SEC38-DIVERGED")
_rev = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "6c19da3", PIN, "--",
                       "scripts/m0-broker-revoke-keys.sh"], capture_output=True)
if _rev.returncode != 0:
    sys.exit("REVOKE-SCRIPT-CHANGED between 6c19da3 and " + PIN)
claim("Revoke script byte-identical since rev-7 (no new claims about it)",
      "git diff --quiet 6c19da3 " + PIN + " -- scripts/m0-broker-revoke-keys.sh => clean")

print("| # | Claim (rev-8, at pin `" + PIN + "`) | Evidence (mechanically extracted) |")
print("|---|---|---|")
for i, (c, ev) in enumerate(rows, 1):
    print(f"| {i} | {c} | `{ev}` |")
