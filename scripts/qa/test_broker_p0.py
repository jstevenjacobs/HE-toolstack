#!/usr/bin/env python3
"""Exercise rev-5 + rev-6 + rev-7 + rev-8 P0 repairs against the broker.

Real mechanisms throughout: ssh-keygen -Y sign/verify for plan authorization, a
local bare git remote (with a real rejecting pre-receive hook) for publish paths,
real ssh-keygen fingerprint inventories for the revoke script, real subprocess
crash/restart simulations (fresh runner PROCESS per pass). Two instrumented
exceptions: P0-12 uses unittest.mock ONLY to COUNT os.fsync calls, and P0-17c
traps subprocess.Popen (argv-scoped) to inject ONE non-OSError at the spawn
call; the writes themselves are real. There is no sshd involvement anywhere —
the revoke tests operate on authorized_keys FILES directly (the docstring
previously overclaimed "no mocks"; corrected rev-7, ChatGPT re-pin-5 P1). No
network. Suite: 22 scenarios / 57 checks — 57 PASS / 0 FAIL at the rev-8 pin
(b134df3; run log `rev8_test_final.log`). Checks:
  P0-1 unsigned plan            -> nothing executes; requests stay PENDING
                                  (rev-7: unverifiable is never terminal) and a
                                  later signature runs the SAME id
  P0-2 tampered plan            -> signature FAILED -> PENDING, no disposition,
                                  no execution; superseded by a later valid sign
  P0-3 signed plan, in-plan     -> executes; record has full capture fields
  P0-4 out-of-plan argv         -> refusal record, never executed
  P0-5 evidence pushed          -> broker commits visible on the remote branch
  P0-6 restart / replay         -> an executed request NEVER re-executes on a fresh
                                  runner process (durable state replaces memory set)
  P0-7 exec ok, push FAILED     -> retry publishes WITHOUT re-executing the command
  P0-8 crash mid-exec (started) -> UNPROVEN refusal, zero automatic re-execution
  P0-9 malformed / id-less lines-> invalid-request refusal records (no silent drop)
  P0-9b non-UTF8 queue byte     -> that line refused on record; the pass continues
                                  with the next line (rev-7, Claude re-pin-5)
  P0-9c empty-argv plan entry   -> plan invalid -> PENDING; never spawns, never
                                  crashes the pass (rev-7)
  P0-9d plan not an object /    -> explicit PENDING, never an uncaught
      commands not a list          structural exception (rev-8, ChatGPT re-pin-6)
  P0-10 --once                  -> exactly one cycle (cycle-counted), exact exit 0
  P0-11 revoke script           -> selective by fingerprint; owner key retained;
                                  inventory-wide expected-state verification;
                                  strict recovery declarations (rev-6); missing
                                  inventory FAILS closed (rev-7, P1 regression)
  P0-12 fsync durability        -> durable_write fsyncs file AND full new-directory
                                  chain (rev-6 repair 1 + rev-7 P1 hardening)
  P0-13 request-ID collision    -> reused id + different content = explicit refusal
                                  preserving both hashes, checked BEFORE every
                                  lifecycle branch incl. started (rev-6 repair 3 +
                                  rev-7 blocker 1); original stays separately
                                  recoverable as UNPROVEN
  P0-14 pinned artifacts        -> script swapped after signing = nothing runs
                                  (rev-6, Claude condition 1)
  P0-15 use budget              -> executed argv under a FRESH id is refused by the
                                  PER-COMMAND budget (rev-6 cond 2; rev-7 re-keys
                                  argv+artifacts+max_runs, not the whole plan)
  P0-16 plan absent -> pending  -> later signature authorizes; absence never
                                  blacklists an id (rev-6, Claude condition 3)
  P0-17 spawn failure           -> definite failed-spawn record, never UNPROVEN;
                                  ANY spawn exception, not just OSError (rev-6
                                  condition 4 + rev-7 residual)
  P0-17d post-spawn decode      -> a command printing invalid UTF-8 is recorded
                                  EXECUTED (spawn_succeeded true), budget consumed,
                                  never re-run under a fresh id (rev-8, Claude
                                  re-pin-6 REQUIRED regression)
  P0-18 record-before-state     -> crash between definite record and state save
                                  RECOVERS the definite outcome, never degrades to
                                  UNPROVEN (rev-7, ChatGPT blocker 2); the definite
                                  SPAWN-FAILURE record variant is covered too
                                  (rev-8, ChatGPT re-pin-6 P0)
  P0-19 corrupt budget state    -> FAILS CLOSED with refusal; zero executions;
                                  owner file removal is the recovery path (rev-7,
                                  ChatGPT blocker 3); non-object usage JSON and
                                  corrupt execution-history records fail closed
                                  too (rev-8, ChatGPT re-pin-6 3A/3B)
  P0-20 budget vs state loss    -> usage counter removed but durable execution
                                  record kept = budget still exhausted (rev-8,
                                  ChatGPT Q2 dedicated coverage for row 12)
  P0-21 corrupt state file      -> request HELD (unreadable-corrupt), never
                                  re-executed, never silently blacklisted (rev-8,
                                  Claude re-pin-6 non-blocking 1)
Usage: python3 scripts/qa/test_broker_p0.py
"""
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest.mock as mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "m0-broker-runner.py"
REVOKE = ROOT / "scripts" / "m0-broker-revoke-keys.sh"
PRINCIPAL = "steven@he-toolstack.local"
FAILS = []


def sh(*a, cwd=None):
    return subprocess.run(a, cwd=cwd, capture_output=True, text=True)


