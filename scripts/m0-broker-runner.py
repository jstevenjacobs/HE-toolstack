#!/usr/bin/env python3
"""m0-broker-runner.py — M0 interview protocol §3.3/§3.4 plan-gated broker (DRAFT).

Runs as the m0broker account (systemd). Hermes has no credentials for this account.
Loop: fetch the evidence repo's request queue branch -> for each new request, accept
ONLY if its command digest is listed in the currently open wave's signed plan; execute;
push the full capture record (request, argv, timestamps, exit code, full stdout/stderr,
artifact digests) back to the evidence branch under the broker's own key. Every refusal
is itself committed as a refusal record (a detected bypass attempt, §3.3).

This draft is committed for council review at the rev-3 pin. It is NOT installed or run
until the protocol is council-ACCEPTED and the owner executes m0-broker-setup.sh in
Wave 0. Queue/branch layout finalized in the Wave-0 plan file.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess, time
from pathlib import Path

PLAN_PATH = "workflows/m0-plans/open.json"          # {wave, plan_digest, commands:[{digest, argv:[...]}]}
QUEUE_PATH = "workflows/m0-evidence/requests.jsonl"   # append-only request lines pushed by Hermes
RECORD_DIR = "workflows/m0-evidence/records"          # broker-authored capture records
REFUSAL_DIR = "workflows/m0-evidence/refusals"        # broker-authored refusal records


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def git(repo: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(("git", "-C", repo, *args), capture_output=True, text=True)


def load_plan(repo: str) -> dict:
    p = Path(repo) / PLAN_PATH
    if not p.exists():
        return {"commands": []}
    plan = json.loads(p.read_text())
    listed = {c["digest"]: c["argv"] for c in plan.get("commands", [])}
    # plan integrity: recomputed digest over argv list must equal plan_digest
    canon = json.dumps([listed[d] for d in sorted(listed)], sort_keys=True).encode()
    if hashlib.sha256(canon).hexdigest() != plan.get("plan_digest", ""):
        return {"commands": []}   # tampered/unverified plan -> nothing is executable
    return {"commands": listed, "wave": plan.get("wave")}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--branch", default="m0-evidence")
    ap.add_argument("--poll", type=int, default=10)
    a = ap.parse_args()

    processed: set[str] = set()
    while True:
        git(a.repo, "fetch", "origin", a.branch)
        git(a.repo, "reset", "--hard", f"origin/{a.branch}")
        plan = load_plan(a.repo)
        q = Path(a.repo) / QUEUE_PATH
        new_requests = []
        if q.exists():
            for line in q.read_text().splitlines():
                try:
                    req = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rid = req.get("id")
                if rid and rid not in processed:
                    new_requests.append(req)
                    processed.add(rid)

        for req in new_requests:
            rid = req["id"]
            digest = req.get("command_digest", "")
            argv = req.get("argv")
            if digest not in plan["commands"] or (argv and argv != plan["commands"][digest]):
                # §3.3 refusal record — visible to council, never silently dropped
                dest = Path(a.repo) / REFUSAL_DIR / f"{rid}.json"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps({
                    "id": rid, "refused_at": now(), "command_digest": digest,
                    "reason": "digest not in currently open signed plan (§3.3)",
                }, indent=2))
            else:
                t0 = now()
                cp = subprocess.run(argv, capture_output=True, text=True, timeout=3600)
                rec = {
                    "id": rid, "wave": plan.get("wave"), "started": t0, "ended": now(),
                    "argv": argv, "exit": cp.returncode,
                    "stdout": cp.stdout, "stderr": cp.stderr,
                }
                dest = Path(a.repo) / RECORD_DIR / f"{rid}.json"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps(rec, indent=2))

        if not new_requests:
            time.sleep(a.poll)
            continue

        git(a.repo, "add", RECORD_DIR, REFUSAL_DIR)
        if git(a.repo, "diff", "--cached", "--quiet").returncode != 0:
            msg = f"broker({a.branch}): {len(new_requests)} request records at {now()}"
            git(a.repo, "commit", "-m", msg)
            git(a.repo, "push", "origin", a.branch)


if __name__ == "__main__":
    main()
