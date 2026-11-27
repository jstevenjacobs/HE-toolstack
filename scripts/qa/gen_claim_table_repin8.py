#!/usr/bin/env python3
"""Generate the claim->evidence table for the re-pin-8 prompt.
Every anchor is extracted mechanically from `git show <PIN>:<file>` —
nothing here is asserted from memory. FAILS LOUD if any anchor is absent.
Suite row is read from the COMMITTED run artifact at the pin (ChatGPT
re-pin-7 P1: no scratch-dir logs, no hardcoded counts)."""
import subprocess, sys, re, hashlib

PIN = "0d156d7"
REPO = "/opt/data/cache/scratch/HE-toolstack-review"

def at(path, pin=PIN):
    return subprocess.run(["git", "-C", REPO, "show", f"{pin}:{path}"],
                          capture_output=True, text=True, check=True).stdout

runner = at("scripts/m0-broker-runner.py")
test = at("scripts/qa/test_broker_p0.py")
proto = at("workflows/m0-interview-protocol.md")

def anchor(src, path, needle, label, want=1):
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

R, T, P = ("scripts/m0-broker-runner.py", "scripts/qa/test_broker_p0.py",
           "workflows/m0-interview-protocol.md")
ART = "scripts/qa/run-artifacts/rev9_test_atpin.log"
HDR = "scripts/qa/run-artifacts/rev9_test_atpin.header"

# ---- ChatGPT re-pin-7 P0: post-spawn region guarded end-to-end ----
claim("Post-spawn region enters a guard flag before the first post-Popen call; exit_code bound pre-try",
      anchor(runner, R, "child_ran = False", "post-spawn guard init"))
claim("TIMEOUT path sets err BEFORE kill/reap, and kill+communicate failure is folded INTO the recorded error at the site (cannot escape to the generic handler or past bump_usage)",
      anchor(runner, R, 'exit_code, err = None, "TIMEOUT exceeded 3600s"', "err pre-cleanup") + " + " +
      anchor(runner, R, "cleanup failed ({type(e2).__name__})", "cleanup-failure fold"))
claim("Generic post-spawn handler kills + reaps the child (no orphan on uncertain outcome; Claude NB3)",
      anchor(runner, R, "if child_ran or exit_code is None:", "generic kill+reap"))
claim("Invariant documented at the site: successful Popen construction => bump_usage + durable spawn_succeeded=True on EVERY post-spawn path",
      anchor(runner, R, "bump_usage + a durable spawn_succeeded=True record follow on", "invariant comment"))
claim("bump_usage runs the moment the child was run (pre-decode)",
      anchor(runner, R, "bump_usage(L, use_key)", "bump site"))
claim("P0-17e: timeout whose kill() ITSELF raises (in-process Popen trap, argv-scoped) -> TIMEOUT-with-cleanup-failure recorded, budget consumed",
      anchor(test, T, '"P0-17e', "P0-17e"))
claim("P0-17e2: the SAME signed command is BUDGET-EXHAUSTED for a FRESH id afterwards (no re-execution)",
      anchor(test, T, '"P0-17e2', "P0-17e2"))

# ---- Claude re-pin-7 blocking: corrupt-state terminal -> HOLD + same-ID repair ----
claim("Corrupt durable usage is a HOLD now: logs BUDGET-STATE-CORRUPT, executes nothing, writes NO disposition",
      anchor(runner, R, "durable usage state for this signed", "usage hold log"))
claim("Corrupt execution history is a HOLD (same retype at the history site)",
      anchor(runner, R, "durable execution history for this", "history hold log"))
claim("P0-19a/b + P0-20d/e/e2 rewritten to hold semantics: after the owner repairs the file the SAME request id runs again (repair-then-rerun-same-ID legs)",
      anchor(test, T, '"P0-19a', "P0-19a") + " … " + anchor(test, T, '"P0-20e', "P0-20e"))

# ---- OSError / fail-closed trio (ChatGPT P1-1, Claude NB1/NB2) ----
claim("Ledger.load: valid-JSON-non-object -> unreadable-corrupt HOLD sentinel, 'held, never re-executed' (OSError caught too — chmod-000 exercised for real as non-root)",
      anchor(runner, R, "object — held, never re-executed", "load non-object hold"))
claim("verify_plan catches UnicodeDecodeError: invalid-UTF-8 signed plan -> UNVERIFIABLE -> PENDING, every pass survives (P0-9e)",
      anchor(test, T, '"P0-9e', "P0-9e"))
claim("P0-20g/20h: non-object state + unreadable state file both HOLD the owning request while siblings still run",
      anchor(test, T, '"P0-20g', "P0-20g") + " + " + anchor(test, T, '"P0-20h', "P0-20h"))

# ---- claim hygiene (ChatGPT P1-2/P1-3, Claude NB4): committed run artifact ----
hdr = at(HDR)
mm = re.search(r"REVIEW-PIN: ([0-9a-f]{40})", hdr)
pp = re.search(r"PASS-COUNT: (\d+)", hdr)
ff = re.search(r"FAIL-COUNT: (\d+)", hdr)
if not (mm and pp and ff):
    sys.exit("HEADER-FIELDS-MISSING in committed run artifact header")
log = at(ART)
real_pass = sum(1 for l in log.splitlines() if l.startswith("PASS "))
real_fail = sum(1 for l in log.splitlines() if l.startswith("FAIL "))
if (real_pass, real_fail) != (int(pp.group(1)), int(ff.group(1))):
    sys.exit(f"HEADER/LOG MISMATCH: header {pp.group(1)}/{ff.group(1)} log {real_pass}/{real_fail}")
