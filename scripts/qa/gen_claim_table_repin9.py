#!/usr/bin/env python3
"""Generate the claim->evidence table for the re-pin-9 prompt.
Every anchor is extracted mechanically from `git show <PIN>:<file>` —
nothing here is asserted from memory. FAILS LOUD if any anchor is absent.
Suite row is read from the COMMITTED run artifact at the pin (ChatGPT
re-pin-7 P1: no scratch-dir logs, no hardcoded counts).
Rev-9 -> rev-10 delta rows target ChatGPT re-pin-8 blocking P0 (across-pass
budget accounting halt) + Claude re-pin-8 blockers (publish integrity under
undecodable record bytes; kill/reap on generic post-spawn failure)."""
import subprocess, sys, re, hashlib

PIN = "57fb6fb"
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
ART = "scripts/qa/run-artifacts/rev10_test_atpin.log"
HDR = "scripts/qa/run-artifacts/rev10_test_atpin.header"

# ---- ChatGPT re-pin-8 blocking P0: budget accounting fails CLOSED ACROSS PASSES ----
claim("Accounting failure (budget-counter write OR durable completion-record write OR state save) post-spawn writes a DURABLE owner-only halt marker and ends the pass with exit 3, evidence PUBLISH held (no partial evidence published)",
      anchor(runner, R, "def write_accounting_halt", "halt writer") + " + " +
      anchor(runner, R, 'ACCOUNTING_HALT_PATH = "accounting-halt.json"', "marker constant") + " + " +
      anchor(runner, R, "PUBLISH-HELD: accounting halt this pass", "publish hold"))
claim("The marker is read at EVERY pass entry (fresh runner process / systemd restart): while present the pass refuses dispatch — logs ACCOUNTING-HALT, executes nothing, writes no disposition — until the OWNER clears it",
      anchor(runner, R, "ACCOUNTING-HALT: durable marker present", "pass-entry halt read"))
claim("All three accounting-failure sites wired to the same halt: counter-write, completion-record write, state save",
      anchor(runner, R, "budget counter write failed", "counter site") + " + " +
      anchor(runner, R, "durable completion record write failed", "record site") + " + " +
      anchor(runner, R, "state save failed", "state site"))
claim("P0-22a: counter-write failure post-spawn -> exit 3, marker present, child NOT re-executed",
      anchor(test, T, '"P0-22a', "P0-22a"))
claim("P0-22b: a LATER fresh runner process with a NEW request id dispatches NOTHING while the marker stands (this is the across-pass leg ChatGPT re-pin-8 required)",
      anchor(test, T, '"P0-22b', "P0-22b"))
claim("P0-22c: after the owner CLEARS the marker and repairs the counter, the surviving execution history still enforces the cap (BUDGET-EXHAUSTED, no re-execution) — repair-then-hold, never repair-and-re-execute",
      anchor(test, T, '"P0-22c', "P0-22c"))
claim("P0-22d: completion-record write failure post-spawn -> same halt, same marker",
      anchor(test, T, '"P0-22d', "P0-22d"))
claim("P0-17e2b: bump_usage EXECUTES during a real spawn (mechanical usage-file delta, no mock counter)",
      anchor(test, T, '"P0-17e2b', "P0-17e2b"))

# ---- Claude re-pin-8 blocker 1: decode-safety + byte-exact publish integrity ----
claim("Every durable read site catches UnicodeDecodeError (a ValueError, NOT an OSError) alongside OSError/JSONDecodeError — state load, usage load, pending scan, completion-record scan; undecodable bytes retype to the same corruption HOLD, never a pass-killing crash",
      anchor(runner, R, "except (json.JSONDecodeError, OSError, UnicodeDecodeError) as e:", "load-site catch") + " (site 1 of 4)")
claim("Queue scan reads BYTES and decodes lossily with a loud bad-line log — one corrupt line cannot delete or crash over later lines",
      anchor(runner, R, "q.read_bytes().split(b\"\\n\")", "queue byte-read"))
