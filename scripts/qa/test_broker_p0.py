#!/usr/bin/env python3
"""Exercise rev-5 P0 repairs (ChatGPT re-pin-3 REJECT items) against the broker.

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
  P0-10 --once                  -> exactly one cycle; process exits on its own
  P0-11 revoke script           -> selective by fingerprint; owner key retained;
                                  per-credential verification record correct
Usage: python3 scripts/qa/test_broker_p0.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
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


def write_plan(clone, argv_lists):
    cmds = [{"argv": a, "artifacts": []} for a in argv_lists]
    plan = {"wave": "0", "commands": cmds,
            "plan_digest": canon(sorted(canon(c["argv"]) for c in cmds))}
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
    body["commands"].append({"argv": extra_argv, "artifacts": []})
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


def run_broker(tmp, home, *flags):
    """A FRESH runner process per call — exactly what a systemd restart gives."""
    env = dict(os.environ, HOME=str(home))
    return subprocess.run(
        [sys.executable, str(RUNNER), "--branch", "m0-evidence", *flags],
        capture_output=True, text=True, env=env, timeout=120)


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
        cmds2 = [{"argv": c2_argv, "artifacts": []}]
        pf.write_text(json.dumps({"wave": "0", "commands": cmds2,
                                  "plan_digest": canon([canon(c2_argv)])}))
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

        # P0-10 --once performs exactly one cycle and exits (process exit proves it).
        r10 = run_broker(tmp, home, "--once")
        check("P0-10 --once exits after a single cycle",
              r10.returncode in (0, 3) and r10.returncode != 2)

        # P0-11 revoke script: selective revocation, owner key retained.
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
            rv = subprocess.run(
                ["bash", str(REVOKE), "--revoke", str(ak)],
                capture_output=True, text=True,
                env=dict(os.environ,
                         M0_REVOKE_FPR=f"{fpr['hermes1']} {fpr['hermes2']}",
                         M0_RECOVERY=f"keep:{fpr['ownerkeep']}",
                         CUTOVER_DIR=str(Path(tmp) / "cutover")))
            remaining = ak.read_text()
            verif = (Path(tmp) / "cutover" / "cutover-verification.txt")
            vt = verif.read_text() if verif.exists() else ""
            check("P0-11a revoke is SELECTIVE (Hermes keys gone, owner key kept)",
                  rv.returncode == 0
                  and kh["hermes1"] not in remaining and kh["hermes2"] not in remaining
                  and kh["ownerkeep"] in remaining, rv.stdout[-300:] + rv.stderr[-200:])
            check("P0-11b per-credential verification record correct",
                  vt.count("ABSENT (revoked OK)") == 2
                  and "PRESENT (owner recovery retained OK)" in vt, vt[:400])
            rv2 = subprocess.run(
                ["bash", str(REVOKE), "--revoke", str(ak)],
                capture_output=True, text=True,
                env=dict(os.environ, M0_REVOKE_FPR=fpr["hermes1"]))  # M0_RECOVERY unset
            check("P0-11c refuses to run without declared recovery path",
                  rv2.returncode != 0 and "M0_RECOVERY" in rv2.stdout + rv2.stderr)
        else:
            check("P0-11 skipped (no ssh-keygen)", False)

    print("FAILS:", FAILS or "none")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
