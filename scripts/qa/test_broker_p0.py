#!/usr/bin/env python3
"""Exercise rev-5 + rev-6 P0 repairs against the broker.

Real mechanisms, no mocks: ssh-keygen -Y sign/verify for plan authorization and a
local bare git remote (with a real rejecting pre-receive hook) for publish paths.
No network. Checks:
  P0-1 unsigned plan            -> nothing executes; refusal recorded ON RECORD
  P0-2 tampered plan            -> signature FAILED -> refusals on record
  P0-3 signed plan, in-plan     -> executes; record has full capture fields
  P0-4 out-of-plan argv         -> refusal record, never executed
  P0-5 evidence pushed          -> broker commits visible on the remote branch
  P0-6 restart / replay         -> an executed request NEVER re-executes on a fresh
                                  runner process (durable state replaces memory set)
  P0-7 exec ok, push FAILED     -> retry publishes WITHOUT re-executing the command
  P0-8 crash mid-exec (started) -> UNPROVEN refusal, zero automatic re-execution
  P0-9 malformed / id-less lines-> invalid-request refusal records (no silent drop)
  P0-10 --once                  -> exactly one cycle (cycle-counted), exact exit 0
  P0-11 revoke script           -> selective by fingerprint; owner key retained;
                                  inventory-wide expected-state verification;
                                  strict recovery declarations (rev-6)
  P0-12 fsync durability        -> durable_write fsyncs file AND parent directory
                                  (rev-6, ChatGPT repair 1)
  P0-13 request-ID collision    -> reused id + different content = explicit refusal
                                  preserving both hashes (rev-6, ChatGPT repair 3)
  P0-14 pinned artifacts        -> script swapped after signing = nothing runs
                                  (rev-6, Claude condition 1)
  P0-15 use budget              -> executed argv under a FRESH id is refused by the
                                  plan+argv-keyed budget (rev-6, Claude condition 2)
  P0-16 plan absent -> pending  -> later signature authorizes; absence never
                                  blacklists an id (rev-6, Claude condition 3)
  P0-17 spawn OSError           -> definite failed-spawn record, never UNPROVEN
                                  (rev-6, Claude condition 4)
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

        # P0-1: unsigned plan authorizes nothing, refusal is ON RECORD.
        write_plan(clone, [["echo", "hi"]])
        enqueue(clone, [{"id": "r1", "argv": ["echo", "hi"]}])
        run_broker(tmp, home)
        recs = all_records(clone)
        check("P0-1a unsigned plan -> no execution",
              not [r for r in recs if "exit" in r])
        check("P0-1b unsigned plan -> refusal on record",
              any(r.get("id") == "r1" and "reason" in r for r in recs), str(recs)[:400])

        # P0-2: sign, then tamper -> verification must fail closed.
        write_plan(clone, [["echo", "hi"]])
        sign_plan_authority(tmp, key)
        tamper_plan(tmp, ["rm", "-rf", "/"])
        enqueue(clone, [{"id": "r2", "argv": ["echo", "hi"]}])
        run_broker(tmp, home)
        recs = all_records(clone)
        check("P0-2 tampered plan -> no execution",
              not [r for r in recs if "exit" in r and r["id"] == "r2"])
        check("P0-2b tampered plan -> refusal cites signature",
              any(r.get("id") == "r2" and "signature" in r.get("reason", "")
                  for r in recs))

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

        # P0-8 crash mid-exec: state stuck 'started' -> UNPROVEN, no re-run.
        (state / "state").mkdir(parents=True, exist_ok=True)
        (state / "state" / "r8.json").write_text(json.dumps(
            {"id": "r8", "status": "started", "updated": "2026-11-25T00:00:00+00:00",
             "note": "argv=[]", "request_line_sha256": "0" * 64}))
        count3 = Path(tmp) / "counter3.txt"
        c3_argv = ["sh", "-c", f"echo x >> {count3}"]
        write_plan(clone, [c3_argv])
        sign_plan_authority(tmp, key)
        enqueue(clone, [{"id": "r8", "argv": c3_argv}])
        run_broker(tmp, home)
        ran8 = count3.exists() and count3.read_text().count("x") > 0
        recs = all_records(clone)
        u8 = next((x for x in recs if x.get("id") == "r8"), None)
        check("P0-8a uncertain execution NEVER auto-reruns", not ran8)
        check("P0-8b uncertain execution recorded as UNPROVEN refusal",
              u8 is not None and u8.get("unproven") is True
              and "UNPROVEN" in u8.get("reason", ""), str(u8)[:300])

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
        check("P0-15 budget survives fresh request ids (plan+argv-keyed)",
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

    print("FAILS:", FAILS or "none")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
