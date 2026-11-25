#!/usr/bin/env python3
"""Exercise rev-4 P0 repairs (ChatGPT round-3 REJECT items) against the broker.

Real mechanisms, no mocks: ssh-keygen -Y sign/verify for plan authorization and a
local bare git remote for the publish path. No network. Checks:
  P0-1 unsigned plan           -> nothing executes; refusal recorded ON RECORD
  P0-2 tampered plan           -> signature FAILED -> refusals on record
  P0-3 signed plan, in-plan    -> executes; record has full capture fields
  P0-4 out-of-plan argv        -> refusal record, never executed
  P0-5 evidence pushed         -> broker commits visible on the remote branch
Usage: python3 scripts/qa/test_broker_p0.py
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "scripts" / "m0-broker-runner.py"
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
        "allowed_signers": str(signers), "owner_principal": PRINCIPAL}))
    return clone, key, home


def stage_and_push(clone, msg):
    sh("git", "add", "-A", cwd=clone)
    sh("git", "commit", "-m", msg, cwd=clone)
    sh("git", "push", "origin", "m0-evidence", cwd=clone)


def write_plan(clone, argv_lists):
    cmds = [{"argv": a, "artifacts": []} for a in argv_lists]
    # runner rule: plan_digest = sha256 over the SORTED list of per-argv digests
    plan = {"wave": "0", "commands": cmds,
            "plan_digest": canon(sorted(canon(c["argv"]) for c in cmds))}
    pf = clone / "workflows/m0-plans/open.json"
    pf.parent.mkdir(parents=True, exist_ok=True)
    pf.write_text(json.dumps(plan))
    for stale in (pf.parent / "open.json.sig", pf.parent / "open.sig"):
        if stale.exists():
            stale.unlink()   # stale sig must never follow a new plan body
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
    """Attack sim: a plan author pushes a plan that no longer matches the
    owner's signature — exactly what rev-4 verification must catch."""
    auth = authority_clone(tmp)
    pf = auth / "workflows/m0-plans/open.json"
    body = json.loads(pf.read_text())
    body["commands"].append({"argv": extra_argv, "artifacts": []})
    pf.write_text(json.dumps(body))
    stage_and_push(auth, "tamper (attack sim)")


def sign_plan_authority(tmp, key):
    """The owner's own clone: sign the plan there (signer's private key lives
    only with the owner), push plan+sig."""
    auth = authority_clone(tmp)
    pf = auth / "workflows/m0-plans/open.json"
    for stale in (pf.parent / "open.json.sig", pf.parent / "open.sig"):
        if stale.exists():
            stale.unlink()
    r = sh("ssh-keygen", "-Y", "sign", "-f", str(key), "-n", "file", str(pf))
    assert r.returncode == 0, r.stderr
    stage_and_push(auth, "plan + owner signature")


def enqueue(clone, reqs):
    """As Hermes would: the queue reaches the broker via the REMOTE branch
    (the runner reset --hard's to origin at loop start). Sync first — the
    authority clone may have advanced the branch."""
    q = clone / "workflows/m0-evidence/requests.jsonl"
    sh("git", "pull", "--rebase", "origin", "m0-evidence", cwd=clone)
    q.parent.mkdir(parents=True, exist_ok=True)
    q.write_text("".join(json.dumps(r) + "\n" for r in reqs))
    sh("git", "add", "-A", cwd=clone)
    sh("git", "commit", "-m", "requests", cwd=clone)
    sh("git", "push", "origin", "m0-evidence", cwd=clone)


def run_broker(tmp, home):
    env = dict(os.environ, HOME=str(home))
    return subprocess.run(
        [sys.executable, str(RUNNER), "--branch", "m0-evidence"],
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
        clone, key, home = make_env(tmp)

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
        # and they're real content on the remote, not local-only
        show = sh("git", "show", "--stat", "--format=", "m0-evidence", cwd=str(remote))
        check("P0-5b pushed diff contains record files",
              "m0-evidence/records" in show.stdout or "m0-evidence/refusals" in show.stdout)

    print("FAILS:", FAILS or "none")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
