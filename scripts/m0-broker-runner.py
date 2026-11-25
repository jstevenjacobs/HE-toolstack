#!/usr/bin/env python3
"""m0-broker-runner.py — M0 interview protocol §3.3/§3.4 plan-gated broker (rev-4).

Runs as the m0broker account (systemd). Fails CLOSED everywhere: an unverifiable plan
authorizes nothing; unchecked git/push failures stop the loop rather than continue on
stale state; a request is only marked processed after its record is committed AND pushed
successfully.

rev-4 repairs (ChatGPT round-3 P0/P1 at cf4a804):
- Plan AUTHENTICATION: open.json must carry an OpenSSH detached signature (open.sig)
  verifiable against the owner-pinned allowed_signers file (`ssh-keygen -Y verify`,
  namespace "file"). A matching digest is consistency; the signature is authorization.
  Unverifiable plan -> nothing executes; every request is refused on-record.
- Request digest is COMPUTED by the runner from argv (canonical sha256); the
  caller-supplied digest is never trusted, only recorded.
- Every git/push result is checked; repeated push failure exits non-zero so systemd
  restarts under the unit's backoff (fail visible, not silent).
- Processed-marking happens only after a successful push (a failed evidence publish
  cannot make requests disappear).
- Capture records now include the raw request line and digests of plan-declared
  artifact paths (missing artifacts are recorded as MISSING, never omitted).
- Commits are expected to be GPG/SSH-signed via broker git config (configured at
  provisioning); the council verifies commit authorship with `git verify-commit`.

Not installed or run until protocol ACCEPT and owner-run provisioning (m0-broker-setup.sh).
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, subprocess, sys, time
from pathlib import Path

PLAN_PATH = "workflows/m0-plans/open.json"
PLAN_SIG_PATH = "workflows/m0-plans/open.json.sig"  # ssh-keygen -Y sign writes <file>.sig
QUEUE_PATH = "workflows/m0-evidence/requests.jsonl"
RECORD_DIR = "workflows/m0-evidence/records"
REFUSAL_DIR = "workflows/m0-evidence/refusals"
PUSH_FAIL_LIMIT = 5

def now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()

def log(msg: str) -> None:
    print(f"[m0-broker {now()}] {msg}", flush=True)

def git_checked(repo: str, *args: str) -> str:
    r = subprocess.run(("git", "-C", repo, *args), capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed rc={r.returncode}: {r.stderr.strip()[:400]}")
    return r.stdout.strip()

def canonical_sha256(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

def verify_plan(repo: str, allowed_signers: Path, principal: str) -> dict:
    """Return {commands:{digest: {argv, artifacts}}, wave, plan_digest} ONLY if the
    plan file is owner-signed and internally consistent. Fail closed otherwise."""
    plan_file, sig_file = Path(repo) / PLAN_PATH, Path(repo) / PLAN_SIG_PATH
    if not (plan_file.exists() and sig_file.exists() and allowed_signers.exists()):
        return {"commands": {}, "wave": None, "why": "plan/sig/allowed_signers missing"}
    v = subprocess.run(
        ("ssh-keygen", "-Y", "verify", "-f", str(allowed_signers), "-I", principal,
         "-n", "file", "-s", str(sig_file)),
        stdin=open(plan_file, "rb"), capture_output=True, text=True)
    if v.returncode != 0:
        return {"commands": {}, "wave": None,
                "why": f"plan signature FAILED owner verification: {v.stderr.strip()[:300]}"}
    try:
        plan = json.loads(plan_file.read_text())
    except json.JSONDecodeError as e:
        return {"commands": {}, "wave": None, "why": f"plan JSON invalid: {e}"}
    commands = {}
    for c in plan.get("commands", []):
        argv = c.get("argv")
        if isinstance(argv, list) and all(isinstance(x, str) for x in argv):
            # runner computes the authoritative digest itself
            commands[canonical_sha256(argv)] = {"argv": argv, "artifacts": c.get("artifacts", [])}
        else:
            return {"commands": {}, "wave": None, "why": "plan entry argv malformed"}
    digests_sorted = [canonical_sha256(commands[d]["argv"]) for d in sorted(commands)]
    if canonical_sha256(digests_sorted) != plan.get("plan_digest", ""):
        return {"commands": {}, "wave": None, "why": "plan_digest does not match command set"}
    return {"commands": commands, "wave": plan.get("wave"),
            "plan_digest": plan.get("plan_digest"), "signed_by": principal}

def digest_artifacts(base: Path, artifacts: list) -> dict:
    out = {}
    for rel in artifacts:
        p = base / rel
        out[rel] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"
    return out

def load_config() -> dict:
    """Broker config written at provisioning; systemd needs no CLI flags."""
    cfg = Path.home() / ".m0-broker.json"
    if cfg.exists():
        try:
            return json.loads(cfg.read_text())
        except json.JSONDecodeError:
            return {}
    return {}

def main() -> None:
    c = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=c.get("repo", "/opt/m0-broker/evidence"))
    ap.add_argument("--branch", default=c.get("branch", "m0-evidence"))
    ap.add_argument("--poll", type=int, default=c.get("poll", 10))
    ap.add_argument("--allowed-signers", default=c.get(
        "allowed_signers", str(Path.home() / ".ssh" / "m0-allowed-signers")))
    ap.add_argument("--owner-principal", default=c.get("owner_principal", ""))
    ap.add_argument("--daemon", action="store_true", help="loop mode (systemd)")
    ap.add_argument("--verify", action="store_true",
                    help="self-check deps and plan-verify path, then exit 0/1")
    a = ap.parse_args()
    allowed_signers = Path(a.allowed_signers)

    if a.verify:
        # Provisioning gate: everything the loop needs must exist and work.
        problems = []
        if not a.owner_principal:
            problems.append("owner_principal not configured")
        if not allowed_signers.exists():
            problems.append(f"allowed_signers missing: {allowed_signers}")
        if not Path(a.repo).is_dir():
            problems.append(f"evidence repo clone missing: {a.repo}")
        else:
            v = verify_plan(a.repo, allowed_signers, a.owner_principal)
            # An absent/unsigned plan is a VALID state before Wave 0 (plan is
            # drafted during Wave 0); the check is that the verify PATH works.
            if v.get("why", "").startswith("plan signature FAILED"):
                problems.append("plan signature verification path errors")
        for p in problems:
            log(f"VERIFY FAIL: {p}")
        if problems:
            sys.exit(1)
        log("VERIFY OK: config, signer file, repo clone, verification path")
        return

    processed: set[str] = set()
    push_failures = 0
    passes = 0
    max_passes = 2 if not a.daemon else 10**9
    while passes < max_passes:
        passes += 1
        try:
            git_checked(a.repo, "fetch", "origin", a.branch)
            git_checked(a.repo, "reset", "--hard", f"origin/{a.branch}")
        except RuntimeError as e:
            push_failures += 1
            log(f"FATAL loop: {e}")
            if push_failures >= PUSH_FAIL_LIMIT:
                sys.exit(2)   # systemd restarts with backoff; never run on unverifiable state
            time.sleep(a.poll * 3)
            continue

        plan = verify_plan(a.repo, allowed_signers, a.owner_principal)
        q = Path(a.repo) / QUEUE_PATH
        batch = []
        if q.exists():
            for line in q.read_text().splitlines():
                try:
                    req = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rid = req.get("id")
                if rid and rid not in processed:
                    batch.append((line, req))

        if not batch:
            time.sleep(a.poll)
            continue

        authored = 0
        for raw_line, req in batch:
            rid, argv = req["id"], req.get("argv")
            req_hash = hashlib.sha256(raw_line.encode()).hexdigest()
            # authoritative digest computed HERE, from the argv the runner would run
            own_digest = canonical_sha256(argv) if isinstance(argv, list) else ""
            entry = plan["commands"].get(own_digest)
            if entry is None:
                reason = plan.get("why") or "digest not in owner-signed open plan (§3.3)"
                dest = Path(a.repo) / REFUSAL_DIR / f"{rid}.json"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(json.dumps({
                    "id": rid, "refused_at": now(), "request_line_sha256": req_hash,
                    "runner_computed_digest": own_digest,
                    "caller_supplied_digest": req.get("command_digest"),
                    "reason": reason,
                }, indent=2))
                authored += 1
                log(f"REFUSED {rid}: {reason}")
                continue
            started = now()
            err = None
            try:
                cp = subprocess.run(entry["argv"], capture_output=True, text=True,
                                    timeout=3600, cwd=a.repo)
                exit_code, stdout, stderr = cp.returncode, cp.stdout, cp.stderr
            except subprocess.TimeoutExpired:
                exit_code, stdout, stderr, err = None, "", "", "TIMEOUT exceeded 3600s"
            dest = Path(a.repo) / RECORD_DIR / f"{rid}.json"
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(json.dumps({
                "id": rid, "wave": plan["wave"], "plan_digest": plan.get("plan_digest"),
                "signed_by": plan.get("signed_by"),
                "started": started, "ended": now(),
                "request_line_sha256": req_hash, "request_raw": raw_line,
                "argv": entry["argv"], "runner_computed_digest": own_digest,
                "caller_supplied_digest": req.get("command_digest"),
                "exit": exit_code, "stdout": stdout, "stderr": stderr,
                "error": err,
                "artifact_digests": digest_artifacts(Path(a.repo), entry["artifacts"]),
            }, indent=2))
            authored += 1

        paths = [str(Path(a.repo) / d) for d in (RECORD_DIR, REFUSAL_DIR)
                 if (Path(a.repo) / d).exists()]
        if not paths:
            time.sleep(a.poll)
            continue
        git_checked(a.repo, "add", *paths)
        # rc=1 from `diff --cached --quiet` means "staged changes exist" — not an error.
        staged = subprocess.run(("git", "-C", a.repo, "diff", "--cached", "--quiet"),
                                capture_output=True, text=True)
        if staged.returncode == 0:
            time.sleep(a.poll)
            continue   # nothing actually staged (e.g. race) — do not mark processed
        try:
            git_checked(a.repo, "commit",
                        "-m", f"broker({a.branch}): {authored} records {now()}")
            git_checked(a.repo, "push", "origin", a.branch)
        except RuntimeError as e:
            push_failures += 1
            log(f"evidence push FAILED ({push_failures}/{PUSH_FAIL_LIMIT}): {e}")
            if push_failures >= PUSH_FAIL_LIMIT:
                sys.exit(3)   # visible failure; requests stay unprocessed -> retried on restart
            time.sleep(a.poll * 3)
            continue
        push_failures = 0
        for _, req in batch:
            processed.add(req["id"])   # only now: evidence is published
        log(f"published {authored} records; processed={len(processed)}")

if __name__ == "__main__":
    main()