claim("Evidence publication copies record/refusal files BYTE-EXACT (write_bytes(read_bytes())) — an undecodable record can no longer crash the publish loop mid-copy",
      anchor(runner, R, "dest.write_bytes(src.read_bytes())", "byte-exact copy"))
claim("P0-22e: bad-byte completion record over a valid 'started' state -> conservative UNPROVEN refusal, child NOT re-executed, no crash, no partial marker",
      anchor(test, T, '"P0-22e', "P0-22e"))
claim("P0-23: undecodable (non-UTF-8) state/usage/record files -> corruption HOLD at every read site exercised",
      anchor(test, T, '"P0-23', "P0-23"))

# ---- Claude re-pin-8 blocker 2: generic post-spawn handler kills/reaps ----
claim("Generic post-spawn failure path kills AND reaps the child before the uncertain-outcome refusal (no live orphan behind an UNPROVEN record)",
      anchor(runner, R, "if child_ran or exit_code is None:", "generic kill+reap"))
claim("P0-24: post-spawn handler failure -> child process confirmed DEAD + REAPED at refusal time",
      anchor(test, T, '"P0-24', "P0-24"))

# ---- ChatGPT re-pin-8 P1s: proof hygiene + line anchors + SKIP semantics ----
claim("Suite archive run executes as non-root and SKIP counts against a clean run (exit 1 on any skip — a chmod-000 scenario that cannot execute is surfaced, never hidden)",
      anchor(test, T, "sys.exit(1 if (FAILS or SKIPS) else 0)", "skip-is-failure") + " + " +
      anchor(test, T, "def skip(name, why):", "skip helper"))
claim("Artifact header records RUN-ENV (python version, non-root, platform) so the archive run's environment is stated, not assumed",
      f"git show {PIN}:{HDR}")

# ---- claim hygiene: committed run artifact, mechanically re-counted ----
hdr = at(HDR)
mm = re.search(r"REVIEW-PIN: ([0-9a-f]{40})", hdr)
pp = re.search(r"PASS-COUNT: (\d+)", hdr)
ff = re.search(r"FAIL-COUNT: (\d+)", hdr)
ss = re.search(r"SKIP-COUNT: (\d+)", hdr)
if not (mm and pp and ff and ss):
    sys.exit("HEADER-FIELDS-MISSING in committed run artifact header")
log = at(ART)
real_pass = sum(1 for l in log.splitlines() if l.startswith("PASS "))
real_fail = sum(1 for l in log.splitlines() if l.startswith("FAIL "))
real_skip = sum(1 for l in log.splitlines() if l.startswith("SKIP "))
if (real_pass, real_fail, real_skip) != (int(pp.group(1)), int(ff.group(1)), int(ss.group(1))):
    sys.exit(f"HEADER/LOG MISMATCH: header {pp.group(1)}/{ff.group(1)}/{ss.group(1)} log {real_pass}/{real_fail}/{real_skip}")
if not log.rstrip().endswith("FAILS: none | SKIPS: none"):
    sys.exit("LOG-TAIL not 'FAILS: none | SKIPS: none'")
claim(f"Test suite green AT THIS PIN per the COMMITTED artifact (mechanically re-counted here from the committed log, not from the header alone): {real_pass} PASS / {real_fail} FAIL / {real_skip} SKIP / tail 'FAILS: none | SKIPS: none'; artifact header pins the CODE commit {mm.group(1)} — the suite ran from a clean git archive of it (no scratch-dir log, no hardcoded count in any docstring)",
      f"git show {PIN}:{HDR} re-counted against git show {PIN}:{ART}")

# ---- code identity between the code-pinned commit and the review pin ----
def _docspan(pin):
    src = at("scripts/qa/test_broker_p0.py", pin).splitlines()
    start = next(i for i, l in enumerate(src, 1) if l.startswith('"""'))
    end = next(i for i, l in enumerate(src[start + 1:], start + 1) if l == '"""')
    return start, end
_runner_same = subprocess.run(["git", "-C", REPO, "diff", "--quiet", "b10913d", PIN, "--",
                               "scripts/m0-broker-runner.py"], capture_output=True).returncode == 0