def canon(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def make_env(tmp):
    home = Path(tmp) / "home"
    home.mkdir()
    state = Path(tmp) / "state"
    remote = Path(tmp) / "remote.git"
    sh("git", "init", "--bare", "-b", "m0-evidence", str(remote))
    clone = Path(tmp) / "clone"
    sh("git", "clone", str(remote), str(clone))   # empty repo: -b would fail
    sh("git", "checkout", "-b", "m0-evidence", cwd=clone)
    sh("git", "commit", "--allow-empty", "-m", "bootstrap", cwd=clone)
    sh("git", "push", "origin", "m0-evidence", cwd=clone)
    sh("git", "config", "user.email", "m0-broker@local", cwd=clone)
    sh("git", "config", "user.name", "m0-broker", cwd=clone)
    key = Path(tmp) / "owner_key"
    sh("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(key), "-C", PRINCIPAL)
    pub = Path(str(key) + ".pub").read_text().split()
    signers = Path(tmp) / "allowed_signers"
    signers.write_text(f'{PRINCIPAL} namespaces="file" {pub[0]} {pub[1]}\n')
    (home / ".m0-broker.json").write_text(json.dumps({
        "repo": str(clone), "branch": "m0-evidence", "poll": 1,
        "allowed_signers": str(signers), "owner_principal": PRINCIPAL,
        "state_dir": str(state)}))
    return clone, key, home, state


def stage_and_push(clone, msg):
    sh("git", "add", "-A", cwd=clone)
    sh("git", "commit", "-m", msg, cwd=clone)
    sh("git", "push", "origin", "m0-evidence", cwd=clone)


def plan_payload(cmds):
    """rev-6 plan_digest: covers argv + pinned artifacts + max_runs per command."""
    return canon(sorted(canon({"argv": c["argv"], "artifacts": c["artifacts"],
                               "max_runs": c.get("max_runs", 1)}) for c in cmds))


def write_plan(clone, argv_lists, artifacts=None, budgets=None):
    cmds = [{"argv": a, "artifacts": (artifacts or {}).get(tuple(a), []),
             "max_runs": (budgets or {}).get(tuple(a), 1)}
            for a in argv_lists]
    plan = {"wave": "0", "commands": cmds, "plan_digest": plan_payload(cmds)}
    pf = clone / "workflows/m0-plans/open.json"
    pf.parent.mkdir(parents=True, exist_ok=True)
    pf.write_text(json.dumps(plan))
    for stale in (pf.parent / "open.json.sig", pf.parent / "open.sig"):
        if stale.exists():
            stale.unlink()
    stage_and_push(clone, "plan draft")


def authority_clone(tmp):
    auth = Path(tmp) / "authority"
    if not auth.exists():
        sh("git", "clone", "-b", "m0-evidence", str(Path(tmp) / "remote.git"), str(auth))
        sh("git", "config", "user.email", "owner@local", cwd=auth)
        sh("git", "config", "user.name", "owner", cwd=auth)
    sh("git", "pull", "--rebase", "origin", "m0-evidence", cwd=auth)
    return auth


def tamper_plan(tmp, extra_argv):
    auth = authority_clone(tmp)
    pf = auth / "workflows/m0-plans/open.json"
    body = json.loads(pf.read_text())
    body["commands"].append({"argv": extra_argv, "artifacts": [], "max_runs": 1})
    body["plan_digest"] = plan_payload(body["commands"])
    pf.write_text(json.dumps(body))
    stage_and_push(auth, "tamper (attack sim)")


def sign_plan_authority(tmp, key):
    auth = authority_clone(tmp)
    pf = auth / "workflows/m0-plans/open.json"
    for stale in (pf.parent / "open.json.sig", pf.parent / "open.sig"):
        if stale.exists():
            stale.unlink()
    r = sh("ssh-keygen", "-Y", "sign", "-f", str(key), "-n", "file", str(pf))
    assert r.returncode == 0, r.stderr
    stage_and_push(auth, "plan + owner signature")


def enqueue(clone, reqs, raw_lines=()):
    """Queue reaches the broker via the REMOTE branch. Sync first — the
    authority clone may have advanced the branch."""
    q = clone / "workflows/m0-evidence/requests.jsonl"
    sh("git", "pull", "--rebase", "origin", "m0-evidence", cwd=clone)
    q.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(r) + "\n" for r in reqs) + \
        "".join(l + "\n" for l in raw_lines)
    q.write_text(body)
    sh("git", "add", "-A", cwd=clone)
    sh("git", "commit", "-m", "requests", cwd=clone)
    sh("git", "push", "origin", "m0-evidence", cwd=clone)


def run_broker(tmp, home, *flags, extra_env=None):
    """A FRESH runner process per call — exactly what a systemd restart gives.
    Returns the CompletedProcess plus 'cycles' (EXECUTED/REFUSED/PENDING/
    UNPROVEN/COLLISION decision lines emitted by that one process)."""
    env = dict(os.environ, HOME=str(home))
    if extra_env:
        env.update(extra_env)
    r = subprocess.run(
        [sys.executable, str(RUNNER), "--branch", "m0-evidence", *flags],
        capture_output=True, text=True, env=env, timeout=120)
    r.cycles = sum(r.stdout.count(f"{tag} ") for tag in
                   ("EXECUTED", "REFUSED", "PENDING", "UNPROVEN"))
    return r


def all_records(clone):
    out = []
    for d in ("records", "refusals"):
        p = clone / "workflows/m0-evidence" / d
        if p.is_dir():
            out += [json.loads(f.read_text()) for f in p.glob("*.json")]
    return out


def check(name, cond, detail=""):
    print(("PASS  " if cond else "FAIL  ") + name + (f"   {detail[:300]}" if not cond else ""))
    if not cond:
        FAILS.append(name)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        clone, key, home, state = make_env(tmp)
        counter = Path(tmp) / "counter.txt"

        # P0-1: unsigned plan authorizes NOTHING — and (rev-7, Claude re-pin-5
        # required change) is not terminal either: the request stays PENDING with
        # zero disposition, and the SAME id executes once the owner signs.
        def line_hash(req):
            return hashlib.sha256(json.dumps(req).encode()).hexdigest()

        write_plan(clone, [["echo", "hi"]])
        enqueue(clone, [{"id": "r1", "argv": ["echo", "hi"]}])
        rp1 = run_broker(tmp, home)
        recs = all_records(clone)
        check("P0-1a unsigned plan -> no execution; request stays PENDING (never terminal)",
              "PENDING r1" in rp1.stdout and not [r for r in recs if "exit" in r]
              and not any(r.get("id") == "r1" for r in recs), rp1.stdout[-250:])
        sign_plan_authority(tmp, key)
        run_broker(tmp, home)
        recs = all_records(clone)
        check("P0-1b later owner signature runs the SAME id (unsigned plan blacklists nobody)",
              any(r.get("id") == "r1" and r.get("exit") == 0 for r in recs), str(recs)[:300])

        # P0-2: sign, then tamper -> signature FAILED. rev-7: unverifiable is PENDING,
        # zero disposition, zero execution; a later valid signature supersedes.
        write_plan(clone, [["echo", "hi2"]])   # fresh argv: rev-7 per-command budget
        sign_plan_authority(tmp, key)          # was spent by r1's identical argv
        tamper_plan(tmp, ["rm", "-rf", "/"])
        enqueue(clone, [{"id": "r2", "argv": ["echo", "hi2"]}])
        rp2 = run_broker(tmp, home)
        recs = all_records(clone)
        check("P0-2 tampered plan -> no execution",
              not [r for r in recs if "exit" in r and r["id"] == "r2"])
        check("P0-2b tampered plan -> PENDING, zero disposition written",
              "PENDING r2" in rp2.stdout
              and not any(r.get("id") == "r2" and "reason" in r for r in recs),
              rp2.stdout[-250:])
        write_plan(clone, [["echo", "hi2"]])   # supersede = the queued argv
        sign_plan_authority(tmp, key)
        run_broker(tmp, home)
        recs = all_records(clone)
        check("P0-2c tamper superseded by re-sign -> the queued id still runs",
              any(r.get("id") == "r2" and r.get("exit") == 0 for r in recs), str(recs)[:300])

        # P0-3/4: valid signature -> in-plan executes, out-of-plan refused.
        write_plan(clone, [["echo", "hello"], ["true"]])
        sign_plan_authority(tmp, key)
        enqueue(clone, [
            {"id": "r3", "argv": ["echo", "hello"]},
            {"id": "r4", "argv": ["id", "evil"]},
        ])
        run_broker(tmp, home)
        recs = all_records(clone)
        r3 = next((r for r in recs if r.get("id") == "r3"), None)
        r4 = next((r for r in recs if r.get("id") == "r4"), None)
        check("P0-3 in-plan executes; full capture fields",
              r3 is not None and r3.get("exit") == 0 and "request_raw" in r3
              and "artifact_digests" in r3 and "runner_computed_digest" in r3
              and "caller_supplied_digest" in r3, str(r3)[:400])
        check("P0-4 out-of-plan refused, never executed",
              r4 is not None and "exit" not in r4 and "reason" in r4, str(r4)[:400])

        # P0-5: broker evidence commits reached the REMOTE branch.
        remote = Path(tmp) / "remote.git"
        ls = sh("git", "log", "--oneline", "m0-evidence", cwd=str(remote))
        check("P0-5 records+refusals pushed to remote", "broker(" in ls.stdout,
              ls.stdout[:300])
        show = sh("git", "show", "--stat", "--format=", "m0-evidence", cwd=str(remote))
        check("P0-5b pushed diff contains record files",
              "m0-evidence/records" in show.stdout or "m0-evidence/refusals" in show.stdout)

        # ---- rev-5 lifecycle tests (ChatGPT re-pin-3 principal P0) ----
        # P0-6 restart/replay: executed request must NEVER run twice across
        # fresh processes. Side effect counted via a real counter file.
        count_argv = ["sh", "-c", f"echo x >> {counter}"]
        write_plan(clone, [count_argv])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r6", "argv": count_argv}])
        run_broker(tmp, home)
        first = counter.read_text().count("x") if counter.exists() else 0
        run_broker(tmp, home)              # fresh process = restart simulation
        run_broker(tmp, home)              # and again
        after = counter.read_text().count("x") if counter.exists() else 0
        check("P0-6 executed request never re-executes across restarts",
              first == 1 and after == 1, f"first={first} after={after}")

        # P0-7 exec ok + push FAILED -> retry must publish WITHOUT re-execution.
        # Real rejecting hook, broker-specific: rejects pushes whose tip was
        # committed by the broker identity; owner (test harness) pushes still pass.
        hook = remote / "hooks" / "pre-receive"
        hook.write_text(
            "#!/bin/sh\n"
            "while read -r old new ref; do\n"
            "  case \"$new\" in *[!0]*) : ;; *) continue ;; esac\n"
            "  ce=$(git show -s --format=%ce \"$new\" 2>/dev/null || echo \"\")\n"
            "  if [ \"$ce\" = \"m0-broker@local\" ]; then\n"
            "    echo 'rejecting broker push (test hook)'; exit 1\n"
            "  fi\n"
            "done\n"
            "exit 0\n")
        hook.chmod(0o755)
        count2 = Path(tmp) / "counter2.txt"
        c2_argv = ["sh", "-c", f"echo x >> {count2}"]
        # During the hook window, test pushes must carry the OWNER identity:
        auth = authority_clone(tmp)
        pf = auth / "workflows/m0-plans/open.json"
        cmds2 = [{"argv": c2_argv, "artifacts": [], "max_runs": 1}]
        pf.write_text(json.dumps({"wave": "0", "commands": cmds2,
                                  "plan_digest": plan_payload(cmds2)}))
        for stale in (pf.parent / "open.json.sig", pf.parent / "open.sig"):
            if stale.exists():
                stale.unlink()
        r = sh("ssh-keygen", "-Y", "sign", "-f", str(key), "-n", "file", str(pf))
        assert r.returncode == 0, r.stderr
        stage_and_push(auth, "r7 plan + owner signature")
        q = auth / "workflows/m0-evidence/requests.jsonl"
        sh("git", "pull", "--rebase", "origin", "m0-evidence", cwd=auth)
        q.write_text(json.dumps({"id": "r7", "argv": c2_argv}) + "\n")
        sh("git", "add", "-A", cwd=auth)
        sh("git", "commit", "-m", "r7 requests", cwd=auth)
        sh("git", "push", "origin", "m0-evidence", cwd=auth)
        r = run_broker(tmp, home)
        exec_once = count2.read_text().count("x") if count2.exists() else 0
        hook.unlink()                       # network "restored"
        run_broker(tmp, home)               # retry cycle
        exec_retry = count2.read_text().count("x") if count2.exists() else 0
        ls2 = sh("git", "log", "--oneline", "m0-evidence", cwd=str(remote))
        pushed = sh("git", "show", "--format=", "--name-only", "m0-evidence",
                    cwd=str(remote)).stdout
        check("P0-7a failed-push evidence retried WITHOUT re-execution",
              exec_once == 1 and exec_retry == 1 and r.returncode == 3,
              f"exec_once={exec_once} exec_retry={exec_retry} rc={r.returncode}")
        check("P0-7b delayed evidence eventually published to remote",
              "broker(" in ls2.stdout and "r7.json" in pushed, pushed[:200])

        # P0-8 crash mid-exec: state stuck 'started', NO durable record -> genuinely
        # uncertain -> UNPROVEN refusal, never re-executed (rev-7: the original
        # queue line is reproduced EXACTLY so its hash matches the planted state).
        (state / "state").mkdir(parents=True, exist_ok=True)
        count3 = Path(tmp) / "counter3.txt"
        c3_argv = ["sh", "-c", f"echo x >> {count3}"]
        write_plan(clone, [c3_argv])
        sign_plan_authority(tmp, key)
        orig_line = json.dumps({"id": "r8", "argv": c3_argv})
        orig_hash = hashlib.sha256(orig_line.encode()).hexdigest()
        (state / "state" / "r8.json").write_text(json.dumps(
            {"id": "r8", "status": "started", "updated": "2026-11-25T00:00:00+00:00",
             "note": "argv=[]", "request_line_sha256": orig_hash}))
        enqueue(clone, [], raw_lines=[orig_line])
        run_broker(tmp, home)
        recs = all_records(clone)
        u8 = next((x for x in recs if x.get("id") == "r8" and x.get("unproven") is True),
                  None)
        check("P0-8a 'started' + no record -> UNPROVEN refusal",
              u8 is not None and "UNPROVEN" in u8.get("reason", ""), str(u8)[:300])
        check("P0-8b uncertain execution NEVER re-executes (counter file untouched)",
              not count3.exists())
        # rev-7: a CONFLICTING line reusing the 'started' id is caught by the
        # collision-first rule (never masquerades as the original's UNPROVEN):
        enqueue(clone, [{"id": "r8", "argv": ["true"]}])   # different hash, same id
        run_broker(tmp, home)
        recs = all_records(clone)
        col8 = next((x for x in recs if x.get("id") == "r8"
                     and "ID-COLLISION" in x.get("reason", "")), None)
        check("P0-8c conflicting line under an already-disposed 'started' id -> ID-COLLISION "
              "(not UNPROVEN), original line-hash cited in the refusal",
              col8 is not None and col8.get("original_status") == "published"
              and col8.get("original_request_line_sha256") == orig_hash
              and not count3.exists(),
              f"orig_status={col8.get('original_status') if col8 else None} "
              f"ohash_ok={col8.get('original_request_line_sha256') == orig_hash if col8 else None} "
              f"count3={count3.exists()}")

        # P0-9 malformed / id-less lines get refusal records, never vanish.
        enqueue(clone, [], raw_lines=[
            "this is not json {{{",
            '["an", "array", "not", "object"]',
            '{"argv": ["true"]}',                    # no id
            '{"id": "bad/../id", "argv": ["true"]}', # invalid id chars
        ])
        run_broker(tmp, home)
        recs = all_records(clone)
        inval = [x for x in recs if x.get("id", "").startswith(("invalid-", "noid-"))
                 and "invalid-request" in x.get("reason", "")]
        check("P0-9 malformed/id-less lines -> refusal records (no silent drop)",
              len(inval) >= 4, f"invalid refusal records: {len(inval)}")

        # P0-9b rev-7 (Claude re-pin-5): ONE undecodable byte must kill only its
        # own line, never the whole pass (queue is read as bytes, decoded per line).
        write_plan(clone, [["true"]])
        sign_plan_authority(tmp, key)
        q9 = clone / "workflows/m0-evidence/requests.jsonl"
        sh("git", "pull", "--rebase", "origin", "m0-evidence", cwd=clone)
        q9.write_bytes(b'{"id": "bad\xffutf8", "argv": ["true"]}\n'
                       + (json.dumps({"id": "r9b", "argv": ["true"]}) + "\n").encode())
        sh("git", "add", "-A", cwd=clone)
        sh("git", "commit", "-m", "one bad byte (attack sim)", cwd=clone)
        sh("git", "push", "origin", "m0-evidence", cwd=clone)
        rb = run_broker(tmp, home)
        recs = all_records(clone)
        bad9 = [x for x in recs if "not valid UTF-8" in x.get("reason", "")]
        ok9 = next((x for x in recs if x.get("id") == "r9b" and "exit" in x), None)
        check("P0-9b undecodable queue byte -> that line refused on record, "
              "the NEXT line still executes (pass survives)",
              len(bad9) >= 1 and ok9 is not None and ok9.get("exit") == 0,
              f"bad={len(bad9)} r9b={str(ok9)[:150]}")

        # P0-9c rev-7: EMPTY argv inside a SIGNED plan is a plan error caught at
        # verification time -> everything stays PENDING, no crash, no 'started'.
        marker9c = Path(tmp) / "marker9c"
        write_plan(clone, [[], ["touch", str(marker9c)]])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r9c", "argv": ["touch", str(marker9c)]}])
        rc9 = run_broker(tmp, home)
        recs = all_records(clone)
        check("P0-9c empty-argv plan entry -> plan unverifiable: PENDING, no exec, "
              "no crash (rc=0, pass completed)",
              "PENDING r9c" in rc9.stdout and rc9.returncode == 0
              and not marker9c.exists()
              and not any(x.get("id") == "r9c" for x in recs), rc9.stdout[-200:])
        write_plan(clone, [["touch", str(marker9c)]])   # owner fixes the plan
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r9c", "argv": ["touch", str(marker9c)]}])
        run_broker(tmp, home)
        check("P0-9c2 corrected signature then executes the same id", marker9c.exists())

        # P0-9d rev-8 (ChatGPT re-pin-6 P1): a syntactically VALID JSON plan whose
        # top level is a LIST (not an object) used to crash verify_plan with an
        # uncaught AttributeError instead of the promised PENDING path.
        auth9d = authority_clone(tmp)
        pf9d = auth9d / "workflows/m0-plans/open.json"
        argv9d = ["touch", str(Path(tmp) / "marker9d")]
        list9d = [{"argv": argv9d, "artifacts": [], "max_runs": 1}]   # valid JSON, WRONG shape
        pf9d.write_text(json.dumps(list9d))
        for stale in (pf9d.parent / "open.json.sig", pf9d.parent / "open.sig"):
            if stale.exists():
                stale.unlink()
        r9d = sh("ssh-keygen", "-Y", "sign", "-f", str(key), "-n", "file", str(pf9d))
        assert r9d.returncode == 0, r9d.stderr
        stage_and_push(auth9d, "structurally invalid plan (list top level)")
        enqueue(clone, [{"id": "r9d", "argv": argv9d}])
        rc9d = run_broker(tmp, home)
        check("P0-9d valid-JSON list plan -> PENDING, no crash, no exec",
              rc9d.returncode == 0 and "PENDING r9d" in rc9d.stdout
              and not (Path(tmp) / "marker9d").exists(),
              f"rc={rc9d.returncode} out={rc9d.stdout[-180:]} err={rc9d.stderr[-120:]}")

        # P0-10 --once performs exactly ONE cycle (decision-line counted) and exits 0.
        # Stage exactly one fresh in-plan request so the counted cycle count is 1.
        argv10 = ["echo", "once-10"]
        write_plan(clone, [argv10])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r10", "argv": argv10}])
        r10 = run_broker(tmp, home, "--once")
        check("P0-10 --once = exactly one counted cycle, exit 0",
              r10.returncode == 0 and r10.cycles == 1 and "EXECUTED r10" in r10.stdout,
              f"rc={r10.returncode} cycles={r10.cycles}")

        # P0-11 revoke script (rev-6): selective revocation + inventory-wide
        # expected-state verification + STRICT recovery declarations.
        if shutil.which("ssh-keygen"):
            ak = Path(tmp) / "authorized_keys"
            kh = {}
            for nm in ("hermes1", "hermes2", "ownerkeep"):
                kp = Path(tmp) / f"hostkey_{nm}"
                sh("ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-f", str(kp), "-C", nm)
                kh[nm] = Path(str(kp) + ".pub").read_text().strip()
            ak.write_text("".join(v + "\n" for v in kh.values()))
            fpr = {nm: sh("ssh-keygen", "-lf", str(Path(str(kp) + ".pub"))).stdout.split()[1]
                   for nm, kp in (("hermes1", Path(tmp) / "hostkey_hermes1"),
                                  ("hermes2", Path(tmp) / "hostkey_hermes2"),
                                  ("ownerkeep", Path(tmp) / "hostkey_ownerkeep"))}
            # inventory: every credential that ever existed on this account, in
            # the setup.sh format: "<file>  <bits> SHA256:... <comment>"
            inv = Path(tmp) / "inventory.txt"
            lines = []
            for nm in ("hermes1", "hermes2", "ownerkeep"):
                rec = sh("ssh-keygen", "-lf", str(Path(tmp) / f"hostkey_{nm}.pub")).stdout.strip()
                lines.append(f"{str(ak)}  {rec}\n")
            inv.write_text("".join(lines))
            cutover = Path(tmp) / "cutover"
            rv = subprocess.run(
                ["bash", str(REVOKE), "--revoke", str(ak)],
                capture_output=True, text=True,
                env=dict(os.environ,
                         M0_REVOKE_FPR=f"{fpr['hermes1']} {fpr['hermes2']}",
                         M0_RECOVERY=f"keep:{fpr['ownerkeep']}",
                         M0_INVENTORY=str(inv),
                         CUTOVER_DIR=str(cutover)))
            remaining = ak.read_text()
            verif = cutover / "cutover-verification.txt"
            vt = verif.read_text() if verif.exists() else ""
            check("P0-11a revoke is SELECTIVE (Hermes keys gone, owner key kept)",
                  rv.returncode == 0
                  and kh["hermes1"] not in remaining and kh["hermes2"] not in remaining
                  and kh["ownerkeep"] in remaining, rv.stdout[-300:] + rv.stderr[-200:])
            check("P0-11b consolidated EXPECTED=/OBSERVED= verification record, inventory complete",
                  "REVOKE" in vt and "EXPECTED=ABSENT OBSERVED=ABSENT OK" in vt
                  and "RECOVERY" in vt and "EXPECTED=PRESENT OBSERVED=PRESENT OK" in vt
                  and vt.count("INVENTORY") == 3
                  and "FAIL" not in vt, vt[:400])
            # fail-closed: a declared recovery key that is NOT actually present
            # must FAIL the verification and exit non-zero (repair 4 enforcement).
            sh("ssh-keygen", "-q", "-t", "ed25519", "-N", "",
               "-f", str(Path(tmp) / "hostkey_ghost"), "-C", "ghost")
            ghost = sh("ssh-keygen", "-lf", str(Path(tmp) / "hostkey_ghost.pub")).stdout.split()[1]
            rv_s = subprocess.run(
                ["bash", str(REVOKE), "--revoke", str(ak)],
                capture_output=True, text=True,
                env=dict(os.environ, M0_REVOKE_FPR=fpr["hermes1"],
                         M0_RECOVERY=f"keep:{ghost}",
                         M0_INVENTORY=str(inv),
                         CUTOVER_DIR=str(Path(tmp) / "cutover-short")))
            vt_s = (Path(tmp) / "cutover-short" / "cutover-verification.txt")
            vts = vt_s.read_text() if vt_s.exists() else ""
            check("P0-11b2 declared-but-absent recovery key FAILS verification (exit non-zero)",
                  rv_s.returncode != 0
                  and "EXPECTED=PRESENT OBSERVED=ABSENT FAIL" in vts,
                  f"rc={rv_s.returncode} " + vts[:300])
            rv2 = subprocess.run(
                ["bash", str(REVOKE), "--revoke", str(ak)],
                capture_output=True, text=True,
                env=dict(os.environ, M0_REVOKE_FPR=fpr["hermes1"],
                         M0_INVENTORY=str(inv)))  # M0_RECOVERY unset
            check("P0-11c refuses to run without declared recovery path",
                  rv2.returncode != 0 and "M0_RECOVERY" in rv2.stdout + rv2.stderr)
            # rev-6 strict declaration grammar: old 'recovery:<fpr>' form is REMOVED
            rv3 = subprocess.run(
                ["bash", str(REVOKE), "--revoke", str(ak)],
                capture_output=True, text=True,
                env=dict(os.environ, M0_REVOKE_FPR=fpr["hermes1"],
                         M0_RECOVERY=f"recovery:{fpr['ownerkeep']}",
                         M0_INVENTORY=str(inv),
                         CUTOVER_DIR=str(Path(tmp) / "cutover-r3")))
            check("P0-11d removed recovery:<fpr> form is REFUSED (never implicit local-console)",
                  rv3.returncode != 0 and "unrecognized M0_RECOVERY" in rv3.stdout + rv3.stderr,
                  (rv3.stdout + rv3.stderr)[:200])
            # rev-7 (ChatGPT re-pin-5 P1): an UNSET inventory must fail closed —
            # rev-6 treated it as WARN+proceed, so the operator could skip the
            # inventory precisely when completeness mattered most.
            rv4 = subprocess.run(
                ["bash", str(REVOKE), "--revoke", str(ak)],
                capture_output=True, text=True,
                env=dict(os.environ, M0_INVENTORY="",  # explicitly unset (deterministic)
                         M0_REVOKE_FPR=fpr["hermes1"],
                         M0_RECOVERY=f"keep:{fpr['ownerkeep']}"))
            check("P0-11e missing M0_INVENTORY fails CLOSED (rev-6 WARN+proceed removed)",
                  rv4.returncode != 0 and "M0_INVENTORY" in rv4.stdout + rv4.stderr,
                  (rv4.stdout + rv4.stderr)[:200])
        else:
            check("P0-11 skipped (no ssh-keygen)", False)

        # ---- rev-6 repairs: P0-12..P0-17 (bodies matching the docstring) ----

        # P0-12 fsync durability: durable_write fsyncs the temp FILE and then the
        # parent DIRECTORY (so the rename itself survives power loss).
        spec = importlib.util.spec_from_file_location("m0_runner", RUNNER)
        runner_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(runner_mod)
        probe = Path(tmp) / "fsync-probe" / "obj.json"
        with mock.patch.object(runner_mod.os, "fsync") as fs:
            runner_mod.durable_write(probe, {"hello": "world"})
        real_ok = json.loads(probe.read_text()) == {"hello": "world"}
        check("P0-12a durable_write fsyncs file AND parent dir (>=2 calls)",
              fs.call_count >= 2, f"fsync calls: {fs.call_count}")
        check("P0-12b durable_write real write is atomic + correct",
              real_ok and not probe.with_suffix(".json.tmp").exists())

        # P0-12c rev-7 (ChatGPT P1): creating a nested layout must fsync the WHOLE
        # new-directory chain, not just the immediate parent — a rename survives
        # power loss only if every new dir's ENTRY is durable too.
        deep = Path(tmp) / "fsync-probe" / "a" / "b" / "obj.json"
        with mock.patch.object(runner_mod.os, "fsync") as fs:
            runner_mod.durable_write(deep, {"n": 1})
        check("P0-12c first nested write fsyncs file + full new-directory chain",
              fs.call_count >= 4 and json.loads(deep.read_text()) == {"n": 1},
              f"fsync calls: {fs.call_count}")

        # P0-13 request-ID collision: same id, different line content.
        argv13 = ["echo", "collide-1"]
        write_plan(clone, [argv13])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r13", "argv": argv13}])
        run_broker(tmp, home)
        recs = all_records(clone)
        r13 = next((x for x in recs if x.get("id") == "r13" and "exit" in x), None)
        # second line reuses r13 with DIFFERENT argv (tamper/reuse sim)
        enqueue(clone, [{"id": "r13", "argv": ["echo", "collide-2-different"]}])
        run_broker(tmp, home)
        recs = all_records(clone)
        col = next((x for x in recs if x.get("id_collision") is True), None)
        r13b = next((x for x in recs if x.get("id") == "r13"
                     and x.get("argv") == ["echo", "collide-2-different"]
                     and "exit" in x), None)
        check("P0-13a reused id + different content -> explicit ID-COLLISION refusal",
              r13 is not None and col is not None
              and col.get("original_request_line_sha256")
              and col.get("conflicting_request_line_sha256")
              and col["original_request_line_sha256"] != col["conflicting_request_line_sha256"],
              str(col)[:300])
        check("P0-13b colliding argv NEVER executes; original disposition stands",
              r13b is None and r13 is not None and r13.get("exit") == 0)

        # P0-13c/d rev-7 blocker 1 (ChatGPT re-pin-5): collision is checked BEFORE
        # the 'started' recovery branch — a conflicting line reusing a 'started'
        # id must never masquerade as the original's UNPROVEN/recovery outcome.
        (state / "state").mkdir(parents=True, exist_ok=True)
        start_line13 = json.dumps({"id": "r13c", "argv": ["echo", "start-13"]})
        start_hash13 = hashlib.sha256(start_line13.encode()).hexdigest()
        (state / "state" / "r13c.json").write_text(json.dumps(
            {"id": "r13c", "status": "started", "updated": "2026-11-25T00:00:00+00:00",
             "note": "argv=[\"echo\", \"start-13\"]",
             "request_line_sha256": start_hash13}))
        enqueue(clone, [{"id": "r13c", "argv": ["echo", "evil-reuse"]}])
        run_broker(tmp, home)
        recs = all_records(clone)
        col13 = next((x for x in recs if x.get("id") == "r13c"
                      and x.get("id_collision") is True), None)
        unp13 = next((x for x in recs if x.get("id") == "r13c"
                      and x.get("unproven") is True), None)
        s13 = json.loads((state / "state" / "r13c.json").read_text())
        check("P0-13c collision BEFORE started-branch (ID-COLLISION, never UNPROVEN)",
              col13 is not None and unp13 is None
              and col13.get("original_status") == "started"
              and col13.get("original_request_line_sha256") == start_hash13,
              str(col13)[:250])
        check("P0-13d original 'started' state survives the collision untouched",
              s13.get("status") == "started"
              and s13.get("request_line_sha256") == start_hash13, str(s13)[:200])
        # P0-14 pinned artifacts swapped AFTER signing -> refuse before spawn.
        c14 = Path(tmp) / "counter14.txt"
        script14 = clone / "tools" / "job14.sh"
        script14.parent.mkdir(exist_ok=True)
        script14.write_text("#!/bin/sh\necho x >> " + str(c14) + "\n")
        stage_and_push(clone, "artifact v1")
        good_sha = hashlib.sha256(script14.read_bytes()).hexdigest()
        argv14 = ["sh", str(Path(".") / "tools" / "job14.sh")]
        write_plan(clone, [argv14], artifacts={tuple(argv14): [
            {"path": "tools/job14.sh", "sha256": good_sha}]})
        sign_plan_authority(tmp, key)
        # attacker with evidence-repo push rights swaps the script AFTER the owner sign
        script14.write_text("#!/bin/sh\neecho pwned >> /tmp/never\n")
        stage_and_push(clone, "artifact swap (attack sim)")
        enqueue(clone, [{"id": "r14", "argv": argv14}])
        run_broker(tmp, home)
        recs = all_records(clone)
        a14 = next((x for x in recs if x.get("id") == "r14" and "reason" in x), None)
        check("P0-14a post-sign artifact swap -> ARTIFACT-MISMATCH refusal, nothing ran",
              a14 is not None and "ARTIFACT-MISMATCH" in a14.get("reason", "")
              and not c14.exists(),
              str(a14)[:300])
        check("P0-14b refusal preserves observed vs pinned digests",
              a14 is not None and "artifact_verification" in a14
              and a14["artifact_verification"].get("tools/job14.sh", {}).get("match") is False)

        # P0-15 use budget keyed by plan+argv digest: fresh id does not reset it.
        c15 = Path(tmp) / "counter15.txt"
        argv15 = ["sh", "-c", f"echo x >> {c15}"]
        write_plan(clone, [argv15], budgets={tuple(argv15): 1})
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r15", "argv": argv15}])
        run_broker(tmp, home)
        first_count = c15.read_text().count("x") if c15.exists() else 0
        enqueue(clone, [{"id": "r15b", "argv": argv15}])   # FRESH id, same argv
        run_broker(tmp, home)
        recs = all_records(clone)
        b15 = next((x for x in recs if x.get("id") == "r15b"), None)
        second_count = c15.read_text().count("x") if c15.exists() else 0
        check("P0-15 budget survives fresh request ids (per-command key: argv+artifacts+max_runs)",
              first_count == 1 and second_count == 1
              and b15 is not None and "BUDGET-EXHAUSTED" in b15.get("reason", ""),
              f"counts {first_count}->{second_count} rec={str(b15)[:200]}")

        # P0-16 plan ABSENT -> PENDING (never a blacklisting refusal); a later
        # owner signature authorizes the same id.
        argv16 = ["touch", str(Path(tmp) / "marker16")]
        auth = authority_clone(tmp)
        (auth / "workflows/m0-plans/open.json").unlink(missing_ok=True)
        (auth / "workflows/m0-plans/open.json.sig").unlink(missing_ok=True)
        stage_and_push(auth, "withdraw plan (owner action)")
        enqueue(clone, [{"id": "r16", "argv": argv16}])
        rp = run_broker(tmp, home)
        pending_ok = "PENDING r16" in rp.stdout
        mid_recs = all_records(clone)
        check("P0-16a plan absent -> request stays PENDING, no disposition, no exec",
              pending_ok and not (Path(tmp) / "marker16").exists()
              and not any(x.get("id") == "r16" for x in mid_recs),
              rp.stdout[-300:])
        write_plan(clone, [argv16])           # same id re-entered below
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r16", "argv": argv16}])
        run_broker(tmp, home)
        recs = all_records(clone)
        r16 = next((x for x in recs if x.get("id") == "r16" and "exit" in x), None)
        check("P0-16b later owner signature authorizes the SAME id (absence != blacklist)",
              r16 is not None and (Path(tmp) / "marker16").exists(),
              str(r16)[:200])

        # P0-17 spawn OSError -> DEFINITE failed record, never UNPROVEN on restart.
        argv17 = ["m0-no-such-binary-zzz"]
        write_plan(clone, [argv17])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r17", "argv": argv17}])
        run_broker(tmp, home)
        recs = all_records(clone)
        r17 = next((x for x in recs if x.get("id") == "r17"
                    and x.get("spawn_succeeded") is False), None)
        check("P0-17a spawn OSError -> definite record (spawn_succeeded=false, never ran)",
              r17 is not None and "SPAWN-FAILED" in r17.get("error", "")
              and r17.get("exit") is None, str(r17)[:300])
        run_broker(tmp, home, "--once")       # restart over the same queue
        recs = all_records(clone)
        unp = [x for x in recs if x.get("id") == "r17" and x.get("unproven") is True]
        r17dup = [x for x in recs if x.get("id") == "r17" and x.get("spawn_succeeded") is False]
        check("P0-17b definite spawn failure never becomes UNPROVEN after restart",
              not unp and len(r17dup) == 1)

        # P0-17c rev-7 (ChatGPT re-pin-5 P1) / rev-8: the spawn catch is
        # `except Exception` around Popen CONSTRUCTION — a NON-OSError raised at
        # spawn (internal failure) never starts the process, is recorded definite
        # (spawn_succeeded=False), never 'started'. In-process: subprocess.Popen is
        # trapped by argv so only the request spawn is affected; the broker's own
        # git subprocess.run calls run untouched.
        mk17c = Path(tmp) / "marker17c"
        write_plan(clone, [["touch", str(mk17c)]])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r17c", "argv": ["touch", str(mk17c)]}])
        import types as _types
        real_popen = subprocess.Popen
        def trap_popen(cmd, *a2, **k2):
            if isinstance(cmd, (list, tuple)) and cmd and cmd[0] == "touch":
                raise ValueError("injected non-OSError at spawn")
            return real_popen(cmd, *a2, **k2)
        a17 = _types.SimpleNamespace(repo=str(clone), branch="m0-evidence", poll=1,
                                     state_dir=str(state), owner_principal=PRINCIPAL)
        L17 = runner_mod.Ledger(str(state))
        signers17 = Path(tmp) / "allowed_signers"
        with mock.patch.object(runner_mod.subprocess, "Popen", side_effect=trap_popen):
            runner_mod.run_pass(a17, signers17, L17)
        recs = all_records(clone)
        r17c = next((x for x in recs if x.get("id") == "r17c"), None)
        s17c = json.loads((state / "state" / "r17c.json").read_text())
        check("P0-17c non-OSError at spawn -> definite SPAWN-FAILED, "
              "spawn_succeeded=false, never 'started', never executed",
              r17c is not None and r17c.get("spawn_succeeded") is False
              and "SPAWN-FAILED (ValueError" in r17c.get("error", "")
              and not mk17c.exists() and s17c.get("status") != "started",
              str(r17c)[:250])

        # P0-17d rev-8 (Claude re-pin-6 REQUIRED): rev-7's subprocess.run(text=True)
        # decoded output strictly AFTER the child ran; invalid UTF-8 raised
        # UnicodeDecodeError INSIDE the except-Exception "never executed" branch ->
        # spawn_succeeded=False, budget NOT consumed -> an executed command could
        # run again. rev-8 separates Popen (spawn) from communicate+lossy decode.
        # (printf \377\376 is valid shell — only the OUTPUT bytes are invalid UTF-8.)
        counter17d = Path(tmp) / "counter17d.txt"
        script17d = clone / "tools" / "job17d.sh"
        script17d.parent.mkdir(parents=True, exist_ok=True)
        script17d.write_text(f"#!/bin/sh\nprintf '\\377\\376'\n"
                             f"echo x >> {counter17d}\n")
        script17d.chmod(0o755)
        argv17d = ["sh", str(script17d)]
        write_plan(clone, [argv17d])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r17d", "argv": argv17d}])
        run_broker(tmp, home)
        recs = all_records(clone)
        r17d = next((x for x in recs if x.get("id") == "r17d"), None)
        check("P0-17d invalid-UTF8 output -> recorded EXECUTED (spawn_succeeded=true), "
              "lossy decode, never 'never executed'",
              r17d is not None and r17d.get("spawn_succeeded") is True
              and r17d.get("exit") == 0 and counter17d.exists()
              and "\ufffd" in r17d.get("stdout", ""),
              str(r17d)[:300])
        run_broker(tmp, home, "--once")   # restart over the same queue
        check("P0-17d2 executed bad-UTF8 command never re-executes across restart",
              counter17d.read_text().count("x") == 1,
              counter17d.read_text())
        enqueue(clone, [{"id": "r17d2", "argv": argv17d}])   # fresh request id
        run_broker(tmp, home)
        recs = all_records(clone)
        r17d2 = next((x for x in recs if x.get("id") == "r17d2"), None)
        check("P0-17d3 post-decode-failure execution consumed the budget "
              "(BUDGET-EXHAUSTED under fresh id, second run refused)",
              r17d2 is not None and "BUDGET-EXHAUSTED" in r17d2.get("reason", "")
              and counter17d.read_text().count("x") == 1,
              str(r17d2)[:250])

        # P0-18 rev-7 blocker 2 (ChatGPT re-pin-5): a crash AFTER the durable
        # completion record but BEFORE the state save leaves status 'started' with a
        # PROVEN outcome. Recovery must read the record and RECOVER the definite
        # result — a known outcome never degrades to UNPROVEN.
        c18 = Path(tmp) / "counter18.txt"
        script18 = clone / "tools" / "job18.sh"
        script18.parent.mkdir(parents=True, exist_ok=True)
        script18.write_text(f"#!/bin/sh\necho x >> {c18}\n")
        script18.chmod(0o755)
        argv18 = ["sh", str(script18)]
        write_plan(clone, [argv18])
        sign_plan_authority(tmp, key)
        line18 = json.dumps({"id": "r18", "argv": argv18})
        hash18 = hashlib.sha256(line18.encode()).hexdigest()
        (state / "state").mkdir(parents=True, exist_ok=True)
        (state / "state" / "r18.json").write_text(json.dumps(
            {"id": "r18", "status": "started", "updated": "2026-11-25T00:00:00+00:00",
             "note": f"argv={json.dumps(argv18)}", "request_line_sha256": hash18}))
        (state / "records").mkdir(parents=True, exist_ok=True)
        (state / "records" / "r18.json").write_text(json.dumps(
            {"id": "r18", "argv": argv18, "exit": 0, "stdout": "x\n", "stderr": "",
             "error": None, "spawn_succeeded": True, "request_line_sha256": hash18,
             "max_runs": 1, "artifact_contract": []}))
        enqueue(clone, [{"id": "r18", "argv": argv18}])
        rp18 = run_broker(tmp, home)
        recs = all_records(clone)
        unp18 = [x for x in recs if x.get("id") == "r18" and x.get("unproven") is True]
        check("P0-18a definite completion record + 'started' -> RECOVERED, never UNPROVEN",
              "RECOVERED r18" in rp18.stdout and not unp18, rp18.stdout[-250:])
        check("P0-18b recovered definite outcome never RE-EXECUTES the command",
              not c18.exists())

        # P0-18c rev-8 (ChatGPT re-pin-6 P0): the EXACT rev-6 failure window —
        # 'started' state + durable record with spawn_succeeded=FALSE (crash
        # between the definite spawn-failure record and the state save). Recovery
        # must restore the definite spawn failure: never UNPROVEN, never re-exec.
        c18c = Path(tmp) / "counter18c.txt"
        script18c = clone / "tools" / "job18c.sh"
        argv18c = ["sh", str(script18c)]
        script18c.write_text(f"#!/bin/sh\necho x >> {c18c}\n")
        script18c.chmod(0o755)
        write_plan(clone, [argv18c])
        sign_plan_authority(tmp, key)
        line18c = json.dumps({"id": "r18c", "argv": argv18c})
        hash18c = hashlib.sha256(line18c.encode()).hexdigest()
        (state / "state").mkdir(parents=True, exist_ok=True)
        (state / "state" / "r18c.json").write_text(json.dumps(
            {"id": "r18c", "status": "started", "updated": "2026-11-25T00:00:00+00:00",
             "note": f"argv={json.dumps(argv18c)}", "request_line_sha256": hash18c}))
        (state / "records").mkdir(parents=True, exist_ok=True)
        (state / "records" / "r18c.json").write_text(json.dumps(
            {"id": "r18c", "argv": argv18c, "exit": None, "stdout": "", "stderr": "",
             "error": "SPAWN-FAILED (FileNotFoundError, never executed): sim",
             "spawn_succeeded": False, "request_line_sha256": hash18c,
             "max_runs": 1, "artifact_contract": []}))
        enqueue(clone, [{"id": "r18c", "argv": argv18c}])
        rp18c = run_broker(tmp, home)
        recs = all_records(clone)
        unp18c = [x for x in recs if x.get("id") == "r18c" and x.get("unproven") is True]
        s18c = json.loads((state / "state" / "r18c.json").read_text())
        check("P0-18c started + spawn_succeeded=false record -> RECOVERED definite, "
              "never UNPROVEN",
              "RECOVERED r18c" in rp18c.stdout and not unp18c
              and s18c.get("status") in ("executed", "published"),
              f"stdout={rp18c.stdout[-200:]} state={s18c.get('status')}")
        check("P0-18c2 crash-window spawn failure never re-executes",
              not c18c.exists())

        # P0-19 rev-7 blocker 3 (ChatGPT re-pin-5): a CORRUPT durable budget file
        # must fail CLOSED — corrupt authorization state can never grant runs.
        mk19 = Path(tmp) / "marker19"
        argv19 = ["touch", str(mk19)]
        write_plan(clone, [argv19])
        sign_plan_authority(tmp, key)
        use_key19 = runner_mod.canonical_sha256([argv19, [], 1])
        ufile = state / "usage" / f"{use_key19}.json"
        ufile.parent.mkdir(parents=True, exist_ok=True)
        ufile.write_text("{not json at all")
        enqueue(clone, [{"id": "r19", "argv": argv19}])
        run_broker(tmp, home)
        recs = all_records(clone)
        r19 = next((x for x in recs if x.get("id") == "r19"), None)
        check("P0-19a corrupt budget file -> BUDGET-STATE-CORRUPT refusal, zero exec",
              r19 is not None and "BUDGET-STATE-CORRUPT" in r19.get("reason", "")
              and not mk19.exists(), str(r19)[:200])
        ufile.unlink()   # explicit owner intervention: remove the corrupt state
        enqueue(clone, [{"id": "r19b2", "argv": argv19}])
        run_broker(tmp, home)
        check("P0-19b owner removed corrupt file -> budget path executes again",
              mk19.exists())

        # ================= rev-8 budget-history & corrupt-state block =================
        # P0-20 rev-8 (ChatGPT re-pin-6 Q2 REQUIRED): dedicated coverage for the
        # durable-record budget history that row 12 of the re-pin-6 table declared
        # untested.

        # P0-20a/b executed command + usage counter deleted -> the durable execution
        # record preserves max_runs; a fresh request id is still refused.
        mk20 = Path(tmp) / "marker20"
        argv20 = ["touch", str(mk20)]
        write_plan(clone, [argv20])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r20", "argv": argv20}])
        run_broker(tmp, home)
        check("P0-20a first execution runs the command", mk20.exists())
        use20 = runner_mod.canonical_sha256([argv20, [], 1])
        (state / "usage" / f"{use20}.json").unlink()      # simulated state loss
        mk20.unlink()
        enqueue(clone, [{"id": "r20b", "argv": argv20}])  # fresh request id
        run_broker(tmp, home)
        r20b = next((x for x in all_records(clone) if x.get("id") == "r20b"), None)
        check("P0-20b usage counter wiped -> durable-record history preserves budget "
              "(BUDGET-EXHAUSTED under fresh id, no second execution)",
              r20b is not None and "BUDGET-EXHAUSTED" in r20b.get("reason", "")
              and not mk20.exists(), str(r20b)[:220])

        # P0-20c a spawn_succeeded=false record consumes NO budget (never spawned):
        # a fresh id with the exact never-spawned argv REACHES SPAWN again (a new
        # definite spawn attempt) instead of a BUDGET-EXHAUSTED refusal. (argv17
        # is a nonexistent binary — reaching spawn at all IS the budget grant.)
        r17rec = next((x for x in all_records(clone) if x.get("id") == "r17"
                       and x.get("spawn_succeeded") is False), None)
        if r17rec is not None:
            argv20c = r17rec["argv"]
            write_plan(clone, [argv20c])
            sign_plan_authority(tmp, key)
            enqueue(clone, [{"id": "r20c", "argv": argv20c}])
            run_broker(tmp, home)
            recs20c = [x for x in all_records(clone) if x.get("id") == "r20c"]
            exhausted = [x for x in recs20c if "BUDGET-EXHAUSTED" in x.get("reason", "")]
            spawn_again = any(x.get("spawn_succeeded") is False
                              and "SPAWN-FAILED" in x.get("error", "")
                              for x in recs20c)
            check("P0-20c spawn_succeeded=false record consumed no budget (fresh-id "
                  "same argv reaches spawn again, never BUDGET-EXHAUSTED)",
                  spawn_again and not exhausted, str(recs20c)[:220])
        else:
            check("P0-20c spawn_succeeded=false record consumed no budget", False,
                  "P0-17 never-spawned record missing — cannot test budget exclusion")

        # P0-20d structurally invalid usage JSON (valid syntax, wrong shape: [])
        # -> explicit BUDGET-STATE-CORRUPT refusal, no crash, no execution (rev-8 3A).
        mk20d = Path(tmp) / "marker20d"
        argv20d = ["touch", str(mk20d)]
        write_plan(clone, [argv20d])              # must clear the plan gate first —
        sign_plan_authority(tmp, key)             # budget check runs AFTER verification
        use20d = runner_mod.canonical_sha256([argv20d, [], 1])
        (state / "usage").mkdir(parents=True, exist_ok=True)
        (state / "usage" / f"{use20d}.json").write_text("[]")   # valid JSON, not an object
        enqueue(clone, [{"id": "r20d", "argv": argv20d}])
        run_broker(tmp, home)
        r20d = next((x for x in all_records(clone) if x.get("id") == "r20d"), None)
        check("P0-20d usage JSON '[]' (wrong shape) -> BUDGET-STATE-CORRUPT refusal, "
              "no crash, no exec",
              r20d is not None and "BUDGET-STATE-CORRUPT" in r20d.get("reason", "")
              and not mk20d.exists(), str(r20d)[:220])

        # P0-20e corrupt execution-HISTORY record -> fail closed, NOT silently
        # skipped: an unparseable record refuses a brand-new command even though
        # the intact history around it would grant a run (rev-8 3B).
        mk20e = Path(tmp) / "marker20e"
        argv20e = ["touch", str(mk20e)]
        write_plan(clone, [argv20e])              # clear the plan gate first
        sign_plan_authority(tmp, key)
        (state / "records" / "zz-corrupt.json").write_text("{not json at all")
        enqueue(clone, [{"id": "r20e", "argv": argv20e}])
        run_broker(tmp, home)
        r20e = next((x for x in all_records(clone) if x.get("id") == "r20e"), None)
        check("P0-20e corrupt execution-history record -> BUDGET-STATE-CORRUPT fail "
              "closed (never silently skipped), no exec",
              r20e is not None and "BUDGET-STATE-CORRUPT" in r20e.get("reason", "")
              and not mk20e.exists(), str(r20e)[:220])
        # Owner recovery (same as P0-19b) before the next scenario: while the
        # corrupt record stands, EVERY dispatch refuses fail-closed — proven
        # behavior, and 20f must start from a clean history.
        (state / "records" / "zz-corrupt.json").unlink()

        # P0-20f corrupt REQUEST STATE file is held, not treated as unseen (never
        # re-executed); the broker keeps running other requests.
        write_plan(clone, [["touch", str(Path(tmp) / "marker20g")]])
        sign_plan_authority(tmp, key)
        (state / "state" / "r20f.json").write_text("{broken")
        enqueue(clone, [{"id": "r20f", "argv": ["touch", str(Path(tmp) / "marker20f")]},
                        {"id": "r20g", "argv": ["touch", str(Path(tmp) / "marker20g")]}])
        rp20f = run_broker(tmp, home)
        s20f = (state / "state" / "r20f.json").read_text()
        check("P0-20f corrupt request-state file -> LEDGER-STATE-CORRUPT held, "
              "never re-executed, other requests still run",
              "LEDGER-STATE-CORRUPT r20f" in rp20f.stdout and s20f == "{broken"
              and not (Path(tmp) / "marker20f").exists()
              and (Path(tmp) / "marker20g").exists(),
              f"stdout={rp20f.stdout}")

    print("FAILS:", FAILS or "none")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
