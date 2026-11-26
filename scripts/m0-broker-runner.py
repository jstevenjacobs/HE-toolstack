#!/usr/bin/env python3
"""m0-broker-runner.py — M0 interview protocol §3.3/§3.4 plan-gated broker (rev-5).

Runs as the m0broker account (systemd). Fails CLOSED everywhere: an unverifiable plan
authorizes nothing; unchecked git failures stop the loop rather than continue on stale
state; nothing is ever "processed" until its evidence is durably stored AND pushed.

rev-5 repairs (ChatGPT re-pin-3 REJECT at 1ce2b3c — the five P0s):
- DURABLE REQUEST STATE: every request carries a lifecycle file under
  <state_dir>/state (started BEFORE exec, executed after, published after a
  confirmed push). The in-memory processed-set is gone; a systemd restart cannot
  replay an executed operation.
- UNPROVEN semantics: a request whose state reads "started" at recovery time
  (crash during/after exec, outcome uncertain) NEVER auto-reruns. The broker
  writes an UNPROVEN refusal record; a second attempt requires a separate,
  explicit owner recovery decision.
- Evidence durability: record/refusal files are authored in broker-owned
  <state_dir> FIRST and copied into the evidence worktree at publish time, so
  `git reset --hard` or a failed push can never destroy unpublished evidence.
- No silent drops: every queue line gets a broker-committed disposition —
  valid+authorized executes; valid+unauthorized refuses; malformed JSON and
  missing/invalid request IDs produce invalid-request refusal records.
- Real --once mode (default: exactly one fetch/process/publish cycle, then exit;
  exit 3 if publication is pending). --daemon loops. Rev-4's prompt claimed
  --once existed; it did not — correction on record, ChatGPT re-pin-3 §3.
- Owner principal is read from broker config, matching §3.3 (rev-4 doc said the
  plan declared it; the protocol text is corrected to match this code).

Not installed or run until protocol ACCEPT and owner-run provisioning (m0-broker-setup.sh).
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, subprocess, sys, time
from pathlib import Path

PLAN_PATH = "workflows/m0-plans/open.json"
PLAN_SIG_PATH = "workflows/m0-plans/open.json.sig"  # ssh-keygen -Y sign writes <file>.sig
QUEUE_PATH = "workflows/m0-evidence/requests.jsonl"
RECORD_DIR = "workflows/m0-evidence/records"
REFUSAL_DIR = "workflows/m0-evidence/refusals"
PUSH_FAIL_LIMIT = 5
STATE_DEFAULT = "/opt/m0-broker/state"

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

def durable_write(path: Path, obj) -> None:
    """Atomic write: temp file in the same directory, then rename."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2))
    os.replace(tmp, path)

class Ledger:
    """Durable per-request state + evidence, OUTSIDE the git worktree (a
    `reset --hard` between passes must never destroy execution history)."""
    def __init__(self, root: str):
        self.root = Path(root)
    def state(self, rid: str) -> Path:
        return self.root / "state" / f"{rid}.json"
    def record(self, rid: str) -> Path:
        return self.root / "records" / f"{rid}.json"
    def refusal(self, rid: str) -> Path:
        return self.root / "refusals" / f"{rid}.json"
    def load(self, rid: str) -> dict | None:
        p = self.state(rid)
        return json.loads(p.read_text()) if p.exists() else None
    def save(self, rid: str, status: str, note: str = "", req_hash: str = "") -> None:
        durable_write(self.state(rid), {
            "id": rid, "status": status, "updated": now(), "note": note,
            "request_line_sha256": req_hash})
    def pending(self) -> list[str]:
        """IDs with a local disposition not yet confirmed pushed."""
        out = []
        d = self.root / "state"
        if d.is_dir():
            for f in d.glob("*.json"):
                try:
                    st = json.loads(f.read_text())
                except json.JSONDecodeError:
                    continue
                if st.get("status") in ("executed", "dispositioned"):
                    out.append(st["id"])
        return out

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