_diff = subprocess.run(["git", "-C", REPO, "diff", "-U0", "b10913d", PIN, "--",
                        "scripts/qa/test_broker_p0.py"], capture_output=True, text=True).stdout
_hunks = re.findall(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", _diff, re.M)
_a, _b = _docspan("b10913d"), _docspan(PIN)
_doc_only = all(
    _a[0] <= int(h0) and int(h0) + int(h1 or 1) <= _a[1] and
    _b[0] <= int(h2) and int(h2) + int(h3 or 1) <= _b[1] for h0, h1, h2, h3 in _hunks) if _hunks else True
_codeident = _runner_same and _doc_only
claim("Code executed by the suite at the pinned commit (" + "b10913d" + ", run from clean `git archive`, artifact header cites its full SHA) is the code AT THIS REVIEW PIN: runner byte-identical b10913d→" + PIN + " (git diff --quiet, 0 lines) and the only test-file delta b10913d→" + PIN + " is inside the module docstring — every `git diff -U0` hunk of the test file falls within the docstring line span at BOTH endpoints (verified here programmatically)" + (", the artifact commit adds only the run log + header" if _doc_only else ""),
      "git diff --quiet b10913d " + PIN + " -- runner => clean; test hunks "
      + str(_hunks) + f" ⊂ docstring spans {_a}/{_b}"
      if _codeident else "CODE-DIVERGED-BETWEEN-PINS")

# ---- rev-9 baseline rows: the parts of the runner Grok already ACCEPTED ----
_claim_base = subprocess.run(["git", "-C", REPO, "log", "--oneline", "-1", "d1c0e09"],
                             capture_output=True, text=True).stdout.strip()
claim("Post-spawn region enters a guard flag before the first post-Popen call; exit_code bound pre-try (rev-9, UNCHANGED since d1c0e09 which Grok ACCEPTED at re-pin-8)",
      anchor(runner, R, "child_ran = False", "post-spawn guard init"))
claim("TIMEOUT path sets err BEFORE kill/reap, cleanup failure folded INTO the recorded error at the site (rev-9, unchanged)",
      anchor(runner, R, 'exit_code, err = None, "TIMEOUT exceeded 3600s"', "err pre-cleanup") + " + " +
      anchor(runner, R, "cleanup failed ({type(e2).__name__})", "cleanup-failure fold"))
claim("Corrupt durable usage / execution history are HOLDs, not terminal refusals: logs, executes nothing, writes NO disposition; owner repair + same-ID re-run supported (rev-9, unchanged)",
      anchor(runner, R, "durable usage state for this signed", "usage hold log") + " + " +
      anchor(runner, R, "durable execution history for this", "history hold log"))
claim("digest_artifacts: unreadable artifact path -> observed='UNREADABLE', never an uncaught OSError (rev-9, unchanged)",
      anchor(runner, R, 'observed = f"UNREADABLE ({type(e).__name__})"', "digest OSError fold"))

# ---- protocol state ----
claim("Protocol title is rev-10; changelog records the rev-10 repair + all three re-pin-8 verdicts (Grok ACCEPT, ChatGPT AWC, Claude AWC)",
      anchor(proto, P, "— rev-10", "rev-10 title") + " + " +
      anchor(proto, P, "**rev-10.** Council re-pin-8", "rev-10 changelog"))
claim("§3.3 carries the rev-10 accounting-halt invariant (durable marker across passes, publish held, owner-clear-then-hold, byte-exact evidence copies)",
      anchor(proto, P, "The halt is therefore durable: a", "3.3 durable halt") + " + " +
      anchor(proto, P, "the publish copy-loop is", "3.3 byte-exact publish") + " + " +
      anchor(proto, P, "OWNER RECOVERY for an accounting halt", "3.3 owner recovery"))

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

print("| # | Claim (rev-10, at pin `" + PIN + "`) | Evidence (mechanically extracted) |")
print("|---|---|---|")
for i, (c, ev) in enumerate(rows, 1):
    print(f"| {i} | {c} | `{ev}` |")