if not log.rstrip().endswith("FAILS: none"):
    sys.exit("LOG-TAIL not 'FAILS: none'")
claim("digest_artifacts: directory or unreadable artifact path -> observed='UNREADABLE' (never an uncaught OSError crashing the pass; ChatGPT re-pin-7 P1 / Claude NB2)",
      anchor(runner, R, 'observed = f"UNREADABLE ({type(e).__name__})"', "digest OSError fold"))
claim(f"Test suite green AT THIS PIN per the COMMITTED artifact (mechanically re-counted here from the committed log, not from the header alone): {real_pass} PASS / {real_fail} FAIL / tail 'FAILS: none'; artifact header pins the code commit {mm.group(1)} (run from a clean git archive of it — no scratch-dir log, no hardcoded count in any docstring)",
      f"git show {PIN}:{HDR} re-counted against git show {PIN}:{ART}")
claim("Test docstring cites the committed artifact path (not b134df3, not /tmp)",
      anchor(test, T, "scripts/qa/run-artifacts/", "artifact citation") +
      f"; b134df3 occurs {test.count('b134df3')} times in {T}@{PIN}")

# ---- code identity between the run-pinned commit and the review pin ----
def _docspan(pin):
    src = at("scripts/qa/test_broker_p0.py", pin).splitlines()
    start = next(i for i, l in enumerate(src, 1) if l.startswith('"""'))
    end = next(i for i, l in enumerate(src[start + 1:], start + 1) if l == '"""')
    return start, end
_runner_same = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "d1c0e09", PIN, "--",
                               "scripts/m0-broker-runner.py"], capture_output=True).returncode == 0
_diff = subprocess.run(["git", "-C", REPO, "diff", "-U0", "d1c0e09", PIN, "--",
                        "scripts/qa/test_broker_p0.py"], capture_output=True, text=True).stdout
_hunks = re.findall(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", _diff, re.M)
_a, _b = _docspan("d1c0e09"), _docspan(PIN)
_doc_only = bool(_hunks) and all(
    _a[0] <= int(h0) and int(h0) + int(h1 or 1) <= _a[1] and
    _b[0] <= int(h2) and int(h2) + int(h3 or 1) <= _b[1] for h0, h1, h2, h3 in _hunks)
_codeident = _runner_same and _doc_only
claim("Code executed by the suite at the pinned commit (e78f1c2, run from clean `git archive`, artifact header cites its full SHA) is the code AT THIS REVIEW PIN: runner byte-identical d1c0e09→" + PIN + " (git diff --quiet, 0 lines) and the only test-file delta d1c0e09→" + PIN + " is inside the module docstring — every `git diff -U0` hunk of the test file falls within the docstring line span at BOTH endpoints (verified here programmatically; between e78f1c2 and " + PIN + " even that delta is nil, the artifact commit adds only the run log, its header, and this generator)",
      "git diff --quiet d1c0e09 " + PIN + " -- runner => clean; test hunks "
      + str(_hunks) + f" ⊂ docstring spans {_a}/{_b}"
      if _codeident else "CODE-DIVERGED-BETWEEN-PINS")

# ---- protocol state ----
claim("Protocol title is rev-9; changelog records all three re-pin-7 verdicts (Grok ACCEPT, ChatGPT AWC, Claude AWC)",
      anchor(proto, P, "— rev-9", "rev-9 title") + " + " +
      anchor(proto, P, "**rev-9.** Council re-pin-7", "rev-9 changelog"))
claim("§3.3 states the rev-9 post-spawn invariant (guard end-to-end; kill/reap+bump+record on every path) and the corrupt-state HOLD retype with same-ID repair",
      anchor(proto, P, "post-spawn region after a successful", "3.3 invariant") + " + " +
      anchor(proto, P, "retypes that integrity failure from a", "3.3 hold retype"))

# ---- §3.8 byte-identity: the accepted slice, verified to the ORIGINAL acceptance ----
def sec38(text):
    m = re.search(r"^\*\*3\.8 —.*?(?=\n## |\Z)", text, re.S | re.M)
    if not m:
        sys.exit("SEC38-NOT-FOUND in protocol")
    return hashlib.sha256(m.group(0).encode()).hexdigest()
s_pin, s_base = sec38(proto), sec38(at("workflows/m0-interview-protocol.md", "8509096"))
s_prev = sec38(at("workflows/m0-interview-protocol.md", "a695398"))
claim("§3.8 architecture limitation byte-identical to the ORIGINAL accepted slice (rev-5) AND to the last reviewed pin",
      f"sha256 at {PIN} = {s_pin[:16]} == 8509096 ({s_base[:16]}) == a695398 ({s_prev[:16]})"
      if s_pin == s_base == s_prev else "SEC38-DIVERGED")
_rev = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "a695398", PIN, "--",
                       "scripts/m0-broker-revoke-keys.sh"], capture_output=True)
if _rev.returncode != 0:
    sys.exit("REVOKE-SCRIPT-CHANGED between a695398 and " + PIN)
claim("Revoke script byte-identical since re-pin-7 pin (no new claims about it)",
      "git diff --quiet a695398 " + PIN + " -- scripts/m0-broker-revoke-keys.sh => clean")

print("| # | Claim (rev-9, at pin `" + PIN + "`) | Evidence (mechanically extracted) |")
print("|---|---|---|")
for i, (c, ev) in enumerate(rows, 1):
    print(f"| {i} | {c} | `{ev}` |")