def refuse(L: Ledger, rid: str, reason: str, req_hash: str = "",
           extra: dict | None = None) -> None:
    """Durably author a refusal record + mark the request dispositioned. Refusals
    have no side effects, so this is safe to record before any push."""
    body = {"id": rid, "refused_at": now(), "request_line_sha256": req_hash,
            "reason": reason}
    if extra:
        body.update(extra)
    durable_write(L.refusal(rid), body)
    L.save(rid, "dispositioned", note=reason, req_hash=req_hash)
    log(f"REFUSED {rid}: {reason}")

def run_pass(a, allowed_signers: Path, L: Ledger) -> int:
    """One fetch/process/publish cycle. Returns 0 ok, 2 fetch/reset failure,
    3 publication still pending (caller retries or exits)."""
    try:
        git_checked(a.repo, "fetch", "origin", a.branch)
        git_checked(a.repo, "reset", "--hard", f"origin/{a.branch}")
    except RuntimeError as e:
        log(f"PASS FAIL (fetch/reset): {e}")
        return 2
    plan = verify_plan(a.repo, allowed_signers, a.owner_principal)
    q = Path(a.repo) / QUEUE_PATH
    lines = q.read_text().splitlines() if q.exists() else []

    for raw in lines:
        if not raw.strip():
            continue
        req_hash = hashlib.sha256(raw.encode()).hexdigest()
        # --- every line gets a disposition: nothing disappears silently (rev-5 P0) ---
        try:
            req = json.loads(raw)
            if not isinstance(req, dict):
                raise json.JSONDecodeError("not an object", raw, 0)
        except json.JSONDecodeError as e:
            rid = f"invalid-{req_hash[:16]}"
            if not L.load(rid):
                refuse(L, rid, f"invalid-request: malformed queue line ({e})", req_hash)
            continue
        rid = req.get("id")
        if not isinstance(rid, str) or not rid or not rid.replace("-", "").replace("_", "").isalnum():
            rid = f"noid-{req_hash[:16]}"
            if not L.load(rid):
                refuse(L, rid, "invalid-request: missing or invalid request id", req_hash)
            continue
        st = L.load(rid)
        if st and st.get("status") in ("started",):
            # outcome UNCERTAIN after a crash: never re-execute automatically.
            refuse(L, rid,
                   "UNPROVEN: execution was started before a broker restart and its outcome "
                   "is uncertain; re-execution requires a separate explicit owner recovery "
                   "decision (§3.3 rev-5)", req_hash,
                   extra={"unproven": True, "started_note": st.get("note", "")})
            continue
        if st and st.get("status") in ("executed", "dispositioned", "published"):
            continue  # already decided; publish step handles pending ones
        argv = req.get("argv")
        own_digest = canonical_sha256(argv) if isinstance(argv, list) else ""
        entry = plan["commands"].get(own_digest)
        if entry is None:
            reason = plan.get("why") or "digest not in owner-signed open plan (§3.3)"
            refuse(L, rid, reason, req_hash, extra={
                "runner_computed_digest": own_digest,
                "caller_supplied_digest": req.get("command_digest")})
            continue
        # execution lifecycle: started BEFORE the subprocess (durable)
        started = now()
        durable_note = f"argv={json.dumps(entry['argv'])}"
        L.save(rid, "started", note=durable_note, req_hash=req_hash)
        err = None
        try:
            cp = subprocess.run(entry["argv"], capture_output=True, text=True,
                                timeout=3600, cwd=a.repo)
            exit_code, stdout, stderr = cp.returncode, cp.stdout, cp.stderr
        except subprocess.TimeoutExpired:
            exit_code, stdout, stderr, err = None, "", "", "TIMEOUT exceeded 3600s"
        durable_write(L.record(rid), {
            "id": rid, "wave": plan["wave"], "plan_digest": plan.get("plan_digest"),
            "signed_by": plan.get("signed_by"),
            "started": started, "ended": now(),
            "request_line_sha256": req_hash, "request_raw": raw,
            "argv": entry["argv"], "runner_computed_digest": own_digest,
            "caller_supplied_digest": req.get("command_digest"),
            "exit": exit_code, "stdout": stdout, "stderr": stderr,
            "error": err,
            "artifact_digests": digest_artifacts(Path(a.repo), entry["artifacts"])})
        L.save(rid, "executed", note="record written; publication pending",
               req_hash=req_hash)
        log(f"EXECUTED {rid} exit={exit_code}")

    # ---- publish: copy durable evidence into the worktree, commit, push ----
    pend = L.pending()
    if not pend:
        return 0
    for rid in pend:
        for src, reldir in ((L.record(rid), RECORD_DIR), (L.refusal(rid), REFUSAL_DIR)):
            if src.exists():
                dest = Path(a.repo) / reldir / f"{rid}.json"
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(src.read_text())
    paths = [str(Path(a.repo) / d) for d in (RECORD_DIR, REFUSAL_DIR)
             if (Path(a.repo) / d).exists()]
    if not paths:
        return 3
    try:
        git_checked(a.repo, "add", *paths)
        staged = subprocess.run(("git", "-C", a.repo, "diff", "--cached", "--quiet"),
                                capture_output=True, text=True)
        if staged.returncode != 0:  # rc=1 means changes staged — the normal path
            git_checked(a.repo, "commit",
                        "-m", f"broker({a.branch}): {len(pend)} records {now()}")
        git_checked(a.repo, "push", "origin", a.branch)
    except RuntimeError as e:
        log(f"evidence publication FAILED (state kept, will retry): {e}")
        return 3
    for rid in pend:
        st = L.load(rid) or {"id": rid}
        durable_write(L.state(rid), {**st, "status": "published", "updated": now()})
    log(f"published {len(pend)} dispositions (durable, confirmed push)")
    return 0

def main() -> None:
    c = load_config()
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=c.get("repo", "/opt/m0-broker/evidence"))
    ap.add_argument("--branch", default=c.get("branch", "m0-evidence"))
    ap.add_argument("--poll", type=int, default=c.get("poll", 10))
    ap.add_argument("--state-dir", default=c.get("state_dir", STATE_DEFAULT))
    ap.add_argument("--allowed-signers", default=c.get(
        "allowed_signers", str(Path.home() / ".ssh" / "m0-allowed-signers")))
    ap.add_argument("--owner-principal", default=c.get("owner_principal", ""))
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--daemon", action="store_true", help="loop mode (systemd)")
    mode.add_argument("--once", action="store_true",
                      help="exactly one fetch/process/publish cycle, then exit (default)")
    ap.add_argument("--verify", action="store_true",
                    help="self-check deps and plan-verify path, then exit 0/1")
    a = ap.parse_args()
    allowed_signers = Path(a.allowed_signers)
    L = Ledger(a.state_dir)

    if a.verify:
        problems = []
        if not a.owner_principal:
            problems.append("owner_principal not configured")
        if not allowed_signers.exists():
            problems.append(f"allowed_signers missing: {allowed_signers}")
        if not Path(a.repo).is_dir():
            problems.append(f"evidence repo clone missing: {a.repo}")
        try:
            Path(a.state_dir).mkdir(parents=True, exist_ok=True)
        except OSError as e:
            problems.append(f"state_dir not writable: {a.state_dir} ({e})")
        if Path(a.repo).is_dir():
            v = verify_plan(a.repo, allowed_signers, a.owner_principal)
            if v.get("why", "").startswith("plan signature FAILED"):
                problems.append("plan signature verification path errors")
        for p in problems:
            log(f"VERIFY FAIL: {p}")
        if problems:
            sys.exit(1)
        log("VERIFY OK: config, signer file, repo clone, state dir, verification path")
        return

    if a.daemon:
        push_fails = 0
        while True:
            rc = run_pass(a, allowed_signers, L)
            if rc == 2:
                push_fails += 1
                if push_fails >= PUSH_FAIL_LIMIT:
                    sys.exit(2)   # visible failure; systemd backoff restart
                time.sleep(a.poll * 3)
            elif rc == 3:
                push_fails += 1
                if push_fails >= PUSH_FAIL_LIMIT:
                    sys.exit(3)
                time.sleep(a.poll * 3)
            else:
                push_fails = 0
                time.sleep(a.poll)
    else:
        sys.exit(run_pass(a, allowed_signers, L))

if __name__ == "__main__":
    main()
